import json
import re
import traceback

import pandas as pd
import requests

_CODE_BLOCK_RE = re.compile(r"```python\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)
_HTML_BLOCK_RE = re.compile(r"```html\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)
_ATTACHMENT_RE = re.compile(r'ATTACHMENT:\s*(\{[^}]+\})')
_DEPLOYED_URL_RE = re.compile(r'https://[a-z0-9-]+\.devinapps\.com')


def _devin_messages(messages: list[dict] | None) -> list[dict]:
    """Return only messages from Devin (source='devin'), preserving order."""
    return [m for m in (messages or []) if m.get("source") == "devin"]


def extract_code(messages: list[dict] | None) -> str | None:
    """Return the last Python code block found in Devin's messages."""
    for msg in reversed(_devin_messages(messages)):
        text = msg.get("message", "")
        matches = _CODE_BLOCK_RE.findall(text)
        if matches:
            return matches[-1].strip()
    return None


def extract_html(messages: list[dict] | None) -> str | None:
    """Return the last HTML code block found in Devin's messages.

    Falls back to fetching HTML from an ``ATTACHMENT:`` URL if no fenced
    ``html`` code block is present (Devin sometimes deploys the HTML and
    attaches the file instead of inlining it).
    """
    for msg in reversed(_devin_messages(messages)):
        text = msg.get("message", "")
        matches = _HTML_BLOCK_RE.findall(text)
        if matches:
            return matches[-1].strip()

    # Fallback 1: look for a publicly deployed devinapps.com URL.
    for msg in reversed(_devin_messages(messages)):
        text = msg.get("message", "")
        url_match = _DEPLOYED_URL_RE.search(text)
        if url_match:
            try:
                resp = requests.get(url_match.group(0), timeout=30)
                if resp.ok and "<!DOCTYPE" in resp.text[:100].upper():
                    return resp.text
            except requests.RequestException:
                continue

    # Fallback 2: look for an ATTACHMENT URL pointing to an .html file.
    for msg in reversed(_devin_messages(messages)):
        text = msg.get("message", "")
        att_match = _ATTACHMENT_RE.search(text)
        if att_match:
            try:
                att = json.loads(att_match.group(1))
                url = att.get("url", "")
                if url.endswith(".html"):
                    resp = requests.get(url, timeout=30)
                    if resp.ok:
                        return resp.text
            except (json.JSONDecodeError, requests.RequestException):
                continue
    return None


def extract_any_code(messages: list[dict] | None) -> tuple[str | None, str | None]:
    """Try HTML first, then Python. Returns ``(code_string, code_type)``."""
    html = extract_html(messages)
    if html:
        return html, "html"
    py = extract_code(messages)
    if py:
        return py, "python"
    return None, None


def execute_chart_code(code: str, df: pd.DataFrame):
    """
    Execute Plotly chart code with df in scope.
    Returns (figure, error_string). One of the two will always be None.
    """
    import plotly.express as px
    import plotly.graph_objects as go

    namespace = {
        "df": df,
        "pd": pd,
        "px": px,
        "go": go,
    }
    try:
        exec(code, namespace)  # noqa: S102
    except Exception:
        return None, traceback.format_exc()

    fig = namespace.get("fig")
    if fig is None:
        return None, "Code ran without errors but did not assign a variable named `fig`."
    return fig, None
