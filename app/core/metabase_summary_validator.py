"""Generic deterministic validator for Metabase pilot summaries."""

import re
from decimal import Decimal

from app.core.metabase_insights import CategoricalMultiSeriesInsight, CompositionInsight
from app.core.summary_validator import ValidationResult, count_sentences, extract_numbers

_CAUSAL = re.compile(r"\b(?:karena|disebabkan|menyebabkan|didorong|dipengaruhi|akibat|berkat)\b", re.I)
_RECOMMENDATION = re.compile(r"\b(?:sebaiknya|disarankan|direkomendasikan|hendaknya|harus)\b|\bperlu\s+dilakukan\b", re.I)


class MetabaseSummaryValidator:
    def validate(self, summary: str, insight: CategoricalMultiSeriesInsight | CompositionInsight) -> ValidationResult:
        if not summary or not summary.strip():
            return ValidationResult(False, ("summary is empty",))
        errors = []
        if not 2 <= count_sentences(summary) <= 3:
            errors.append("summary must contain 2 to 3 sentences")
        if re.search(r"(?m)^\s*(?:#|[-*])\s+", summary):
            errors.append("summary must be plain prose without markdown")
        if _CAUSAL.search(summary):
            errors.append("unsupported causal claim detected")
        if _RECOMMENDATION.search(summary):
            errors.append("recommendation language detected")
        allowed = self._allowed_numbers(insight)
        for number in extract_numbers(summary):
            if number not in allowed:
                errors.append(f"unsupported numeric fact: {number}")
        return ValidationResult(not errors, tuple(dict.fromkeys(errors)))

    @staticmethod
    def _allowed_numbers(insight: CategoricalMultiSeriesInsight | CompositionInsight) -> set[Decimal]:
        if isinstance(insight, CompositionInsight):
            return {insight.total, insight.largest_value, insight.difference, insight.difference_pct_points, *(value for _, value in insight.categories), *(value for _, value in insight.shares)}
        return {
            Decimal(insight.row_count), Decimal(insight.dimension_count),
            *(item.value for item in insight.top_item_per_series),
            *(item.value for item in insight.bottom_item_per_series),
            insight.overall_max.value,
            *(value for _, value in insight.series_totals),
            *(number for _, income, expense, gap in insight.comparison_pairs for number in (income, expense, gap)),
        }
