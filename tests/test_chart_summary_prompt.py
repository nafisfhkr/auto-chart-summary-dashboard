from datetime import date
from decimal import Decimal

from app.core.models import StructuredInsight
from app.prompts.chart_summary import (
    PROMPT_VERSION,
    build_chart_summary_messages,
    format_number,
    format_period,
)


def insight(**overrides):
    values = dict(
        dashboard_id="dashboard",
        chart_id="chart",
        indicator="Indeks Pembangunan Manusia",
        region="Jawa Timur",
        frequency="yearly",
        latest_period=date(2024, 1, 1),
        latest_value=Decimal("74.6500"),
        previous_period=date(2023, 1, 1),
        previous_value=Decimal("73.6100"),
        change=Decimal("1.0400"),
        change_pct=Decimal("1.41"),
        trend="meningkat",
        min_value=Decimal("72.14"),
        min_period=date(2021, 1, 1),
        max_value=Decimal("74.65"),
        max_period=date(2024, 1, 1),
        unit="indeks",
        period_range="2021-01-01 to 2024-01-01",
    )
    values.update(overrides)
    return StructuredInsight(**values)


def prompt_text(item):
    return "\n".join(message["content"] for message in build_chart_summary_messages(item))


def test_yearly_ipm_prompt_contains_formatted_facts_and_range():
    text = prompt_text(insight())
    for expected in ("Indeks Pembangunan Manusia", "Jawa Timur", "2024", "74,65", "2023", "73,61", "1,04", "72,14", "2021"):
        assert expected in text


def test_monthly_inflation_prompt_uses_month_names_and_percentage_points():
    text = prompt_text(insight(
        indicator="Inflasi", frequency="monthly", unit="persen",
        latest_period=date(2026, 6, 1), latest_value=Decimal("2.84"),
        previous_period=date(2026, 5, 1), previous_value=Decimal("2.51"),
        change=Decimal("0.33"), change_pct=Decimal("13.15"),
        min_value=Decimal("2.22"), min_period=date(2026, 1, 1),
        max_value=Decimal("2.84"), max_period=date(2026, 6, 1),
    ))
    assert "Juni 2026" in text and "Mei 2026" in text
    assert "2,84" in text and "2,51" in text and "0,33" in text
    assert "poin persentase" in text
    assert "13,15" not in text


def test_non_percent_prompt_keeps_relative_percentage_change():
    text = prompt_text(insight())
    assert "1,41" in text


def test_large_numbers_are_formatted_consistently():
    assert format_number(Decimal("995000.0000")) == "995.000"


def test_negative_numbers_are_formatted_consistently():
    assert format_number(Decimal("-15000.0000")) == "-15.000"


def test_prompt_safety_rules_and_version():
    text = prompt_text(insight())
    assert "menambahkan atau mengubah angka" in text
    assert "menginferensikan sebab" in text
    assert "rekomendasi" in text
    assert PROMPT_VERSION == "chart-summary-v1"


def test_period_formatting_falls_back_to_iso():
    assert format_period(date(2024, 1, 1), "quarterly") == "2024-01-01"
