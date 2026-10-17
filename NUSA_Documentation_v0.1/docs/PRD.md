# NUSA --- Product Requirements Document (PRD)

**Versi:** 0.1\
**Status:** Draft awal untuk validasi dan pengembangan MVP\
**Produk:** NUSA --- AI Business & Workforce Ecosystem

## 1. Ringkasan Produk

NUSA adalah platform berbasis AI yang membantu UMKM memahami kondisi
bisnis, menemukan tenaga kerja yang relevan, dan mencatat pengalaman
kerja yang dapat menjadi rekam jejak profesional pekerja.

NUSA menggabungkan empat konsep: business intelligence, pengelolaan
tenaga kerja, pencarian kerja, dan AI decision support. Fokusnya bukan
menggantikan keputusan manusia, tetapi menyediakan informasi dan
alternatif yang lebih mudah dipahami.

## 2. Masalah yang Ingin Diselesaikan

### Untuk UMKM

-   Data penjualan dan biaya sering tersebar atau belum mudah
    dianalisis.
-   Pemilik usaha kesulitan memahami perubahan performa bisnis dari data
    yang terbatas.
-   Proses mencari kandidat yang sesuai membutuhkan waktu.
-   Riwayat tugas dan pengalaman pekerja tidak selalu terdokumentasi
    dengan baik.

### Untuk pekerja

-   Sulit menunjukkan keterampilan dan pengalaman secara terstruktur.
-   Pengalaman kerja dari UMKM belum tentu tercatat sebagai bukti
    profesional yang dapat digunakan untuk kesempatan berikutnya.
-   Informasi lowongan dan kecocokan pekerjaan bisa tersebar di berbagai
    tempat.

## 3. Visi dan Nilai Produk

**Visi:** Menghubungkan perkembangan bisnis UMKM dengan perkembangan
profesional pekerja melalui data, AI, dan pengalaman kerja yang
terverifikasi.

**Nilai utama:** NUSA membantu UMKM memahami bisnis dan menemukan tenaga
kerja yang sesuai, sementara pekerja dapat membangun Work Passport
berdasarkan pengalaman yang tercatat dan diverifikasi.

## 4. Target Pengguna

### Pengguna utama

1.  **Pemilik/pengelola UMKM** --- mencatat data dasar usaha, memahami
    insight, membuat lowongan, dan mengelola rekam kerja.
2.  **Pekerja/pencari kerja** --- membuat profil, mencari lowongan,
    melamar, dan mengelola Work Passport.

### Asumsi awal

-   Pengguna MVP mengakses NUSA melalui web.
-   Pengguna membutuhkan alur sederhana dan istilah yang mudah dipahami.
-   MVP diuji pada skenario UMKM dan lowongan yang terbatas, bukan
    langsung untuk skala nasional.

## 5. Tujuan MVP

Membuktikan tiga hal: 1. Data bisnis sederhana dapat diubah menjadi
ringkasan dan insight yang berguna. 2. UMKM dan pekerja dapat melewati
alur lowongan, lamaran, dan pencocokan kandidat. 3. Pengalaman kerja
dapat dicatat, diverifikasi oleh pemberi kerja, lalu ditautkan ke Work
Passport pekerja.

### Indikator keberhasilan awal

-   Pemilik UMKM dapat menyelesaikan input data bisnis contoh dan
    melihat ringkasan yang benar.
-   AI Decision Room menjawab berdasarkan data yang tersedia, menyatakan
    keterbatasan data, dan tidak mengarang angka.
-   Pekerja dapat membuat profil dan melamar lowongan.
-   Pemilik UMKM dapat melihat lamaran dan alasan kecocokan kandidat.
-   Work Record yang diverifikasi dapat tampil sebagai catatan
    terverifikasi pada Work Passport.
-   Alur utama dapat didemonstrasikan dari awal hingga akhir tanpa
    intervensi developer.

## 6. Ruang Lingkup Fitur MVP

### A. Akun dan akses

-   Registrasi, login, logout.
-   Dua tipe akun: `EMPLOYER` dan `WORKER`.
-   Akses data dibatasi berdasarkan pemilik bisnis, keanggotaan bisnis,
    dan pemilik profil.

### B. Fitur UMKM

-   Profil bisnis dasar.
-   Dashboard ringkas.
-   Input produk sederhana.
-   Input transaksi penjualan dan biaya.
-   Ringkasan omzet, jumlah transaksi, biaya tercatat, dan estimasi
    hasil usaha berdasarkan data yang tersedia.
-   Analisis tren dasar jika tersedia data dari lebih dari satu periode.
-   Daftar pekerja dan catatan kerja dasar.
-   Pembuatan lowongan.
-   Daftar lamaran dan perubahan status lamaran.
-   Pembuatan serta verifikasi Work Record.
-   AI Decision Room dengan konteks data bisnis dan referensi
    pengetahuan terbatas.

### C. Fitur pekerja

-   Profil profesional dasar.
-   Daftar keterampilan.
-   Pencarian dan detail lowongan.
-   Melamar lowongan dan melihat status lamaran.
-   Work Passport.
-   Klaim/tautkan Work Record yang dibuat pemberi kerja.
-   Melaporkan atau meminta koreksi pada catatan yang tidak akurat.

### D. Fitur AI

1.  **AI Business Analyst** --- merangkum metrik dan tren yang dihitung
    backend.
2.  **AI Decision Room** --- menjelaskan kondisi, kemungkinan penyebab,
    beberapa opsi, trade-off, dan keterbatasan data menggunakan data
    bisnis serta hasil retrieval RAG.
3.  **AI Job Matching** --- memberi urutan kecocokan berdasarkan
    persyaratan terstruktur; AI dapat menjelaskan hasil, tetapi tidak
    menjadi satu-satunya penentu perekrutan.

## 7. Di Luar Ruang Lingkup MVP

-   Payroll dan perpajakan.
-   Akuntansi lengkap atau pengganti aplikasi pembukuan resmi.
-   Absensi biometrik dan penjadwalan shift kompleks.
-   Chat sosial, feed, atau marketplace produk.
-   Aplikasi mobile native.
-   Analitik prediktif kompleks dan simulasi bisnis tingkat lanjut.
-   Pelatihan model AI sendiri.
-   Keputusan otomatis untuk menerima/menolak kandidat atau
    memberhentikan pekerja.

## 8. Alur Pengguna Utama

### Alur bisnis

1.  Pemilik mendaftar dan membuat profil bisnis.
2.  Pemilik memasukkan produk, penjualan, dan biaya sederhana.
3.  Backend menghitung metrik secara deterministik.
4.  Dashboard menampilkan ringkasan.
5.  Pemilik bertanya melalui AI Decision Room.
6.  Backend memeriksa izin, mengambil data relevan dan potongan
    referensi RAG.
7.  AI mengembalikan analisis, opsi, risiko, asumsi, serta sumber
    referensi jika digunakan.
8.  Pemilik menentukan tindakan sendiri.

### Alur tenaga kerja

1.  Pemberi kerja membuat lowongan dengan persyaratan terstruktur.
2.  Pekerja membuat profil dan mengisi keterampilan.
3.  Sistem menghitung kecocokan awal.
4.  Pekerja melamar dan pemberi kerja meninjau lamaran.
5.  Jika direkrut, pemberi kerja mencatat pengalaman dan tugas.
6.  Pemberi kerja memverifikasi catatan kerja.
7.  Pekerja mengklaim atau menautkan catatan ke Work Passport.
8.  Pekerja dapat meminta koreksi jika ada informasi yang keliru.

## 9. Persyaratan Fungsional

  -----------------------------------------------------------------------
  ID                      Persyaratan             Prioritas
  ----------------------- ----------------------- -----------------------
  FR-01                   Pengguna dapat          Must
                          registrasi, login, dan  
                          logout                  

  FR-02                   Sistem menerapkan akses Must
                          berdasarkan role dan    
                          kepemilikan data        

  FR-03                   Employer dapat membuat  Must
                          dan mengelola profil    
                          bisnis                  

  FR-04                   Employer dapat mencatat Must
                          produk, penjualan, dan  
                          biaya sederhana         

  FR-05                   Dashboard menampilkan   Must
                          metrik yang dihitung    
                          backend                 

  FR-06                   AI Decision Room        Must
                          menggunakan konteks     
                          bisnis yang diizinkan   

  FR-07                   Sistem menyimpan        Must
                          lowongan dan menerima   
                          lamaran                 

  FR-08                   Worker dapat membuat    Must
                          profil dan keterampilan 

  FR-09                   Sistem menghasilkan     Must
                          kecocokan kandidat yang 
                          dapat dijelaskan        

  FR-10                   Employer dapat membuat  Must
                          dan memverifikasi Work  
                          Record                  

  FR-11                   Worker dapat melihat    Must
                          Work Passport dan       
                          mengklaim catatan yang  
                          cocok                   

  FR-12                   Worker dapat meminta    Should
                          koreksi catatan kerja   

  FR-13                   RAG menampilkan sumber  Should
                          dokumen yang dipakai AI 
  -----------------------------------------------------------------------

## 10. Persyaratan Nonfungsional

-   **Keamanan:** password di-hash dengan Argon2id; sesi server-side;
    cookie aman; validasi input; pembatasan akses pada setiap endpoint.
-   **Privasi:** data bisnis tidak otomatis terlihat oleh pekerja;
    catatan internal pemberi kerja tidak otomatis menjadi publik.
-   **Keandalan AI:** angka dihitung backend, bukan dibuat oleh LLM; AI
    menyatakan jika data tidak cukup.
-   **Keterlacakan:** catatan terverifikasi dibedakan dari klaim mandiri
    dan teks yang dihasilkan AI.
-   **Kemudahan penggunaan:** formulir ringkas, bahasa sederhana, dan
    input seminimal mungkin.
-   **Maintainability:** backend modular monolith; layanan AI dipisahkan
    melalui modul/service interface.

## 11. Prinsip AI dan Keadilan

-   AI adalah alat bantu keputusan, bukan pengambil keputusan akhir.
-   Tidak ada rekomendasi otomatis untuk memecat pekerja berdasarkan
    penurunan penjualan.
-   Matching menilai relevansi terhadap persyaratan pekerjaan, bukan
    nilai manusia.
-   Alasan kecocokan harus bisa dipahami.
-   Work Record harus menunjukkan status verifikasi dan asal
    informasinya.
-   AI tidak boleh menambahkan keterampilan atau pengalaman yang tidak
    didukung sumber.
-   Jika data tidak cukup, sistem harus menyatakannya.

## 12. Asumsi dan Risiko

  -----------------------------------------------------------------------
  Risiko                              Mitigasi awal
  ----------------------------------- -----------------------------------
  UMKM enggan mengisi banyak data     Form sederhana dan data minimum
                                      untuk demo

  Data bisnis terlalu sedikit untuk   Tampilkan batasan data; sediakan
  analisis                            data demo yang jelas ditandai

  Jawaban AI tidak akurat             Hitung angka di backend, batasi
                                      konteks, tampilkan sumber dan
                                      disclaimer

  Matching bias atau tidak transparan Gunakan kriteria relevan yang
                                      eksplisit dan penjelasan hasil

  Catatan kerja diperselisihkan       Status verifikasi, proses koreksi,
                                      dan jejak perubahan

  Scope membesar                      Bekukan daftar fitur MVP dan
                                      prioritaskan alur end-to-end
  -----------------------------------------------------------------------

## 13. Rencana Implementasi Awal

1.  Fondasi repository, konfigurasi, database, dan autentikasi.
2.  Model data serta API bisnis dan profil pekerja.
3.  Input bisnis, dashboard, dan metrik deterministik.
4.  Lowongan, lamaran, dan matching dasar.
5.  Work Record dan Work Passport.
6.  RAG dan AI Decision Room.
7.  Integrasi frontend, pengujian, seed data, dan demo end-to-end.

Urutan dapat disesuaikan berdasarkan kemampuan tim, tetapi autentikasi,
skema data, dan alur inti perlu ditetapkan sebelum membangun fitur
tambahan.

## 14. Definisi Selesai (MVP)

MVP dianggap siap didemonstrasikan jika: - Semua alur inti dapat
diselesaikan melalui UI. - Data antar akun dan bisnis terisolasi sesuai
izin. - Metrik dashboard dapat diverifikasi dengan perhitungan manual. -
Jawaban AI menggunakan konteks yang diizinkan dan menangani data yang
tidak cukup. - Lamaran, status, Work Record, dan Work Passport tersimpan
konsisten. - Ada pengujian untuk autentikasi, otorisasi, matching dasar,
dan alur Work Record. - Dokumentasi instalasi dan konfigurasi tersedia.
