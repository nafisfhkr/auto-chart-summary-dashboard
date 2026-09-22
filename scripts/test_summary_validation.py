"""Generate and deterministically validate summaries for five demo charts."""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.config.settings import get_llm_settings
from app.core.insight_engine import InsightEngine
from app.core.summary_service import SummaryService
from app.core.summary_validator import SummaryValidator
from app.providers.factory import create_llm_provider
from app.repositories.clean_data_repository import CleanDataRepository


DASHBOARD_ID = "dashboard_jatim_demo"
CHART_IDS = ["chart_ipm", "chart_kemiskinan", "chart_tpt", "chart_inflasi", "chart_produksi_padi"]


def main() -> None:
    repository = CleanDataRepository()
    engine = InsightEngine()
    service = SummaryService(create_llm_provider(get_llm_settings()))
    validator = SummaryValidator()
    for chart_id in CHART_IDS:
        observations = repository.get_chart_data(DASHBOARD_ID, chart_id)
        insight = engine.calculate(observations)
        summary = service.generate(insight)
        result = validator.validate(summary, insight)
        print(f"\n=== {chart_id} ===")
        print("Generated Summary:")
        print(summary)
        print("Valid:", result.is_valid)
        print("Errors:", result.errors)


if __name__ == "__main__":
    main()
