CREATE UNIQUE INDEX IF NOT EXISTS uq_chart_summary_idempotency
ON chart_summary (
    dashboard_id, chart_id, data_hash, provider, model_name,
    prompt_version, validation_status
);

CREATE INDEX IF NOT EXISTS idx_chart_summary_retrieval
ON chart_summary (dashboard_id, chart_id, validation_status, generated_at DESC);
