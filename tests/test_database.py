import pytest

from app.repositories.database import get_database_url


@pytest.mark.parametrize(
    ("database_url", "driver_override", "expected"),
    [
        (
            "postgresql+psycopg://user:password@host:5432/db",
            None,
            "postgresql+psycopg://user:password@host:5432/db",
        ),
        (
            "postgresql+psycopg://user:password@host:5432/db",
            "psycopg2",
            "postgresql+psycopg2://user:password@host:5432/db",
        ),
        (
            "mysql+pymysql://user:password@host:3306/db",
            "psycopg2",
            "mysql+pymysql://user:password@host:3306/db",
        ),
    ],
)
def test_get_database_url_driver_override(
    monkeypatch, database_url, driver_override, expected
):
    monkeypatch.setenv("DATABASE_URL", database_url)
    if driver_override is None:
        monkeypatch.delenv("DATABASE_DRIVER_OVERRIDE", raising=False)
    else:
        monkeypatch.setenv("DATABASE_DRIVER_OVERRIDE", driver_override)

    assert get_database_url() == expected
