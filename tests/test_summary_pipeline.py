from datetime import date
from decimal import Decimal

import pytest

from app.core.models import ChartObservation, StructuredInsight
from app.core.summary_validator import ValidationResult
from app.providers.base import LLMProviderError
from app.repositories.chart_summary_repository import (
    SummaryPersistenceInput,
    SummarySaveResult,
    build_data_hash,
)
from app.services.summary_pipeline import PipelineResult, SummaryPipeline, SummaryPipelineError


def observation(indicator_code="IPM_CODE"):
    return ChartObservation(
        dashboard_id="dashboard_jatim", chart_id="chart_ipm", indicator_code=indicator_code,
        indicator_name="IPM", region_code="JATIM", region_name="Jawa Timur",
        period_start=date(2023, 1, 1), period_end=date(2023, 12, 31), frequency="yearly",
        value=Decimal("73.61"), unit="indeks", dimensions={}, source_name="dummy",
    )


def insight():
    return StructuredInsight(
        dashboard_id="dashboard_jatim", chart_id="chart_ipm", indicator="IPM",
        region="Jawa Timur", frequency="yearly", latest_period=date(2024, 1, 1),
        latest_value=Decimal("74.65"), previous_period=date(2023, 1, 1),
        previous_value=Decimal("73.61"), change=Decimal("1.04"),
        change_pct=Decimal("1.41"), trend="meningkat", min_value=Decimal("73.61"),
        min_period=date(2023, 1, 1), max_value=Decimal("74.65"),
        max_period=date(2024, 1, 1), unit="indeks",
        period_range="2023-01-01 to 2024-01-01",
    )


class FakeDataRepository:
    def __init__(self, observations):
        self.observations = observations
        self.calls = []

    def get_chart_data(self, dashboard_id, chart_id):
        self.calls.append((dashboard_id, chart_id))
        return self.observations


class FakeEngine:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def calculate(self, observations):
        self.calls.append(observations)
        return self.result


class FakeSummaryService:
    def __init__(self, result=None, error=None):
        self.result, self.error, self.calls = result, error, []

    def generate(self, insight_value):
        self.calls.append(insight_value)
        if self.error:
            raise self.error
        return self.result


class FakeValidator:
    def __init__(self, result):
        self.result, self.calls = result, []

    def validate(self, summary, insight_value):
        self.calls.append((summary, insight_value))
        return self.result


class FakeSummaryRepository:
    def __init__(self, result):
        self.result, self.calls = result, []

    def save(self, item):
        self.calls.append(item)
        return self.result


def make_pipeline(observations=None, summary="Ringkasan.", validation=None, save=None, error=None):
    data = FakeDataRepository(observations if observations is not None else [observation()])
    engine = FakeEngine(insight())
    service = FakeSummaryService(summary, error)
    validator = FakeValidator(validation or ValidationResult(True, ()))
    repository = FakeSummaryRepository(save or SummarySaveResult(7, True))
    pipeline = SummaryPipeline(data, engine, service, validator, repository, "9router", "model-x", "v1")
    return pipeline, data, engine, service, validator, repository


def test_valid_flow_composes_dependencies_and_returns_result():
    pipeline, data, engine, service, validator, repository = make_pipeline()
    result = pipeline.run("dashboard_jatim", "chart_ipm")

    assert data.calls == [("dashboard_jatim", "chart_ipm")]
    assert engine.calls == [[observation()]]
    assert service.calls == [insight()]
    assert validator.calls == [("Ringkasan.", insight())]
    item = repository.calls[0]
    assert isinstance(item, SummaryPersistenceInput)
    assert item.provider == "9router" and item.model_name == "model-x"
    assert item.prompt_version == "v1" and item.indicator_code == "IPM_CODE"
    assert isinstance(result, PipelineResult)
    assert result.summary_id == 7 and result.inserted is True
    assert result.data_hash == build_data_hash(insight())


def test_invalid_summary_is_still_persisted():
    validation = ValidationResult(False, ("unsupported numeric fact: 99",))
    pipeline, _, _, _, _, repository = make_pipeline(validation=validation)

    result = pipeline.run("dashboard_jatim", "chart_ipm")

    assert result.validation == validation
    assert repository.calls[0].validation == validation


def test_no_observations_stops_before_llm_validation_and_persistence():
    pipeline, _, _, service, validator, repository = make_pipeline(observations=[])

    with pytest.raises(SummaryPipelineError, match="No observations found for dashboard_jatim/chart_ipm"):
        pipeline.run("dashboard_jatim", "chart_ipm")

    assert service.calls == [] and validator.calls == [] and repository.calls == []


def test_provider_failure_is_propagated_and_not_persisted():
    error = LLMProviderError("provider unavailable")
    pipeline, _, _, _, validator, repository = make_pipeline(error=error)

    with pytest.raises(LLMProviderError, match="provider unavailable"):
        pipeline.run("dashboard_jatim", "chart_ipm")

    assert validator.calls == [] and repository.calls == []


def test_persistence_failure_is_propagated():
    class FailingRepository(FakeSummaryRepository):
        def save(self, item):
            self.calls.append(item)
            raise RuntimeError("database unavailable")

    pipeline, _, _, _, _, repository = make_pipeline()
    pipeline.chart_summary_repository = FailingRepository(SummarySaveResult(0, False))

    with pytest.raises(RuntimeError, match="database unavailable"):
        pipeline.run("dashboard_jatim", "chart_ipm")


def test_existing_row_preserves_inserted_false():
    pipeline, _, _, _, _, _ = make_pipeline(save=SummarySaveResult(10, False))

    result = pipeline.run("dashboard_jatim", "chart_ipm")

    assert result.summary_id == 10 and result.inserted is False
