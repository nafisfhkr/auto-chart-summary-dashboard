CREATE TABLE IF NOT EXISTS result_cleansing (
    id BIGSERIAL PRIMARY KEY,

    dashboard_id VARCHAR(100) NOT NULL,
    chart_id VARCHAR(100) NOT NULL,

    indicator_code VARCHAR(100),
    indicator_name VARCHAR(200) NOT NULL,

    region_code VARCHAR(100),
    region_name VARCHAR(150) NOT NULL,

    period_start DATE NOT NULL,
    period_end DATE,
    frequency VARCHAR(20) NOT NULL,

    value NUMERIC(20,4) NOT NULL,
    unit VARCHAR(50),

    dimensions JSONB NOT NULL DEFAULT '{}'::jsonb,

    source_name VARCHAR(200),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS chart_summary (
    id BIGSERIAL PRIMARY KEY,

    dashboard_id VARCHAR(100) NOT NULL,
    chart_id VARCHAR(100) NOT NULL,

    indicator_code VARCHAR(100),
    indicator_name VARCHAR(200),

    period_start DATE,
    period_end DATE,

    summary_text TEXT,

    status VARCHAR(20) NOT NULL DEFAULT 'draft',

    provider VARCHAR(50),
    model_name VARCHAR(150),
    prompt_version VARCHAR(50),

    validation_status VARCHAR(20),
    validation_error TEXT,

    latency_ms INT,

    data_hash VARCHAR(128),

    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMPTZ
);


CREATE INDEX IF NOT EXISTS idx_result_cleansing_chart
ON result_cleansing (dashboard_id, chart_id);


CREATE INDEX IF NOT EXISTS idx_result_cleansing_period
ON result_cleansing (chart_id, period_start);


CREATE INDEX IF NOT EXISTS idx_chart_summary_chart
ON chart_summary (dashboard_id, chart_id);