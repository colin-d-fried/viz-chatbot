# Viz Chatbot

A Streamlit app that lets you upload a dataset and build visualizations through a chat interface, powered by the [Devin API](https://docs.devin.ai/api-reference/overview).

## How it works

1. Upload a dataset (CSV, Excel, JSON, or Parquet) via the sidebar
2. Choose a **Visualization Mode** — Devin (default, auto-selects library), Plotly, or a specific React library
3. Type a visualization request in the chat (e.g. *"show me sales by region as a bar chart"*)
4. The app uploads your data to Devin, triggers a session using the appropriate playbook, and polls for the result
5. The generated chart renders inline — follow-up requests reuse the same Devin session

Datasets larger than 500 rows are truncated before being sent to Devin. In Plotly mode the full dataset is used when rendering the final chart locally. In React modes the truncated JSON is embedded directly in the generated HTML.

## Visualization Modes

| Mode | Library | Best for | Example request |
|---|---|---|---|
| **Devin** *(default)* | Auto-selected (Plotly.js, recharts, visx, leaflet, vis.js) | Any visualization — Devin picks the best library | *"visualize this data"* |
| **Plotly (Python)** | Plotly Express / Graph Objects | Standard data charts (uses full dataset locally) | *"show me sales by region as a bar chart"* |
| **recharts** | Recharts (React) | Bar, line, pie, area charts | *"create a line chart of revenue over time"* |
| **visx** | visx (React) | Custom/artistic SVG visualizations | *"make a radial chart of category scores"* |
| **leaflet** | Leaflet | Maps and geographic data | *"show store locations on a map"* |
| **vis.js** | vis-network / vis-timeline | Network graphs, timelines | *"show a network graph of connections"* |

**Devin** mode is the default and recommended for most users — it analyses your data and request to choose the best library and chart type automatically. **Plotly (Python)** is the best choice when you need the full dataset (no 500-row truncation) rendered locally. The other modes let you force a specific React/JS library.

## Prerequisites

- Python 3.11+
- A Devin **Service User** API key (`cog_…`) and **Organization ID** (`org-…`) — both found under **Settings → Service Users** in Devin ([auth docs](https://docs.devin.ai/api-reference/authentication))

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

Copy `.env.example` to `.env` and add your credentials:

```bash
cp .env.example .env
```

```
DEVIN_API_KEY=cog_your_key_here
DEVIN_ORG_ID=org-your_org_id_here
```

Alternatively, leave `.env` empty and enter both values in the **Devin Credentials** section of the sidebar at runtime.

## Running

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501` by default.

## Project structure

```
viz-chatbot/
├── app.py                                # Streamlit UI — sidebar, chat loop, result rendering
├── devin_client.py                       # Devin v3 API wrapper (sessions, messages, polling)
├── prompt_builder.py                     # Playbook injection + prompt assembly (Plotly & React)
├── data_utils.py                         # Dataset loading, schema summary, upload/JSON truncation
├── code_extractor.py                     # Parses Python & HTML code blocks from Devin messages
├── playbooks/
│   ├── __init__.py
│   ├── devin_auto_builder.py             # Auto-select playbook — Devin picks the best library
│   ├── react_component_builder.py        # React/HTML playbook for CDN-based visualizations
│   └── README.md                         # Playbook registration & usage documentation
├── requirements.txt
└── .env.example
```

## Playbook Registration (Optional)

Playbooks are embedded inline by default. For more token-efficient follow-up
messages you can register them in Devin's UI:

1. Open **Settings → Playbooks** in the Devin dashboard
2. Create a playbook titled `devin-auto-visualization` (or `react-component-builder` for the React-only playbook)
3. Paste the playbook text from `playbooks/devin_auto_builder.py` (or `playbooks/react_component_builder.py`)
4. Pass the resulting `playbook_id` when creating sessions

See [`playbooks/README.md`](playbooks/README.md) for full details.

## Supported file formats

| Format | Extensions |
|---|---|
| CSV | `.csv` |
| Excel | `.xlsx`, `.xls` |
| JSON | `.json` |
| Parquet | `.parquet` |
