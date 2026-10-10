"""Small, transparent data-quality checks and cleaning."""
import pandas as pd

REQUIRED_COLUMNS = ["event_id", "user_id", "event_timestamp", "event_type", "device", "country", "page_latency_ms", "conversion", "revenue"]

def validate_and_clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    report = {"input_rows": int(len(df)), "missing_required_columns": missing_columns}
    report["duplicate_event_ids"] = int(df["event_id"].duplicated().sum())
    report["missing_user_ids"] = int(df["user_id"].isna().sum())
    report["invalid_latency_rows"] = int((pd.to_numeric(df["page_latency_ms"], errors="coerce") <= 0).sum())
    report["invalid_revenue_rows"] = int((pd.to_numeric(df["revenue"], errors="coerce") < 0).sum())
    cleaned = df.drop_duplicates(subset=["event_id"], keep="first").copy()
    cleaned["user_id"] = pd.to_numeric(cleaned["user_id"], errors="coerce")
    cleaned["page_latency_ms"] = pd.to_numeric(cleaned["page_latency_ms"], errors="coerce")
    cleaned["revenue"] = pd.to_numeric(cleaned["revenue"], errors="coerce")
    cleaned["conversion"] = pd.to_numeric(cleaned["conversion"], errors="coerce")
    cleaned["event_timestamp"] = pd.to_datetime(cleaned["event_timestamp"], errors="coerce", utc=True)
    cleaned = cleaned.dropna(subset=["user_id", "event_timestamp", "page_latency_ms", "revenue", "conversion"])
    cleaned = cleaned[(cleaned["page_latency_ms"] > 0) & (cleaned["revenue"] >= 0) & cleaned["conversion"].isin([0, 1])]
    cleaned["user_id"] = cleaned["user_id"].astype(int)
    cleaned["event_date"] = cleaned["event_timestamp"].dt.strftime("%Y-%m-%d")
    report["clean_rows"] = int(len(cleaned))
    report["rejected_rows"] = int(report["input_rows"] - len(cleaned))
    report["cleaning_retention_pct"] = round(100 * len(cleaned) / max(1, len(df)), 2)
    return cleaned, report
