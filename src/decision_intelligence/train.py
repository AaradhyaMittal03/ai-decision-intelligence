"""Train and evaluate an inactivity classifier."""
import json
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from .config import MODEL_PATH, MODEL_METRICS_PATH
from .features import build_user_features, FEATURES

def train_model() -> dict:
    data = build_user_features()
    X, y = data[FEATURES], data["inactive_7d"]
    if y.nunique() < 2 or len(data) < 50:
        raise RuntimeError("Need at least 50 users and both label classes. Generate more events.")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.25, random_state=42, stratify=y)
    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])
    model.fit(X_train, y_train)
    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= .5).astype(int)
    metrics = {
        "model": "LogisticRegression",
        "label": "inactive_7d (synthetic label derived from last observed event)",
        "users": int(len(data)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "positive_rate": round(float(y.mean()), 4),
        "roc_auc": round(float(roc_auc_score(y_test, probabilities)), 4),
        "pr_auc": round(float(average_precision_score(y_test, probabilities)), 4),
        "precision_at_0_5": round(float(precision_score(y_test, predictions, zero_division=0)), 4),
        "recall_at_0_5": round(float(recall_score(y_test, predictions, zero_division=0)), 4),
        "f1_at_0_5": round(float(f1_score(y_test, predictions, zero_division=0)), 4),
        "features": FEATURES,
        "note": "Metrics are from synthetic data; temporal validation should replace random splitting in a production-grade version.",
    }
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": FEATURES}, MODEL_PATH)
    MODEL_METRICS_PATH.write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))
    return metrics

if __name__ == "__main__":
    train_model()
