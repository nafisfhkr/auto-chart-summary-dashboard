from datetime import date
from decimal import Decimal

from app.core.models import ChartObservation
from app.repositories.chart_summary_repository import StoredSummary
from app.services.dashboard_service import DashboardService


def observation(chart_id, year):
    return ChartObservation("dashboard_jatim_demo", chart_id, "CODE", chart_id,
        "JTM", "Jawa Timur", date(year, 1, 1), None, "yearly",
        Decimal("10.5"), "indeks")


class FakeData:
    def get_chart_data(self, dashboard_id, chart_id):
        return [observation(chart_id, 2023), observation(chart_id, 2024)] if chart_id in {"chart_ipm", "chart_tpt"} else []


class FakeSummaries:
    def get_latest_valid_summary(self, dashboard_id, chart_id):
        return StoredSummary(1, "Ringkasan.", "draft", "valid", "9router", "model", "v1", 10, "hash", None) if chart_id == "chart_ipm" else None


def test_dashboard_combines_data_and_keeps_chart_without_summary():
    result = DashboardService(FakeData(), FakeSummaries()).get_dashboard("dashboard_jatim_demo")
    assert [chart["chart_id"] for chart in result["charts"]] == ["chart_ipm", "chart_tpt"]
    assert result["charts"][0]["summary"]["summary_text"] == "Ringkasan."
    assert result["charts"][1]["summary"] is None
