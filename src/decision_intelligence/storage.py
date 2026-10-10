"""SQLite persistence layer for the local demo."""
import sqlite3
from pathlib import Path
import pandas as pd
from .config import DATABASE_PATH

def connect(path: Path | str | None = None):
    db_path = Path(path or DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def load_events(df: pd.DataFrame, path: Path | str | None = None) -> int:
    conn = connect(path)
    try:
        conn.execute("""CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY, user_id INTEGER NOT NULL, session_id TEXT,
            event_timestamp TEXT NOT NULL, event_date TEXT NOT NULL, event_type TEXT NOT NULL,
            device TEXT NOT NULL, country TEXT NOT NULL, product_id TEXT,
            session_duration_seconds REAL, page_latency_ms REAL NOT NULL,
            click_count INTEGER, conversion INTEGER NOT NULL, revenue REAL NOT NULL
        )""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_user ON events(user_id)")
        records = df.copy()
        records["event_timestamp"] = records["event_timestamp"].astype(str)
        cols = ["event_id", "user_id", "session_id", "event_timestamp", "event_date", "event_type", "device", "country", "product_id", "session_duration_seconds", "page_latency_ms", "click_count", "conversion", "revenue"]
        records = records[cols]
        records.to_sql("events_staging", conn, if_exists="replace", index=False)
        conn.execute("INSERT OR IGNORE INTO events SELECT * FROM events_staging")
        conn.execute("DROP TABLE events_staging")
        conn.commit()
        return int(conn.execute("SELECT COUNT(*) FROM events").fetchone()[0])
    finally:
        conn.close()

def query_df(sql: str, params: tuple = (), path: Path | str | None = None) -> pd.DataFrame:
    conn = connect(path)
    try:
        return pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()
