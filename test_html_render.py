"""Temporary test harness to verify st.components.v1.html() renders a recharts chart."""
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="HTML Render Test", layout="wide")
st.title("HTML Component Render Test")

sample_html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<style>body { margin: 0; } #root { width: 100%; height: 500px; }</style>
<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/recharts/umd/Recharts.min.js"></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
</head>
<body>
<div id="root"></div>
<script>
const data = [
  {"name": "Alice", "sales": 100, "region": "North"},
  {"name": "Bob", "sales": 250, "region": "South"},
  {"name": "Charlie", "sales": 175, "region": "East"},
  {"name": "Diana", "sales": 300, "region": "West"},
  {"name": "Eve", "sales": 220, "region": "North"},
  {"name": "Frank", "sales": 190, "region": "South"},
  {"name": "Grace", "sales": 280, "region": "East"},
  {"name": "Hank", "sales": 150, "region": "West"}
];
</script>
<script type="text/babel">
const { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } = Recharts;

function App() {
  return (
    <ResponsiveContainer width="100%" height={450}>
      <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="sales" fill="#8884d8" />
      </BarChart>
    </ResponsiveContainer>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
</script>
</body>
</html>"""

st.subheader("Recharts Bar Chart (via st.components.v1.html)")
components.html(sample_html, height=600, scrolling=True)

with st.expander("Generated HTML"):
    st.code(sample_html, language="html")
