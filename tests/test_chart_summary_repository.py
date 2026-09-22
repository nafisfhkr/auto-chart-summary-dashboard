from datetime import date
from decimal import Decimal
import json

import pytest

from app.core.models import StructuredInsight
from app.core.summary_validator import ValidationResult
from app.repositories.chart_summary_repository import (
    ChartSummaryRepository, SummaryPersistenceInput, SummarySaveResult,
    build_data_hash, canonical_decimal,
)


def insight(**changes):
    values = dict(dashboard_id="d", chart_id="c", indicator="IPM", region="Jawa Timur",
        frequency="yearly", latest_period=date(2024, 1, 1), latest_value=Decimal("74.6500"),
        previous_period=date(2023, 1, 1), previous_value=Decimal("73.61"), change=Decimal("1.04"),
        change_pct=Decimal("1.41"), trend="meningkat", min_value=Decimal("72.14"),
        min_period=date(2021, 1, 1), max_value=Decimal("74.65"), max_period=date(2024, 1, 1),
        unit="indeks", period_range="2021-01-01 to 2024-01-01")
    values.update(changes)
    return StructuredInsight(**values)


class FakeResult:
    def __init__(self, row): self.row = row
    def first(self): return self.row


class FakeConnection:
    def __init__(self, rows): self.rows, self.calls = iter(rows), []
    def execute(self, statement, parameters):
        self.calls.append((str(statement), parameters))
        return FakeResult(next(self.rows))


class FakeBegin:
    def __init__(self, connection): self.connection = connection
    def __enter__(self): return self.connection
    def __exit__(self, *args): return False


class FakeEngine:
    def __init__(self, rows): self.connection = FakeConnection(rows)
    def begin(self): return FakeBegin(self.connection)


def item(validation, **changes):
    values = dict(insight=insight(), summary_text="Ringkasan.", validation=validation,
        provider="9router", model_name="model", prompt_version="chart-summary-v1",
        latency_ms=123, indicator_code="IPM_CODE")
    values.update(changes)
    return SummaryPersistenceInput(**values)


def test_decimal_and_relevant_hash_behavior():
    assert canonical_decimal(Decimal("995000.000")) == "995000"
    assert canonical_decimal(Decimal("-0.000")) == "0"
    assert canonical_decimal(None) is None
    assert build_data_hash(insight()) == build_data_hash(insight(latest_value=Decimal("74.65")))
    assert build_data_hash(insight(min_period=date(2020, 1, 1))) != build_data_hash(insight())
    assert build_data_hash(insight(max_period=date(2025, 1, 1))) != build_data_hash(insight())


def test_percent_change_pct_is_not_exposed_to_hash():
    assert build_data_hash(insight(unit="persen", change_pct=Decimal("13.15"))) == build_data_hash(insight(unit="persen", change_pct=Decimal("99.99")))
    assert build_data_hash(insight(unit="ton", change_pct=Decimal("-1.49"))) != build_data_hash(insight(unit="ton", change_pct=Decimal("-2.00")))


def test_save_insert_maps_valid_parameters():
    engine = FakeEngine([(7,)])
    result = ChartSummaryRepository(engine).save(item(ValidationResult(True, ())))
    params = engine.connection.calls[0][1]
    assert result == SummarySaveResult(summary_id=7, inserted=True)
    assert params["dashboard_id"] == "d" and params["chart_id"] == "c"
    assert params["indicator_code"] == "IPM_CODE" and params["indicator_name"] == "IPM"
    assert params["period_start"] == date(2021, 1, 1) and params["period_end"] == date(2024, 1, 1)
    assert params["summary_text"] == "Ringkasan." and params["status"] == "draft"
    assert params["provider"] == "9router" and params["model_name"] == "model"
    assert params["prompt_version"] == "chart-summary-v1" and params["validation_status"] == "valid"
    assert params["validation_error"] is None and params["latency_ms"] == 123
    assert len(params["data_hash"]) == 64 and "ON CONFLICT" in engine.connection.calls[0][0]


def test_save_insert_maps_invalid_parameters():
    errors = ("unsupported numeric fact: 13.15", "recommendation language detected")
    engine = FakeEngine([(8,)])
    ChartSummaryRepository(engine).save(item(ValidationResult(False, errors)))
    params = engine.connection.calls[0][1]
    assert params["status"] == "rejected" and params["validation_status"] == "invalid"
    assert params["validation_error"] == json.dumps(list(errors), ensure_ascii=False, separators=(",", ":"))


def test_save_conflict_looks_up_existing_row():
    engine = FakeEngine([None, (7,)])
    result = ChartSummaryRepository(engine).save(item(ValidationResult(True, ())))
    assert result == SummarySaveResult(summary_id=7, inserted=False)
    assert len(engine.connection.calls) == 2 and engine.connection.calls[1][0].lstrip().startswith("SELECT id")


def test_save_conflict_without_existing_row_raises():
    with pytest.raises(RuntimeError, match="existing row was not found"):
        ChartSummaryRepository(FakeEngine([None, None])).save(item(ValidationResult(True, ())))


@pytest.mark.parametrize("field", ["provider", "model_name", "prompt_version"])
def test_blank_generation_metadata_is_rejected(field):
    original = item(ValidationResult(True, ()))
    invalid = SummaryPersistenceInput(**{**original.__dict__, field: "   "})
    with pytest.raises(ValueError, match="must not be blank"):
        ChartSummaryRepository(FakeEngine([])).save(invalid)


def test_negative_latency_is_rejected():
    original = item(ValidationResult(True, ()))
    invalid = SummaryPersistenceInput(**{**original.__dict__, "latency_ms": -1})
    with pytest.raises(ValueError, match="latency_ms"):
        ChartSummaryRepository(FakeEngine([])).save(invalid)
