-- ============================================================
-- MIGRASI v2: Perluas tabel chart_summary untuk mendukung
-- multi-persona, HITL moderation, evaluasi performa model, dan
-- interactive fact-checking hover.
--
-- Referensi: docs/v2/architecturev2.md Seksi 3.6
-- Idempotent: aman dijalankan berulang kali.
-- ============================================================

-- 1. Tambah kolom baru ke chart_summary
ALTER TABLE chart_summary ADD COLUMN IF NOT EXISTS question_id INT;
ALTER TABLE chart_summary ADD COLUMN IF NOT EXISTS persona VARCHAR(30) DEFAULT 'katadata';
ALTER TABLE chart_summary ADD COLUMN IF NOT EXISTS strategy_track VARCHAR(20);
ALTER TABLE chart_summary ADD COLUMN IF NOT EXISTS input_tokens INT;
ALTER TABLE chart_summary ADD COLUMN IF NOT EXISTS output_tokens INT;
ALTER TABLE chart_summary ADD COLUMN IF NOT EXISTS estimated_cost NUMERIC(10, 6);
ALTER TABLE chart_summary ADD COLUMN IF NOT EXISTS factual_payload JSONB;
ALTER TABLE chart_summary ADD COLUMN IF NOT EXISTS analyst_notes TEXT;

-- 2. Hapus indeks unik lama yang tidak memasukkan persona
--    (dari 003_add_chart_summary_idempotency.sql)
DROP INDEX IF EXISTS uq_chart_summary_idempotency;

-- 3. Buat indeks unik baru yang memasukkan persona
CREATE UNIQUE INDEX IF NOT EXISTS uq_chart_summary_idempotency_v2
ON chart_summary (
    dashboard_id, chart_id, persona, data_hash,
    provider, model_name, prompt_version, validation_status
);

-- 4. Hapus indeks lookup lama dan buat yang baru sesuai v2
DROP INDEX IF EXISTS idx_chart_summary_chart;
DROP INDEX IF EXISTS idx_chart_summary_retrieval;

CREATE INDEX IF NOT EXISTS idx_chart_summary_lookup_v2
ON chart_summary (dashboard_id, chart_id, persona, status);

CREATE INDEX IF NOT EXISTS idx_chart_summary_retrieval_v2
ON chart_summary (dashboard_id, chart_id, persona, validation_status, generated_at DESC);
