import json
import shutil
from pathlib import Path

from pydantic import ValidationError

from anomaly_detector import run_all_detectors
from data_merger import build_fused_dataset, load_transactions
from gemini_client import GeminiUnavailableError, call_gemini
from offline_synthesizer import synthesize
from schemas import RiskSummary

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
FRONTEND_DATA_DIR = Path(__file__).resolve().parent.parent / "frontend" / "public" / "data"


def run() -> dict:
    tx_df = load_transactions()
    fused = build_fused_dataset()
    signals = run_all_detectors(tx_df, fused["accounts"])

    try:
        risk_summary = call_gemini(fused, signals)
        risk_summary["generation_mode"] = "gemini"
    except GeminiUnavailableError:
        risk_summary = synthesize(fused, signals)
        risk_summary["generation_mode"] = "offline_fallback"

    try:
        validated = RiskSummary.model_validate(risk_summary)
    except ValidationError as exc:
        raise RuntimeError(
            f"risk summary failed schema validation, refusing to write output:\n{exc}"
        ) from exc
    risk_summary = validated.model_dump(mode="json")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FRONTEND_DATA_DIR.mkdir(parents=True, exist_ok=True)

    out_path = OUTPUT_DIR / "risk_summary.json"
    out_path.write_text(json.dumps(risk_summary, indent=2))
    shutil.copy(out_path, FRONTEND_DATA_DIR / "risk_summary.json")

    return risk_summary


if __name__ == "__main__":
    summary = run()
    print(f"generation_mode: {summary['generation_mode']}")
    print(f"findings: {len(summary['findings'])}")
    print(f"written to: {OUTPUT_DIR / 'risk_summary.json'}")
