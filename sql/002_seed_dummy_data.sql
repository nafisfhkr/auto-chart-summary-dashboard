-- ============================================================
-- Synthetic Dummy Data
-- Auto Chart Summary Generation - Jawa Timur
-- ============================================================
--
-- NOTE:
-- Seluruh nilai pada file ini adalah data sintetis/dummy
-- untuk development dan demonstration purposes.
-- Bukan data resmi pemerintah/BPS.
--
-- ============================================================


-- ------------------------------------------------------------
-- Bersihkan dummy data sebelumnya agar script aman dijalankan
-- ulang tanpa menghasilkan duplikasi.
-- ------------------------------------------------------------

DELETE FROM result_cleansing
WHERE dashboard_id = 'dashboard_jatim_demo';


-- ============================================================
-- 1. IPM
-- Frequency : yearly
-- Unit      : indeks
-- Pattern   : meningkat
-- Rows      : 4
-- ============================================================

INSERT INTO result_cleansing (
    dashboard_id,
    chart_id,
    indicator_code,
    indicator_name,
    region_code,
    region_name,
    period_start,
    period_end,
    frequency,
    value,
    unit,
    dimensions,
    source_name
)
VALUES
(
    'dashboard_jatim_demo',
    'chart_ipm',
    'IPM',
    'Indeks Pembangunan Manusia',
    'JATIM',
    'Jawa Timur',
    '2021-01-01',
    NULL,
    'yearly',
    72.14,
    'indeks',
    '{}'::jsonb,
    'synthetic_demo'
),
(
    'dashboard_jatim_demo',
    'chart_ipm',
    'IPM',
    'Indeks Pembangunan Manusia',
    'JATIM',
    'Jawa Timur',
    '2022-01-01',
    NULL,
    'yearly',
    72.75,
    'indeks',
    '{}'::jsonb,
    'synthetic_demo'
),
(
    'dashboard_jatim_demo',
    'chart_ipm',
    'IPM',
    'Indeks Pembangunan Manusia',
    'JATIM',
    'Jawa Timur',
    '2023-01-01',
    NULL,
    'yearly',
    73.61,
    'indeks',
    '{}'::jsonb,
    'synthetic_demo'
),
(
    'dashboard_jatim_demo',
    'chart_ipm',
    'IPM',
    'Indeks Pembangunan Manusia',
    'JATIM',
    'Jawa Timur',
    '2024-01-01',
    NULL,
    'yearly',
    74.65,
    'indeks',
    '{}'::jsonb,
    'synthetic_demo'
);


-- ============================================================
-- 2. Tingkat Kemiskinan
-- Frequency : yearly
-- Unit      : persen
-- Pattern   : menurun
-- Rows      : 4
-- ============================================================

INSERT INTO result_cleansing (
    dashboard_id,
    chart_id,
    indicator_code,
    indicator_name,
    region_code,
    region_name,
    period_start,
    period_end,
    frequency,
    value,
    unit,
    dimensions,
    source_name
)
VALUES
(
    'dashboard_jatim_demo',
    'chart_kemiskinan',
    'POVERTY_RATE',
    'Tingkat Kemiskinan',
    'JATIM',
    'Jawa Timur',
    '2021-01-01',
    NULL,
    'yearly',
    11.40,
    'persen',
    '{}'::jsonb,
    'synthetic_demo'
),
(
    'dashboard_jatim_demo',
    'chart_kemiskinan',
    'POVERTY_RATE',
    'Tingkat Kemiskinan',
    'JATIM',
    'Jawa Timur',
    '2022-01-01',
    NULL,
    'yearly',
    10.80,
    'persen',
    '{}'::jsonb,
    'synthetic_demo'
),
(
    'dashboard_jatim_demo',
    'chart_kemiskinan',
    'POVERTY_RATE',
    'Tingkat Kemiskinan',
    'JATIM',
    'Jawa Timur',
    '2023-01-01',
    NULL,
    'yearly',
    10.35,
    'persen',
    '{}'::jsonb,
    'synthetic_demo'
),
(
    'dashboard_jatim_demo',
    'chart_kemiskinan',
    'POVERTY_RATE',
    'Tingkat Kemiskinan',
    'JATIM',
    'Jawa Timur',
    '2024-01-01',
    NULL,
    'yearly',
    9.79,
    'persen',
    '{}'::jsonb,
    'synthetic_demo'
);


-- ============================================================
-- 3. Tingkat Pengangguran Terbuka
-- Frequency : yearly
-- Unit      : persen
-- Pattern   : menurun
-- Rows      : 4
--
-- dimensions digunakan untuk contoh extra dimension.
-- ============================================================

INSERT INTO result_cleansing (
    dashboard_id,
    chart_id,
    indicator_code,
    indicator_name,
    region_code,
    region_name,
    period_start,
    period_end,
    frequency,
    value,
    unit,
    dimensions,
    source_name
)
VALUES
(
    'dashboard_jatim_demo',
    'chart_tpt',
    'TPT',
    'Tingkat Pengangguran Terbuka',
    'JATIM',
    'Jawa Timur',
    '2021-01-01',
    NULL,
    'yearly',
    5.74,
    'persen',
    '{"category":"total"}'::jsonb,
    'synthetic_demo'
),
(
    'dashboard_jatim_demo',
    'chart_tpt',
    'TPT',
    'Tingkat Pengangguran Terbuka',
    'JATIM',
    'Jawa Timur',
    '2022-01-01',
    NULL,
    'yearly',
    5.49,
    'persen',
    '{"category":"total"}'::jsonb,
    'synthetic_demo'
),
(
    'dashboard_jatim_demo',
    'chart_tpt',
    'TPT',
    'Tingkat Pengangguran Terbuka',
    'JATIM',
    'Jawa Timur',
    '2023-01-01',
    NULL,
    'yearly',
    4.88,
    'persen',
    '{"category":"total"}'::jsonb,
    'synthetic_demo'
),
(
    'dashboard_jatim_demo',
    'chart_tpt',
    'TPT',
    'Tingkat Pengangguran Terbuka',
    'JATIM',
    'Jawa Timur',
    '2024-01-01',
    NULL,
    'yearly',
    4.19,
    'persen',
    '{"category":"total"}'::jsonb,
    'synthetic_demo'
);


-- ============================================================
-- 4. Inflasi
-- Frequency : monthly
-- Unit      : persen
-- Pattern   : fluktuatif
-- Rows      : 6
-- ============================================================

INSERT INTO result_cleansing (
    dashboard_id,
    chart_id,
    indicator_code,
    indicator_name,
    region_code,
    region_name,
    period_start,
    period_end,
    frequency,
    value,
    unit,
    dimensions,
    source_name
)
VALUES
(
    'dashboard_jatim_demo',
    'chart_inflasi',
    'INFLATION',
    'Inflasi',
    'JATIM',
    'Jawa Timur',
    '2026-01-01',
    NULL,
    'monthly',
    2.31,
    'persen',
    '{}'::jsonb,
    'synthetic_demo'
),
(
    'dashboard_jatim_demo',
    'chart_inflasi',
    'INFLATION',
    'Inflasi',
    'JATIM',
    'Jawa Timur',
    '2026-02-01',
    NULL,
    'monthly',
    2.48,
    'persen',
    '{}'::jsonb,
    'synthetic_demo'
),
(
    'dashboard_jatim_demo',
    'chart_inflasi',
    'INFLATION',
    'Inflasi',
    'JATIM',
    'Jawa Timur',
    '2026-03-01',
    NULL,
    'monthly',
    2.22,
    'persen',
    '{}'::jsonb,
    'synthetic_demo'
),
(
    'dashboard_jatim_demo',
    'chart_inflasi',
    'INFLATION',
    'Inflasi',
    'JATIM',
    'Jawa Timur',
    '2026-04-01',
    NULL,
    'monthly',
    2.67,
    'persen',
    '{}'::jsonb,
    'synthetic_demo'
),
(
    'dashboard_jatim_demo',
    'chart_inflasi',
    'INFLATION',
    'Inflasi',
    'JATIM',
    'Jawa Timur',
    '2026-05-01',
    NULL,
    'monthly',
    2.51,
    'persen',
    '{}'::jsonb,
    'synthetic_demo'
),
(
    'dashboard_jatim_demo',
    'chart_inflasi',
    'INFLATION',
    'Inflasi',
    'JATIM',
    'Jawa Timur',
    '2026-06-01',
    NULL,
    'monthly',
    2.84,
    'persen',
    '{}'::jsonb,
    'synthetic_demo'
);


-- ============================================================
-- 5. Produksi Padi
-- Frequency : yearly
-- Unit      : ton
-- Pattern   : naik kemudian sedikit turun
-- Rows      : 4
-- ============================================================

INSERT INTO result_cleansing (
    dashboard_id,
    chart_id,
    indicator_code,
    indicator_name,
    region_code,
    region_name,
    period_start,
    period_end,
    frequency,
    value,
    unit,
    dimensions,
    source_name
)
VALUES
(
    'dashboard_jatim_demo',
    'chart_produksi_padi',
    'RICE_PRODUCTION',
    'Produksi Padi',
    'JATIM',
    'Jawa Timur',
    '2021-01-01',
    NULL,
    'yearly',
    950000,
    'ton',
    '{}'::jsonb,
    'synthetic_demo'
),
(
    'dashboard_jatim_demo',
    'chart_produksi_padi',
    'RICE_PRODUCTION',
    'Produksi Padi',
    'JATIM',
    'Jawa Timur',
    '2022-01-01',
    NULL,
    'yearly',
    980000,
    'ton',
    '{}'::jsonb,
    'synthetic_demo'
),
(
    'dashboard_jatim_demo',
    'chart_produksi_padi',
    'RICE_PRODUCTION',
    'Produksi Padi',
    'JATIM',
    'Jawa Timur',
    '2023-01-01',
    NULL,
    'yearly',
    1010000,
    'ton',
    '{}'::jsonb,
    'synthetic_demo'
),
(
    'dashboard_jatim_demo',
    'chart_produksi_padi',
    'RICE_PRODUCTION',
    'Produksi Padi',
    'JATIM',
    'Jawa Timur',
    '2024-01-01',
    NULL,
    'yearly',
    995000,
    'ton',
    '{}'::jsonb,
    'synthetic_demo'
);