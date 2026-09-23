"""Deterministic processor for Q695."""

from decimal import Decimal, ROUND_HALF_UP

from app.config.metabase_charts import MetabaseChartConfig
from app.core.metabase_insights import CompositionInsight
from app.repositories.metabase_question_repository import MetabaseQuestionRepository, MetabaseQuestionResult


def calculate_composition_insight(config: MetabaseChartConfig, result: MetabaseQuestionResult) -> CompositionInsight:
    if config.insight_type != "composition" or not config.category_column:
        raise ValueError("Invalid composition Metabase configuration")
    key_category, key_value = MetabaseQuestionRepository._normalise(config.category_column), MetabaseQuestionRepository._normalise(config.value_column)
    values = {}
    for row in result.rows:
        category = str(row.get(key_category, "")).strip()
        if not category or category in values:
            raise ValueError(f"Invalid or duplicate Q695 category: {category}")
        values[category] = MetabaseQuestionRepository.value(row, key_value)
    if not values:
        raise ValueError("Q695 result is empty")
    categories = tuple(sorted(values.items()))
    total = sum(values.values(), Decimal("0"))
    if total == 0:
        raise ValueError("Q695 total must not be zero")
    shares = tuple((category, (value / total * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)) for category, value in categories)
    largest_category, largest_value = min(categories, key=lambda item: (-item[1], item[0]))
    ordered = sorted(values.values(), reverse=True)
    difference = ordered[0] - ordered[1] if len(ordered) > 1 else ordered[0]
    share_values = sorted((share for _, share in shares), reverse=True)
    difference_pct_points = share_values[0] - share_values[1] if len(share_values) > 1 else share_values[0]
    return CompositionInsight(config.dashboard_id, config.chart_id, config.question_id, config.title, categories, total, shares, largest_category, largest_value, difference, difference_pct_points)
