from dataclasses import asdict
import sys
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.insight_engine import InsightEngine
from app.repositories.clean_data_repository import CleanDataRepository


DASHBOARD_ID = "dashboard_jatim_demo"
CHART_IDS = [
    "chart_ipm",
    "chart_kemiskinan",
    "chart_tpt",
    "chart_inflasi",
    "chart_produksi_padi",
]


def main() -> None:
    repository = CleanDataRepository()
    engine = InsightEngine()

    for chart_id in CHART_IDS:
        observations = repository.get_chart_data(DASHBOARD_ID, chart_id)
        if not observations:
            raise RuntimeError(f"No data found for {DASHBOARD_ID}/{chart_id}")
        print(f"\n=== {chart_id} ===")
        pprint(asdict(engine.calculate(observations)))


if __name__ == "__main__":
    main()
