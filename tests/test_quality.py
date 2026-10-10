import pandas as pd
from decision_intelligence.quality import validate_and_clean

def test_cleaning_removes_duplicate_missing_and_invalid_rows():
    df = pd.DataFrame({
        "event_id": ["a", "a", "b", "c"],
        "user_id": [1, 1, None, 3],
        "event_timestamp": ["2025-01-01T00:00:00Z"] * 4,
        "event_type": ["page_view"] * 4,
        "device": ["Desktop"] * 4,
        "country": ["India"] * 4,
        "page_latency_ms": [100, 100, 120, -1],
        "conversion": [0, 0, 0, 0],
        "revenue": [0, 0, 0, 0],
    })
    clean, report = validate_and_clean(df)
    assert len(clean) == 1
    assert clean.iloc[0]["event_id"] == "a"
    assert report["duplicate_event_ids"] == 1
    assert report["missing_user_ids"] == 1
