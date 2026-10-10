"""FastAPI service for metrics, model evaluation, anomaly findings, and analyst queries."""
import json
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from .storage import query_df
from .config import MODEL_METRICS_PATH, QUALITY_REPORT_PATH, MODEL_PATH
from .analyst import answer_question
from .anomalies import detect_anomalies

app = FastAPI(title="AI Decision Intelligence API", version="0.1.0", description="Synthetic product analytics and evidence-grounded analyst demo")

class AnalystQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=500)

@app.get("/health")
def health():
    try:
        rows = query_df("SELECT COUNT(*) AS n FROM events")
        return {"status": "ok", "event_rows": int(rows.iloc[0]["n"]), "model_available": MODEL_PATH.exists()}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Data store not ready. Run pipeline first. ({type(exc).__name__})")

@app.get("/metrics/summary")
def summary():
    try:
        df = query_df("SELECT COUNT(*) AS events, COUNT(DISTINCT user_id) AS users, ROUND(SUM(revenue),2) AS revenue, ROUND(100.0*SUM(conversion)/COUNT(*),2) AS conversion_pct, ROUND(AVG(page_latency_ms),2) AS avg_latency_ms FROM events")
        return df.iloc[0].to_dict()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Data store not ready: {type(exc).__name__}")

@app.get("/metrics/daily")
def daily_metrics(limit: int = 90):
    limit = max(1, min(limit, 365))
    df = query_df("SELECT event_date, COUNT(*) AS events, COUNT(DISTINCT user_id) AS users, ROUND(SUM(revenue),2) AS revenue, ROUND(100.0*SUM(conversion)/COUNT(*),2) AS conversion_pct, ROUND(AVG(page_latency_ms),2) AS avg_latency_ms FROM events GROUP BY event_date ORDER BY event_date DESC LIMIT ?", (limit,))
    return df.to_dict(orient="records")

@app.get("/anomalies")
def anomalies():
    return {"count": len(detect_anomalies()), "findings": detect_anomalies()}

@app.get("/model/metrics")
def model_metrics():
    if not MODEL_METRICS_PATH.exists():
        raise HTTPException(status_code=404, detail="Model metrics not found. Run `python -m decision_intelligence.train` first.")
    return json.loads(MODEL_METRICS_PATH.read_text())

@app.get("/quality/report")
def quality_report():
    if not QUALITY_REPORT_PATH.exists():
        raise HTTPException(status_code=404, detail="Quality report not found. Run the pipeline first.")
    return json.loads(QUALITY_REPORT_PATH.read_text())

@app.post("/analyst/ask")
def ask(body: AnalystQuestion):
    return answer_question(body.question)

@app.get("/analyst/ask")
def ask_get(question: str = Query(min_length=1, max_length=500)):
    return answer_question(question)
