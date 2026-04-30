import re
import traceback
import pandas as pd

_CODE_BLOCK_RE = re.compile(r"```python\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)


def extract_code(messages: list[dict] | None) -> str | None:
    """Return the last Python code block found in Devin session messages."""
    for msg in reversed(messages or []):
        text = msg.get("message", "")
        matches = _CODE_BLOCK_RE.findall(text)
        if matches:
            return matches[-1].strip()
    return None


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
