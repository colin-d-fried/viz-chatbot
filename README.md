# Viz Chatbot

A Streamlit app that lets you upload a dataset and build visualizations through a chat interface, powered by the [Devin API](https://docs.devin.ai/api-reference/overview).

## How it works

1. Upload a dataset (CSV, Excel, JSON, or Parquet) via the sidebar
2. Type a visualization request in the chat (e.g. *"show me sales by region as a bar chart"*)
3. The app uploads your data to Devin, triggers a session using the **visualization-builder** playbook, and polls for the result
4. The generated Plotly chart renders inline — follow-up requests reuse the same Devin session

Datasets larger than 500 rows are truncated before being sent to Devin. The full dataset is always used when rendering the final chart locally.

## Prerequisites

- Python 3.11+
- A Devin API key — create a Service User key (`cog_…`) under **Settings → Service Users** in Devin

## Setup

```bash
git clone https://github.com/colin-d-fried/viz-chatbot.git
cd viz-chatbot

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and add your key:

```bash
cp .env.example .env
```

```
DEVIN_API_KEY=cog_your_key_here
```

Alternatively, leave `.env` empty and paste the key into the **Devin API Key** field in the sidebar at runtime.

## Running

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501` by default.

## Project structure

```
viz-chatbot/
├── app.py               # Streamlit UI — sidebar, chat loop, result rendering
├── devin_client.py      # Devin API wrapper (upload, create/poll/message session)
├── prompt_builder.py    # Inline visualization-builder playbook + prompt assembly
├── data_utils.py        # Dataset loading, schema summary, upload truncation
├── code_extractor.py    # Parses Python code blocks from Devin messages and executes them
├── requirements.txt
└── .env.example
```

## Supported file formats

| Format | Extensions |
|---|---|
| CSV | `.csv` |
| Excel | `.xlsx`, `.xls` |
| JSON | `.json` |
| Parquet | `.parquet` |
