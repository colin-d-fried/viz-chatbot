REACT_COMPONENT_BUILDER_PLAYBOOK = """
## Playbook: react-component-builder

You are executing the **react-component-builder** playbook. Follow every step in order.

### Step 1 — Analyse the Data
- Review the dataset schema and sample rows provided below.
- Identify each column's type: categorical, numeric (continuous/discrete), temporal, or geographic.
- Note the cardinality of categorical columns and the range of numeric ones.

### Step 2 — Understand the Request
- Parse the user's request carefully.
- Identify which columns map to the dimensions/measures they want.
- Identify the analytical intent: distribution, comparison, trend over time, correlation, composition, geographic, network/relationship, or timeline.

### Step 3 — Select the Best Library
Use this decision framework:

| Intent | Recommended library |
|---|---|
| Standard charts (bar, line, pie, area) | recharts |
| Custom/artistic SVG visualizations | visx |
| Geographic / map data | react-leaflet |
| Network graphs / relationships | vis.js (vis-network) |
| Timelines / temporal event data | vis.js (vis-timeline) |

If a specific library is requested, use that library. Otherwise, choose the best fit from the table above.

### Step 4 — Generate the Visualization Code

Output a **single fenced `html` code block** (not Python). The HTML must be a fully self-contained file:
- All dependencies loaded via CDN `<script>` tags — do NOT use any build tools, bundlers, or ES module imports.
- The visualization renders into a `<div id="root">` element.
- The HTML is responsive: 100% width, auto height.
- Include inline `<style>` for basic layout: `body { margin: 0; }`, root div sizing.
- The dataset is provided as a JSON array in a `<script>` tag as `const data = [...]`. Reference this `data` variable in the visualization code.
- Do NOT call `document.write()` or use `alert()`.

**CRITICAL**: Babel standalone (`@babel/standalone`) auto-transforms `<script type="text/babel">` tags the moment it loads. Therefore, **Babel must be the LAST `<script>` in the `<head>`**, after React, ReactDOM, and all library scripts. If Babel loads before a library, that library's global will be `undefined` when the JSX code runs.

#### Library-Specific CDN URLs and Patterns

**recharts** — for standard charts (bar, line, area, pie, radar, scatter):
```
<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/recharts/umd/Recharts.min.js"></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
```
- Use Babel standalone for JSX transpilation: `<script type="text/babel">`
- Access components from the `Recharts` global: `Recharts.BarChart`, `Recharts.LineChart`, `Recharts.PieChart`, `Recharts.AreaChart`, `Recharts.RadarChart`, `Recharts.ScatterChart`, etc.
- Use `Recharts.ResponsiveContainer` with `width="100%"` and a fixed `height`.
- Render with `ReactDOM.createRoot(document.getElementById("root")).render(<App />)`.

**visx** — for custom/artistic SVG visualizations, low-level SVG control:
```
<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<!-- Load visx sub-packages BEFORE Babel -->
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
```
- Load only the visx sub-packages needed via unpkg UMD builds **before** the Babel script, e.g.:
  `<script src="https://unpkg.com/@visx/shape/lib/index.js"></script>`
  `<script src="https://unpkg.com/@visx/scale/lib/index.js"></script>`
  `<script src="https://unpkg.com/@visx/axis/lib/index.js"></script>`
  `<script src="https://unpkg.com/@visx/group/lib/index.js"></script>`
- visx has many sub-packages (@visx/shape, @visx/scale, @visx/axis, @visx/group, @visx/gradient, @visx/curve, etc.) — only load the ones needed.
- Use Babel standalone for JSX: `<script type="text/babel">` — Babel MUST be the last script in `<head>`.
- Render with `ReactDOM.createRoot(document.getElementById("root")).render(<App />)`.

**react-leaflet** — for geographic/map visualizations, markers, tile layers, choropleth overlays:
```
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/react-leaflet/umd/react-leaflet.min.js"></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
```
- Must include the Leaflet CSS `<link>` tag.
- Set an explicit height on the map container div (e.g. `style="height: 500px"`).
- Access components from `ReactLeaflet` global: `ReactLeaflet.MapContainer`, `ReactLeaflet.TileLayer`, `ReactLeaflet.Marker`, `ReactLeaflet.Popup`, etc.
- Use OpenStreetMap tiles: `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`
- Render with `ReactDOM.createRoot(document.getElementById("root")).render(<App />)`.

**vis.js** — for network graphs, timelines, 3D visualizations (does NOT require React):
```
<!-- For network graphs -->
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<link href="https://unpkg.com/vis-network/styles/vis-network.min.css" rel="stylesheet" />

<!-- For timelines -->
<script src="https://unpkg.com/vis-timeline/standalone/umd/vis-timeline-graph2d.min.js"></script>
<link href="https://unpkg.com/vis-timeline/styles/vis-timeline-graph2d.min.css" rel="stylesheet" />
```
- Does NOT require React — use vanilla JS API.
- For network graphs: `new vis.Network(container, { nodes, edges }, options)`
- For timelines: `new vis.Timeline(container, items, options)`
- Container div must have an explicit height.

### Step 5 — Output Format
Return **only** a single fenced HTML code block — no prose before or after it:

```html
<!DOCTYPE html>
<html lang="en">
<head>...</head>
<body>
  <div id="root"></div>
  <script>const data = [...];</script>
  ...
</body>
</html>
```

### Data Handling
- The dataset is provided as a JSON array embedded directly in a `<script>` tag as `const data = [...]`.
- Reference this `data` variable in the visualization code.
- For large datasets, the data may be truncated (500-row limit).
""".strip()
