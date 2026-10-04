# Dokumentasi Perbaikan — Pocket Cube Solver

> File yang diubah: `templates/index.html`

---

## Ringkasan Masalah

Ada **dua kategori bug utama** yang dilaporkan:

1. **Warna tidak sesuai input saat masuk mode solving**
2. **Animasi rotasi kubus tidak jelas / tidak sesuai referensi**

---

## Bug 1 — Warna Tidak Sesuai Input Saat Solving

### Penyebab

#### 1a. Shallow Copy di `buildFrames()`

**Kode lama (bermasalah):**
```js
frames = [{ state: { ...selections } }]; // frame 0 = persis input user
```

Operator `{ ...selections }` hanya melakukan **shallow copy**. Objek `selections` berisi:
```js
{ 0: ["White","Red","Green"], 1: [...], ... }
```

Spread operator menyalin *referensi* ke array-array di dalamnya — bukan isi array-nya. Artinya `frames[0].state[0]` dan `selections[0]` menunjuk ke **array yang sama di memori**. Jika `selections` diubah kemudian (misal saat reset), `frames[0].state` ikut berubah, sehingga saat `renderCubeFromCorners(frames[0].state)` dipanggil, warna yang ditampilkan bisa salah.

**Solusi — fungsi `copySelections()`:**
```js
function copySelections(sel) {
  const out = {};
  for (let s = 0; s < 8; s++) {
    out[s] = sel[s] ? [...sel[s]] : [null, null, null];
  }
  return out;
}

// buildFrames() sekarang:
frames = [{ state: copySelections(selections) }];
```

Setiap array warna per-slot disalin dengan spread `[...sel[s]]`, sehingga benar-benar **deep copy independen**.

---

#### 1b. Shallow Copy di `cornerColorsFromStateObj()`

**Kode lama (bermasalah):**
```js
function cornerColorsFromStateObj(stateObj) {
  const out = {};
  for (let s = 0; s < 8; s++) out[s] = stateObj[String(s)];
  return out;
}
```

`stateObj[String(s)]` adalah array dari respons backend. Kode lama menyimpan referensi aslinya, bukan salinannya.

**Solusi:**
```js
function cornerColorsFromStateObj(stateObj) {
  const out = {};
  for (let s = 0; s < 8; s++) {
    const arr = stateObj[String(s)];
    out[s] = arr ? [...arr] : [null, null, null];
  }
  return out;
}
```

---

#### 1c. Format Payload ke Backend

**Kode lama:**
```js
body: JSON.stringify({ corners: selections }),
```

`selections` adalah objek JavaScript dengan key integer `0–7`. Kode baru secara eksplisit mengonversinya ke string agar konsisten:

```js
const cornersPayload = {};
for (let s = 0; s < 8; s++) {
  cornersPayload[String(s)] = selections[s];
}
body: JSON.stringify({ corners: cornersPayload }),
```

Ini memastikan backend Python menerima key `"0"`, `"1"`, dst. yang lalu dikonversi dengan `int(slot)` di `app.py`.

---

## Bug 2 — Animasi Rotasi Tidak Jelas / Salah

### Penyebab

#### 2a. Teknik Animasi Lama: Transform String Salah

**Kode lama (bermasalah):**
```js
// Di animateSlots():
el.style.transform = `rotate${axis}(${angleDeg}deg) ${el.dataset.base}`;
```

Dalam CSS, transform dibaca **dari kanan ke kiri**. Jadi `rotateX(90deg) translate3d(44px, -44px, 44px)` artinya:
1. Pertama **translate** cubie ke posisinya
2. Lalu **rotate** di titik asal CSS elemen tersebut

Masalahnya: rotasi terjadi di sekitar titik yang salah — bukan di pusat kubus, melainkan di titik hasil translate. Cubie terlihat "terbang" ke posisi aneh alih-alih berputar mengitari sumbu kubus.

#### 2b. Solusi: Pivot Element

Perbaikan menggunakan **pivot element** — sebuah `div` kosong yang diposisikan tepat di tengah `cube-inner` (via `left:50% top:50% width:0 height:0`). Cubie dipindahkan ke dalam pivot, pivot yang dirotasi, lalu cubie dikembalikan ke `cube-inner` setelah animasi selesai.

```js
function animateSlots(slots, cssAxis, angleDeg, durationMs, onDone) {
  // Buat pivot div di tengah cube-inner
  const pivot = document.createElement("div");
  pivot.className = "layer-pivot"; // position:absolute; left:50%; top:50%; width:0; height:0;
  cubeInnerEl.appendChild(pivot);

  // Pindahkan cubie ke pivot (transform tetap, tapi parent berubah)
  const cubies = slots.map(s => cubieEls[s]);
  cubies.forEach(el => {
    el.style.transform = el.dataset.base;
    pivot.appendChild(el);
  });

  void pivot.offsetWidth; // paksa reflow

  requestAnimationFrame(() => {
    // Rotasi pivot = semua cubie berputar mengelilingi PUSAT KUBUS
    pivot.style.transition = `transform ${durationMs}ms cubic-bezier(.4,0,.2,1)`;
    pivot.style.transform = `rotate${cssAxis}(${angleDeg}deg)`;
  });

  setTimeout(() => {
    cubies.forEach(el => {
      el.style.transform = el.dataset.base; // snap ke posisi base baru
      cubeInnerEl.appendChild(el);
    });
    pivot.remove();
    onDone(); // warna update ke state berikutnya
  }, durationMs + 60);
}
```

---

#### 2c. Mapping Axis Reorientasi yang Benar

**Kode lama (salah):**
```js
const axis = t.axis === "x" ? "X" : "Y";
animateSlots([0,1,2,3,4,5,6,7], axis, forward ? 90 : -90, 420, onDone);
// Semua reorientasi selalu pakai +90, padahal _rot_y Python = -90 di CSS
```

**Analisa Python vs CSS:**

| Token Python | Fungsi Python | Efek Geometri | CSS yang Benar |
|---|---|---|---|
| `x` | `_rot_x(x,y,z) = (x,-z,y)` | Rotasi sumbu X positif 90° | `rotateX(+90deg)` |
| `y` | `_rot_y(x,y,z) = (z,y,-x)` | Rotasi sumbu Y **negatif** 90° | `rotateY(-90deg)` |

**Solusi:**
```js
const REORIENT_AXIS_ANGLE = {
  x: { axis: "X", angle:  90 },  // _rot_x Python = rotateX(+90) CSS
  y: { axis: "Y", angle: -90 },  // _rot_y Python = rotateY(-90) CSS
};

// Di animateTransition():
const info = REORIENT_AXIS_ANGLE[t.axis];
const angle = forward ? info.angle : -info.angle;
animateSlots([0,1,2,3,4,5,6,7], info.axis, angle, 420, onDone);
```

---

#### 2d. Arah Sudut Gerakan Lapisan (U, R, F)

`BASE_ANGLE` tetap `{ U: -90, R: -90, F: -90 }` karena ketiga axis rotasinya berbeda (Y, X, Z), sehingga `-90` pada masing-masing axis menghasilkan arah visual yang benar:

| Gerakan | Axis CSS | Sudut | Verifikasi |
|---|---|---|---|
| U (CW dari atas) | `rotateY` | `-90°` | Corner URF→UBR→ULB→UFL = CW dari atas ✓ |
| R (CW dari kanan) | `rotateX` | `-90°` | Corner URF→DFR→DRB→UBR = CW dari kanan ✓ |
| F (CW dari depan) | `rotateZ` | `-90°` | Corner URF→UFL→DLF→DFR = CW dari depan ✓ |

Gerakan `X'` = `+BASE_ANGLE`, gerakan `X2` = `180°` — logika ini sudah benar di kode sebelumnya.

---

## Ringkasan Perubahan per Fungsi

| Fungsi / Bagian | Perubahan |
|---|---|
| `copySelections()` | **Baru** — deep copy `selections` untuk `frames[0]` |
| `cornerColorsFromStateObj()` | Tambah `[...arr]` agar array disalin, bukan shared reference |
| Payload `fetch /api/solve` | Konversi key ke `String(s)` secara eksplisit |
| `animateSlots()` | **Tulis ulang** — pakai pivot element agar rotasi di pusat kubus |
| `animateTransition()` | Pakai `REORIENT_AXIS_ANGLE` map dengan sudut yang benar per token |
| `REORIENT_AXIS_ANGLE` | **Konstanta baru** — mapping token `x`/`y` ke axis dan sudut CSS yang tepat |
| `buildFrames()` | Gunakan `copySelections()` untuk frame 0 |
| `.layer-pivot` CSS | **Baru** — style untuk pivot element animasi |

---

## Cara Verifikasi

1. Jalankan server: `python app.py`
2. Buka `http://127.0.0.1:5000`
3. Klik **"Isi Contoh Acak"** — warna muncul sesuai
4. Klik **"Selesaikan"** — warna di kubus 3D harus **persis sama** dengan yang baru diinput
5. Klik **"Berikutnya"** berulang kali — tiap gerakan harus terlihat **kubus berputar jelas pada lapisan yang tepat**, dan setelah animasi warna langsung update ke posisi benar
6. Klik **"Sebelumnya"** — animasi mundur harus benar pula
