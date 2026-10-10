"""Immutable deterministic insights for the Metabase pilot."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class RankedItem:
    dimension: str
    series: str
    value: Decimal


@dataclass(frozen=True)
class CategoricalMultiSeriesInsight:
    dashboard_id: str
    chart_id: str
    question_id: int
    title: str
    row_count: int
    dimension_count: int
    series_names: tuple[str, ...]
    top_item_per_series: tuple[RankedItem, ...]
    bottom_item_per_series: tuple[RankedItem, ...]
    overall_max: RankedItem
    series_totals: tuple[tuple[str, Decimal], ...]
    comparison_pairs: tuple[tuple[str, Decimal, Decimal, Decimal], ...]


@dataclass(frozen=True)
class CompositionInsight:
    dashboard_id: str
    chart_id: str
    question_id: int
    title: str
    categories: tuple[tuple[str, Decimal], ...]
    total: Decimal
    shares: tuple[tuple[str, Decimal], ...]
    largest_category: str
    largest_value: Decimal
    difference: Decimal
    difference_pct_points: Decimal
