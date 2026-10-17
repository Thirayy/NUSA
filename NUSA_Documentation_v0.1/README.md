# NUSA --- AI Business & Workforce Ecosystem

NUSA adalah platform berbasis AI untuk membantu UMKM memahami kondisi
bisnis dan menemukan tenaga kerja yang relevan, sekaligus membantu
pekerja membangun rekam jejak profesional melalui **Work Passport**.

## Tujuan MVP

Membuktikan satu alur end-to-end yang menghubungkan: 1. Data usaha →
dashboard dan insight bisnis. 2. Lowongan → profil pekerja → lamaran dan
pencocokan kandidat. 3. Pengalaman kerja → verifikasi pemberi kerja →
Work Passport.

## Fitur inti

### UMKM

-   Profil bisnis dan dashboard.
-   Pencatatan produk, penjualan, dan biaya sederhana.
-   AI Business Analyst dan AI Decision Room.
-   Workforce Management dasar.
-   Job Posting, review lamaran, dan Candidate Matching.
-   Pembuatan serta verifikasi Work Record.

### Pekerja

-   Profil profesional dan keterampilan.
-   Pencarian lowongan dan lamaran.
-   Work Passport dengan status verifikasi catatan kerja.

### AI

-   Analisis berbasis metrik yang dihitung backend.
-   Decision support berbasis data bisnis dan RAG.
-   Matching kandidat dengan kriteria yang dapat dijelaskan.

## Stack yang direncanakan

-   **Frontend:** Next.js, TypeScript, Tailwind CSS, shadcn/ui.
-   **Backend:** Python, FastAPI, SQLAlchemy, Pydantic.
-   **Database:** PostgreSQL + pgvector.
-   **Authentication:** server-side session dengan cookie aman; bukan
    JWT.
-   **AI:** LLM provider melalui service abstraction, embeddings, dan
    RAG.

Stack ini merupakan rencana awal dan bisa diperbarui melalui keputusan
teknis yang terdokumentasi.

## Gambaran arsitektur

``` text
Browser
  │
  ▼
Next.js UI
  │ HTTP API
  ▼
FastAPI backend
  ├── Auth & authorization
  ├── Business & analytics
  ├── Jobs & matching
  ├── Work records & passport
  └── AI services
        ├── Business Analyst
        ├── Decision Room
        ├── RAG retrieval
        └── Matching explanation
  │
  ▼
PostgreSQL + pgvector
```

## Struktur repository yang disarankan

``` text
nusa/
├── README.md
├── docs/
│   ├── PRD.md
│   └── TECHNICAL.md
├── frontend/
└── backend/
    └── app/
        ├── main.py
        ├── core/
        ├── auth/
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
```

Struktur tersebut adalah target awal, bukan berarti seluruh folder harus
dibuat sekaligus. Buat modul saat fitur terkait mulai dikerjakan.

## Status proyek

**Tahap:** dokumentasi dan perancangan MVP.\
**Status kode:** belum dinyatakan siap sampai repository dan
implementasi dibuat serta diuji.

## Dokumen

-   [`docs/PRD.md`](docs/PRD.md) --- kebutuhan produk, scope, alur, dan
    kriteria selesai.
-   [`docs/TECHNICAL.md`](docs/TECHNICAL.md) --- arsitektur, database,
    API, keamanan, dan pendekatan AI.

## Prinsip pengembangan

1.  Bangun alur inti end-to-end sebelum menambah fitur.
2.  Backend menghitung angka; LLM menjelaskan hasilnya.
3.  AI membantu manusia mengambil keputusan, bukan mengambil keputusan
    final.
4.  Data bisnis dan data pekerja harus dipisahkan berdasarkan izin.
5.  Catatan terverifikasi harus dibedakan dari klaim mandiri.
6.  Hindari overengineering: mulai dengan modular monolith.
