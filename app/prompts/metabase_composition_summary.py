"""Prompt for Q695 composition summaries."""

import json

from app.core.metabase_insights import CompositionInsight
from app.prompts.chart_summary import format_number

PROMPT_VERSION = "metabase-composition-v1"


def build_messages(insight: CompositionInsight) -> list[dict[str, str]]:
    facts = {
        "judul": insight.title,
        "jenis": "komposisi",
        "nilai_kategori": {category: format_number(value) for category, value in insight.categories},
        "total": format_number(insight.total),
        "pangsa_persen": {category: format_number(share) for category, share in insight.shares},
        "kategori_dominan": insight.largest_category,
        "nilai_kategori_dominan": format_number(insight.largest_value),
        "selisih_nominal": format_number(insight.difference),
        "selisih_poin_persentase": format_number(insight.difference_pct_points),
    }
    system = "Anda menulis ringkasan statistik Metabase dalam Bahasa Indonesia formal, 2-3 kalimat ringkas, tanpa markdown. Gunakan hanya fakta terstruktur yang diberikan. Bedakan nilai nominal, pangsa persen, dan selisih poin persentase. Jangan mengarang atau mengubah angka, menyebut sebab, atau memberi rekomendasi."
    return [{"role": "system", "content": system}, {"role": "user", "content": "Fakta terverifikasi (JSON):\n" + json.dumps(facts, ensure_ascii=False, indent=2)}]
