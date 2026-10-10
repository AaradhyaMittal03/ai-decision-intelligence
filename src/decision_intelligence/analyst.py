"""Safe question routing: map supported questions to fixed, read-only analytics queries."""
import os
from .storage import query_df
from .anomalies import detect_anomalies
from .knowledge import retrieve_context

SUPPORTED = ["conversion yesterday", "revenue by device", "country with most events", "average latency", "number of events", "detected anomalies"]

def answer_question(question: str) -> dict:
    q = question.lower().strip()
    retrieved_context = retrieve_context(question)
    if not q:
        return {"question": question, "answer": "Please enter a question.", "evidence": [], "intent": "empty"}
    if "anomal" in q:
        rows = detect_anomalies()[:10]
        return {"question": question, "answer": f"Detected {len(detect_anomalies())} daily anomaly finding(s). The first 10 are shown as evidence.", "evidence": rows, "intent": "anomalies"}
    if "revenue" in q and "device" in q:
        df = query_df("SELECT device, ROUND(SUM(revenue),2) AS revenue FROM events GROUP BY device ORDER BY revenue DESC")
        evidence = df.to_dict(orient="records")
        answer = "Revenue by device: " + "; ".join(f"{r['device']}: {r['revenue']}" for r in evidence)
        intent = "revenue_by_device"
    elif "country" in q and ("most" in q or "events" in q or "traffic" in q):
        df = query_df("SELECT country, COUNT(*) AS events FROM events GROUP BY country ORDER BY events DESC LIMIT 1")
        evidence = df.to_dict(orient="records")
        answer = f"The highest event count is for {evidence[0]['country']}: {evidence[0]['events']} events." if evidence else "No event data is available."
        intent = "top_country"
    elif "latency" in q:
        df = query_df("SELECT ROUND(AVG(page_latency_ms),2) AS avg_latency_ms FROM events")
        evidence = df.to_dict(orient="records")
        answer = f"Average page latency is {evidence[0]['avg_latency_ms']} ms." if evidence else "No event data is available."
        intent = "average_latency"
    elif "conversion" in q and ("yesterday" in q or "daily" in q or "rate" in q):
        df = query_df("SELECT event_date, COUNT(*) AS events, ROUND(100.0*SUM(conversion)/COUNT(*),2) AS conversion_pct FROM events GROUP BY event_date ORDER BY event_date DESC LIMIT 1")
        evidence = df.to_dict(orient="records")
        answer = f"Most recent available date ({evidence[0]['event_date']}) has a conversion-event rate of {evidence[0]['conversion_pct']}% across {evidence[0]['events']} events. This is the latest dataset date, not today's live data." if evidence else "No event data is available."
        intent = "latest_conversion"
    elif "how many" in q or "number of events" in q or "events processed" in q or "event count" in q:
        df = query_df("SELECT COUNT(*) AS event_count FROM events")
        evidence = df.to_dict(orient="records")
        answer = f"The analytical store contains {evidence[0]['event_count']} events." if evidence else "No event data is available."
        intent = "event_count"
    else:
        return {"question": question, "answer": "I couldn't confidently map that to a supported query. Try: 'What is the average latency?', 'Show revenue by device', 'Which country has the most events?', 'What was conversion yesterday?', 'How many events were processed?', or 'What anomalies were detected?'", "evidence": [], "intent": "unsupported", "supported_intents": SUPPORTED}
    result = {"question": question, "answer": answer, "evidence": evidence, "intent": intent, "method": "predefined read-only SQL query + local documentation retrieval", "retrieved_context": retrieved_context}
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                temperature=0,
                messages=[
                    {"role": "system", "content": "Explain the supplied analytical answer clearly. Use only the provided answer and evidence. If evidence is insufficient, say so. Do not invent facts."},
                    {"role": "user", "content": f"Question: {question}\nComputed answer: {answer}\nEvidence: {evidence}\nRetrieved documentation context: {retrieved_context}"},
                ],
            )
            result["llm_explanation"] = response.choices[0].message.content
        except Exception as exc:
            result["llm_note"] = f"Optional LLM explanation unavailable ({type(exc).__name__}); deterministic answer is still valid."
    return result
