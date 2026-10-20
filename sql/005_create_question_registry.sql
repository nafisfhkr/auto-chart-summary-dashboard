-- ============================================================
-- TABEL BARU: question_registry
-- Menyimpan mapping question_id Metabase → konfigurasi insight engine.
-- Menggantikan hardcode di app/config/metabase_charts.py.
--
-- Referensi: docs/v2/PRDv2.md FR-14, docs/v2/UIUX.md Halaman 3
-- ============================================================

CREATE TABLE IF NOT EXISTS question_registry (
    id BIGSERIAL PRIMARY KEY,

    -- Identitas Metabase
    question_id INT NOT NULL UNIQUE,
    title VARCHAR(300) NOT NULL,

    -- Klasifikasi otomatis oleh sistem
    display_type VARCHAR(30),          -- 'line', 'bar', 'pie', 'scalar', 'row', 'area'
    insight_type VARCHAR(50) NOT NULL, -- 'time_series', 'ranking', 'composition', 'scalar'

    -- Mapping kolom data Metabase
    dimension_column VARCHAR(100),     -- Kolom sumbu X / dimensi (misal: 'bulan', 'tahun')
    series_column VARCHAR(100),        -- Kolom seri data (untuk multi-series chart)
    category_column VARCHAR(100),      -- Kolom kategori (untuk pie/composition)
    value_column VARCHAR(100) NOT NULL,-- Kolom nilai numerik utama

    -- Metadata pengelolaan
    topic VARCHAR(100),                -- 'ekonomi', 'ketenagakerjaan', 'kemiskinan', 'fiskal'
    priority INT DEFAULT 0,            -- Urutan tampil (0 = paling atas)
    is_active BOOLEAN NOT NULL DEFAULT true,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indeks untuk pencarian cepat
CREATE INDEX IF NOT EXISTS idx_question_registry_active
ON question_registry (is_active, priority);

CREATE INDEX IF NOT EXISTS idx_question_registry_topic
ON question_registry (topic, is_active);
