"""Explainable daily anomaly checks using median absolute deviation (MAD)."""
import numpy as np
import pandas as pd
from .storage import query_df

def detect_anomalies() -> list[dict]:
    daily = query_df("""SELECT event_date, COUNT(*) AS event_count,
        AVG(page_latency_ms) AS avg_latency_ms,
        SUM(conversion) * 1.0 / COUNT(*) AS conversion_rate,
        SUM(revenue) AS revenue
        FROM events GROUP BY event_date ORDER BY event_date""")
    if len(daily) < 7:
        return []
    findings = []
    for metric in ["event_count", "avg_latency_ms", "conversion_rate", "revenue"]:
        values = daily[metric].astype(float).to_numpy()
        median = float(np.median(values))
        mad = float(np.median(np.abs(values - median)))
        # A tiny floor avoids division by zero for flat metrics.
        robust_z = 0.6745 * (values - median) / max(mad, 1e-9)
        for idx in np.where(np.abs(robust_z) > 3.5)[0]:
            findings.append({
                "date": str(daily.iloc[idx]["event_date"]),
                "metric": metric,
                "value": round(float(values[idx]), 4),
                "baseline_median": round(median, 4),
                "robust_z_score": round(float(robust_z[idx]), 2),
                "direction": "high" if robust_z[idx] > 0 else "low",
                "method": "median absolute deviation; threshold |robust z| > 3.5",
            })
    return sorted(findings, key=lambda x: abs(x["robust_z_score"]), reverse=True)
