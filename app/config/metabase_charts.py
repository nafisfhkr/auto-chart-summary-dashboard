"""Central configuration for the Metabase pilot questions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MetabaseChartConfig:
    dashboard_id: str
    chart_id: str
    question_id: int
    title: str
    insight_type: str
    dimension_column: str | None = None
    series_column: str | None = None
    category_column: str | None = None
    value_column: str = ""


METABASE_CHARTS = (
    MetabaseChartConfig(
        dashboard_id="metabase_pilot",
        chart_id="metabase_question_694",
        question_id=694,
        title="Distribusi Pendapatan dan Pengeluaran Kabupaten di Jawa Timur",
        insight_type="categorical_multi_series",
        dimension_column="Kabupatenkota",
        series_column="Kategori",
        value_column="Sum of Jumlah",
    ),
    MetabaseChartConfig(
        dashboard_id="metabase_pilot",
        chart_id="metabase_question_695",
        question_id=695,
        title="Persentase Pendapatan dan Pengeluaran Kabupaten di Jawa Timur",
        insight_type="composition",
        category_column="kelompok_fiskal",
        value_column="total_nilai",
    ),
)


def get_metabase_chart(chart_id: str) -> MetabaseChartConfig:
    for chart in METABASE_CHARTS:
        if chart.chart_id == chart_id:
            return chart
    raise KeyError(f"Unknown Metabase chart: {chart_id}")
