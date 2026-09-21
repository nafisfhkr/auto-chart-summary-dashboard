from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL belum diisi di file .env")

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1,
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

def test_connection():
    print("Testing database connection...")

    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        result.scalar_one()

    print("✓ Database connection: SUCCESS")


def test_dummy_data():
    with engine.connect() as conn:
        total_rows = conn.execute(
            text(
                """
                SELECT COUNT(*)
                FROM result_cleansing
                WHERE dashboard_id = 'dashboard_jatim_demo'
                """
            )
        ).scalar_one()

        print(f"✓ Dummy rows found: {total_rows}")

        charts = conn.execute(
            text(
                """
                SELECT
                    chart_id,
                    indicator_name,
                    frequency,
                    unit,
                    COUNT(*) AS total_rows
                FROM result_cleansing
                WHERE dashboard_id = 'dashboard_jatim_demo'
                GROUP BY
                    chart_id,
                    indicator_name,
                    frequency,
                    unit
                ORDER BY chart_id
                """
            )
        ).mappings().all()

        print("\nCharts:")
        for row in charts:
            print(
                f"- {row['chart_id']}: "
                f"{row['indicator_name']} | "
                f"{row['frequency']} | "
                f"{row['unit']} | "
                f"{row['total_rows']} rows"
            )

    assert total_rows == 22, (
        f"Expected 22 dummy rows, found {total_rows}"
    )

    assert len(charts) == 5, (
        f"Expected 5 charts, found {len(charts)}"
    )

    print("\n✓ Dummy data validation: SUCCESS")


def test_write():
    """
    Test INSERT + DELETE.
    Record test dibersihkan kembali sehingga tidak
    mengotori chart_summary.
    """

    test_dashboard = "__connection_test__"
    test_chart = "__connection_test__"

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO chart_summary (
                    dashboard_id,
                    chart_id,
                    summary_text,
                    status
                )
                VALUES (
                    :dashboard_id,
                    :chart_id,
                    :summary_text,
                    'draft'
                )
                """
            ),
            {
                "dashboard_id": test_dashboard,
                "chart_id": test_chart,
                "summary_text": "Phase 1 database connection test",
            },
        )

        inserted = conn.execute(
            text(
                """
                SELECT COUNT(*)
                FROM chart_summary
                WHERE dashboard_id = :dashboard_id
                  AND chart_id = :chart_id
                """
            ),
            {
                "dashboard_id": test_dashboard,
                "chart_id": test_chart,
            },
        ).scalar_one()

        assert inserted == 1

        conn.execute(
            text(
                """
                DELETE FROM chart_summary
                WHERE dashboard_id = :dashboard_id
                  AND chart_id = :chart_id
                """
            ),
            {
                "dashboard_id": test_dashboard,
                "chart_id": test_chart,
            },
        )

    print("✓ INSERT / DELETE test: SUCCESS")


if __name__ == "__main__":
    test_connection()
    test_dummy_data()
    test_write()

    print("\n==============================")
    print("PHASE 1 DATABASE TEST PASSED")
    print("==============================")