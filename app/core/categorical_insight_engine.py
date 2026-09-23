"""Deterministic processor for Q694."""

from decimal import Decimal

from app.config.metabase_charts import MetabaseChartConfig
from app.core.metabase_insights import CategoricalMultiSeriesInsight, RankedItem
from app.repositories.metabase_question_repository import MetabaseQuestionRepository, MetabaseQuestionResult


def calculate_categorical_insight(config: MetabaseChartConfig, result: MetabaseQuestionResult) -> CategoricalMultiSeriesInsight:
    if config.insight_type != "categorical_multi_series" or not config.dimension_column or not config.series_column:
        raise ValueError("Invalid categorical Metabase configuration")
    key_dimension, key_series, key_value = map(MetabaseQuestionRepository._normalise, (config.dimension_column, config.series_column, config.value_column))
    values: dict[tuple[str, str], Decimal] = {}
    for row in result.rows:
        dimension, series = str(row.get(key_dimension, "")).strip(), str(row.get(key_series, "")).strip()
        if not dimension or not series:
            raise ValueError("Q694 contains a blank dimension or series")
        if (dimension, series) in values:
            raise ValueError(f"Duplicate Q694 row: {dimension}/{series}")
        values[(dimension, series)] = MetabaseQuestionRepository.value(row, key_value)
    if not values:
        raise ValueError("Q694 result is empty")
    series_names = tuple(sorted({series for _, series in values}))
    top, bottom = [], []
    for series in series_names:
        items = sorted((RankedItem(d, series, v) for (d, s), v in values.items() if s == series), key=lambda item: (-item.value, item.dimension))
        top.append(items[0])
        bottom.append(items[-1])
    overall = min(top, key=lambda item: (-item.value, item.dimension, item.series))
    totals = tuple((series, sum((value for (dimension, current), value in values.items() if current == series), Decimal("0"))) for series in series_names)
    pairs = []
    dimensions = sorted({dimension for dimension, _ in values})
    for dimension in dimensions:
        income, expense = values.get((dimension, "Penerimaan")), values.get((dimension, "Pengeluaran"))
        if income is not None and expense is not None:
            pairs.append((dimension, income, expense, income - expense))
    pairs = tuple(sorted(pairs, key=lambda item: (-abs(item[3]), item[0])))
    return CategoricalMultiSeriesInsight(config.dashboard_id, config.chart_id, config.question_id, config.title, len(result.rows), len(dimensions), series_names, tuple(top), tuple(bottom), overall, totals, pairs[:3])
