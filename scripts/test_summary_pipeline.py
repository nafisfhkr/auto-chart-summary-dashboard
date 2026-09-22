"""Manual five-chart end-to-end pipeline check."""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.services.factory import create_summary_pipeline


DASHBOARD_ID = "dashboard_jatim_demo"

CHART_IDS = [
    "chart_ipm",
    "chart_kemiskinan",
    "chart_tpt",
    "chart_inflasi",
    "chart_produksi_padi",
]


def main() -> None:
    pipeline = create_summary_pipeline()

    for chart_id in CHART_IDS:
        result = pipeline.run(DASHBOARD_ID, chart_id)

        print({
            "chart_id": chart_id,
            "summary": result.summary_text,
            "is_valid": result.validation.is_valid,
            "validation_errors": list(result.validation.errors),
            "summary_id": result.summary_id,
            "inserted": result.inserted,
            "latency_ms": result.latency_ms,
            "data_hash": result.data_hash,
        })


if __name__ == "__main__":
    main()
