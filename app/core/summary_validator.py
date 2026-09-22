"""Deterministic validation for generated chart summaries."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import re

from app.core.models import StructuredInsight
from app.prompts.chart_summary import format_period


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    errors: tuple[str, ...]


# A dot is treated as a sentence boundary only when it is not inside a number.
_SENTENCE_END = re.compile(r"[.!?]+(?=\s|$)")
_NUMBER = re.compile(
    r"(?<![\w])[-+]?"
    r"(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?(?![\w])"
)
_PERCENTAGE_POINT = re.compile(
    r"(?P<number>[-+]?"
    r"(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?)"
    r"\s+poin\s+persentase\b",
    re.IGNORECASE,
)
_CAUSAL_TERMS = re.compile(
    r"\b(?:karena|disebabkan|menyebabkan|didorong(?:\s+oleh)?|"
    r"dipengaruhi|memengaruhi|akibat|berkat|faktor penyebab)\b",
    re.IGNORECASE,
)
_RECOMMENDATION_TERMS = re.compile(
    r"\b(?:sebaiknya|disarankan|direkomendasikan|hendaknya|harus)\b|"
    r"\bperlu\s+dilakukan\b",
    re.IGNORECASE,
)


def parse_indonesian_number(token: str) -> Decimal:
    """Parse the Indonesian numeric forms emitted by the prompt."""
    normalized = token.replace(".", "").replace(",", ".")
    try:
        return Decimal(normalized)
    except InvalidOperation as exc:
        raise ValueError(f"invalid Indonesian number: {token}") from exc


def extract_numbers(text: str) -> tuple[Decimal, ...]:
    """Extract and normalize Indonesian-formatted numbers from prose."""
    return tuple(parse_indonesian_number(match.group()) for match in _NUMBER.finditer(text))


def count_sentences(text: str) -> int:
    """Count terminal punctuation without splitting thousands separators."""
    return len(_SENTENCE_END.findall(text))


class SummaryValidator:
    """Validate summary shape, factuality, and unsupported claims."""

    def validate(self, summary: str, insight: StructuredInsight) -> ValidationResult:
        if not summary or not summary.strip():
            return ValidationResult(False, ("summary is empty",))

        errors: list[str] = []
        sentence_count = count_sentences(summary)
        if not 2 <= sentence_count <= 3:
            errors.append("summary must contain 2 to 3 sentences")

        if re.search(r"(?m)^\s*(?:#|[-*])\s+", summary):
            errors.append("summary must be plain prose without markdown")
        if _CAUSAL_TERMS.search(summary):
            errors.append("unsupported causal claim detected")
        if _RECOMMENDATION_TERMS.search(summary):
            errors.append("recommendation language detected")

        allowed = self._allowed_numbers(insight)
        for number in extract_numbers(summary):
            if number not in allowed:
                errors.append(f"unsupported numeric fact: {number}")

        self._require_period(summary, insight.latest_period, insight.frequency, "latest period", errors)
        self._require_period(summary, insight.previous_period, insight.frequency, "previous period", errors)
        self._require_number(summary, insight.latest_value, "latest value", errors)
        self._require_number(summary, insight.change, "change magnitude", errors, absolute=True, required=insight.change != 0)
        if not self._contains_number(summary, insight.previous_value):
            errors.append("previous value is missing")

        if insight.unit == "persen" and self._contains_number(summary, insight.change, absolute=True):
            percentage_point_numbers = {
                parse_indonesian_number(match.group("number"))
                for match in _PERCENTAGE_POINT.finditer(summary)
            }
            if abs(insight.change) not in percentage_point_numbers:
                errors.append("percent-unit absolute change must use 'poin persentase'")

        return ValidationResult(not errors, tuple(dict.fromkeys(errors)))

    @staticmethod
    def _allowed_numbers(insight: StructuredInsight) -> set[Decimal]:
        values = {
            insight.latest_value,
            insight.previous_value,
            insight.min_value,
            insight.max_value,
            insight.change,
            abs(insight.change),
            *SummaryValidator._period_years(insight),
        }
        if insight.unit != "persen" and insight.change_pct is not None:
            values.add(insight.change_pct)
            values.add(abs(insight.change_pct))
        return values

    @staticmethod
    def _period_years(insight: StructuredInsight) -> set[Decimal]:
        years = {
            Decimal(str(period.year))
            for period in (
                insight.latest_period,
                insight.previous_period,
                insight.min_period,
                insight.max_period,
            )
        }
        range_parts = [part.strip() for part in insight.period_range.split(" to ", maxsplit=1)]
        if len(range_parts) == 2:
            for value in range_parts:
                years.add(Decimal(str(int(value[:4]))))
        return years

    @staticmethod
    def _contains_number(summary: str, expected: Decimal, *, absolute: bool = False) -> bool:
        target = abs(expected) if absolute else expected
        return any(
            abs(number) == target if absolute else number == target
            for number in extract_numbers(summary)
        )

    @classmethod
    def _require_number(
        cls,
        summary: str,
        expected: Decimal,
        label: str,
        errors: list[str],
        *,
        absolute: bool = False,
        required: bool = True,
    ) -> None:
        if required and not cls._contains_number(summary, expected, absolute=absolute):
            errors.append(f"{label} is missing")

    @staticmethod
    def _require_period(summary: str, period, frequency: str, label: str, errors: list[str]) -> None:
        formatted = format_period(period, frequency)
        if frequency == "monthly":
            month, year = formatted.rsplit(" ", maxsplit=1)
            present = bool(
                re.search(
                    rf"\b{re.escape(month)}(?:\s+tahun)?\s+{re.escape(year)}\b",
                    summary,
                    re.IGNORECASE,
                )
            )
        else:
            present = str(period.year) in summary
        if not present:
            errors.append(f"{label} is missing")
