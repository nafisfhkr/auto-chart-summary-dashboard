"""Repository for clean chart observations."""

from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.core.models import ChartObservation
from app.repositories.database import create_database_engine


class CleanDataRepository:
    """Read generic chart data from result_cleansing."""

    def __init__(self, engine: Engine | None = None) -> None:
        self.engine = engine or create_database_engine()

    def get_chart_data(
        self, dashboard_id: str, chart_id: str
    ) -> list[ChartObservation]:
        query = text(
            """
            SELECT dashboard_id, chart_id, indicator_code, indicator_name,
                   region_code, region_name, period_start, period_end,
                   frequency, value, unit, dimensions, source_name
            FROM result_cleansing
            WHERE dashboard_id = :dashboard_id
              AND chart_id = :chart_id
            ORDER BY period_start ASC
            """
        )
        with self.engine.connect() as connection:
            rows = connection.execute(
                query, {"dashboard_id": dashboard_id, "chart_id": chart_id}
            ).mappings().all()
        return [self._to_observation(row) for row in rows]

    @staticmethod
    def _to_observation(row: dict[str, Any]) -> ChartObservation:
        return ChartObservation(
            dashboard_id=row["dashboard_id"],
            chart_id=row["chart_id"],
            indicator_code=row["indicator_code"],
            indicator_name=row["indicator_name"],
            region_code=row["region_code"],
            region_name=row["region_name"],
            period_start=row["period_start"],
            period_end=row["period_end"],
            frequency=row["frequency"],
            value=Decimal(row["value"]),
            unit=row["unit"],
            dimensions=dict(row["dimensions"] or {}),
            source_name=row["source_name"],
        )
