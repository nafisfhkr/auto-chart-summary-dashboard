"""Run the two Metabase pilot summaries sequentially."""

from app.config.settings import get_llm_settings, get_metabase_settings
from app.providers.factory import create_llm_provider
from app.repositories.chart_summary_repository import ChartSummaryRepository
from app.repositories.metabase_question_repository import MetabaseQuestionRepository
from app.services.metabase_summary_pipeline import MetabaseSummaryPipeline


def main() -> None:
    metabase = get_metabase_settings()
    llm = get_llm_settings()
    pipeline = MetabaseSummaryPipeline(
        MetabaseQuestionRepository(site_url=metabase.site_url, api_key=metabase.api_key, username=metabase.username, password=metabase.password, timeout_seconds=metabase.timeout_seconds),
        create_llm_provider(llm), ChartSummaryRepository(), llm.provider, llm.model,
    )
    for result in pipeline.run_all():
        print({"question_id": result.question_id, "chart_id": result.chart_id, "insight_type": result.insight_type, "summary_id": result.summary_id, "is_valid": result.is_valid, "inserted": result.inserted, "latency_ms": result.latency_ms, "data_hash": result.data_hash})


if __name__ == "__main__":
    main()
