PYTHON ?= python

.PHONY: install data train api dashboard test clean
install:
	$(PYTHON) -m pip install -e ".[dev]"
data:
	$(PYTHON) -m decision_intelligence.pipeline --events 100000
train:
	$(PYTHON) -m decision_intelligence.train
api:
	uvicorn decision_intelligence.api:app --reload

dashboard:
	streamlit run dashboard.py

test:
	pytest -q
clean:
	rm -f data/decision_intelligence.db artifacts/*.joblib artifacts/*.json
