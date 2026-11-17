# Laporan Perbaikan — Koneksi Frontend ke Backend `app.py` (2026-11-17)

## Gejala
Frontend menampilkan pesan *"Tidak bisa terhubung ke server. Pastikan app.py sedang berjalan."* saat menekan tombol **Selesaikan**, atau tidak merespons saat menekan tombol **Isi Contoh Acak**.

## Penyebab & Perbaikan
| # | Lokasi | Penyebab | Perbaikan |
|---|---|---|---|
| 1 | `templates/index.html` | Pemanggilan `fetch("/api/example")` dan `fetch("/api/solve")` menggunakan path relatif murni. Jika halaman dibuka melalui VS Code Live Server (`:5500`) atau klik langsung berkas (`file://`), request mengarah ke origin yang salah dan gagal. | Menambahkan deteksi otomatis `API_BASE` yang mengarahkan request ke `http://127.0.0.1:5000` apabila halaman tidak dibuka dari port `5000`, serta membungkus handler `#btn-example` dengan `try...catch`. |
| 2 | `app.py` | Belum ada header CORS dan penanganan preflight `OPTIONS` pada `/api/solve`, sehingga browser memblokir request lintas origin/port (misal dari Live Server `:5500` atau `file://` ke `:5000`). | Menambahkan middleware `@app.after_request` untuk menyertakan header `Access-Control-Allow-Origin: *`, `Access-Control-Allow-Headers: Content-Type`, dan `Access-Control-Allow-Methods: GET, POST, OPTIONS`, serta mendukung metode `OPTIONS` pada `/api/solve`. |
| 3 | Environment Python | Paket `flask` belum terpasang di global `/usr/bin/python3` (Python 3.14) dan proses daemon `app.py` belum berjalan. | Menjalankan server `app.py` di background pada `http://127.0.0.1:5000` menggunakan interpreter virtualenv yang memiliki Flask (`/usr/pgadmin4/venv/bin/python3`). |

## Verifikasi
- `GET /api/example`: HTTP `200 OK` (dengan header `Access-Control-Allow-Origin: *`).
- `POST /api/solve`: HTTP `200 OK`, mengembalikan langkah solusi optimal dengan benar.
- Server aktif dan listening di `http://127.0.0.1:5000`.
