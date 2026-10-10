# Architecture and design decisions

## Current implementation

The first version uses a local CSV source and SQLite store to keep setup simple for a beginner. The pipeline is reproducible and does not require cloud accounts or API keys.

1. `generate.py` produces synthetic product-event records and injects a small, controlled set of data defects.
2. `quality.py` measures duplicates, missing user IDs, invalid latency, and invalid revenue; it removes invalid records.
3. `storage.py` loads valid events into SQLite and creates indexes for date and user lookups.
4. `features.py` creates one row per user for a demonstration inactivity classifier.
5. `train.py` trains a Logistic Regression baseline and writes held-out metrics.
6. `anomalies.py` aggregates daily metrics and uses median absolute deviation for a transparent baseline.
7. `analyst.py` maps a narrow set of natural-language questions to predefined, read-only SQL. Optional LLM calls only explain computed results.
8. `api.py` serves metrics and analyst results; `dashboard.py` provides a small interface.

## Security and limitations

- Never put API keys in source control. Use environment variables or a local `.env` file that remains ignored by Git.
- The analyst does not execute arbitrary LLM-generated SQL. Its narrow intent router is intentionally safer and easier to test.
- Synthetic labels and random train/test splitting are educational. A production model should use a time-based split, independently defined outcomes, calibration, fairness analysis, and monitoring.
- SQLite is appropriate for local learning, not distributed multi-writer workloads.

## Production evolution

CSV producer -> Kafka -> Spark Structured Streaming -> object storage -> warehouse -> dbt models/tests -> Airflow orchestration -> MLflow experiment tracking -> FastAPI model/analyst service -> dashboard/alerts. Add a registry, CI/CD, access control, audit logs, secrets management, data contracts, and SLOs before real production use.
