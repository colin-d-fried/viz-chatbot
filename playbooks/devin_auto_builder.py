DEVIN_AUTO_BUILDER_PLAYBOOK = """
## Playbook: devin-auto-visualization

You are executing the **devin-auto-visualization** playbook. Your job is to analyse
the user's data and request, **choose the best visualization library and chart type
yourself**, then produce a single self-contained HTML file. Follow every step in
order.

### Step 1 — Analyse the Data
- Review the dataset schema and sample rows provided below.
- Identify each column's type: categorical, numeric (continuous/discrete),
  temporal, or geographic (lat/lng, country names, etc.).
- Note the cardinality of categorical columns and the range of numeric ones.

### Step 2 — Understand the Request
- Parse the user's natural-language request carefully.
- Identify which columns map to the dimensions/measures they want.
- Determine the analytical intent. Common intents include:
  distribution, comparison, trend over time, correlation, composition,
  geographic/spatial, network/relationship, or timeline.

### Step 3 — Choose the Best Library

Pick **one** library from the table below. Choose the one whose strengths best
match the data shape and user intent.

| Library | Strengths | When to choose |
|---|---|---|
| **Plotly.js** | Polished interactive charts; hover tooltips, zoom, pan; wide chart catalogue | Standard analytical charts (bar, line, scatter, pie, heatmap, box, histogram, 3D, treemap, sunburst, funnel) when interactivity matters |
| **recharts** | Clean, declarative React charts; easy colour customisation | Simple categorical/time-series charts (bar, line, area, pie, radar) when a minimal React style is preferred |
| **visx** | Low-level SVG primitives built on D3 scales; maximum creative control | Custom/artistic visualisations, unconventional layouts, small-multiples, or when the user explicitly asks for something creative |
| **leaflet** | Tile-based maps; markers, popups, choropleth, GeoJSON layers | Any request involving geographic coordinates, addresses, regions on a map |
| **vis.js** | Network graphs (vis-network) and event timelines (vis-timeline) | Relationship/connection data (nodes + edges) or temporal event sequences |

**Tie-breaking rules**:
- If the data has lat/lng or place names and the user wants a map → **leaflet**.
- If the data has source/target or node/edge columns → **vis.js (vis-network)**.
- If the data has start/end dates for events → **vis.js (vis-timeline)**.
- For general analytical charts, prefer **Plotly.js** (broadest chart set and richest interactivity). Use **recharts** if the user says "React" or asks for a simpler/cleaner look.
- Only use **visx** when the user explicitly asks for a custom/artistic SVG visualisation or when no other library fits.

### Step 4 — Choose the Best Chart Type

Once you have selected a library, pick the chart type that reveals the most
insight for the data shape. Use these guidelines:

| Intent | Recommended chart types |
|---|---|
| Distribution of one numeric variable | Histogram, box plot, violin |
| Compare values across categories (≤12) | Vertical bar chart |
| Compare values across categories (>12) | Horizontal bar chart |
| Trend over time | Line chart, area chart |
| Relationship between two numeric variables | Scatter plot |
| Part-of-whole (≤6 categories) | Pie / donut chart |
| Part-of-whole (>6 categories) | Stacked bar, treemap |
| Correlation across many numeric columns | Heatmap |
| Geographic data (points) | Map with markers |
| Geographic data (regions) | Choropleth map |
| Hierarchical data | Treemap, sunburst |
| Network / relationships | Force-directed graph |
| Timeline / event sequence | Timeline |
| Multi-dimensional comparison | Radar / spider chart |

If the request is ambiguous, choose the chart that reveals the most insight.

### Step 5 — Generate the HTML

Output a **single fenced `html` code block** (not Python). The HTML must be a
fully self-contained file:

- All dependencies loaded via CDN `<script>` tags — do NOT use any build tools,
  bundlers, or ES module imports.
- The visualisation renders into a `<div id="root">` element.
- The HTML is responsive: 100% width, auto height.
- Include inline `<style>` for basic layout: `body { margin: 0; }`, root div sizing.
- The dataset is provided as a JSON array in a `<script>` tag as
  `const data = [...]`. Reference this `data` variable in the visualisation code.
- Do NOT call `document.write()` or use `alert()`.

**CRITICAL**: When using React-based libraries (recharts, visx, Plotly.js React),
Babel standalone (`@babel/standalone`) auto-transforms `<script type="text/babel">`
tags the moment it loads. Therefore, **Babel must be the LAST `<script>` in the
`<head>`**, after React, ReactDOM, and all library scripts. If Babel loads before
a library, that library's global will be `undefined` when the JSX code runs.

#### Library-Specific CDN URLs and Patterns

**Plotly.js** — for rich interactive analytical charts:
```
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
```
- Does NOT require React — use the vanilla JS API.
- Create charts with `Plotly.newPlot('root', traces, layout, config)`.
- Use `config: { responsive: true }` for auto-resizing.
- Supports: bar, scatter, line, pie, heatmap, box, histogram, violin, treemap,
  sunburst, funnel, waterfall, 3D scatter/surface, choropleth, scattergeo, and more.

**recharts** — for clean React-based standard charts:
```
<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/prop-types/prop-types.min.js"></script>
<script src="https://unpkg.com/recharts@2/umd/Recharts.js"></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
```
- recharts@2 UMD requires `prop-types` as a peer dependency — load it before `Recharts.js`.
- Use Babel standalone for JSX transpilation: `<script type="text/babel">`
- Access components from the `Recharts` global: `Recharts.BarChart`,
  `Recharts.LineChart`, `Recharts.PieChart`, `Recharts.AreaChart`, etc.
- Use `Recharts.ResponsiveContainer` with `width="100%"` and a fixed `height`.
- Render with `ReactDOM.createRoot(document.getElementById("root")).render(<App />)`.

**visx** — for custom/artistic SVG visualisations, low-level SVG control:
```
<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/prop-types/prop-types.min.js"></script>
<!-- Load visx sub-packages BEFORE Babel -->
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
```
- Load only the visx sub-packages needed via unpkg UMD builds **before** the Babel
  script, e.g.:
  `<script src="https://unpkg.com/@visx/shape/lib/index.js"></script>`
  `<script src="https://unpkg.com/@visx/scale/lib/index.js"></script>`
- visx has many sub-packages — only load the ones needed.
- Use Babel standalone for JSX: `<script type="text/babel">`
- Render with `ReactDOM.createRoot(document.getElementById("root")).render(<App />)`.

**leaflet** — for geographic/map visualisations (does NOT require React):
```
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
```
- Must include the Leaflet CSS `<link>` tag.
- Set an explicit height on the map container div (e.g. `style="height: 500px"`).
- Use `L.map(container)`, `L.tileLayer(url).addTo(map)`,
  `L.marker([lat, lng]).addTo(map)`, `L.popup()`, etc.
- Use OpenStreetMap tiles: `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`

**vis.js** — for network graphs and timelines (does NOT require React):
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

### Step 6 — Output Format

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
- The dataset is provided as a JSON array embedded directly in a `<script>` tag
  as `const data = [...]`.
- Reference this `data` variable in the visualisation code.
- For large datasets, the data may be truncated (500-row limit).
""".strip()
