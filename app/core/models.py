"""Domain models shared by repositories and the insight engine."""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class ChartObservation:
    """One clean observation belonging to a logical chart series."""

    dashboard_id: str
    chart_id: str
    indicator_code: str | None
    indicator_name: str
    region_code: str | None
    region_name: str
    period_start: date
    period_end: date | None
    frequency: str
    value: Decimal
    unit: str | None
    dimensions: dict[str, Any] = field(default_factory=dict)
    source_name: str | None = None


@dataclass(frozen=True)
class StructuredInsight:
    """Deterministic facts calculated from one chart's observations."""

    dashboard_id: str
    chart_id: str
    indicator: str
    region: str
    frequency: str
    latest_period: date
    latest_value: Decimal
    previous_period: date
    previous_value: Decimal
    change: Decimal
    change_pct: Decimal | None
    trend: str
    min_value: Decimal
    min_period: date
    max_value: Decimal
    max_period: date
    unit: str | None
    period_range: str
