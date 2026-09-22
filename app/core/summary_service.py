"""Application service for turning deterministic insights into summaries."""

from app.core.models import StructuredInsight
from app.prompts.chart_summary import build_chart_summary_messages
from app.providers.base import LLMProvider


class SummaryService:
    """Generate a narrative without calculating facts or knowing provider details."""

    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    def generate(self, insight: StructuredInsight) -> str:
        return self.provider.generate(build_chart_summary_messages(insight))
