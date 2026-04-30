import os

import streamlit as st
from dotenv import load_dotenv

from code_extractor import execute_chart_code, extract_code
from data_utils import get_schema_summary, load_dataset, prepare_for_upload
from devin_client import DevinAPIError, DevinClient
from prompt_builder import build_followup_message, build_initial_prompt

load_dotenv()

st.set_page_config(page_title="Viz Chatbot", layout="wide")
st.title("Visualization Chatbot")

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
defaults = {
    "messages": [],          # list of chat message dicts
    "df": None,              # loaded DataFrame (full dataset)
    "source_key": None,      # fingerprint of the current dataset source
    "source_name": None,     # original filename / URL tail
    "attachment_url": None,  # URL returned by Devin after upload
    "devin_session_id": None,
    "devin_session_url": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def reset_conversation():
    st.session_state.messages = []
    st.session_state.devin_session_id = None
    st.session_state.devin_session_url = None


def reset_dataset():
    reset_conversation()
    st.session_state.df = None
    st.session_state.source_key = None
    st.session_state.source_name = None
    st.session_state.attachment_url = None


# ---------------------------------------------------------------------------
# Sidebar — dataset loading + API key
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Dataset")

    upload = st.file_uploader(
        "Upload a file",
        type=["csv", "xlsx", "xls", "json", "parquet"],
        help="Datasets larger than 500 rows are truncated when sent to Devin.",
    )
    url_input = st.text_input("Or enter a URL / file path")

    # Build a stable fingerprint so we only reload on actual source changes.
    if upload:
        source_key = f"file:{upload.name}:{upload.size}"
        source_name = upload.name
        raw_source = upload
    elif url_input.strip():
        source_key = f"url:{url_input.strip()}"
        source_name = url_input.strip().rstrip("/").split("/")[-1] or "dataset.csv"
        raw_source = url_input.strip()
    else:
        source_key = None
        source_name = None
        raw_source = None

    if source_key and source_key != st.session_state.source_key:
        try:
            df = load_dataset(raw_source)
            reset_dataset()
            st.session_state.df = df
            st.session_state.source_key = source_key
            st.session_state.source_name = source_name
            st.success(f"Loaded {df.shape[0]:,} rows × {df.shape[1]} columns")
        except Exception as exc:
            st.error(f"Failed to load dataset: {exc}")

    if st.session_state.df is not None:
        st.dataframe(st.session_state.df.head(10), use_container_width=True)

    st.divider()

    st.header("Devin API Key")
    api_key = st.text_input(
        "API Key",
        value=os.getenv("DEVIN_API_KEY", ""),
        type="password",
        help="Create a Service User key (cog_…) in Devin Settings.",
    )

    st.divider()

    if st.button("New Conversation", use_container_width=True):
        reset_conversation()
        st.rerun()

    if st.session_state.devin_session_url:
        st.markdown(f"[Open in Devin]({st.session_state.devin_session_url})")


# ---------------------------------------------------------------------------
# Helpers for rendering stored messages
# ---------------------------------------------------------------------------
def render_message(msg: dict):
    if msg["type"] == "text":
        st.markdown(msg["content"])
    elif msg["type"] == "chart":
        try:
            fig, err = execute_chart_code(msg["code"], st.session_state.df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                with st.expander("Generated code"):
                    st.code(msg["code"], language="python")
            else:
                st.warning(f"Could not re-render chart: {err}")
                st.code(msg["code"], language="python")
        except Exception as exc:
            st.warning(f"Could not re-render chart: {exc}")
    elif msg["type"] == "error":
        st.error(msg["content"])


# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        render_message(msg)

# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------
user_input = st.chat_input("Describe the visualization you want…")

if user_input:
    if st.session_state.df is None:
        st.warning("Please upload a dataset first.")
        st.stop()
    if not api_key:
        st.warning("Please enter your Devin API key in the sidebar.")
        st.stop()

    client = DevinClient(api_key)

    # Show user message immediately.
    with st.chat_message("user"):
        st.markdown(user_input)

    # Build + execute the Devin request, show assistant response inline.
    with st.chat_message("assistant"):
        try:
            with st.spinner("Working…"):
                # 1. Upload dataset once per session.
                if st.session_state.attachment_url is None:
                    data_bytes, filename = prepare_for_upload(
                        st.session_state.df, st.session_state.source_name or "dataset.csv"
                    )
                    st.session_state.attachment_url = client.upload_attachment(data_bytes, filename)

                # 2. Create a new Devin session or reuse the active one.
                if st.session_state.devin_session_id is None:
                    schema = get_schema_summary(st.session_state.df)
                    prompt = build_initial_prompt(
                        user_input, schema, st.session_state.attachment_url
                    )
                    session_id, session_url = client.create_session(prompt)
                    st.session_state.devin_session_id = session_id
                    st.session_state.devin_session_url = session_url
                else:
                    session_id = st.session_state.devin_session_id
                    client.send_message(session_id, build_followup_message(user_input))

                # 3. Block until Devin finishes.
                session = client.poll_until_done(session_id)

            # 4. Extract and execute the chart code.
            messages = session.get("messages") or []
            code = extract_code(messages)

            if code:
                fig, err = execute_chart_code(code, st.session_state.df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    with st.expander("Generated code"):
                        st.code(code, language="python")
                    # Persist chart for re-render on future runs.
                    st.session_state.messages.append(
                        {"role": "user", "type": "text", "content": user_input}
                    )
                    st.session_state.messages.append(
                        {"role": "assistant", "type": "chart", "code": code}
                    )
                else:
                    error_text = f"Devin returned code but it could not be executed:\n\n{err}\n\n```python\n{code}\n```"
                    st.error(error_text)
                    st.session_state.messages.append(
                        {"role": "user", "type": "text", "content": user_input}
                    )
                    st.session_state.messages.append(
                        {"role": "assistant", "type": "error", "content": error_text}
                    )
            else:
                # No code block — show whatever Devin said as plain text.
                devin_msgs = [m for m in messages if m.get("type") == "devin_message"]
                fallback = (
                    devin_msgs[-1]["message"]
                    if devin_msgs
                    else "Devin did not return a visualization. Try rephrasing your request."
                )
                st.markdown(fallback)
                st.session_state.messages.append(
                    {"role": "user", "type": "text", "content": user_input}
                )
                st.session_state.messages.append(
                    {"role": "assistant", "type": "text", "content": fallback}
                )

        except TimeoutError as exc:
            msg_text = str(exc)
            st.error(msg_text)
            st.session_state.messages.append(
                {"role": "user", "type": "text", "content": user_input}
            )
            st.session_state.messages.append(
                {"role": "assistant", "type": "error", "content": msg_text}
            )
        except DevinAPIError as exc:
            msg_text = f"Devin API error: {exc}"
            st.error(msg_text)
            st.session_state.messages.append(
                {"role": "user", "type": "text", "content": user_input}
            )
            st.session_state.messages.append(
                {"role": "assistant", "type": "error", "content": msg_text}
            )
