import importlib.util
from pathlib import Path

import pytest


pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("airflow") is None,
    reason="Airflow is available in the Docker environment, not the project venv",
)


def _load_dag_module():
    path = Path(__file__).parents[1] / "dags" / "chart_summary_dag.py"
    spec = importlib.util.spec_from_file_location("chart_summary_dag", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_dag_configuration():
    module = _load_dag_module()

    assert module.dag.dag_id == "chart_summary_generation"
    assert module.dag.schedule is None
    assert module.dag.catchup is False
    assert {task.task_id for task in module.dag.tasks} == {
        "generate_chart_ipm",
        "generate_chart_kemiskinan",
        "generate_chart_tpt",
        "generate_chart_inflasi",
        "generate_chart_produksi_padi",
    }
    assert all(task.retries == 1 for task in module.dag.tasks)
