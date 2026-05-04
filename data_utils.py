import io
import pandas as pd

MAX_UPLOAD_ROWS = 500
SAMPLE_ROWS = 5


def load_dataset(source) -> pd.DataFrame:
    """Load a DataFrame from a Streamlit UploadedFile or a URL/path string."""
    if hasattr(source, "name"):
        name = source.name.lower()
    else:
        name = str(source).lower()

    if name.endswith(".csv"):
        return pd.read_csv(source)
    elif name.endswith((".xlsx", ".xls")):
        return pd.read_excel(source)
    elif name.endswith(".json"):
        return pd.read_json(source)
    elif name.endswith(".parquet"):
        return pd.read_parquet(source)
    else:
        return pd.read_csv(source)


def get_schema_summary(df: pd.DataFrame) -> str:
    lines = [
        f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns",
        "",
        "Columns:",
    ]
    for col, dtype in df.dtypes.items():
        null_pct = df[col].isna().mean() * 100
        extra = ""
        if pd.api.types.is_numeric_dtype(df[col]):
            extra = f"  range [{df[col].min():.4g}, {df[col].max():.4g}]"
        elif pd.api.types.is_object_dtype(df[col]) or isinstance(df[col].dtype, pd.CategoricalDtype):
            n_unique = df[col].nunique()
            extra = f"  {n_unique} unique values"
        lines.append(f"  - {col} ({dtype}){extra}  {null_pct:.1f}% null")

    lines += ["", f"Sample ({min(SAMPLE_ROWS, len(df))} rows):"]
    lines.append(df.head(SAMPLE_ROWS).to_string(index=False))
    return "\n".join(lines)


def prepare_for_upload(df: pd.DataFrame, original_name: str = "dataset.csv") -> tuple[bytes, str]:
    """Truncate to MAX_UPLOAD_ROWS and serialize to CSV bytes for Devin attachment."""
    truncated = df.head(MAX_UPLOAD_ROWS)
    buf = io.StringIO()
    truncated.to_csv(buf, index=False)
    filename = original_name if original_name.lower().endswith(".csv") else "dataset.csv"
    return buf.getvalue().encode("utf-8"), filename


def prepare_data_as_json(df: pd.DataFrame, max_rows: int = MAX_UPLOAD_ROWS) -> str:
    """Truncate to *max_rows* and return a JSON-records string for embedding in HTML."""
    return df.head(max_rows).to_json(orient="records")
