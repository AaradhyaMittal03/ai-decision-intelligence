"""Generate repeatable synthetic product events for a portfolio demo."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

EVENT_TYPES = ["page_view", "search", "product_view", "add_to_cart", "checkout", "purchase"]
DEVICES = ["Android", "iOS", "Desktop", "Tablet"]
COUNTRIES = ["India", "United States", "United Kingdom", "Canada", "Germany", "Nepal"]

def generate_events(n_events: int = 100_000, seed: int = 42, inject_issues: bool = True) -> pd.DataFrame:
    if n_events < 100:
        raise ValueError("n_events must be at least 100 so the demo has useful data")
    rng = np.random.default_rng(seed)
    n_users = max(100, n_events // 20)
    user_ids = rng.integers(1, n_users + 1, size=n_events)
    timestamps = pd.Timestamp("2025-01-01", tz="UTC") + pd.to_timedelta(
        rng.integers(0, 90 * 24 * 60 * 60, size=n_events), unit="s"
    )
    event_type = rng.choice(EVENT_TYPES, size=n_events, p=[.34, .12, .25, .13, .09, .07])
    device = rng.choice(DEVICES, size=n_events, p=[.43, .25, .27, .05])
    country = rng.choice(COUNTRIES, size=n_events, p=[.43, .25, .10, .08, .08, .06])
    latency = np.maximum(80, rng.lognormal(mean=5.9, sigma=.45, size=n_events)).round(1)
    # A synthetic incident window gives anomaly detection something meaningful to find.
    incident = (timestamps >= pd.Timestamp("2025-02-20", tz="UTC")) & (timestamps < pd.Timestamp("2025-02-23", tz="UTC"))
    latency[incident] *= 2.2
    conversion_prob = np.where(event_type == "purchase", .92, .015)
    conversion = (rng.random(n_events) < conversion_prob).astype(int)
    revenue = np.where(event_type == "purchase", rng.gamma(shape=2.0, scale=35.0, size=n_events), 0.0).round(2)
    session_duration = np.maximum(1, rng.gamma(shape=2.2, scale=75, size=n_events)).round(1)
    session_id = [f"s{x:08d}" for x in rng.integers(1, max(2, n_events // 2), size=n_events)]
    df = pd.DataFrame({
        "event_id": [f"e{x:09d}" for x in range(1, n_events + 1)],
        "user_id": user_ids,
        "session_id": session_id,
        "event_timestamp": timestamps.astype(str),
        "event_type": event_type,
        "device": device,
        "country": country,
        "product_id": [f"p{x:04d}" for x in rng.integers(1, 501, size=n_events)],
        "session_duration_seconds": session_duration,
        "page_latency_ms": latency,
        "click_count": rng.poisson(3, size=n_events),
        "conversion": conversion,
        "revenue": revenue,
    })
    if inject_issues:
        # Controlled defects to demonstrate data-quality checks. Keep their indices reproducible.
        count = max(1, n_events // 1000)
        missing_idx = rng.choice(n_events, size=count, replace=False)
        df.loc[missing_idx, "user_id"] = np.nan
        duplicate_rows = df.iloc[:max(1, n_events // 2000)].copy()
        df = pd.concat([df, duplicate_rows], ignore_index=True)
        bad_idx = rng.choice(df.index, size=max(1, len(df) // 2000), replace=False)
        df.loc[bad_idx, "page_latency_ms"] = -5
    return df

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--no-issues", action="store_true", help="Do not inject example data-quality issues")
    args = parser.parse_args()
    from .config import RAW_EVENTS_PATH
    output = args.output or RAW_EVENTS_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    df = generate_events(args.events, args.seed, not args.no_issues)
    df.to_csv(output, index=False)
    print(f"Wrote {len(df):,} raw rows to {output}")

if __name__ == "__main__":
    main()
