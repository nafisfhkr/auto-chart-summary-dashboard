"""Short-lived signed Metabase question embeds."""

from datetime import datetime, timedelta, timezone

from app.config.settings import ConfigurationError


class MetabaseEmbedService:
    def __init__(self, site_url: str, secret_key: str, ttl_seconds: int = 300) -> None:
        if not secret_key:
            raise ConfigurationError("METABASE_EMBED_SECRET_KEY belum diisi")
        self.site_url, self.secret_key, self.ttl_seconds = site_url.rstrip("/"), secret_key, ttl_seconds

    def create_question_url(self, question_id: int) -> str:
        import jwt

        exp = datetime.now(timezone.utc) + timedelta(seconds=self.ttl_seconds)
        token = jwt.encode({"resource": {"question": question_id}, "params": {}, "exp": exp}, self.secret_key, algorithm="HS256")
        return f"{self.site_url}/embed/question/{token}#bordered=true&titled=true"
