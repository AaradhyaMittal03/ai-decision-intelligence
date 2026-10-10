"""Run synthetic generation -> validation -> local analytical storage."""
import argparse, json
from .config import RAW_EVENTS_PATH, QUALITY_REPORT_PATH
from .generate import generate_events
from .quality import validate_and_clean
from .storage import load_events

def run_pipeline(n_events: int = 100_000, seed: int = 42) -> dict:
    RAW_EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    raw = generate_events(n_events=n_events, seed=seed, inject_issues=True)
    raw.to_csv(RAW_EVENTS_PATH, index=False)
    clean, report = validate_and_clean(raw)
    report["database_rows_after_load"] = load_events(clean)
    report["seed"] = seed
    report["generator_requested_events"] = n_events
    QUALITY_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    QUALITY_REPORT_PATH.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return report

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    run_pipeline(args.events, args.seed)

if __name__ == "__main__":
    main()
