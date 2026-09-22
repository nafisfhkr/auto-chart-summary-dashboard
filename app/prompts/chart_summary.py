"""Build factual prompts for chart summary generation."""

import json
from datetime import date
from decimal import Decimal

from app.core.models import StructuredInsight


PROMPT_VERSION = "chart-summary-v1"
_MONTHS = (
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
)


def format_period(period: date, frequency: str) -> str:
    """Format a period deterministically for the requested chart frequency."""
    if frequency == "yearly":
        return str(period.year)
    if frequency == "monthly":
        return f"{_MONTHS[period.month - 1]} {period.year}"
    return period.isoformat()


def format_number(value: Decimal) -> str:
    """Format Decimal without binary-float conversion for Indonesian display."""
    raw = format(value, "f")
    integer, _, fraction = raw.partition(".")
    sign = ""
    if integer.startswith("-"):
        sign, integer = "-", integer[1:]
    grouped = f"{int(integer):,}".replace(",", ".")
    fraction = fraction.rstrip("0")
    return f"{sign}{grouped}{',' + fraction if fraction else ''}"


def format_period_range(period_range: str, frequency: str) -> str:
    """Format the engine's ISO range without asking the LLM to parse dates."""
    start_raw, end_raw = (part.strip() for part in period_range.split(" to ", maxsplit=1))
    return f"{format_period(date.fromisoformat(start_raw), frequency)} hingga {format_period(date.fromisoformat(end_raw), frequency)}"


def build_chart_summary_messages(insight: StructuredInsight) -> list[dict[str, str]]:
    """Return system and user messages compatible with ``LLMProvider``."""
    system = (
        "Anda adalah generator ringkasan statistik dashboard. Gunakan hanya fakta "
        "terstruktur yang diberikan. Tulis Bahasa Indonesia formal dalam 2-3 kalimat "
        "ringkas, maksimal 3 kalimat, tanpa markdown, bullet, heading, atau label. "
        "Jangan menambahkan atau mengubah angka, menginferensikan sebab, atau membuat "
        "rekomendasi. Sebutkan nilai dan periode terbaru serta perbandingan dengan "
        "periode sebelumnya. Gunakan konteks minimum/maksimum jika berguna. Untuk unit "
        "persen, nyatakan perubahan absolut sebagai poin persentase, bukan persen. "
        "Sebab hanya boleh disebut jika ada fakta konteks/driver terverifikasi yang "
        "secara eksplisit diberikan."
    )
    period = lambda value: format_period(value, insight.frequency)
    relative_change = (
        None
        if insight.unit == "persen"
        else (
            format_number(insight.change_pct)
            if insight.change_pct is not None
            else None
        )
    )
    facts = {
        "indikator": insight.indicator,
        "wilayah": insight.region,
        "frekuensi": insight.frequency,
        "periode_terbaru": period(insight.latest_period),
        "nilai_terbaru": format_number(insight.latest_value),
        "periode_sebelumnya": period(insight.previous_period),
        "nilai_sebelumnya": format_number(insight.previous_value),
        "perubahan_absolut": format_number(insight.change),
        "perubahan_relatif_persen": relative_change,
        "tren": insight.trend,
        "nilai_minimum": format_number(insight.min_value),
        "periode_nilai_minimum": period(insight.min_period),
        "nilai_maksimum": format_number(insight.max_value),
        "periode_nilai_maksimum": period(insight.max_period),
        "unit": insight.unit,
        "rentang_periode": format_period_range(insight.period_range, insight.frequency),
    }
    user = "Fakta terverifikasi (JSON):\n" + json.dumps(facts, ensure_ascii=False, indent=2)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]
