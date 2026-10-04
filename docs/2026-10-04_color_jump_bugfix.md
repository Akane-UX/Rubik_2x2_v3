# Laporan Perbaikan — Warna Melompat Saat Solving (2026-10-04)

## Gejala
Saat klik "Berikutnya", warna stiker berubah/melompat tepat setelah animasi putaran selesai, terutama di langkah awal (reorientasi seluruh kubus).

## Penyebab & Perbaikan
| # | Lokasi | Penyebab | Perbaikan |
|---|---|---|---|
| 1 | `color_mapping.py` → `state_to_colors`, `_identify_corner` | Tabel `movements.py` memakai konvensi Kociemba (stiker kanonik ke-n ada di posisi `(n+o)%3`), tapi konversi warna membaca orientasi terbalik → warna setelah tiap gerakan U/R/F terpelintir. | Pakai `(3 - o) % 3` saat konversi warna ↔ orientasi. |
| 2 | `color_mapping.py` → `apply_rotation` | Sempat ikut diubah ke `(3 - o) % 3` padahal di sini `rotate3(dirs, o)` = arah stiker milik piece, yang sudah benar dgn nilai mentah. Semua rotasi sumbu `x` saat reorientasi jadi salah twist. | Dikembalikan ke nilai mentah + komentar penjelas. |
| 3 | `templates/index.html` | Cubie hanya punya 3 plate stiker; sisi dalam bolong sehingga belakang stiker cubie lain terlihat saat lapisan berputar. | Tambah 3 face `.cubie-core` hitam di sisi dalam tiap cubie. |

## Verifikasi
Simulator level-stiker meniru persis transformasi CSS frontend dan membandingkan tiap frame animasi dengan frame backend berikutnya (300 scramble acak, orientasi pegang acak):

- Sebelum fix #2: 515 transisi reorientasi salah, 0 transisi gerakan salah.
- Sesudah: **0 / 0**, frame akhir selalu solved.
- `test_color_mapping.py`: 19/19 OK · `test_solver.py`: 36/36 OK.
- `bfs_table.bin` tidak diubah.
