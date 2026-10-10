FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY dashboard.py ./dashboard.py
RUN pip install --no-cache-dir -e ".[dev]"
EXPOSE 8000
CMD ["uvicorn", "decision_intelligence.api:app", "--host", "0.0.0.0", "--port", "8000"]
