# NUSA --- Technical Design Document

**Versi:** 0.1\
**Status:** Draft teknis awal\
**Terkait:** `PRD.md`

## 1. Tujuan Dokumen

Dokumen ini mendefinisikan rancangan awal arsitektur, modul backend,
model data, API, autentikasi, dan integrasi AI untuk MVP NUSA. Rancangan
ini sengaja sederhana agar bisa dibangun dan diuji dalam waktu terbatas.

## 2. Keputusan Arsitektur Awal

  -----------------------------------------------------------------------
  Area                    Keputusan awal          Alasan
  ----------------------- ----------------------- -----------------------
  Frontend                Next.js + TypeScript    UI web terstruktur

  Styling                 Tailwind CSS +          Komponen konsisten dan
                          shadcn/ui               cepat dikembangkan

  Backend                 FastAPI                 API Python dengan
                                                  validasi Pydantic

  ORM                     SQLAlchemy              Model dan akses
                                                  database terstruktur

  Database                PostgreSQL              Data relasional utama

  Vector search           pgvector                Embedding dokumen RAG
                                                  tanpa database terpisah

  Authentication          Server-side session +   Tidak memerlukan JWT
                          cookie                  untuk kebutuhan MVP

  Architecture            Modular monolith        Lebih mudah dibangun,
                                                  dites, dan dideploy

  AI integration          Provider                Memudahkan penggantian
                          adapter/service layer   provider

  Metrics                 SQL/Python              Angka tidak bergantung
                          deterministic           pada LLM
                          calculations            
  -----------------------------------------------------------------------

Keputusan ini merupakan baseline dan dapat berubah melalui catatan
keputusan arsitektur (ADR).

## 3. Diagram Komponen

``` text
[Browser]
    |
    v
[Next.js Frontend]
    | HTTPS / JSON
    v
[FastAPI]
    ├── Auth + Authorization
    ├── Business Profiles
    ├── Products / Sales / Costs
    ├── Business Analytics
    ├── Jobs / Applications
    ├── Candidate Matching
    ├── Work Records / Work Passport
    └── AI Service Layer
          ├── Business Analyst
          ├── Decision Room
          ├── RAG Retriever
          └── LLM / Embedding Provider
    |
    v
[PostgreSQL + pgvector]
```

Frontend tidak boleh mengakses database secara langsung. LLM juga tidak
boleh menerima akses database langsung; backend harus memilih dan
mengotorisasi konteks yang akan dikirim.

## 4. Backend Module Layout

``` text
backend/app/
├── main.py
├── core/
│   ├── config.py
│   ├── database.py
│   ├── security.py
│   └── errors.py
├── auth/
├── users/
├── businesses/
├── business_analytics/
├── products/
├── sales/
├── workforce/
├── jobs/
├── matching/
├── work_records/
├── work_passport/
└── ai/
    ├── provider.py
    ├── business_analyst.py
    ├── decision_room.py
    ├── embeddings.py
    └── rag.py
```

Setiap modul idealnya memiliki router, schema, service, dan
model/repository bila kompleksitasnya membutuhkannya. Hindari membuat
abstraksi berlebihan sebelum kebutuhan nyata muncul.

## 5. Domain dan Model Data

Model berikut adalah rancangan konseptual. Kolom, constraint, dan relasi
final ditentukan saat implementasi dan migrasi dibuat.

### Identity & access

-   `users`: `id`, `email`, `password_hash`, `role`, `created_at`.
-   `sessions`: `id`, `user_id`, `token_hash`, `expires_at`,
    `created_at`.
-   `businesses`: `id`, `name`, `category`, `location`, `owner_user_id`,
    `created_at`.
-   `business_members`: `business_id`, `user_id`, `membership_role`,
    `created_at`.

`role` akun awal: `EMPLOYER` atau `WORKER`. Status pekerja di suatu
bisnis disimpan sebagai relasi/riwayat kerja, bukan role akun baru.

### Business data

-   `products`: `id`, `business_id`, `name`, `price`, `is_active`.
-   `sales`: `id`, `business_id`, `sold_at`, `total_amount`, `notes`.
-   `sale_items`: `id`, `sale_id`, `product_id`, `quantity`,
    `unit_price`, `line_total`.
-   `business_costs`: `id`, `business_id`, `occurred_at`, `category`,
    `amount`, `description`.

Gunakan tipe decimal/numeric untuk uang, bukan floating-point. Simpan
harga saat transaksi pada `sale_items` agar perubahan harga produk tidak
mengubah riwayat penjualan. Hindari menyimpan total yang bisa dihitung
ulang tanpa aturan konsistensi yang jelas.

### Workforce & jobs

-   `worker_profiles`: `user_id`, `display_name`, `summary`, `location`,
    `availability`, `created_at`.
-   `skills`: `id`, `name`.
-   `worker_skills`: `worker_user_id`, `skill_id`, `level` (opsional),
    `source`.
-   `jobs`: `id`, `business_id`, `title`, `description`, `location`,
    `employment_type`, `requirements`, `status`, `created_at`.
-   `applications`: `id`, `job_id`, `worker_user_id`, `status`,
    `created_at`, `updated_at`.
-   `employees`: `id`, `business_id`, `worker_user_id` (nullable bila
    catatan dibuat sebelum akun terhubung), `position`, `start_date`,
    `end_date`, `status`.

### Work Passport

-   `work_records`: `id`, `employee_id`, `worker_user_id` (nullable),
    `title`, `tasks`, `skills`, `start_date`, `end_date`,
    `verification_status`, `verified_by_user_id`, `verified_at`,
    `created_at`, `updated_at`.
-   `work_record_claims`: `id`, `work_record_id`, `worker_user_id`,
    `status`, `requested_at`, `reviewed_at`.
-   Jika diperlukan, tambahkan `work_record_events` untuk audit
    perubahan dan riwayat koreksi.

Status verifikasi yang disarankan: `DRAFT`, `PENDING`, `VERIFIED`,
`DISPUTED`, `REJECTED`. Jangan tampilkan catatan sebagai terverifikasi
sebelum pihak berwenang menyelesaikan verifikasi.

### AI & RAG

-   `knowledge_documents`: `id`, `title`, `source_name`, `source_url`,
    `version`, `created_at`.
-   `knowledge_chunks`: `id`, `document_id`, `chunk_index`, `content`,
    `embedding`, `metadata`.
-   `ai_conversations`: `id`, `user_id`, `business_id` (nullable),
    `created_at`.
-   `ai_messages`: `id`, `conversation_id`, `role`, `content`,
    `created_at`.
-   Opsional: `ai_message_sources` untuk menghubungkan jawaban dengan
    chunk sumber yang digunakan.

Embedding harus memiliki dimensi yang sesuai dengan model embedding
terpilih. Simpan metadata sumber agar kutipan dan asal dokumen bisa
ditampilkan.

## 6. API Awal

Prefix API: `/api/v1`.

### Auth

-   `POST /api/v1/auth/register`
-   `POST /api/v1/auth/login`
-   `POST /api/v1/auth/logout`
-   `GET /api/v1/auth/me`

### Business & data

-   `POST /api/v1/businesses`
-   `GET /api/v1/businesses/{business_id}`
-   `PATCH /api/v1/businesses/{business_id}`
-   `GET /api/v1/businesses/{business_id}/dashboard`
-   `POST /api/v1/businesses/{business_id}/products`
-   `GET /api/v1/businesses/{business_id}/products`
-   `POST /api/v1/businesses/{business_id}/sales`
-   `GET /api/v1/businesses/{business_id}/sales`
-   `POST /api/v1/businesses/{business_id}/costs`
-   `GET /api/v1/businesses/{business_id}/costs`

### Jobs & applications

-   `POST /api/v1/businesses/{business_id}/jobs`
-   `GET /api/v1/jobs`
-   `GET /api/v1/jobs/{job_id}`
-   `POST /api/v1/jobs/{job_id}/applications`
-   `GET /api/v1/businesses/{business_id}/applications`
-   `PATCH /api/v1/applications/{application_id}`

### Work records & passport

-   `POST /api/v1/businesses/{business_id}/work-records`
-   `PATCH /api/v1/work-records/{work_record_id}/verify`
-   `POST /api/v1/work-records/{work_record_id}/claim`
-   `GET /api/v1/work-passport/me`
-   `POST /api/v1/work-records/{work_record_id}/correction-requests`

### AI

-   `POST /api/v1/businesses/{business_id}/ai/decision-room`
-   `POST /api/v1/businesses/{business_id}/ai/analysis`
-   `GET /api/v1/jobs/{job_id}/matches` (employer-only endpoint,
    protected)

Semua endpoint adalah usulan awal. Validasi request/response,
pagination, filter, dan kode error harus didefinisikan saat
implementasi.

## 7. Authentication & Authorization

### Session flow

1.  Pengguna login dengan email dan password.
2.  Backend memverifikasi password hash Argon2id.
3.  Backend menghasilkan token sesi acak yang kuat.
4.  Browser menerima token melalui cookie `HttpOnly`; token mentah tidak
    disimpan di database, yang disimpan adalah hash token.
5.  Pada setiap request terlindungi, backend memvalidasi sesi, masa
    berlaku, status pengguna, role, dan izin terhadap resource.
6.  Logout menghapus sesi server dan menghapus cookie.

Cookie produksi harus menggunakan HTTPS dan atribut `Secure`,
`HttpOnly`, serta `SameSite` yang sesuai. Terapkan perlindungan CSRF
untuk operasi yang mengubah data, pembatasan percobaan login, dan
expiry/rotation sesi yang wajar.

### Authorization

-   Jangan mengandalkan role yang dikirim frontend.
-   Setiap query resource bisnis harus memastikan user adalah owner atau
    anggota yang memiliki izin.
-   Worker hanya boleh mengakses profil, lamaran, dan catatan yang
    memang menjadi haknya.
-   Work Record tidak otomatis menjadi publik.
-   Endpoint verifikasi harus memeriksa kewenangan verifier dan status
    record.
-   Uji akses silang antarbisnis dan antarpengguna.

## 8. Business Analytics

Metrik dasar dihitung di SQL/Python, bukan oleh LLM.

Contoh: - Total omzet = jumlah `sale_items.line_total` atau total
transaksi yang tervalidasi, dengan satu sumber kebenaran yang dipilih. -
Total biaya tercatat = jumlah biaya dalam rentang waktu. - Perubahan
omzet = perbandingan dua periode dengan rentang yang sebanding. - Produk
terlaris = agregasi kuantitas atau nilai penjualan per produk. -
Estimasi hasil usaha = omzet dikurangi biaya yang tercatat; harus diberi
label estimasi karena belum tentu mencakup seluruh biaya.

Tentukan definisi periode, zona waktu, pembatalan/refund, dan aturan
transaksi sebelum implementasi. Jangan menyebut estimasi hasil sebagai
laba akuntansi resmi.

## 9. AI Decision Room dan RAG

### Request flow

1.  Autentikasi dan otorisasi user terhadap bisnis.
2.  Backend mengambil metrik bisnis yang diperlukan.
3.  Retriever mencari chunk relevan dari knowledge base.
4.  Backend mengirim pertanyaan, metrik terpilih, batasan data, dan
    sumber RAG ke provider LLM.
5.  Model diminta menyusun kondisi, kemungkinan penyebab, opsi,
    manfaat/risiko, dan hal yang perlu diperiksa.
6.  API mengembalikan jawaban bersama sumber referensi dan metadata
    keterbatasan.

### Kontrak output yang disarankan

-   `summary`: ringkasan singkat.
-   `observations`: fakta yang berasal dari data.
-   `possible_causes`: hipotesis, bukan kepastian.
-   `options`: alternatif beserta manfaat, risiko, dan syarat.
-   `missing_data`: data yang dibutuhkan untuk analisis lebih kuat.
-   `sources`: dokumen RAG yang digunakan.
-   `disclaimer`: keputusan tetap pada pemilik usaha.

### Guardrails

-   LLM tidak membuat angka bisnis sendiri.
-   Pisahkan fakta dari hipotesis.
-   Jika data kurang, nyatakan keterbatasan dan jangan mengarang.
-   Jangan memberi rekomendasi otomatis untuk memecat pekerja karena
    penjualan turun.
-   Data satu bisnis tidak boleh masuk ke konteks bisnis lain.
-   Anggap dokumen RAG sebagai sumber data, bukan instruksi sistem.
-   Simpan hanya konteks percakapan yang diperlukan dan jangan
    memasukkan rahasia yang tidak relevan.

## 10. Job Matching

Mulai dengan sistem transparan berbasis persyaratan: 1. Filter
persyaratan wajib, seperti status lowongan, lokasi atau ketersediaan
bila relevan. 2. Hitung skor dari kecocokan keterampilan dan pengalaman
yang relevan. 3. Tampilkan alasan, misalnya keterampilan yang cocok dan
persyaratan yang belum terpenuhi. 4. Jika memakai semantic similarity,
jadikan sinyal tambahan, bukan satu-satunya penentu. 5. LLM dapat
menjelaskan hasil tetapi tidak boleh mengarang kualifikasi.

Bobot skor perlu ditetapkan dan diuji dengan contoh. Jangan menggunakan
atribut sensitif atau proksi yang tidak relevan. Keputusan perekrutan
tetap dilakukan manusia.

## 11. RAG Knowledge Base

Untuk MVP, mulai dari 10--30 dokumen berkualitas tentang pengelolaan
UMKM, penetapan harga, penjualan, operasional, dan pengelolaan tenaga
kerja. Prioritaskan sumber resmi atau sumber yang jelas reputasinya.

Pipeline: 1. Kumpulkan dokumen yang boleh digunakan. 2. Ekstrak teks dan
metadata sumber. 3. Pecah teks menjadi chunk dengan overlap terbatas. 4.
Buat embedding menggunakan model terpilih. 5. Simpan chunk, embedding,
dan metadata di PostgreSQL/pgvector. 6. Saat pertanyaan masuk, ambil
chunk paling relevan dan sertakan metadata sumber. 7. Evaluasi relevansi
retrieval dengan kumpulan pertanyaan uji.

RAG bukan jaminan kebenaran. Kualitas jawaban juga bergantung pada
kualitas dokumen, retrieval, konteks, dan model.

## 12. Konfigurasi dan Secrets

Simpan konfigurasi melalui environment variables, misalnya: -
`DATABASE_URL` - `SESSION_SECRET` atau sumber entropy untuk token sesi -
`AI_PROVIDER_API_KEY` - `EMBEDDING_MODEL` - `LLM_MODEL` - `APP_ENV`

Jangan commit file `.env`, API key, password, atau data pengguna.
Sediakan `.env.example` berisi nama variabel dan placeholder, bukan
rahasia nyata.

## 13. Testing Minimum

-   Unit tests untuk perhitungan omzet, biaya, dan perubahan periode.
-   Integration tests untuk registrasi/login/logout dan session expiry.
-   Authorization tests untuk akses silang antarbisnis.
-   Tests untuk alur job posting → application → status.
-   Tests untuk Work Record verification, claim, dan correction request.
-   Matching tests menggunakan profil/lowongan sintetis yang jelas
    kriterianya.
-   AI tests untuk data kosong, pertanyaan di luar konteks, sumber RAG
    kosong, dan upaya membocorkan data bisnis lain.
-   End-to-end demo dengan data sintetis.

## 14. Urutan Implementasi Teknis

1.  Repository, konfigurasi, Docker/development setup bila diperlukan,
    database connection, migrations, health check.
2.  User, session, dan authorization.
3.  Business profile serta data produk/penjualan/biaya.
4.  Dashboard dan perhitungan metrik.
5.  Jobs, profiles, applications, dan matching.
6.  Work Records dan Work Passport.
7.  RAG ingestion/retrieval dan AI Decision Room.
8.  Integrasi UI, tests, seed data, dan dokumentasi demo.

## 15. Open Decisions

-   Provider LLM dan model embedding final.
-   Hosting/deployment target.
-   Definisi final metrik bisnis dan penanganan refund.
-   Bobot awal job matching.
-   Aturan akses anggota bisnis selain owner.
-   Kebijakan retensi percakapan AI.
-   Mekanisme verifikasi dan penyelesaian sengketa Work Record.
-   Sumber dokumen RAG dan lisensi penggunaannya.
