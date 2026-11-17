// State global aplikasi yang dipakai bersama oleh semua modul
const state = {
  currentColor: COLORS[0],
  selections: {},
  mode: "input",
  frames: [],
  transitions: [],
  reorientCount: 0,
  frameIdx: 0,
  animating: false,
  renderGen: 0,
  wasDragged: false,
};

function clearSelections() {
  for (let s = 0; s < 8; s++) state.selections[s] = [null, null, null];
}

function copyCorners(src) {
  const out = {};
  for (let s = 0; s < 8; s++) {
    const arr = src[s] ?? src[String(s)];
    out[s] = arr ? [...arr] : [null, null, null];
  }
  return out;
}

function getUsedCounts() {
  const used = Object.fromEntries(COLORS.map(c => [c, 0]));
  Object.values(state.selections).forEach(arr => {
    arr.forEach(c => { if (c && c in used) used[c]++; });
  });
  return used;
}

function firstAvailableColor(used) {
  return COLORS.find(c => used[c] < MAX_PER_COLOR);
}

clearSelections();
