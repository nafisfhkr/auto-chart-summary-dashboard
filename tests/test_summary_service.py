from datetime import date
from decimal import Decimal

from app.core.models import StructuredInsight
from app.core.summary_service import SummaryService


class FakeProvider:
    def __init__(self):
        self.messages = None

    def generate(self, messages, *, model=None):
        self.messages = messages
        return "Pada 2024, indikator meningkat."


def test_service_delegates_messages_and_returns_provider_output():
    insight = StructuredInsight(
        dashboard_id="dashboard", chart_id="chart", indicator="IPM",
        region="Jawa Timur", frequency="yearly",
        latest_period=date(2024, 1, 1), latest_value=Decimal("74.65"),
        previous_period=date(2023, 1, 1), previous_value=Decimal("73.61"),
        change=Decimal("1.04"), change_pct=Decimal("1.41"), trend="meningkat",
        min_value=Decimal("72.14"), min_period=date(2021, 1, 1),
        max_value=Decimal("74.65"), max_period=date(2024, 1, 1),
        unit="indeks", period_range="2021-01-01 to 2024-01-01",
    )
    provider = FakeProvider()
    result = SummaryService(provider).generate(insight)
    assert result == "Pada 2024, indikator meningkat."
    assert provider.messages[0]["role"] == "system"
    assert "74,65" in provider.messages[1]["content"]
