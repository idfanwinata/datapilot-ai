# Knowledge Base Analisis Error — Glory RBG-100

**Document ID:** KB-RBG100-002  
**Versi:** 1.2  
**Jenis:** Knowledge base analisis error berdasarkan catatan teknisi  
**Cakupan:** Pencocokan kode error, indikasi kerusakan, area/komponen terkait, dan troubleshooting awal RBG-100

## Instruksi umum untuk OpsPilot AI

Gunakan dokumen ini untuk **menganalisis kode error dan gejala** berdasarkan catatan teknisi. Jangan menjadikan RAS Mode sebagai langkah wajib atau sebagai fokus analisis.

- Cocokkan kode error lengkap dan kombinasinya dengan tabel di bawah.
- Jelaskan indikasi area/komponen dan pemeriksaan awal yang relevan.
- Anggap hasilnya sebagai dugaan awal, bukan kepastian bahwa komponen rusak.
- Jika informasi tidak cukup atau kode tidak ditemukan, minta detail kode, gejala, dan kondisi saat error muncul; jangan mengarang penyebab.
- Pemeriksaan fisik, reset, pelepasan kaset, atau penggantian komponen harus mengikuti SOP dan dilakukan oleh teknisi berwenang.
- Catatan ini berasal dari teknisi dan belum diverifikasi terhadap manual servis resmi. Validasi kode serta nama part sebelum tindakan korektif.

## Daftar error dan indikasi troubleshooting

| Error code / kombinasi | Indikasi dari catatan teknisi | Pemeriksaan awal yang disarankan |
|---|---|---|
| `F103 + 141` | Masalah jaringan | Periksa status koneksi dan konfigurasi jaringan/IP sesuai prosedur. |
| `F103 + 030` | Jaringan | Periksa koneksi jaringan dan konfigurasi IP. |
| `Cek IP address 9C0101` | Pemeriksaan IP address | Verifikasi IP address dan komunikasi jaringan sesuai konfigurasi yang disetujui. |
| `8512 + 180` | Escrow dan pathway | Periksa periksa area escrow dan jalur/pathway sesuai prosedur servis. |
| `6304 + 150` | Kemungkinan pathway lubang kaset; juga dicatat sebagai Cassette 1 | Periksa verifikasi Cassette 1 dan pathway pada area lubang kaset. Indikasi perlu dikonfirmasi di unit. |
| `7A0D + OCO` / `7A03` | Upper board (catatan asli: “upperboadr ini”) | Periksa verifikasi kode dan indikasi upper board menggunakan manual servis. |
| `0610 + 110` | Spur gear / gear motor | Periksa periksa gear dan mekanisme penggerak sesuai SOP. Catatan teknisi menyebut spur gear dan motor gear. |
| `2827 + 130` | Escrow atau hopper | Periksa periksa area escrow dan hopper untuk indikasi mekanik/jammed. |
| `B601 + 110` | Cassette 4 | Periksa verifikasi Cassette 4 dan status pemasangannya. |
| `C207 + 150` | Cassette 5 | Periksa verifikasi Cassette 5 dan area terkait. |
| `B202 + OCO` | Cassette 2 | Periksa verifikasi Cassette 2 dan status pemasangannya. |
| `6307 + 150` | Pathway modul C | Periksa periksa pathway modul C. |
| `0701 + 110` | Modul E, filter | Periksa periksa modul E dan filter sesuai prosedur. |
| `0703 + 110` | Modul E, filter | Periksa periksa modul E dan filter sesuai prosedur. |
| `D148 + 110` | Timeout cassette; catatan menyarankan mengangkat kaset satu per satu | Periksa identifikasi kaset yang terkait. Pemeriksaan/pengangkatan kaset satu per satu hanya dilakukan oleh teknisi berwenang sesuai SOP. |
| `2E23 + 150` | Sensor PSVT3 (Transfer cassette guide no. 3) | Periksa periksa sensor PSVT3 dan transfer cassette guide no. 3 sesuai manual. |
| Hopper uang turun sedikit | Kemungkinan front guide pathway patah | Periksa gejala ini dengan inspeksi visual front guide pathway dan eskalasi jika ada komponen patah. |
| `8416 + OCO` | Indikasi terkait cassette pattern/setting berdasarkan catatan teknisi | Periksa kesesuaian cassette pattern dan konfigurasi dengan manual servis serta kondisi unit. Jangan mengubah parameter tanpa dasar yang terverifikasi. |
| `C901` | Cassette 4 | Periksa verifikasi Cassette 4 dan indikasi pada log. |
| `6311 + 110` | Gear rontok/kerusakan gear | Periksa periksa kondisi gear dan mekanisme penggerak. |
| `6301 + 150` | Kemungkinan ada benda/uang tersangkut di pathway | Periksa periksa pathway untuk obstruksi sesuai prosedur servis. |
| `2E11 + 110` | Sensor PSCT1C/S di pathway; catatan menyebut pembersihan pernah menyelesaikan masalah | Periksa periksa dan bersihkan area sensor PSCT1C/S sesuai SOP. Uji ulang dan pastikan error tidak muncul kembali. |
| `3B40 + OCO` | Cassette pattern | Periksa verifikasi cassette pattern dan setting berdasarkan manual servis. |
| `6253 + 150` | Cabut-pasang cassette (catatan teknisi) | Periksa periksa status cassette. Lepas-pasang hanya sesuai SOP dan setelah kondisi aman. |
| `0703` | Motor flipper | Periksa verifikasi motor flipper dan koneksi terkait sesuai manual. |
| `B105 + 150` | Cassette 1 atau area cassette | Periksa verifikasi Cassette 1 dan area cassette terkait. |
| `0601 + 110` | Uang/komponen tersangkut | Periksa periksa jalur uang dan area mekanik sesuai SOP. |
| `3901 + 7B0` | Pintu bawah kurang rapat saat ditutup | Periksa penutupan pintu bawah, mekanisme latch, dan interlock. Pastikan pintu aman sebelum mesin dioperasikan. |
| `0920 + 110` | Escrow | Periksa periksa area escrow dan pathway terkait. |
| `6605 + 200` | Jammed pada jalur modul B → F → Exit; periksa belt modul B/F dan sisir guide modul F | Periksa telusuri jalur B → F → Exit, periksa belt modul B/F dan guide/sisir modul F sesuai SOP. |
| `8416 + 110` | Setting ulang cassette | Verifikasi setting cassette sebelum melakukan perubahan. |
| `PSCT2C` | Box C | Periksa verifikasi sensor/area PSCT2C dan Box C pada manual servis. |
| `B205 + 150` | Motor solenoid dekat lower board; catatan menyarankan mendengarkan suara saat reset | Periksa periksa respons motor/solenoid sesuai prosedur servis. Dengarkan suara hanya sebagai observasi tambahan, bukan satu-satunya dasar diagnosis. |
| `6453 + 150` | Belum ada detail diagnosis pada catatan | Catat gejala dan cocokkan kode dengan manual servis; jangan menebak part penyebab. Jangan menebak part penyebab. |
| `6313 + 200` | Jam saat proses penarikan; kemungkinan belt/pathway | Periksa periksa pathway dan belt yang relevan sesuai prosedur servis. |
| `PSCT1` | Catatan teknisi menyebut modul B dan pemeriksaan belt | Periksa verifikasi sensor PSCT1, modul B, dan kondisi belt menggunakan manual servis. |

## Template informasi saat investigasi

Catat informasi berikut untuk setiap kejadian:
1. Error code lengkap, termasuk kombinasi kode kedua.
2. Waktu kejadian dan proses yang sedang berjalan.
3. Hasil pemeriksaan yang dilakukan dan temuan aktual.
4. Modul/area yang terindikasi.
5. Pemeriksaan yang dilakukan dan hasilnya.
6. Tindakan korektif yang disetujui.
7. Hasil test setelah tindakan.

## Panduan untuk RAG / AI

Saat menjawab pertanyaan tentang error pada dokumen ini:
- Fokus pada kecocokan error code, gejala, indikasi komponen, dan langkah pemeriksaan yang relevan.
- Tampilkan kode error yang cocok dan indikasi komponen dari catatan.
- Jelaskan bahwa indikasi adalah hipotesis awal, bukan kepastian kerusakan.
- Cantumkan nama file/sumber sebagai referensi.
- Untuk tindakan seperti perubahan parameter, reset, pelepasan cassette, atau pembongkaran, ingatkan pengguna agar mengikuti SOP dan otorisasi teknisi.
- Jika kode tidak ditemukan, minta kode lengkap, gejala, dan hasil pemeriksaan yang sudah dilakukan; jangan mengarang penyebab.
