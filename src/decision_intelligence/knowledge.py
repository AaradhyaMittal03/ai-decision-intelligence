"""Tiny local retrieval layer for metric definitions and project documentation.

This deliberately lightweight retriever keeps the demo runnable without a vector database.
It is a stepping stone to embeddings + pgvector/FAISS in a later iteration.
"""
from pathlib import Path
import re
from .config import ROOT

KNOWLEDGE = [
    {
        "title": "Conversion metric",
        "text": "In this demo, conversion-event rate is the number of events marked conversion divided by all events, multiplied by 100. It is a simplified event-level metric, not a rigorous session-level conversion definition.",
    },
    {
        "title": "Revenue metric",
        "text": "Revenue is the sum of the synthetic revenue field. Purchase events can have positive revenue; other events are generated with zero revenue. Currency is illustrative and not tied to a real market.",
    },
    {
        "title": "Latency metric",
        "text": "Page latency is recorded in milliseconds. The anomaly detector aggregates average latency by UTC date and compares each date with a median absolute deviation baseline. A flagged anomaly is a statistical signal, not proof of root cause.",
    },
    {
        "title": "Synthetic data limitations",
        "text": "All event data is synthetic. The inactivity label is derived from the last observed event in the generated timeline and is not a real observed future outcome. Model metrics should not be interpreted as real customer performance.",
    },
    {
        "title": "Data quality rules",
        "text": "The cleaning stage removes duplicate event IDs, missing user IDs, invalid timestamps, non-positive page latency, negative revenue, and invalid conversion values. The quality report records counts before and after cleaning.",
    },
]

def retrieve_context(question: str, top_k: int = 2) -> list[dict]:
    tokens = set(re.findall(r"[a-z0-9]+", question.lower()))
    scored = []
    for doc in KNOWLEDGE:
        doc_tokens = set(re.findall(r"[a-z0-9]+", (doc["title"] + " " + doc["text"]).lower()))
        score = len(tokens & doc_tokens) / max(1, len(tokens))
        if score > 0:
            scored.append((score, doc))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [{**doc, "retrieval_score": round(score, 3)} for score, doc in scored[:top_k]]
