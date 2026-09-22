"""Shared database configuration for SQLAlchemy consumers."""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

ROOT_DIR = Path(__file__).resolve().parents[2]


def get_database_url() -> str:
    """Load and normalize the application's PostgreSQL URL."""
    load_dotenv(ROOT_DIR / ".env")
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL belum diisi di file .env")
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    if (
        os.getenv("DATABASE_DRIVER_OVERRIDE") == "psycopg2"
        and database_url.startswith("postgresql+psycopg://")
    ):
        return database_url.replace("postgresql+psycopg://", "postgresql+psycopg2://", 1)
    return database_url


def create_database_engine() -> Engine:
    """Create the shared SQLAlchemy engine from DATABASE_URL."""
    return create_engine(get_database_url(), pool_pre_ping=True)
