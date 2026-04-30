from playbooks.react_component_builder import REACT_COMPONENT_BUILDER_PLAYBOOK

# Inline representation of the "visualization-builder" playbook.
# In production this would be fetched via GET /v1/playbooks and matched by title,
# but since playbooks cannot be directly triggered via the Devin API they are
# embedded here and injected into each new session prompt.
VISUALIZATION_BUILDER_PLAYBOOK = """
## Playbook: visualization-builder

You are executing the **visualization-builder** playbook. Follow every step in order.

### Step 1 — Analyse the Data
- Review the dataset schema and sample rows provided below.
- Identify each column's type: categorical, numeric (continuous/discrete), temporal, or geographic.
- Note the cardinality of categorical columns and the range of numeric ones.

### Step 2 — Understand the Request
- Parse the user's request carefully.
- Identify which columns map to the dimensions/measures they want.
- Identify the analytical intent: distribution, comparison, trend over time, correlation, composition, or geographic.

### Step 3 — Select the Best Chart Type
Use this decision framework:

| Intent | Recommended chart |
|---|---|
| Distribution of one numeric variable | Histogram or box plot |
| Compare values across categories (≤12 cats) | Vertical bar chart |
| Compare values across categories (>12 cats) | Horizontal bar chart |
| Trend over time | Line chart |
| Relationship between two numeric variables | Scatter plot |
| Part-of-whole (≤5 categories) | Pie chart |
| Part-of-whole (>5 categories) | Stacked bar chart |
| Correlation across many numeric columns | Heatmap |
| Geographic data | Choropleth or scatter_geo |

If the request is ambiguous, choose the chart type that reveals the most insight for the data shape.

### Step 4 — Generate the Visualization Code
- Use **Plotly Express (`px`)** or **Plotly Graph Objects (`go`)** only.
- The dataset is already loaded as a pandas DataFrame in the variable `df`. Do NOT include any file-loading code.
- Add a descriptive title, clear axis labels, and use `template="plotly_white"`.
- Assign the completed figure to a variable named exactly **`fig`**.
- Do NOT call `fig.show()`, `plt.show()`, or write to any file.

### Step 5 — Output Format
Return **only** a single fenced Python code block — no prose before or after it:

```python
# your code here
fig = ...
```
""".strip()


def build_initial_prompt(
    user_request: str,
    schema_summary: str,
    attachment_url: str,
) -> str:
    return f"""{VISUALIZATION_BUILDER_PLAYBOOK}

---

## Data Context

{schema_summary}

The dataset file is attached below. When writing code, assume `df` is already a loaded
pandas DataFrame — do not include any file-reading or import-data logic.

ATTACHMENT:"{attachment_url}"

---

## User Request

{user_request}
"""


def build_followup_message(user_request: str) -> str:
    return f"""New visualization request: {user_request}

As before, return only a fenced Python code block that builds a Plotly figure assigned to `fig`.
Assume `df` is the same DataFrame as in the original session context.
"""


def build_initial_prompt_react(
    user_request: str,
    schema_summary: str,
    data_json: str,
    library_hint: str | None = None,
) -> str:
    hint_line = ""
    if library_hint:
        hint_line = f"\n**Requested library:** {library_hint}\n"
    return f"""{REACT_COMPONENT_BUILDER_PLAYBOOK}

---

## Data Context

{schema_summary}
{hint_line}
The dataset is provided as a JSON array below. Embed it directly in the HTML
inside a `<script>` tag as `const data = [...];`.

```json
{data_json}
```

---

## User Request

{user_request}
"""


def build_followup_message_react(user_request: str) -> str:
    return f"""New visualization request: {user_request}

As before, return only a fenced HTML code block containing a self-contained HTML file.
Use the same `data` variable already defined in the page.
"""
