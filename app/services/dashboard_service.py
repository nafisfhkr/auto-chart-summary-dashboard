"""Read-only dashboard aggregation service."""

from dataclasses import asdict, dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from app.repositories.chart_summary_repository import ChartSummaryRepository, StoredSummary
from app.repositories.clean_data_repository import CleanDataRepository

DEMO_CHARTS = ("chart_ipm", "chart_kemiskinan", "chart_tpt", "chart_inflasi", "chart_produksi_padi")
CHART_TYPES = {"chart_ipm": "line", "chart_kemiskinan": "bar", "chart_tpt": "bar", "chart_inflasi": "area", "chart_produksi_padi": "bar"}


@dataclass(frozen=True)
class DashboardService:
    clean_data_repository: CleanDataRepository
    chart_summary_repository: ChartSummaryRepository

    def get_dashboard(self, dashboard_id: str) -> dict[str, Any] | None:
        charts = []
        for chart_id in DEMO_CHARTS:
            observations = self.clean_data_repository.get_chart_data(dashboard_id, chart_id)
            if not observations:
                continue
            summary = self.chart_summary_repository.get_latest_valid_summary(dashboard_id, chart_id)
            first = observations[0]
            charts.append({
                "chart_id": chart_id,
                "chart_type": CHART_TYPES[chart_id],
                "indicator_code": first.indicator_code,
                "indicator_name": first.indicator_name,
                "region": first.region_name,
                "frequency": first.frequency,
                "unit": first.unit,
                "observations": [{"period": _json_value(item.period_start), "value": str(item.value)} for item in observations],
                "summary": _summary_dict(summary),
            })
        return {"dashboard_id": dashboard_id, "charts": charts} if charts else None


def _json_value(value: date | datetime) -> str:
    return value.isoformat()


def _summary_dict(summary: StoredSummary | None) -> dict[str, Any] | None:
    if summary is None:
        return None
    result = asdict(summary)
    if result["generated_at"] is not None:
        result["generated_at"] = result["generated_at"].isoformat()
    return result
