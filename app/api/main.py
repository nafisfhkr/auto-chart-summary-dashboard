"""Read-only FastAPI demo dashboard."""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config.metabase_charts import METABASE_CHARTS
from app.config.settings import ConfigurationError, get_metabase_settings
from app.repositories.chart_summary_repository import ChartSummaryRepository
from app.repositories.clean_data_repository import CleanDataRepository
from app.services.dashboard_service import DashboardService, _summary_dict
from app.services.metabase_embed_service import MetabaseEmbedService

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


@app.get("/api/metabase/dashboard/metabase_pilot")
def metabase_dashboard() -> dict:
    try:
        settings = get_metabase_settings()
        embed = MetabaseEmbedService(settings.site_url, settings.embed_secret_key)
        repository = ChartSummaryRepository()
        charts = []
        for config in METABASE_CHARTS:
            summary = repository.get_latest_valid_summary(config.dashboard_id, config.chart_id)
            charts.append({
                "question_id": config.question_id, "chart_id": config.chart_id,
                "title": config.title, "insight_type": config.insight_type,
                "embed_url": embed.create_question_url(config.question_id),
                "latest_valid_summary": _summary_dict(summary),
                "provider": summary.provider if summary else None,
                "model_name": summary.model_name if summary else None,
                "validation_status": summary.validation_status if summary else None,
                "generated_at": summary.generated_at.isoformat() if summary and summary.generated_at else None,
            })
        return {"dashboard_id": "metabase_pilot", "charts": charts}
    except (ConfigurationError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/metabase")
def metabase_index() -> FileResponse:
    return FileResponse(STATIC_DIR / "metabase.html")
