"""Shared database configuration for SQLAlchemy consumers."""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine


ROOT_DIR = Path(__file__).resolve().parents[2]


def get_database_url() -> str:
    """Load and normalize the application's PostgreSQL URL."""
    load_dotenv(ROOT_DIR / ".env")
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL belum diisi di file .env")
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def create_database_engine() -> Engine:
    """Create the shared SQLAlchemy engine from DATABASE_URL."""
    return create_engine(get_database_url(), pool_pre_ping=True)
