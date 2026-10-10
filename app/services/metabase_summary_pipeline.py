"""Manual, non-Airflow Metabase summary pipeline."""

from dataclasses import dataclass
from time import perf_counter
import hashlib
import json
from decimal import Decimal

from app.config.metabase_charts import MetabaseChartConfig, METABASE_CHARTS
from app.core.categorical_insight_engine import calculate_categorical_insight
from app.core.composition_insight_engine import calculate_composition_insight
from app.core.metabase_insights import CategoricalMultiSeriesInsight, CompositionInsight
from app.core.metabase_summary_validator import MetabaseSummaryValidator
from app.providers.base import LLMProvider
from app.prompts.metabase_categorical_summary import PROMPT_VERSION as CATEGORICAL_PROMPT_VERSION, build_messages as categorical_messages
from app.prompts.metabase_composition_summary import PROMPT_VERSION as COMPOSITION_PROMPT_VERSION, build_messages as composition_messages
from app.repositories.chart_summary_repository import ChartSummaryRepository, GenericSummaryPersistenceInput
from app.repositories.metabase_question_repository import MetabaseQuestionRepository


@dataclass(frozen=True)
class MetabasePipelineResult:
    question_id: int
    chart_id: str
    insight_type: str
    summary_id: int
    is_valid: bool
    inserted: bool
    latency_ms: int
    data_hash: str
    summary_text: str


def build_metabase_data_hash(config: MetabaseChartConfig, insight: CategoricalMultiSeriesInsight | CompositionInsight) -> str:
    payload = {"question_id": config.question_id, "insight_type": config.insight_type, "insight": _jsonable(insight)}
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _jsonable(value):
    if hasattr(value, "__dataclass_fields__"):
        return {key: _jsonable(getattr(value, key)) for key in value.__dataclass_fields__}
    if isinstance(value, Decimal):
        return format(value.normalize(), "f")
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    return value


class MetabaseSummaryPipeline:
    def __init__(self, question_repository: MetabaseQuestionRepository, provider: LLMProvider, summary_repository: ChartSummaryRepository, provider_name: str, model_name: str) -> None:
        self.question_repository, self.provider, self.summary_repository = question_repository, provider, summary_repository
        self.provider_name, self.model_name = provider_name, model_name

    def run(self, config: MetabaseChartConfig) -> MetabasePipelineResult:
        result = self.question_repository.fetch(config)
        if config.insight_type == "categorical_multi_series":
            insight, prompt_version, messages = calculate_categorical_insight(config, result), CATEGORICAL_PROMPT_VERSION, categorical_messages
        elif config.insight_type == "composition":
            insight, prompt_version, messages = calculate_composition_insight(config, result), COMPOSITION_PROMPT_VERSION, composition_messages
        else:
            raise ValueError(f"Unsupported Metabase insight type: {config.insight_type}")
        started = perf_counter()
        summary = self.provider.generate(messages(insight))
        latency_ms = int((perf_counter() - started) * 1000)
        validation = MetabaseSummaryValidator().validate(summary, insight)
        data_hash = build_metabase_data_hash(config, insight)
        saved = self.summary_repository.save_generic(GenericSummaryPersistenceInput(config.dashboard_id, config.chart_id, config.title, summary, validation, self.provider_name, self.model_name, prompt_version, latency_ms, data_hash))
        return MetabasePipelineResult(config.question_id, config.chart_id, config.insight_type, saved.summary_id, validation.is_valid, saved.inserted, latency_ms, data_hash, summary)

    def run_all(self, configs=METABASE_CHARTS) -> list[MetabasePipelineResult]:
        return [self.run(config) for config in configs]
