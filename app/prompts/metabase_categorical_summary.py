"""Prompt for Q694 categorical summaries."""

import json

from app.core.metabase_insights import CategoricalMultiSeriesInsight
from app.prompts.chart_summary import format_number

PROMPT_VERSION = "metabase-categorical-v2"


def build_messages(insight: CategoricalMultiSeriesInsight) -> list[dict[str, str]]:
    facts = {
        "judul": insight.title,
        "jenis": "perbandingan kategorikal multi-seri",
        "jumlah_baris": insight.row_count,
        "jumlah_kabupaten_kota": insight.dimension_count,
        "seri": insight.series_names,
        "nilai_tertinggi_per_seri": [{"kabupaten_kota": item.dimension, "seri": item.series, "nilai": format_number(item.value)} for item in insight.top_item_per_series],
        "nilai_terendah_per_seri": [{"kabupaten_kota": item.dimension, "seri": item.series, "nilai": format_number(item.value)} for item in insight.bottom_item_per_series],
        "nilai_maksimum_keseluruhan": {"kabupaten_kota": insight.overall_max.dimension, "seri": insight.overall_max.series, "nilai": format_number(insight.overall_max.value)},
        "total_per_seri": {series: format_number(value) for series, value in insight.series_totals},
        "perbandingan_penerimaan_pengeluaran": [{"kabupaten_kota": name, "penerimaan": format_number(income), "pengeluaran": format_number(expense), "selisih": format_number(gap)} for name, income, expense, gap in insight.comparison_pairs],
    }
    system = (
        "Anda adalah penulis ringkasan data bergaya jurnalisme data Indonesia. "
        "Tulis 2-3 kalimat dalam Bahasa Indonesia formal, natural, dan mengalir seperti "
        "naskah berita data, tanpa markdown, heading, atau bullet. Mulai dengan temuan "
        "paling penting dari data, lalu lanjutkan dengan perbandingan terkuat dan satu "
        "konteks tambahan bila membantu. Gunakan transisi yang wajar seperti 'Selain itu', "
        "'Berdasarkan data', atau 'Sementara itu', tetapi jangan memaksakannya. "
        "Prioritaskan nilai tertinggi per seri dan perbandingan Pendapatan dengan Pengeluaran; "
        "hindari daftar panjang kabupaten/kota. Gunakan hanya fakta terstruktur yang diberikan, "
        "jangan mengarang atau mengubah angka, menyebut sebab, memberi rekomendasi, atau "
        "menilai kinerja kabupaten/kota. Jangan meniru kalimat atau fakta dari sumber lain."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": "Fakta terverifikasi (JSON):\n" + json.dumps(facts, ensure_ascii=False, indent=2)}]
