"""Deterministic chart insight calculations."""

from collections.abc import Iterable
from decimal import Decimal, ROUND_HALF_UP
import json

from app.core.models import ChartObservation, StructuredInsight


class InsightValidationError(ValueError):
    """Raised when observations cannot form one valid chart series."""


class InsightEngine:
    """Calculate factual insights without database or LLM dependencies."""

    def calculate(
        self, observations: Iterable[ChartObservation]
    ) -> StructuredInsight:
        ordered = sorted(observations, key=lambda item: item.period_start)
        self._validate(ordered)

        first = ordered[0]
        previous = ordered[-2]
        latest = ordered[-1]
        change = latest.value - previous.value
        change_pct = self._percentage_change(previous.value, change)

        return StructuredInsight(
            dashboard_id=latest.dashboard_id,
            chart_id=latest.chart_id,
            indicator=latest.indicator_name,
            region=latest.region_name,
            frequency=latest.frequency,
            latest_period=latest.period_start,
            latest_value=latest.value,
            previous_period=previous.period_start,
            previous_value=previous.value,
            change=change,
            change_pct=change_pct,
            trend=("meningkat" if change > 0 else "menurun" if change < 0 else "tetap"),
            min_value=min(item.value for item in ordered),
            max_value=max(item.value for item in ordered),
            unit=latest.unit,
            period_range=(
                f"{first.period_start.isoformat()} to "
                f"{latest.period_start.isoformat()}"
            ),
        )

    @staticmethod
    def _percentage_change(
        previous_value: Decimal, change: Decimal
    ) -> Decimal | None:
        if previous_value == 0:
            return None
        # Keep the public prototype result stable to two decimal places.
        return ((change / previous_value) * 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    @staticmethod
    def _validate(observations: list[ChartObservation]) -> None:
        if not observations:
            raise InsightValidationError("At least one observation is required")
        if len(observations) < 2:
            raise InsightValidationError(
                "At least two observations are required for period comparison"
            )

        def ensure_single(field: str, label: str) -> None:
            values = {getattr(item, field) for item in observations}
            if len(values) != 1:
                raise InsightValidationError(
                    f"Observations must have one consistent {label}"
                )

        ensure_single("dashboard_id", "dashboard_id")
        ensure_single("chart_id", "chart_id")
        ensure_single("indicator_code", "indicator_code")
        ensure_single("indicator_name", "indicator_name")
        ensure_single("region_code", "region_code")
        ensure_single("region_name", "region_name")
        ensure_single("frequency", "frequency")
        ensure_single("unit", "unit")

        periods = [item.period_start for item in observations]
        if len(periods) != len(set(periods)):
            raise InsightValidationError(
                "Duplicate period_start values are not supported for one chart series"
            )

        series = {
            json.dumps(item.dimensions, sort_keys=True, separators=(",", ":"))
            for item in observations
        }
        if len(series) != 1:
            raise InsightValidationError(
                "Multiple dimension series are not supported for one chart"
            )
