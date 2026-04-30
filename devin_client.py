import time
import requests

BASE_URL = "https://api.devin.ai"
POLL_INTERVAL = 5
DEFAULT_TIMEOUT = 600

# v3 terminal conditions: status is "exit", "error", or "suspended".
# When status is "running" with status_detail "finished" or "waiting_for_user",
# the task is also done (Devin has produced output).
_TERMINAL_STATUSES = {"exit", "error", "suspended"}


class DevinAPIError(Exception):
    pass


def _devin_id(session_id: str) -> str:
    """Ensure a session_id has the ``devin-`` prefix required by v3 paths."""
    if session_id.startswith("devin-"):
        return session_id
    return f"devin-{session_id}"


class DevinClient:
    """Thin wrapper around the Devin **v3** REST API.

    Requires a Service User API key (``cog_…``) and the organisation ID
    (``org-…``), both available under *Settings → Service Users* in the
    Devin web UI.
    """

    def __init__(self, api_key: str, org_id: str):
        self._auth = {"Authorization": f"Bearer {api_key}"}
        self._org_id = org_id
        self._org_base = f"{BASE_URL}/v3/organizations/{org_id}"

    def _json_headers(self) -> dict:
        return {**self._auth, "Content-Type": "application/json"}

    # ------------------------------------------------------------------
    # Attachments (still on v1 – no v3 equivalent)
    # ------------------------------------------------------------------
    def upload_attachment(self, data: bytes, filename: str) -> str:
        resp = requests.post(
            f"{BASE_URL}/v1/attachments",
            headers=self._auth,
            files={"file": (filename, data, "text/csv")},
        )
        if not resp.ok:
            raise DevinAPIError(f"Attachment upload failed ({resp.status_code}): {resp.text}")
        return resp.text.strip().strip('"')

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------
    def create_session(self, prompt: str, playbook_id: str | None = None) -> tuple[str, str]:
        """Create a new Devin session.  Returns ``(session_id, session_url)``."""
        payload: dict = {"prompt": prompt}
        if playbook_id:
            payload["playbook_id"] = playbook_id
        resp = requests.post(
            f"{self._org_base}/sessions",
            headers=self._json_headers(),
            json=payload,
        )
        if not resp.ok:
            raise DevinAPIError(f"Session creation failed ({resp.status_code}): {resp.text}")
        body = resp.json()
        return body["session_id"], body.get("url", "")

    def get_session(self, session_id: str) -> dict:
        resp = requests.get(
            f"{self._org_base}/sessions/{_devin_id(session_id)}",
            headers=self._auth,
        )
        if not resp.ok:
            raise DevinAPIError(f"Get session failed ({resp.status_code}): {resp.text}")
        return resp.json()

    def send_message(self, session_id: str, message: str) -> None:
        resp = requests.post(
            f"{self._org_base}/sessions/{_devin_id(session_id)}/messages",
            headers=self._json_headers(),
            json={"message": message},
        )
        if not resp.ok:
            raise DevinAPIError(f"Send message failed ({resp.status_code}): {resp.text}")

    def get_messages(self, session_id: str) -> list[dict]:
        """Fetch all messages for a session (paginated, auto-follows cursors)."""
        messages: list[dict] = []
        cursor: str | None = None
        while True:
            params: dict = {"first": 200}
            if cursor:
                params["after"] = cursor
            resp = requests.get(
                f"{self._org_base}/sessions/{_devin_id(session_id)}/messages",
                headers=self._auth,
                params=params,
            )
            if not resp.ok:
                raise DevinAPIError(f"Get messages failed ({resp.status_code}): {resp.text}")
            body = resp.json()
            messages.extend(body.get("items", []))
            if not body.get("has_next_page"):
                break
            cursor = body.get("end_cursor")
            if not cursor:
                break
        return messages

    # ------------------------------------------------------------------
    # Polling
    # ------------------------------------------------------------------
    @staticmethod
    def _is_done(session: dict) -> bool:
        status = session.get("status", "")
        if status in _TERMINAL_STATUSES:
            return True
        if status == "running" and session.get("status_detail") in (
            "finished",
            "waiting_for_user",
        ):
            return True
        return False

    def poll_until_done(self, session_id: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
        deadline = time.time() + timeout
        while time.time() < deadline:
            session = self.get_session(session_id)
            if self._is_done(session):
                return session
            time.sleep(POLL_INTERVAL)
        raise TimeoutError(
            f"Session did not finish within {timeout}s. "
            "Check the Devin session URL for status."
        )
