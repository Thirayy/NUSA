# Implementation Plan — NUSA MVP

## Status Modul & Checklist
- [x] **Tahap 1 — Project Foundation**
  - Struktur direktori modular monolith (`backend/app`, `frontend/`, `docs/`)
  - Konfigurasi environment template (`.env.example`)
  - Dokumentasi awal (`PRD.md`, `TECHNICAL.md`, `IMPLEMENTATION_PLAN.md`, `README.md`)
  - Konfigurasi FastAPI, SQLAlchemy, Alembic, dan Health Check database[cite: 1]
- [ ] **Tahap 2 — Authentication & Session Management**
  - Model User & Session (Argon2id hashing, secure HttpOnly cookie)[cite: 1, 3]
  - Endpoint Register, Login, Logout, `/me`[cite: 3]
  - Backend authorization & role checking (EMPLOYER & WORKER)[cite: 1, 3]
- [ ] **Tahap 3 — Business Core & Analytics**
  - Business profile CRUD & ownership isolation[cite: 1, 3]
  - Products, Sales, dan Costs CRUD dengan tipe Decimal[cite: 1, 3]
  - Deterministic Dashboard metrics (omzet, transaksi, biaya, estimasi hasil)[cite: 1, 3]
- [ ] **Tahap 4 — Workforce & Jobs**
  - Worker profiles & skills[cite: 1, 3]
  - Job posting & application flow[cite: 1, 3]
  - Transparent AI matching explanation rules[cite: 1, 3]
- [ ] **Tahap 5 — Work Passport**
  - Work Records & verification status[cite: 1, 3]
  - Claim & correction requests[cite: 1, 3]
- [ ] **Tahap 6 — AI Services & RAG**
  - Provider abstraction layer, Business Analyst, Decision Room, RAG ingestion/retrieval[cite: 1, 3]
- [ ] **Tahap 7 — Integration, Seed Data & Final Testing**
  - End-to-end integration, demo seed data, pytest suites, dan final verification[cite: 1]