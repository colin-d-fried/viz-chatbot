# Testing viz-chatbot

## Local Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Start the app: `streamlit run app.py --server.port 8501 --server.headless true`
3. Open `http://localhost:8501` in the browser

## Devin Secrets Needed

- `DEVIN_API_KEY` — Service User API key (starts with `cog_`). Created at Settings → Service Users in the Devin web UI.
- `DEVIN_ORG_ID` — Organization ID (starts with `org-`). Found at Settings → Service Users.

Both are auto-populated from environment variables if set. Otherwise, enter them in the sidebar.

## Test Dataset

A test dataset is available at `test_data.csv` in the repo root (8 rows × 4 columns: name, sales, region, date). Load it via the sidebar "Or enter a URL / file path" input.

## Testing Workflows

### Sidebar & Mode Defaults
- The "Visualization Mode" dropdown should default to "Devin" (first entry)
- All 6 modes should appear: Devin, Plotly (Python), recharts, visx, leaflet, vis.js
- Switching modes resets the conversation (clears chat) but preserves the loaded dataset

### Devin API Roundtrip (requires secrets)
1. Load a dataset
2. Ensure "Devin" mode is selected (default)
3. Type a visualization request (e.g., "show a bar chart of sales by name")
4. Wait 1-5 minutes for Devin to respond
5. Verify: chart renders in an iframe, "Generated HTML" expander appears with substantial HTML (>500 chars)
6. Check the HTML source for a CDN URL to confirm which library Devin chose

### React Mode Roundtrip (requires secrets)
1. Switch to a specific mode (e.g., "recharts")
2. Submit a visualization request
3. Verify chart renders in iframe with the expected library's CDN URL in the HTML source

## Known Issues & Gotchas

### CDN Script Load Order
React-based libraries (recharts, visx) require Babel standalone to be loaded **last** in the `<head>`. If Babel loads before a library, that library's global will be `undefined`. The playbooks document this, but Devin might occasionally get it wrong.

### recharts Version
recharts@3 dropped UMD builds. The playbook pins to `recharts@2` which still has UMD support. The `prop-types` CDN dependency is also required as a peer dependency.

### react-leaflet vs vanilla Leaflet
react-leaflet does not have reliable UMD builds. The app uses vanilla Leaflet instead (mode label is "leaflet" not "react-leaflet").

### Devin API Authentication
The app uses the Devin **v3 API** with Service User authentication (org_id + api_key). The legacy v1 API key format does not work. If you get a 403, verify the key starts with `cog_` and the org ID starts with `org-`.

### Polling Timeout
The default polling timeout is 600 seconds. Devin sessions for visualization tasks typically complete in 1-5 minutes. If you hit a timeout, check the Devin session URL (shown in the sidebar as "Open in Devin") to see if Devin is stuck.

### HTML Extraction
`extract_html()` filters to `source="devin"` messages only. It has three fallback strategies: (1) fenced HTML code block, (2) deployed devinapps.com URL, (3) ATTACHMENT URL. If Devin returns the HTML via deployment rather than inline, the app fetches it from the URL.
