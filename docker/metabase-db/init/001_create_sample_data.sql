-- ============================================================
-- SAMPLE DATA: Indikator Strategis Jawa Timur untuk Metabase v2
-- Otomatis dijalankan saat container metabase-db pertama kali start
-- ============================================================

-- Tabel A: Inflasi Bulanan Jawa Timur (untuk Line Chart)
CREATE TABLE IF NOT EXISTS inflasi_bulanan (
    id SERIAL PRIMARY KEY,
    bulan DATE NOT NULL,
    inflasi_yoy NUMERIC(6,2) NOT NULL,
    inflasi_mtm NUMERIC(6,2) NOT NULL
);

INSERT INTO inflasi_bulanan (bulan, inflasi_yoy, inflasi_mtm) VALUES
('2024-01-01', 2.57, 0.23),
('2024-02-01', 2.75, 0.18),
('2024-03-01', 3.05, 0.30),
('2024-04-01', 2.98, -0.07),
('2024-05-01', 2.84, -0.14),
('2024-06-01', 2.51, -0.33),
('2024-07-01', 2.13, -0.38),
('2024-08-01', 2.09, -0.04),
('2024-09-01', 1.84, -0.25),
('2024-10-01', 1.71, -0.13),
('2024-11-01', 1.55, -0.16),
('2024-12-01', 1.57, 0.02),
('2025-01-01', 1.62, 0.05),
('2025-02-01', 1.48, -0.14),
('2025-03-01', 1.65, 0.17),
('2025-04-01', 1.83, 0.18),
('2025-05-01', 2.01, 0.18),
('2025-06-01', 2.22, 0.21);


-- Tabel B: Realisasi PAD per Bakorwil (untuk Bar Chart)
CREATE TABLE IF NOT EXISTS realisasi_pad_bakorwil (
    id SERIAL PRIMARY KEY,
    tahun INT NOT NULL,
    bakorwil VARCHAR(100) NOT NULL,
    target_pad NUMERIC(15,2) NOT NULL,
    realisasi_pad NUMERIC(15,2) NOT NULL
);

INSERT INTO realisasi_pad_bakorwil (tahun, bakorwil, target_pad, realisasi_pad) VALUES
(2024, 'Bakorwil I (Madiun)',       2500000000000, 2350000000000),
(2024, 'Bakorwil II (Bojonegoro)',   1800000000000, 1720000000000),
(2024, 'Bakorwil III (Malang)',      3200000000000, 3150000000000),
(2024, 'Bakorwil IV (Pamekasan)',    1200000000000, 1050000000000),
(2024, 'Bakorwil V (Jember)',        1950000000000, 1880000000000),
(2024, 'Surabaya (Metropolitan)',    5800000000000, 5650000000000);


-- Tabel C: Komposisi PDRB Sektoral Jawa Timur (untuk Pie/Donut Chart)
CREATE TABLE IF NOT EXISTS komposisi_pdrb (
    id SERIAL PRIMARY KEY,
    tahun INT NOT NULL,
    sektor VARCHAR(150) NOT NULL,
    kontribusi_persen NUMERIC(6,2) NOT NULL
);

INSERT INTO komposisi_pdrb (tahun, sektor, kontribusi_persen) VALUES
(2024, 'Industri Pengolahan',           29.34),
(2024, 'Perdagangan Besar & Eceran',    18.12),
(2024, 'Pertanian, Kehutanan & Perikanan', 11.87),
(2024, 'Konstruksi',                      9.45),
(2024, 'Informasi & Komunikasi',          6.23),
(2024, 'Jasa Keuangan & Asuransi',        4.78),
(2024, 'Transportasi & Pergudangan',      3.95),
(2024, 'Akomodasi & Makan Minum',         5.62),
(2024, 'Lainnya',                         10.64);


-- Tabel D: Angka Kemiskinan Jawa Timur (untuk Scalar/KPI & Time-series)
CREATE TABLE IF NOT EXISTS angka_kemiskinan (
    id SERIAL PRIMARY KEY,
    tahun INT NOT NULL,
    semester INT NOT NULL,
    persentase_miskin NUMERIC(5,2) NOT NULL,
    jumlah_penduduk_miskin_ribu NUMERIC(10,2) NOT NULL,
    target_rkpd NUMERIC(5,2)
);

INSERT INTO angka_kemiskinan (tahun, semester, persentase_miskin, jumlah_penduduk_miskin_ribu, target_rkpd) VALUES
(2020, 1, 11.09, 4419.19, 10.50),
(2020, 2, 11.46, 4575.54, 10.50),
(2021, 1, 11.40, 4557.63, 10.20),
(2021, 2, 11.00, 4400.48, 10.20),
(2022, 1, 10.98, 4398.28, 9.90),
(2022, 2, 10.49, 4208.30, 9.90),
(2023, 1, 10.33, 4147.85, 9.60),
(2023, 2,  9.95, 3997.11, 9.60),
(2024, 1,  9.79, 3933.56, 9.30),
(2024, 2,  9.50, 3818.75, 9.30);
