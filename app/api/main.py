"""Read-only FastAPI demo dashboard."""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.repositories.chart_summary_repository import ChartSummaryRepository
from app.repositories.clean_data_repository import CleanDataRepository
from app.services.dashboard_service import DashboardService

STATIC_DIR = Path(__file__).resolve().parents[1] / "web" / "static"
app = FastAPI(title="Dashboard Jawa Timur", version="1.0.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def get_dashboard_service() -> DashboardService:
    return DashboardService(CleanDataRepository(), ChartSummaryRepository())


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/dashboard/{dashboard_id}")
def dashboard(dashboard_id: str) -> dict:
    result = get_dashboard_service().get_dashboard(dashboard_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Dashboard tidak ditemukan")
    return result


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
