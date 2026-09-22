"""Production dependency composition for the summary pipeline."""

from app.config.settings import get_llm_settings
from app.core.insight_engine import InsightEngine
from app.core.summary_service import SummaryService
from app.core.summary_validator import SummaryValidator
from app.prompts.chart_summary import PROMPT_VERSION
from app.providers.factory import create_llm_provider
from app.repositories.chart_summary_repository import ChartSummaryRepository
from app.repositories.clean_data_repository import CleanDataRepository
from app.services.summary_pipeline import SummaryPipeline


def create_summary_pipeline() -> SummaryPipeline:
    """Compose configured production dependencies for one-chart execution."""
    settings = get_llm_settings()
    provider = create_llm_provider(settings)
    return SummaryPipeline(
        clean_data_repository=CleanDataRepository(),
        insight_engine=InsightEngine(),
        summary_service=SummaryService(provider),
        summary_validator=SummaryValidator(),
        chart_summary_repository=ChartSummaryRepository(),
        provider_name=settings.provider,
        model_name=settings.model,
        prompt_version=PROMPT_VERSION,
    )
