// Pembuatan kubus 3D, pewarnaan stiker, dan animasi putaran lapisan
const cubeInnerEl = document.getElementById("cube-inner");
const cubieEls = {};
const plateEls = {};

function buildCube() {
  for (let slot = 0; slot < 8; slot++) {
    const [x, y, z] = CORNER_COORD[slot];
    const cubie = document.createElement("div");
    cubie.className = "cubie";
    cubie.dataset.base = `translate3d(${x * OFFSET}px, ${-y * OFFSET}px, ${z * OFFSET}px)`;
    cubie.style.transform = cubie.dataset.base;

    plateEls[slot] = {};
    CORNER_FACES[slot].forEach((face, faceIdx) => {
      const plate = document.createElement("button");
      plate.type = "button";
      plate.className = "cubie-face";
      plate.style.transform = FACE_LOCAL_TRANSFORM[face];
      plate.dataset.slot = slot;
      plate.dataset.faceIdx = faceIdx;
      plate.title = `${CORNER_NAMES[slot]} · ${face}`;
      plate.addEventListener("click", onPlateClick);
      plate.addEventListener("contextmenu", onPlateClear);
      cubie.appendChild(plate);
      plateEls[slot][face] = plate;
    });

    ["U", "D", "F", "B", "L", "R"].filter(f => !CORNER_FACES[slot].includes(f)).forEach(face => {
      const core = document.createElement("div");
      core.className = "cubie-core";
      core.style.transform = FACE_LOCAL_TRANSFORM[face];
      cubie.appendChild(core);
    });

    cubeInnerEl.appendChild(cubie);
    cubieEls[slot] = cubie;
  }
}

function renderCube(corners) {
  for (let slot = 0; slot < 8; slot++) {
    CORNER_FACES[slot].forEach((face, idx) => {
      const color = corners[slot] ? corners[slot][idx] : null;
      plateEls[slot][face].style.backgroundColor = color ? COLOR_HEX[color] : "var(--sticker-empty)";
    });
  }
}

function setCubeReadonly(readonly) {
  document.querySelectorAll(".cubie-face").forEach(p => p.classList.toggle("readonly", readonly));
}

// Klik kiri: warnai / hapus jika warnanya sama; kuota warna aktif ikut berkurang
function onPlateClick(e) {
  if (state.mode !== "input" || state.wasDragged) return;
  const slot = Number(e.currentTarget.dataset.slot);
  const faceIdx = Number(e.currentTarget.dataset.faceIdx);
  const prev = state.selections[slot][faceIdx];

  if (prev === state.currentColor) {
    state.selections[slot][faceIdx] = null;
  } else {
    if (getUsedCounts()[state.currentColor] >= MAX_PER_COLOR) {
      const next = firstAvailableColor(getUsedCounts());
      if (!next) return;
      state.currentColor = next;
    }
    state.selections[slot][faceIdx] = state.currentColor;
  }

  const used = getUsedCounts();
  if (used[state.currentColor] >= MAX_PER_COLOR) {
    state.currentColor = firstAvailableColor(used) ?? state.currentColor;
  }

  renderCube(state.selections);
  updatePaletteUI();
}

// Klik kanan: kosongkan stiker dan kembalikan kuotanya
function onPlateClear(e) {
  e.preventDefault();
  if (state.mode !== "input" || state.wasDragged) return;
  const slot = Number(e.currentTarget.dataset.slot);
  const faceIdx = Number(e.currentTarget.dataset.faceIdx);
  const prev = state.selections[slot][faceIdx];
  if (prev === null) return;
  state.currentColor = prev;
  state.selections[slot][faceIdx] = null;
  renderCube(state.selections);
  updatePaletteUI();
}

// Putar cubie langsung di tempat (tanpa pindah DOM) agar tidak berkedip
function animateSlots(slots, axis, angle, onDone) {
  const gen = state.renderGen;
  const els = slots.map(s => cubieEls[s]);
  let finished = false;

  const finish = () => {
    if (finished) return;
    finished = true;
    els.forEach(el => {
      el.style.transition = "none";
      el.style.transform = el.dataset.base;
    });
    if (gen === state.renderGen) onDone();
  };

  els.forEach(el => {
    el.style.transition = "none";
    el.style.transform = `rotate${axis}(0deg) ${el.dataset.base}`;
  });
  void cubeInnerEl.offsetWidth;

  els.forEach(el => {
    el.style.transition = `transform ${TURN_MS}ms var(--turn)`;
    el.style.transform = `rotate${axis}(${angle}deg) ${el.dataset.base}`;
  });

  els[0].addEventListener("transitionend", finish, { once: true });
  setTimeout(finish, TURN_MS + 80);
}

function moveAngle(move) {
  const face = move[0], suffix = move.slice(1);
  if (suffix === "2") return 180;
  return suffix === "'" ? -BASE_ANGLE[face] : BASE_ANGLE[face];
}

function animateTransition(t, forward, onDone) {
  const dir = forward ? 1 : -1;
  if (t.kind === "reorient") {
    const info = REORIENT_AXIS_ANGLE[t.axis];
    animateSlots([0, 1, 2, 3, 4, 5, 6, 7], info.axis, info.angle * dir, onDone);
  } else {
    const face = t.move[0];
    animateSlots(LAYER_SLOTS[face], LAYER_AXIS[face], moveAngle(t.move) * dir, onDone);
  }
}

function resetCubieTransforms() {
  Object.values(cubieEls).forEach(el => {
    el.style.transition = "none";
    el.style.transform = el.dataset.base;
  });
}
