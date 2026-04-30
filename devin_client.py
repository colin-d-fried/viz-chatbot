import time
import requests

BASE_URL = "https://api.devin.ai"
POLL_INTERVAL = 5
TERMINAL_STATUSES = {"finished", "expired", "blocked"}
DEFAULT_TIMEOUT = 600


class DevinAPIError(Exception):
    pass


class DevinClient:
    def __init__(self, api_key: str):
        self._auth = {"Authorization": f"Bearer {api_key}"}

    def _json_headers(self) -> dict:
        return {**self._auth, "Content-Type": "application/json"}

    def upload_attachment(self, data: bytes, filename: str) -> str:
        resp = requests.post(
            f"{BASE_URL}/v1/attachments",
            headers=self._auth,
            files={"file": (filename, data, "text/csv")},
        )
        if not resp.ok:
            raise DevinAPIError(f"Attachment upload failed ({resp.status_code}): {resp.text}")
        return resp.text.strip().strip('"')

    def create_session(self, prompt: str, playbook_id: str | None = None) -> tuple[str, str]:
        """Returns (session_id, session_url)."""
        payload: dict = {"prompt": prompt}
        if playbook_id:
            payload["playbook_id"] = playbook_id
        resp = requests.post(
            f"{BASE_URL}/v1/sessions",
            headers=self._json_headers(),
            json=payload,
        )
        if not resp.ok:
            raise DevinAPIError(f"Session creation failed ({resp.status_code}): {resp.text}")
        body = resp.json()
        return body["session_id"], body.get("url", "")

    def get_session(self, session_id: str) -> dict:
        resp = requests.get(
            f"{BASE_URL}/v1/sessions/{session_id}",
            headers=self._auth,
        )
        if not resp.ok:
            raise DevinAPIError(f"Get session failed ({resp.status_code}): {resp.text}")
        return resp.json()

    def send_message(self, session_id: str, message: str) -> None:
        resp = requests.post(
            f"{BASE_URL}/v1/sessions/{session_id}/message",
            headers=self._json_headers(),
            json={"message": message},
        )
        if not resp.ok:
            raise DevinAPIError(f"Send message failed ({resp.status_code}): {resp.text}")

    def poll_until_done(self, session_id: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
        deadline = time.time() + timeout
        while time.time() < deadline:
            session = self.get_session(session_id)
            if session.get("status_enum") in TERMINAL_STATUSES:
                return session
            time.sleep(POLL_INTERVAL)
        raise TimeoutError(
            f"Session did not finish within {timeout}s. "
            "Check the Devin session URL for status."
        )
