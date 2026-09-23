from decimal import Decimal
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.config.metabase_charts import METABASE_CHARTS
from app.core.categorical_insight_engine import calculate_categorical_insight
from app.core.composition_insight_engine import calculate_composition_insight
from app.core.metabase_summary_validator import MetabaseSummaryValidator
from app.repositories.metabase_question_repository import MetabaseQuestionRepository, MetabaseQuestionResult, MetabaseRepositoryError
from app.repositories.chart_summary_repository import StoredSummary
from app.api.main import app
from app.services.metabase_embed_service import MetabaseEmbedService
from app.services.metabase_summary_pipeline import build_metabase_data_hash


def result(rows, columns):
    return MetabaseQuestionResult(694, tuple(columns), tuple(rows))


def test_q694_insight_top_and_gap_are_deterministic():
    config = METABASE_CHARTS[0]
    data = result([
        {"kabupaten/kota": "A", "kategori": "Penerimaan", "sum of jumlah": "100"},
        {"kabupaten/kota": "A", "kategori": "Pengeluaran", "sum of jumlah": "70"},
        {"kabupaten/kota": "B", "kategori": "Penerimaan", "sum of jumlah": "100"},
        {"kabupaten/kota": "B", "kategori": "Pengeluaran", "sum of jumlah": "95"},
    ], ["Kabupaten/kota", "Kategori", "Sum of Jumlah"])
    insight = calculate_categorical_insight(config, data)
    assert insight.top_item_per_series[0].dimension == "A"
    assert insight.comparison_pairs[0] == ("A", Decimal("100"), Decimal("70"), Decimal("30"))
    assert insight.overall_max.dimension == "A"


def test_q695_insight_calculates_total_share_and_difference():
    config = METABASE_CHARTS[1]
    data = MetabaseQuestionResult(695, ("kelompok_fiskal", "total_nilai"), ({"kelompok_fiskal": "Pendapatan", "total_nilai": "526"}, {"kelompok_fiskal": "Pengeluaran", "total_nilai": "474"}))
    insight = calculate_composition_insight(config, data)
    assert insight.total == Decimal("1000")
    assert dict(insight.shares) == {"Pendapatan": Decimal("52.60"), "Pengeluaran": Decimal("47.40")}
    assert insight.difference == Decimal("52") and insight.difference_pct_points == Decimal("5.20")


def test_missing_column_and_nonnumeric_value_fail():
    config = METABASE_CHARTS[0]
    with pytest.raises(MetabaseRepositoryError, match="missing"):
        MetabaseQuestionRepository._parse_result(694, {"data": {"cols": [{"name": "Kabupaten/kota"}], "rows": []}}, config)
    data = result([{"kabupaten/kota": "A", "kategori": "Penerimaan", "sum of jumlah": "oops"}], ["Kabupaten/kota", "Kategori", "Sum of Jumlah"])
    with pytest.raises(MetabaseRepositoryError, match="nonnumeric"):
        calculate_categorical_insight(config, data)


def test_q695_result_parser_resolves_display_names_case_insensitively():
    config = METABASE_CHARTS[1]
    parsed = MetabaseQuestionRepository._parse_result(
        695,
        {"data": {"cols": [{"display_name": "KELOMPOK_FISKAL"}, {"name": "TOTAL_NILAI"}], "rows": [["Pendapatan", "526"], ["Pengeluaran", "474"]]}},
        config,
    )
    assert parsed.rows[0]["kelompok_fiskal"] == "Pendapatan"
    assert parsed.rows[1]["total_nilai"] == "474"


def test_missing_auth_configuration_fails_before_network_call():
    class NeverCalled:
        def post(self, *args, **kwargs):
            raise AssertionError("network should not be called")

    with pytest.raises(Exception, match="METABASE_API_KEY"):
        MetabaseQuestionRepository(site_url="https://metabase.example", session=NeverCalled()).fetch(METABASE_CHARTS[0])


def test_metabase_validator_rejects_unsupported_number_cause_and_recommendation():
    config = METABASE_CHARTS[1]
    insight = calculate_composition_insight(config, MetabaseQuestionResult(695, ("kelompok_fiskal", "total_nilai"), ({"kelompok_fiskal": "Pendapatan", "total_nilai": "526"}, {"kelompok_fiskal": "Pengeluaran", "total_nilai": "474"})))
    validator = MetabaseSummaryValidator()
    assert validator.validate("Pendapatan sebesar 526 dan Pengeluaran sebesar 474. Pangsa Pendapatan 52,60 persen.", insight).is_valid
    invalid = validator.validate("Pendapatan 526 karena kebijakan. Sebaiknya naik menjadi 999.", insight)
    assert not invalid.is_valid
    assert any("unsupported numeric" in error for error in invalid.errors)
    assert "unsupported causal claim detected" in invalid.errors
    assert "recommendation language detected" in invalid.errors


def test_embed_token_contains_question_without_secret_in_url():
    pytest.importorskip("jwt")
    url = MetabaseEmbedService("https://metabase.example", "secret").create_question_url(694)
    assert "/embed/question/" in url and "secret" not in url


def test_metabase_hash_changes_with_insight_data_only():
    config = METABASE_CHARTS[1]
    first = calculate_composition_insight(config, MetabaseQuestionResult(695, ("kelompok_fiskal", "total_nilai"), ({"kelompok_fiskal": "Pendapatan", "total_nilai": "526"}, {"kelompok_fiskal": "Pengeluaran", "total_nilai": "474"})))
    second = calculate_composition_insight(config, MetabaseQuestionResult(695, ("kelompok_fiskal", "total_nilai"), ({"kelompok_fiskal": "Pendapatan", "total_nilai": "527"}, {"kelompok_fiskal": "Pengeluaran", "total_nilai": "473"})))
    assert build_metabase_data_hash(config, first) != build_metabase_data_hash(config, second)


def test_metabase_dashboard_endpoint_serializes_latest_valid_summary(monkeypatch):
    class FakeSettings:
        site_url = "https://metabase.example"
        embed_secret_key = "test-secret"

    class FakeEmbed:
        def __init__(self, site_url, secret_key):
            assert site_url == FakeSettings.site_url
            assert secret_key == FakeSettings.embed_secret_key

        def create_question_url(self, question_id):
            return f"https://metabase.example/embed/question/{question_id}"

    class FakeRepository:
        def get_latest_valid_summary(self, dashboard_id, chart_id):
            return StoredSummary(
                summary_id=1,
                summary_text=f"Ringkasan {chart_id}.",
                status="draft",
                validation_status="valid",
                provider="9router",
                model_name="test-model",
                prompt_version="metabase-v1",
                latency_ms=10,
                data_hash="a" * 64,
                generated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            )

    monkeypatch.setattr("app.api.main.get_metabase_settings", lambda: FakeSettings())
    monkeypatch.setattr("app.api.main.MetabaseEmbedService", FakeEmbed)
    monkeypatch.setattr("app.api.main.ChartSummaryRepository", FakeRepository)

    response = TestClient(app).get("/api/metabase/dashboard/metabase_pilot")

    assert response.status_code == 200
    charts = response.json()["charts"]
    assert len(charts) == 2
    assert charts[0]["latest_valid_summary"]["summary_text"] == "Ringkasan metabase_question_694."
    assert charts[1]["latest_valid_summary"]["validation_status"] == "valid"
