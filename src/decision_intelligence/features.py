"""Build user-level features and a clearly defined synthetic label."""
import pandas as pd
from .storage import query_df
FEATURES = ["event_count", "active_days", "purchase_count", "avg_latency_ms", "avg_session_seconds"]

def build_user_features() -> pd.DataFrame:
    events = query_df("SELECT user_id, event_timestamp, event_type, page_latency_ms, session_duration_seconds, conversion, revenue FROM events")
    if events.empty:
        raise RuntimeError("No events found. Run `python -m decision_intelligence.pipeline` first.")
    events["event_timestamp"] = pd.to_datetime(events["event_timestamp"], utc=True)
    max_date = events["event_timestamp"].max()
    grouped = events.groupby("user_id").agg(
        event_count=("event_type", "size"),
        active_days=("event_timestamp", lambda x: x.dt.date.nunique()),
        purchase_count=("event_type", lambda x: int((x == "purchase").sum())),
        avg_latency_ms=("page_latency_ms", "mean"),
        avg_session_seconds=("session_duration_seconds", "mean"),
        last_event=("event_timestamp", "max"),
    ).reset_index()
    grouped["days_since_last_event"] = (max_date - grouped["last_event"]).dt.total_seconds() / 86400
    # Synthetic educational label. This is not a real-world churn label.
    grouped["inactive_7d"] = (grouped["days_since_last_event"] >= 7).astype(int)
    return grouped.drop(columns=["last_event"])
