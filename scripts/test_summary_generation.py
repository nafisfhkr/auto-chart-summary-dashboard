"""Generate summaries for all synthetic demo charts without persisting them."""

from dataclasses import asdict
from pprint import pprint
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.config.settings import get_llm_settings
from app.core.insight_engine import InsightEngine
from app.core.summary_service import SummaryService
from app.providers.factory import create_llm_provider
from app.repositories.clean_data_repository import CleanDataRepository


DASHBOARD_ID = "dashboard_jatim_demo"
CHART_IDS = [
    "chart_ipm", "chart_kemiskinan", "chart_tpt", "chart_inflasi",
    "chart_produksi_padi",
]


def main() -> None:
    repository = CleanDataRepository()
    engine = InsightEngine()
    settings = get_llm_settings()
    service = SummaryService(create_llm_provider(settings))

    for chart_id in CHART_IDS:
        observations = repository.get_chart_data(DASHBOARD_ID, chart_id)
        if not observations:
            raise RuntimeError(f"No data found for {DASHBOARD_ID}/{chart_id}")
        insight = engine.calculate(observations)
        print(f"\n=== {chart_id} ===")
        pprint(asdict(insight))
        print("Generated Summary:")
        print(service.generate(insight))


if __name__ == "__main__":
    main()
