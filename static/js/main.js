// Penghubung antar modul: tombol aksi, mode input/pratinjau, dan inisialisasi
function showNotice(kind, html) {
  const box = document.getElementById("result-box");
  box.className = "notice" + (kind ? ` ${kind}` : "");
  box.innerHTML = html;
}

function enterInputMode() {
  state.renderGen++;
  state.animating = false;
  state.mode = "input";
  resetCubieTransforms();
  setCubeReadonly(false);
  setPaletteEnabled(true);
  showSteps(false);
  document.getElementById("mode-meta").textContent = "Input";
  document.getElementById("move-count-meta").textContent = "-";
  updatePaletteUI();
}

function enterPreviewMode(data) {
  state.mode = "preview";
  setCubeReadonly(true);
  setPaletteEnabled(false);
  setStatus("solved", `Solusi ditemukan · ${data.moves.length} langkah`);
  document.getElementById("mode-meta").textContent = "Pratinjau Solusi";
  document.getElementById("move-count-meta").textContent = `${data.moves.length} gerakan`;
  showNotice("success", `<div class="moves-list">${data.moves.map(m => `<span class="tok">${m}</span>`).join("")}</div>`);

  buildFrames(data);
  renderCube(state.frames[0]);
  showSteps(true);
  updateStepChrome();
}

function onReset() {
  clearSelections();
  state.currentColor = COLORS[0];
  renderCube(state.selections);
  enterInputMode();
  showNotice("", "Semua stiker direset. Pilih warna pada indeks untuk mulai mengisi.");
}

async function onExample() {
  let data;
  try {
    data = await fetchExample();
  } catch (err) {
    console.error("fetchExample failed:", err);
    showNotice("error", "Tidak dapat terhubung ke server backend <code>app.py</code>.");
    return;
  }
  for (let s = 0; s < 8; s++) state.selections[s] = [...data.corners[String(s)]];
  renderCube(state.selections);
  enterInputMode();
  showNotice("", `Contoh acak dimuat (<span class="mono">${data.scramble_used}</span>). Klik <strong>Selesaikan</strong> untuk mencari solusi.`);
}

async function onSolve() {
  if (Object.values(state.selections).some(s => s.includes(null))) {
    showNotice("error", "Lengkapi ke-24 stiker terlebih dahulu hingga seluruh indeks warna bernilai 0.");
    return;
  }

  const btn = document.getElementById("btn-solve");
  btn.disabled = true;
  btn.textContent = "Memproses...";

  try {
    let ok, data;
    try {
      ({ ok, data } = await requestSolve(state.selections));
    } catch (err) {
      console.error("requestSolve failed:", err);
      showNotice("error", "Gagal menghubungi backend. Pastikan <code>app.py</code> aktif di port 5000.");
      return;
    }

    if (!ok) {
      showNotice("error", data.error || "Konfigurasi warna tidak valid.");
    } else if (data.already_solved) {
      setStatus("solved", "Kubus sudah selesai");
      showNotice("success", "Kubus sudah dalam posisi terpecahkan — tidak diperlukan langkah tambahan.");
      showSteps(false);
    } else {
      enterPreviewMode(data);
    }
  } finally {
    btn.disabled = false;
    btn.textContent = "Selesaikan";
  }
}

document.getElementById("btn-reset").addEventListener("click", onReset);
document.getElementById("btn-example").addEventListener("click", onExample);
document.getElementById("btn-solve").addEventListener("click", onSolve);

buildPalette();
buildCube();
initCamera();
initSteps();
renderCube(state.selections);
updatePaletteUI();
