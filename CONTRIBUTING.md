# 🤝 Panduan Kontribusi (Contributing Guide)

Selamat datang di proyek **Jawa Timur Public Strategic Dashboard & AI Narrative Summary (v2)**! Dokumen ini dirancang sebagai panduan praktis bagi rekan tim dan kontributor agar dapat mulai bekerja secara kolaboratif, rapi, dan seragam tanpa kebingungan.

---

## 🧭 Prinsip Utama Rekayasa (Engineering Principles)

Sebelum mulai menulis kode, harap pahami 3 pilar utama arsitektur sistem ini:

1. **Deterministic Before Generative (Anti-Halusinasi Angka)**:
   - Angka statistik (persentase, nilai absolut, tren kenaikan/penurunan) **wajib dihitung oleh Insight Engine**, BUKAN dihitung atau dikarang oleh LLM.
   - LLM hanya bertugas merangkai narasi berdasarkan fakta terstruktur yang kita sediakan.
   - Semua narasi wajib lolos uji di `SummaryValidator` (regex & math check) sebelum disimpan ke basis data.

2. **Test-Driven & Zero Broken Tests**:
   - Seluruh test di direktori `tests/` harus berstatus hijau (`140+ passed`).
   - Setiap menambahkan modul baru, wajib menyertakan unit test pengujian modul tersebut.

3. **Loose Coupling & Swappability**:
   - Provider LLM, basis data, dan engine visualisasi dibuat modular (berbasis Interface/ABC).
   - Jangan menulis kode yang mengunci sistem ke satu model AI atau satu vendor tertentu.

---

## 🌿 Alur Kerja Git & Percabangan (Git Workflow)

Untuk menjaga kestabilan kode, kita menggunakan alur kerja berbasis fitur (*feature-branch workflow*):

### 1. Aturan Cabang (Branching Rules)
- **`main`**: Branch produksi yang stabil. **DILARANG MELAKUKAN DIRECT COMMIT ATAU DIRECT PUSH KE `main`**.
- **`feature/sprint<N>-<nama-tugas>`**: Digunakan untuk pengerjaan task fitur pada sprint tertentu (contoh: `feature/sprint2-scalar-engine`, `feature/sprint2-multi-persona`).
- **`fix/<nama-perbaikan>`**: Digunakan untuk perbaikan bug spesifik (contoh: `fix/metabase-token-expiration`).
- **`docs/<topik>`**: Digunakan untuk pembaruan dokumentasi (contoh: `docs/readme-and-contributing`).

### 2. Setup Lingkungan Pengembangan (Development Environment)

Kontributor bebas memilih salah satu dari 2 cara di bawah ini (keduanya menghasilkan `.venv` yang 100% kompatibel):

- **Opsi A: Menggunakan `uv` (Direkomendasikan - Sangat Cepat ⚡)**
  ```bash
  # Otomatis membuat .venv dan menginstal seluruh dependencies:
  uv sync
  ```
  *(Dengan `uv`, Anda bahkan bisa langsung menjalankan perintah tanpa aktivasi manual: `uv run pytest` atau `uv run uvicorn ...`)*

- **Opsi B: Menggunakan Standar Python (`pip` bawaan)**
  ```bash
  # 1. Buat virtual environment
  python -m venv .venv

  # 2. Aktivasi virtual environment
  # Windows (PowerShell): .\.venv\Scripts\Activate.ps1
  # Linux / macOS:        source .venv/bin/activate

  # 3. Instal dependencies
  pip install -r requirements.txt
  ```

### 3. Langkah Pengerjaan Fitur Baru
```bash
# 1. Pastikan branch main lokal Anda adalah versi paling mutakhir
git checkout main
git pull origin main

# 2. Buat branch baru untuk tugas Anda
git checkout -b feature/sprint2-nama-tugas

# 3. Lakukan coding & buat unit test yang relevan
# ...

# 4. Jalankan seluruh test suite sebelum commit
pytest # atau: uv run pytest

# 5. Commit perubahan dengan pesan yang deskriptif
git add .
git commit -m "feat: implement scalar insight engine for single-value kpis"

# 6. Push branch Anda ke remote repository
git push -u origin feature/sprint2-nama-tugas
```

### 4. Konvensi Pesan Commit (Conventional Commits)
Gunakan format standar berikut:
- `feat: ...` untuk fitur baru (contoh: `feat: add groq provider`)
- `fix: ...` untuk perbaikan bug (contoh: `fix: handle null dimension column in metabase repository`)
- `test: ...` untuk penambahan atau modifikasi unit test
- `docs: ...` untuk perubahan dokumentasi atau komentar
- `refactor: ...` untuk perapian kode tanpa mengubah fungsi eksternal

### 4. Membuat Pull Request (PR)
- Buka Pull Request dari branch fitur Anda ke branch `main`.
- Berikan deskripsi ringkas mengenai:
  - Apa yang dikerjakan / diselesaikan.
  - Test apa yang sudah dijalankan dan hasilnya.
  - Apakah ada konfigurasi `.env` atau skema SQL baru yang dibutuhkan.
- Minta review dari rekan tim sebelum dilakukan merge.

---

## 🔒 Keamanan & Manajemen Environment

1. **JANGAN PERNAH COMMIT FILE `.env`**:
   - File `.env` berisi kunci API, kredensial basis data, dan token rahasia.
   - File `.env` sudah masuk ke dalam `.gitignore`. Jangan pernah menggunakan `git add -f .env`.
2. **Perbarui `.env.example` Jika Menambah Variabel Baru**:
   - Jika kode Anda membutuhkan variabel environment baru, tambahkan variabel tersebut ke [.env.example](file:///d:/Data%20Science%20Intern/Project/AIsummary-dashboard-jatim/.env.example) dengan nilai default/kosong dan beri komentar penjelas.

---

## 🧪 Panduan Menjalankan & Menulis Pengujian (Testing)

Kita menggunakan framework **pytest**.

```bash
# Menjalankan seluruh test suite
pytest

# Menjalankan test dengan output detail
pytest -v

# Menjalankan test file tertentu saja
pytest tests/test_groq_provider.py
pytest tests/test_chart_summary_repository.py

# Menjalankan test berdasarkan kata kunci nama fungsi
pytest -k "test_save"
```

### Tips Menulis Test:
- Gunakan mock/fake saat menguji modul yang berinteraksi dengan layanan eksternal (API LLM, Metabase API, atau Database fisik).
- Lihat contoh pengujian yang rapi dan terisolasi di `tests/test_groq_provider.py` atau `tests/test_chart_summary_repository.py`.

---

## 📐 Arsitektur Kode & Konvensi Python

1. **Python 3.11+ Type Hinting**:
   - Selalu gunakan type hint pada argumen dan return value fungsi:
     ```python
     def calculate_mom_change(current: Decimal, previous: Decimal) -> Decimal:
         return ((current - previous) / previous) * 100
     ```
2. **Dataclasses & Immutability**:
   - Gunakan `@dataclass(frozen=True)` untuk objek transfer data (DTO) atau model data agar terlindungi dari modifikasi tak terduga (*side effects*).
3. **Pemisahan Layer (Separation of Concerns)**:
   - `app/api/`: Khusus routing HTTP dan validasi payload request/response.
   - `app/services/`: Logika bisnis dan orchestrasi pipeline end-to-end.
   - `app/core/`: Insight calculation murni dan validasi fakta tanpa dependensi I/O.
   - `app/providers/`: Antarmuka komunikasi dengan model LLM eksternal.
   - `app/repositories/`: Akses data (SQL query, Metabase API client).

---

## 📋 Acuan Referensi Dokumen Proyek

Jika ragu mengenai alur fitur, spesifikasi produk, atau jadwal sprint, silakan rujuk dokumen berikut:
- **Spesifikasi Produk**: [docs/v2/PRDv2.md](file:///d:/Data%20Science%20Intern/Project/AIsummary-dashboard-jatim/docs/v2/PRDv2.md)
- **Arsitektur Teknis**: [docs/v2/architecturev2.md](file:///d:/Data%20Science%20Intern/Project/AIsummary-dashboard-jatim/docs/v2/architecturev2.md)
- **Desain UI/UX & Interaksi**: [docs/v2/UIUX.md](file:///d:/Data%20Science%20Intern/Project/AIsummary-dashboard-jatim/docs/v2/UIUX.md)
- **Jadwal & Target Sprint**: [docs/v2/roadmapsv2.md](file:///d:/Data%20Science%20Intern/Project/AIsummary-dashboard-jatim/docs/v2/roadmapsv2.md)
- **Plan Task Spesifik**: [docs/plan/](file:///d:/Data%20Science%20Intern/Project/AIsummary-dashboard-jatim/docs/plan/)

Selamat berkontribusi! Bersama kita bangun dashboard analitik publik yang cerdas, akurat, dan transparan untuk masyarakat Jawa Timur. 🚀
