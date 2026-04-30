# Playbooks

This directory contains the inline playbook strings used to instruct Devin when
generating visualizations.

## Available Playbooks

| File | Constant | Purpose |
|---|---|---|
| `devin_auto_builder.py` | `DEVIN_AUTO_BUILDER_PLAYBOOK` | **Recommended.** Devin analyses the data and request to automatically choose the best library (Plotly.js, recharts, visx, leaflet, or vis.js) and chart type. Outputs self-contained HTML. |
| `react_component_builder.py` | `REACT_COMPONENT_BUILDER_PLAYBOOK` | Generates self-contained HTML using a specific React/JS library (recharts, visx, leaflet, vis.js). Used when a library is explicitly selected. |

The original Plotly playbook (`VISUALIZATION_BUILDER_PLAYBOOK`) lives in
`prompt_builder.py`.

## Registering a Playbook in the Devin UI

If you prefer to use a *registered* playbook (more token-efficient for follow-up
messages), you can create one in the Devin dashboard:

1. Open **Settings → Playbooks** in the Devin UI.
2. Click **Create Playbook**.
3. Set the title to `devin-auto-visualization` (or `react-component-builder`).
4. Paste the full text of `DEVIN_AUTO_BUILDER_PLAYBOOK` (from
   `playbooks/devin_auto_builder.py`) into the body field.
5. Save the playbook and copy its `playbook_id`.
6. Pass the `playbook_id` when calling `DevinClient.create_session()`:

   ```python
   session_id, session_url = client.create_session(
       prompt,
       playbook_id="your-playbook-id-here",
   )
   ```

## Inline vs. Registered Approach

| Approach | Pros | Cons |
|---|---|---|
| **Inline** (current default) | No setup required — works immediately | Full playbook text is sent with every new session prompt |
| **Registered** | More token-efficient for follow-ups — Devin already has the playbook context | Requires one-time manual registration in the Devin UI |

Both approaches produce identical results. The inline approach is the default
because it requires zero configuration.
