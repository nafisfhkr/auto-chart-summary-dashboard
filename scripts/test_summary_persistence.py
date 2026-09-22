"""Manual Supabase persistence and idempotency check for Phase 7."""

import sys
from pathlib import Path
from time import perf_counter

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.config.settings import get_llm_settings
from app.core.insight_engine import InsightEngine
from app.core.summary_validator import SummaryValidator
from app.core.summary_service import SummaryService
from app.providers.factory import create_llm_provider
from app.prompts.chart_summary import PROMPT_VERSION
from app.repositories.chart_summary_repository import (
    ChartSummaryRepository, SummaryPersistenceInput, build_data_hash,
)
from app.repositories.clean_data_repository import CleanDataRepository


DASHBOARD_ID = "dashboard_jatim_demo"
CHART_IDS = ["chart_ipm", "chart_kemiskinan", "chart_tpt", "chart_inflasi", "chart_produksi_padi"]


def main() -> None:
    data = CleanDataRepository()
    engine = InsightEngine()
    settings = get_llm_settings()
    service = SummaryService(create_llm_provider(settings))
    summaries = ChartSummaryRepository()
    validator = SummaryValidator()

    for chart_id in CHART_IDS:
        observations = data.get_chart_data(DASHBOARD_ID, chart_id)
        insight = engine.calculate(observations)
        started = perf_counter()
        summary = service.generate(insight)
        latency_ms = int((perf_counter() - started) * 1000)
        validation = validator.validate(summary, insight)
        item = SummaryPersistenceInput(
            insight=insight, summary_text=summary, validation=validation,
            provider=settings.provider, model_name=settings.model,
            prompt_version=PROMPT_VERSION, latency_ms=latency_ms,
            indicator_code=observations[0].indicator_code,
        )
        first = summaries.save(item)
        second = summaries.save(item)
        if second.inserted or first.summary_id != second.summary_id:
            raise RuntimeError(f"Idempotency check failed for {chart_id}")
        print({
            "chart_id": chart_id, "summary": summary,
            "validation_status": "valid" if validation.is_valid else "invalid",
            "validation_errors": list(validation.errors), "latency_ms": latency_ms,
            "data_hash": build_data_hash(insight), "summary_id": first.summary_id,
            "inserted": first.inserted, "second_inserted": second.inserted,
            "same_id": first.summary_id == second.summary_id,
        })


if __name__ == "__main__":
    main()
