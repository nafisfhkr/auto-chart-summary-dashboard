"""Persistence for generated chart summaries."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
import hashlib
import json

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.core.models import StructuredInsight
from app.core.summary_validator import ValidationResult
from app.prompts.chart_summary import PROMPT_VERSION
from app.repositories.database import create_database_engine


@dataclass(frozen=True)
class StoredSummary:
    summary_id: int
    summary_text: str
    status: str | None
    validation_status: str | None
    provider: str | None
    model_name: str | None
    prompt_version: str | None
    latency_ms: int | None
    data_hash: str | None
    generated_at: object


@dataclass(frozen=True)
class SummaryPersistenceInput:
    insight: StructuredInsight
    summary_text: str
    validation: ValidationResult
    provider: str
    model_name: str
    prompt_version: str = PROMPT_VERSION
    latency_ms: int = 0
    indicator_code: str | None = None


@dataclass(frozen=True)
class SummarySaveResult:
    summary_id: int
    inserted: bool


def canonical_decimal(value: Decimal | None) -> str | None:
    """Serialize a Decimal without float conversion or insignificant zeros."""
    if value is None:
        return None
    normalized = value.normalize()
    if normalized == 0:
        return "0"
    return format(normalized, "f")


def _iso(value: date) -> str:
    return value.isoformat()


def build_data_hash(insight: StructuredInsight) -> str:
    """Hash only deterministic chart facts used by the summary prompt."""
    payload = {
        "dashboard_id": insight.dashboard_id,
        "chart_id": insight.chart_id,
        "indicator": insight.indicator,
        "region": insight.region,
        "frequency": insight.frequency,
        "latest_period": _iso(insight.latest_period),
        "latest_value": canonical_decimal(insight.latest_value),
        "previous_period": _iso(insight.previous_period),
        "previous_value": canonical_decimal(insight.previous_value),
        "change": canonical_decimal(insight.change),
        "change_pct": None if insight.unit == "persen" else canonical_decimal(insight.change_pct),
        "trend": insight.trend,
        "min_value": canonical_decimal(insight.min_value),
        "min_period": _iso(insight.min_period),
        "max_value": canonical_decimal(insight.max_value),
        "max_period": _iso(insight.max_period),
        "unit": insight.unit,
        "period_range": insight.period_range,
    }
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _period_start(period_range: str) -> date:
    return date.fromisoformat(period_range.split(" to ", 1)[0].strip())


class ChartSummaryRepository:
    """Store generated summaries without overwriting the first matching record."""

    def __init__(self, engine: Engine | None = None) -> None:
        self.engine = engine or create_database_engine()

    def get_latest_valid_summary(self, dashboard_id: str, chart_id: str) -> StoredSummary | None:
        query = text("""
            SELECT id, summary_text, status, validation_status, provider, model_name,
                   prompt_version, latency_ms, data_hash, generated_at
            FROM chart_summary
            WHERE dashboard_id = :dashboard_id
              AND chart_id = :chart_id
              AND validation_status = 'valid'
            ORDER BY generated_at DESC, id DESC
            LIMIT 1
        """)
        with self.engine.connect() as connection:
            row = connection.execute(query, {
                "dashboard_id": dashboard_id, "chart_id": chart_id,
            }).mappings().first()
        if row is None:
            return None
        return StoredSummary(
            summary_id=int(row["id"]), summary_text=row["summary_text"] or "",
            status=row["status"], validation_status=row["validation_status"],
            provider=row["provider"], model_name=row["model_name"],
            prompt_version=row["prompt_version"], latency_ms=row["latency_ms"],
            data_hash=row["data_hash"], generated_at=row["generated_at"],
        )

    def save(self, item: SummaryPersistenceInput) -> SummarySaveResult:
        if item.latency_ms < 0:
            raise ValueError("latency_ms must be greater than or equal to 0")
        if not item.provider.strip():
            raise ValueError("provider must not be blank")
        if not item.model_name.strip():
            raise ValueError("model_name must not be blank")
        if not item.prompt_version.strip():
            raise ValueError("prompt_version must not be blank")
        insight = item.insight
        data_hash = build_data_hash(insight)
        valid = item.validation.is_valid
        params = {
            "dashboard_id": insight.dashboard_id,
            "chart_id": insight.chart_id,
            "indicator_code": item.indicator_code,
            "indicator_name": insight.indicator,
            "period_start": _period_start(insight.period_range),
            "period_end": insight.latest_period,
            "summary_text": item.summary_text,
            "status": "draft" if valid else "rejected",
            "provider": item.provider,
            "model_name": item.model_name,
            "prompt_version": item.prompt_version,
            "validation_status": "valid" if valid else "invalid",
            "validation_error": None if valid else json.dumps(
                list(item.validation.errors), ensure_ascii=False, separators=(",", ":")
            ),
            "latency_ms": item.latency_ms,
            "data_hash": data_hash,
        }
        insert = text("""
            INSERT INTO chart_summary (
                dashboard_id, chart_id, indicator_code, indicator_name,
                period_start, period_end, summary_text, status, provider,
                model_name, prompt_version, validation_status, validation_error,
                latency_ms, data_hash
            ) VALUES (
                :dashboard_id, :chart_id, :indicator_code, :indicator_name,
                :period_start, :period_end, :summary_text, :status, :provider,
                :model_name, :prompt_version, :validation_status, :validation_error,
                :latency_ms, :data_hash
            )
            ON CONFLICT (
                dashboard_id, chart_id, data_hash, provider, model_name,
                prompt_version, validation_status
            ) DO NOTHING
            RETURNING id
        """)
        lookup = text("""
            SELECT id FROM chart_summary
            WHERE dashboard_id = :dashboard_id AND chart_id = :chart_id
              AND data_hash = :data_hash AND provider = :provider
              AND model_name = :model_name AND prompt_version = :prompt_version
              AND validation_status = :validation_status
        """)
        with self.engine.begin() as connection:
            row = connection.execute(insert, params).first()
            if row is not None:
                return SummarySaveResult(summary_id=int(row[0]), inserted=True)
            existing = connection.execute(lookup, params).first()
            if existing is None:
                raise RuntimeError("chart_summary insert conflicted but existing row was not found")
            return SummarySaveResult(summary_id=int(existing[0]), inserted=False)
