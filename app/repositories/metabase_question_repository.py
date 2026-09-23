"""Server-side Metabase question result adapter."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

import requests

from app.config.metabase_charts import MetabaseChartConfig
from app.config.settings import ConfigurationError


@dataclass(frozen=True)
class MetabaseQuestionResult:
    question_id: int
    columns: tuple[str, ...]
    rows: tuple[dict[str, Any], ...]


class MetabaseRepositoryError(RuntimeError):
    """Raised when Metabase authentication or result parsing fails."""


class MetabaseQuestionRepository:
    def __init__(self, *, site_url: str, api_key: str = "", username: str = "", password: str = "", timeout_seconds: int = 60, session: Any = requests) -> None:
        self.site_url = site_url.rstrip("/")
        self.api_key = api_key
        self.username = username
        self.password = password
        self.timeout_seconds = timeout_seconds
        self._session = session
        self._session_token: str | None = None

    def fetch(self, config: MetabaseChartConfig) -> MetabaseQuestionResult:
        headers = self._auth_headers()
        try:
            response = self._session.post(
                f"{self.site_url}/api/card/{config.question_id}/query",
                headers=headers,
                json={},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise MetabaseRepositoryError(f"Metabase question request failed: {exc}") from exc
        except (ValueError, TypeError) as exc:
            raise MetabaseRepositoryError("Metabase returned invalid JSON") from exc
        return self._parse_result(config.question_id, payload, config)

    def _auth_headers(self) -> dict[str, str]:
        if self.api_key:
            return {"x-api-key": self.api_key}
        if not self.username or not self.password:
            raise ConfigurationError("Isi METABASE_API_KEY atau METABASE_USERNAME dan METABASE_PASSWORD")
        if self._session_token is None:
            try:
                response = self._session.post(
                    f"{self.site_url}/api/session",
                    json={"username": self.username, "password": self.password},
                    timeout=self.timeout_seconds,
                )
                response.raise_for_status()
                self._session_token = response.json()["id"]
            except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
                raise MetabaseRepositoryError("Metabase session authentication failed") from exc
        return {"X-Metabase-Session": self._session_token}

    @classmethod
    def _parse_result(cls, question_id: int, payload: dict[str, Any], config: MetabaseChartConfig) -> MetabaseQuestionResult:
        data = payload.get("data", payload)
        columns_payload = data.get("cols") or data.get("columns")
        raw_rows = data.get("rows")
        if not isinstance(columns_payload, list) or not isinstance(raw_rows, list):
            raise MetabaseRepositoryError("Metabase response does not contain columns and rows")
        columns = tuple(cls._column_name(column) for column in columns_payload)
        required = [value for value in (config.dimension_column, config.series_column, config.category_column, config.value_column) if value]
        resolved = {cls._normalise(name) for name in columns}
        missing = [name for name in required if cls._normalise(name) not in resolved]
        if missing:
            raise MetabaseRepositoryError(f"Required Metabase columns are missing: {', '.join(missing)}; actual={columns}")
        rows = []
        for raw_row in raw_rows:
            if isinstance(raw_row, dict):
                row = {cls._normalise(key): value for key, value in raw_row.items()}
            elif isinstance(raw_row, list) and len(raw_row) == len(columns):
                row = {cls._normalise(name): value for name, value in zip(columns, raw_row)}
            else:
                raise MetabaseRepositoryError("Metabase returned a row with an invalid shape")
            rows.append(row)
        return MetabaseQuestionResult(question_id, tuple(cls._normalise(name) for name in columns), tuple(rows))

    @staticmethod
    def _column_name(column: Any) -> str:
        if isinstance(column, str):
            return column
        if isinstance(column, dict):
            return str(column.get("display_name") or column.get("name") or "")
        return ""

    @staticmethod
    def _normalise(value: str) -> str:
        return " ".join(value.strip().casefold().split())

    @classmethod
    def value(cls, row: dict[str, Any], column: str) -> Decimal:
        try:
            value = row[cls._normalise(column)]
            return Decimal(str(value))
        except (KeyError, InvalidOperation, TypeError, ValueError) as exc:
            raise MetabaseRepositoryError(f"Column {column!r} contains a nonnumeric value") from exc
