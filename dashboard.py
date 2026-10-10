"""Streamlit dashboard for the local Decision Intelligence API."""
import os
import requests
import pandas as pd
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
st.set_page_config(page_title="Decision Intelligence", page_icon="📊", layout="wide")
st.title("📊 AI-Powered Decision Intelligence")
st.caption("Synthetic product events · analytics · anomaly detection · ML · evidence-grounded AI analyst")
try:
    health = requests.get(f"{API_URL}/health", timeout=3)
    health.raise_for_status()
    summary = requests.get(f"{API_URL}/metrics/summary", timeout=10).json()
    daily = requests.get(f"{API_URL}/metrics/daily", timeout=10).json()
    anomalies = requests.get(f"{API_URL}/anomalies", timeout=10).json()
except requests.RequestException:
    st.error("API is not running. In another terminal, run: uvicorn decision_intelligence.api:app --reload")
    st.stop()

cols = st.columns(5)
for col, label, value in zip(cols, ["Events", "Unique users", "Revenue", "Conversion-event rate", "Avg latency"], [f"{summary['events']:,}", f"{summary['users']:,}", f"${summary['revenue']:,.2f}", f"{summary['conversion_pct']}%", f"{summary['avg_latency_ms']} ms"]):
    col.metric(label, value)

df = pd.DataFrame(daily).sort_values("event_date")
st.subheader("Daily product metrics")
if not df.empty:
    left, right = st.columns(2)
    left.line_chart(df.set_index("event_date")[["events", "users"]])
    right.line_chart(df.set_index("event_date")[["avg_latency_ms", "conversion_pct"]])
    st.dataframe(df, use_container_width=True, hide_index=True)

st.subheader(f"Anomaly findings ({anomalies['count']})")
if anomalies["findings"]:
    st.dataframe(pd.DataFrame(anomalies["findings"]), use_container_width=True, hide_index=True)
else:
    st.info("No anomalies crossed the current robust-z threshold.")

st.subheader("Ask the AI Data Analyst")
question = st.text_input("Ask a question", placeholder="Show revenue by device")
if st.button("Ask", type="primary", disabled=not question.strip()):
    try:
        response = requests.post(f"{API_URL}/analyst/ask", json={"question": question}, timeout=30)
        response.raise_for_status()
        answer = response.json()
        st.write(answer.get("llm_explanation") or answer["answer"])
        st.caption(f"Intent: {answer.get('intent')} · Method: {answer.get('method', 'predefined analytics route')}")
        if answer.get("evidence"):
            st.write("Evidence")
            st.dataframe(pd.DataFrame(answer["evidence"]), use_container_width=True, hide_index=True)
        if answer.get("llm_note"):
            st.caption(answer["llm_note"])
    except requests.RequestException as exc:
        st.error(f"Could not query the analyst API: {exc}")

st.caption("All data is synthetic. Metrics and anomaly findings are for demonstration, not business decisions.")
