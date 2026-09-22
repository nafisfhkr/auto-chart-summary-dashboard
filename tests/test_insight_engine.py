from datetime import date
from decimal import Decimal

import pytest

from app.core.insight_engine import InsightEngine, InsightValidationError
from app.core.models import ChartObservation


def observation(period: str, value: str, **overrides) -> ChartObservation:
    defaults = {
        "dashboard_id": "dashboard",
        "chart_id": "chart",
        "indicator_code": "CODE",
        "indicator_name": "Indicator",
        "region_code": "REGION",
        "region_name": "Region",
        "period_start": date.fromisoformat(period),
        "period_end": None,
        "frequency": "yearly",
        "value": Decimal(value),
        "unit": "indeks",
        "dimensions": {},
        "source_name": "test",
    }
    defaults.update(overrides)
    return ChartObservation(**defaults)


def calculate(values, periods=None, **overrides):
    periods = periods or [f"202{i}-01-01" for i in range(len(values))]
    return InsightEngine().calculate(
        [observation(period, value, **overrides) for period, value in zip(periods, values)]
    )


def test_increasing_yearly_data():
    insight = calculate(["72.14", "73.61", "74.65"])
    assert insight.trend == "meningkat"
    assert insight.change == Decimal("1.04")
    assert insight.change_pct == Decimal("1.41")


def test_decreasing_and_equal_values():
    assert calculate(["10", "8"]).trend == "menurun"
    assert calculate(["8", "8"]).trend == "tetap"


def test_monthly_data_and_fluctuating_min_max():
    insight = calculate(
        ["2.31", "2.48", "2.22", "2.67", "2.51", "2.84"],
        periods=[f"2026-0{month}-01" for month in range(1, 7)],
        frequency="monthly",
        unit="persen",
    )
    assert insight.latest_period == date(2026, 6, 1)
    assert insight.previous_period == date(2026, 5, 1)
    assert insight.change == Decimal("0.33")
    assert insight.change_pct == Decimal("13.15")
    assert insight.min_value == Decimal("2.22")
    assert insight.max_value == Decimal("2.84")
    assert insight.min_period == date(2026, 3, 1)
    assert insight.max_period == date(2026, 6, 1)


def test_repeated_min_and_max_use_earliest_period():
    insight = calculate(
        ["5", "2", "5", "2"],
        periods=["2021-01-01", "2022-01-01", "2023-01-01", "2024-01-01"],
    )
    assert insight.min_period == date(2022, 1, 1)
    assert insight.max_period == date(2021, 1, 1)


def test_unsorted_input_is_sorted():
    insight = InsightEngine().calculate(
        [
            observation("2024-01-01", "74.65"),
            observation("2022-01-01", "72.75"),
            observation("2023-01-01", "73.61"),
        ]
    )
    assert insight.latest_period == date(2024, 1, 1)
    assert insight.previous_period == date(2023, 1, 1)


def test_zero_previous_value_returns_none_percentage():
    insight = calculate(["0", "2"])
    assert insight.change_pct is None


@pytest.mark.parametrize(
    "items, message",
    [
        ([], "At least one observation"),
        ([observation("2024-01-01", "1")], "At least two observations"),
    ],
)
def test_invalid_observation_count(items, message):
    with pytest.raises(InsightValidationError, match=message):
        InsightEngine().calculate(items)


def test_mixed_chart_ids_fail():
    items = [observation("2023-01-01", "1"), observation("2024-01-01", "2", chart_id="other")]
    with pytest.raises(InsightValidationError, match="chart_id"):
        InsightEngine().calculate(items)


def test_mixed_dashboard_ids_fail():
    items = [
        observation(
            "2023-01-01",
            "1",
            dashboard_id="dashboard_a",
        ),
        observation(
            "2024-01-01",
            "2",
            dashboard_id="dashboard_b",
        ),
    ]

    with pytest.raises(
        InsightValidationError,
        match="dashboard_id",
    ):
        InsightEngine().calculate(items)


@pytest.mark.parametrize(
    "field, value",
    [("indicator_code", "OTHER_CODE"), ("indicator_name", "Other indicator")],
)
def test_inconsistent_indicator_fails(field, value):
    items = [
        observation("2023-01-01", "1"),
        observation("2024-01-01", "2", **{field: value}),
    ]
    with pytest.raises(InsightValidationError, match=field):
        InsightEngine().calculate(items)


@pytest.mark.parametrize(
    "field, value",
    [("region_code", "OTHER_REGION"), ("region_name", "Other region")],
)
def test_inconsistent_region_fails(field, value):
    items = [
        observation("2023-01-01", "1"),
        observation("2024-01-01", "2", **{field: value}),
    ]
    with pytest.raises(InsightValidationError, match=field):
        InsightEngine().calculate(items)


def test_duplicate_period_start_fails():
    items = [
        observation("2024-01-01", "1"),
        observation("2024-01-01", "2"),
    ]
    with pytest.raises(InsightValidationError, match="Duplicate period_start"):
        InsightEngine().calculate(items)


def test_inconsistent_frequency_and_unit_fail():
    for field, value in [("frequency", "monthly"), ("unit", "persen")]:
        items = [
            observation("2023-01-01", "1"),
            observation("2024-01-01", "2", **{field: value}),
        ]
        with pytest.raises(InsightValidationError, match=field):
            InsightEngine().calculate(items)


def test_multiple_dimension_series_fail():
    items = [
        observation("2023-01-01", "1"),
        observation("2024-01-01", "2", dimensions={"category": "other"}),
    ]
    with pytest.raises(InsightValidationError, match="dimension"):
        InsightEngine().calculate(items)
