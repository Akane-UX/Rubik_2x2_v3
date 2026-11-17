// Palet warna dengan indeks sisa kuota (4 -> 0)
const paletteEl = document.getElementById("palette");
const colorBtnEls = {};

function buildPalette() {
  COLORS.forEach(color => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "color-card";
    btn.innerHTML = `
      <div class="color-info">
        <span class="swatch" style="background:${COLOR_HEX[color]}"></span>
        <span class="color-name">${COLOR_LABEL_ID[color]}</span>
      </div>
      <div class="quota-wrap">
        <span class="quota-count">${MAX_PER_COLOR}</span>
        <div class="quota-pips">${'<span class="pip filled"></span>'.repeat(MAX_PER_COLOR)}</div>
      </div>`;
    btn.addEventListener("click", () => {
      if (getUsedCounts()[color] >= MAX_PER_COLOR && state.currentColor !== color) return;
      state.currentColor = color;
      updatePaletteUI();
    });
    paletteEl.appendChild(btn);
    colorBtnEls[color] = btn;
  });
}

function updatePaletteUI() {
  const used = getUsedCounts();
  let filled = 0;

  COLORS.forEach(c => {
    const rem = Math.max(0, MAX_PER_COLOR - used[c]);
    filled += used[c];
    const btn = colorBtnEls[c];
    btn.classList.toggle("active", c === state.currentColor);
    btn.classList.toggle("depleted", rem === 0);
    btn.querySelector(".quota-count").textContent = rem;
    btn.querySelectorAll(".pip").forEach((pip, i) => pip.classList.toggle("filled", i < rem));
  });

  document.getElementById("progress-text").textContent = `${filled} / 24 terisi`;
  document.getElementById("progress-fill").style.width = `${(filled / 24) * 100}%`;

  if (state.mode === "input") {
    setStatus(filled === 24 ? "ready" : "",
      filled === 24 ? "24/24 stiker lengkap · Siap diselesaikan" : `Mode Input · Sisa ${24 - filled} stiker`);
  }
}

function setStatus(kind, text) {
  const dot = document.getElementById("status-dot");
  const label = document.getElementById("status-text");
  if (dot) dot.className = "status-dot" + (kind ? ` ${kind}` : "");
  if (label) label.textContent = text;
}

function setPaletteEnabled(enabled) {
  paletteEl.classList.toggle("disabled", !enabled);
}
