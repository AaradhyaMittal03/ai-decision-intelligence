from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
ARTIFACTS_DIR = ROOT / "artifacts"
RAW_EVENTS_PATH = DATA_DIR / "raw_events.csv"
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(DATA_DIR / "decision_intelligence.db")))
MODEL_PATH = ARTIFACTS_DIR / "inactivity_model.joblib"
MODEL_METRICS_PATH = ARTIFACTS_DIR / "model_metrics.json"
QUALITY_REPORT_PATH = ARTIFACTS_DIR / "data_quality_report.json"
