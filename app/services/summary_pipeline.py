"""Reusable single-chart end-to-end summary pipeline."""

from dataclasses import dataclass
from time import perf_counter

from app.core.insight_engine import InsightEngine
from app.core.summary_service import SummaryService
from app.core.summary_validator import SummaryValidator, ValidationResult
from app.prompts.chart_summary import PROMPT_VERSION
from app.repositories.chart_summary_repository import (
    ChartSummaryRepository,
    SummaryPersistenceInput,
    build_data_hash,
)
from app.repositories.clean_data_repository import CleanDataRepository


class SummaryPipelineError(RuntimeError):
    """Raised when a chart cannot be processed by the pipeline."""


@dataclass(frozen=True)
class PipelineResult:
    dashboard_id: str
    chart_id: str
    summary_text: str
    validation: ValidationResult
    summary_id: int
    inserted: bool
    latency_ms: int
    data_hash: str


class SummaryPipeline:
    """Orchestrate existing chart-summary components for one chart."""

    def __init__(
        self,
        clean_data_repository: CleanDataRepository,
        insight_engine: InsightEngine,
        summary_service: SummaryService,
        summary_validator: SummaryValidator,
        chart_summary_repository: ChartSummaryRepository,
        provider_name: str,
        model_name: str,
        prompt_version: str = PROMPT_VERSION,
    ) -> None:
        self.clean_data_repository = clean_data_repository
        self.insight_engine = insight_engine
        self.summary_service = summary_service
        self.summary_validator = summary_validator
        self.chart_summary_repository = chart_summary_repository
        self.provider_name = provider_name
        self.model_name = model_name
        self.prompt_version = prompt_version

    def run(self, dashboard_id: str, chart_id: str) -> PipelineResult:
        observations = self.clean_data_repository.get_chart_data(dashboard_id, chart_id)
        if not observations:
            raise SummaryPipelineError(
                f"No observations found for {dashboard_id}/{chart_id}"
            )

        insight = self.insight_engine.calculate(observations)
        started = perf_counter()
        summary = self.summary_service.generate(insight)
        latency_ms = int((perf_counter() - started) * 1000)
        validation = self.summary_validator.validate(summary, insight)

        item = SummaryPersistenceInput(
            insight=insight,
            summary_text=summary,
            validation=validation,
            provider=self.provider_name,
            model_name=self.model_name,
            prompt_version=self.prompt_version,
            latency_ms=latency_ms,
            indicator_code=observations[0].indicator_code,
        )
        save_result = self.chart_summary_repository.save(item)

        return PipelineResult(
            dashboard_id=dashboard_id,
            chart_id=chart_id,
            summary_text=summary,
            validation=validation,
            summary_id=save_result.summary_id,
            inserted=save_result.inserted,
            latency_ms=latency_ms,
            data_hash=build_data_hash(insight),
        )
