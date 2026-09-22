from datetime import date
from decimal import Decimal

import pytest

from app.core.models import StructuredInsight
from app.core.summary_validator import (
    SummaryValidator,
    count_sentences,
    extract_numbers,
    parse_indonesian_number,
)


def make_insight(**overrides):
    values = dict(
        dashboard_id="dashboard", chart_id="chart", indicator="Indikator",
        region="Jawa Timur", frequency="yearly",
        latest_period=date(2024, 1, 1), latest_value=Decimal("74.6500"),
        previous_period=date(2023, 1, 1), previous_value=Decimal("73.6100"),
        change=Decimal("1.0400"), change_pct=Decimal("1.41"), trend="meningkat",
        min_value=Decimal("72.14"), min_period=date(2021, 1, 1),
        max_value=Decimal("74.65"), max_period=date(2024, 1, 1),
        unit="indeks", period_range="2021-01-01 to 2024-01-01",
    )
    values.update(overrides)
    return StructuredInsight(**values)


def validate(text, insight=None):
    return SummaryValidator().validate(text, insight or make_insight())


IPM = (
    "Pada 2024, Indeks Pembangunan Manusia Jawa Timur mencapai 74,65 indeks. "
    "Nilai tersebut meningkat 1,04 indeks dibandingkan 2023 yang sebesar 73,61."
)
ONE_SENTENCE_VALID_FACTS = (
    "Pada 2024 nilainya 74,65 dibandingkan 2023 sebesar 73,61 dengan perubahan 1,04."
)


def test_valid_ipm_summary():
    assert validate(IPM).is_valid


def test_valid_inflation_summary_requires_percentage_points():
    insight = make_insight(
        indicator="Inflasi", frequency="monthly", unit="persen",
        latest_period=date(2026, 6, 1), latest_value=Decimal("2.84"),
        previous_period=date(2026, 5, 1), previous_value=Decimal("2.51"),
        change=Decimal("0.33"), change_pct=Decimal("13.15"),
        min_value=Decimal("2.22"), min_period=date(2026, 3, 1),
        max_value=Decimal("2.84"), max_period=date(2026, 6, 1),
    )
    text = "Inflasi Juni 2026 sebesar 2,84 persen, naik 0,33 poin persentase dari Mei 2026 sebesar 2,51 persen. Data dibandingkan secara deskriptif."
    assert validate(text, insight).is_valid


def test_valid_production_summary_allows_exposed_relative_change():
    insight = make_insight(
        indicator="Produksi Padi", unit="ton", latest_value=Decimal("995000"),
        previous_value=Decimal("1010000"), change=Decimal("-15000"),
        change_pct=Decimal("-1.49"), min_value=Decimal("950000"),
    )
    text = "Produksi Padi pada 2024 sebesar 995.000 ton, menurun 15.000 ton atau 1,49 persen dibandingkan 2023 sebesar 1.010.000 ton. Nilai tersebut berada dalam rentang data yang tersedia."
    assert validate(text, insight).is_valid


@pytest.mark.parametrize("token, expected", [
    ("74,65", Decimal("74.65")), ("74,6500", Decimal("74.6500")),
    ("995.000", Decimal("995000")), ("1.010.000", Decimal("1010000")),
    ("1.234,56", Decimal("1234.56")),
    ("1.010.000,50", Decimal("1010000.50")),
    ("-15.000", Decimal("-15000")), ("-1.234,56", Decimal("-1234.56")),
    ("2024", Decimal("2024")),
])
def test_indonesian_number_parsing(token, expected):
    assert parse_indonesian_number(token) == expected


def test_number_extraction_and_thousands_do_not_split_sentences():
    assert extract_numbers("995.000 ton, 1.010.000,50 ton, dan 1.010.000 ton.") == (
        Decimal("995000"), Decimal("1010000.50"), Decimal("1010000")
    )
    assert count_sentences("Produksi sebesar 995.000 ton. Nilai berubah 15.000 ton.") == 2


@pytest.mark.parametrize("text, valid", [("", False), (ONE_SENTENCE_VALID_FACTS, False), (IPM, True), (IPM + " Nilai maksimum 74,65.", True), (IPM + " Nilai minimum 72,14.", True)])
def test_sentence_count_contract(text, valid):
    assert validate(text).is_valid is valid


def test_four_sentences_are_invalid():
    text = IPM + " Nilai terendah 72,14 pada 2021. Nilai tertinggi 74,65 pada 2024."
    assert not validate(text).is_valid
    assert "summary must contain 2 to 3 sentences" in validate(text).errors


@pytest.mark.parametrize("blank", ["", "   ", "\n", "\t"])
def test_blank_summaries_are_invalid(blank):
    result = validate(blank)
    assert not result.is_valid
    assert result.errors == ("summary is empty",)


@pytest.mark.parametrize("missing", ["2024", "74,65", "2023", "1,04"])
def test_required_facts_are_enforced(missing):
    assert not validate(IPM.replace(missing, "")).is_valid


def test_percent_change_pct_is_not_allowed():
    insight = make_insight(unit="persen", change=Decimal("-0.56"), change_pct=Decimal("-5.41"), latest_value=Decimal("9.79"), previous_value=Decimal("10.35"))
    text = "Pada 2024 nilainya 9,79 persen, menurun 0,56 poin persentase dari 2023 sebesar 10,35 persen. Perubahan relatif 5,41 persen."
    result = validate(text, insight)
    assert not result.is_valid
    assert any("unsupported numeric fact" in error for error in result.errors)


def test_signed_negative_change_is_allowed():
    insight = make_insight(unit="ton", latest_value=Decimal("995000"), previous_value=Decimal("1010000"), change=Decimal("-15000"))
    text = "Produksi pada 2024 sebesar 995.000 ton. Perubahan sebesar -15.000 ton dibandingkan 2023 sebesar 1.010.000 ton."
    assert validate(text, insight).is_valid


def test_signed_non_percent_change_pct_is_allowed():
    insight = make_insight(change_pct=Decimal("-1.49"))
    text = "Pada 2024 nilainya 74,65, berubah 1,04 dari 2023 sebesar 73,61. Perubahan relatif -1,49 persen."
    assert validate(text, insight).is_valid


def test_period_range_start_year_is_allowed_even_when_not_minimum_period():
    insight = make_insight(period_range="2020-01-01 to 2024-01-01", min_period=date(2021, 1, 1))
    text = "Pada 2024 nilainya 74,65 dibandingkan 2023 sebesar 73,61, berubah 1,04. Data mencakup periode 2020 hingga 2024."
    assert validate(text, insight).is_valid


def test_monthly_period_accepts_tahun_label():
    insight = make_insight(
        frequency="monthly", latest_period=date(2026, 6, 1), previous_period=date(2026, 5, 1),
    )
    text = "Pada Juni tahun 2026 nilainya 74,65 dibandingkan Mei tahun 2026 sebesar 73,61. Perubahannya 1,04."
    assert validate(text, insight).is_valid


def test_percent_change_requires_percentage_point_wording():
    insight = make_insight(unit="persen", change=Decimal("0.33"), latest_value=Decimal("2.84"), previous_value=Decimal("2.51"))
    text = "Pada 2024 nilainya 2,84 persen, meningkat 0,33 persen dari 2023 sebesar 2,51 persen. Perbandingan ini sesuai data."
    result = validate(text, insight)
    assert any("poin persentase" in error for error in result.errors)


def test_percentage_point_phrase_must_be_associated_with_change_magnitude():
    insight = make_insight(unit="persen", change=Decimal("0.33"), latest_value=Decimal("2.84"), previous_value=Decimal("2.51"))
    text = "Pada 2024 nilainya 2,84 persen, meningkat 0,33 persen dari 2023 sebesar 2,51 persen. Poin persentase digunakan dalam analisis."
    result = validate(text, insight)
    assert any("poin persentase" in error for error in result.errors)


@pytest.mark.parametrize("text", [
    "# Ringkasan\n" + IPM,
    "- Ringkasan\n" + IPM,
    "* Ringkasan\n" + IPM,
])
def test_markdown_summary_is_rejected(text):
    result = validate(text)
    assert not result.is_valid
    assert "summary must be plain prose without markdown" in result.errors


@pytest.mark.parametrize("phrase", ["karena harga naik", "disebabkan faktor lain", "didorong oleh permintaan", "akibat perubahan", "dipengaruhi faktor lain", "memengaruhi kondisi", "berkat kebijakan"])
def test_causal_language_is_rejected(phrase):
    assert "unsupported causal claim detected" in validate(IPM + " " + phrase + ".").errors


@pytest.mark.parametrize("phrase", ["sebaiknya ditingkatkan", "disarankan melakukan", "direkomendasikan untuk berubah", "hendaknya berubah", "harus berubah", "perlu dilakukan"])
def test_recommendation_language_is_rejected(phrase):
    assert "recommendation language detected" in validate(IPM + " " + phrase + ".").errors
