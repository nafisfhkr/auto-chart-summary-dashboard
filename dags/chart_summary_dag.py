"""Airflow orchestration for local chart-summary generation."""

from datetime import timedelta

from airflow import DAG
from airflow.decorators import task
from pendulum import datetime

from app.services.factory import create_summary_pipeline


DASHBOARD_ID = "dashboard_jatim_demo"
CHART_IDS = [
    "chart_ipm",
    "chart_kemiskinan",
    "chart_tpt",
    "chart_inflasi",
    "chart_produksi_padi",
]


@task(retries=1, retry_delay=timedelta(minutes=1))
def run_chart_summary(chart_id: str) -> dict:
    """Generate and persist one chart summary through the application pipeline."""
    pipeline = create_summary_pipeline()
    result = pipeline.run(dashboard_id=DASHBOARD_ID, chart_id=chart_id)
    payload = {
        "chart_id": result.chart_id,
        "summary_id": result.summary_id,
        "is_valid": result.validation.is_valid,
        "inserted": result.inserted,
        "latency_ms": result.latency_ms,
        "data_hash": result.data_hash,
    }
    print(payload)
    return payload


with DAG(
    dag_id="chart_summary_generation",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["summary", "local"],
) as dag:
    for chart_id in CHART_IDS:
        run_chart_summary.override(task_id=f"generate_{chart_id}")(chart_id)
