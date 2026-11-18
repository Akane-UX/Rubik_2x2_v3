# Perbaikan Bug Kedip Warna & Pemisahan Kode Frontend

- **Tanggal**: 2026-11-17
- **Backend**: tidak diubah (55/55 unit test lulus; Flask otomatis melayani folder `static/`)

## Bug: warna berkedip saat menjalankan langkah
**Penyebab**
1. `.cubie-face` memiliki `transition: background-color 0.15s`. Setelah animasi putaran selesai, cubie dikembalikan ke posisi awal lalu warna diganti — transisi membuat warna lama memudar ke warna baru selama 150 ms sehingga terlihat berkedip.
2. Cubie dipindah ke elemen pivot sementara lalu dikembalikan (reparenting DOM) setiap langkah, memicu layer 3D dirender ulang sesaat.

**Perbaikan**
- Transisi `background-color` pada stiker dihapus.
- Animasi kini memutar cubie langsung di tempat (`rotateX/Y/Z(deg) translate3d(...)`) tanpa memindah DOM; reset transform dan pewarnaan baru terjadi di frame yang sama.
- Akhir animasi dideteksi via `transitionend` dengan fallback `setTimeout`.

## Struktur Baru
| Berkas | Fungsi |
|---|---|
| `templates/index.html` | Markup saja |
| `static/css/style.css` | Seluruh styling |
| `static/js/config.js` | Konstanta geometri, warna, sudut putaran, `API_BASE` |
| `static/js/state.js` | State global & helper kuota warna |
| `static/js/palette.js` | Palet + indeks kuota warna, status bar |
| `static/js/cube.js` | Pembuatan kubus 3D, pewarnaan stiker, animasi putaran |
| `static/js/camera.js` | Rotasi sudut pandang via drag kursor & tombol |
| `static/js/steps.js` | Frame solusi, label instruksi, navigasi langkah |
| `static/js/api.js` | Request ke `/api/example` & `/api/solve` |
| `static/js/main.js` | Event tombol aksi & inisialisasi |

Path aset memakai `../static/...` sehingga tetap jalan via Flask (`/`), Live Server, maupun dibuka langsung sebagai file.
