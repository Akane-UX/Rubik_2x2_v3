// Rotasi sudut pandang kubus dengan drag kursor dan tombol panah
const viewportEl = document.getElementById("viewport");
const cubeNavEl = document.getElementById("cube-nav");
const camera = { x: DEFAULT_VIEW.x, y: DEFAULT_VIEW.y };
const DRAG_SPEED = 0.65;
const DRAG_THRESHOLD = 5;

function normDeg(d) {
  return Math.round(((d % 360) + 540) % 360 - 180);
}

function applyCamera() {
  cubeNavEl.style.transform = `rotateX(${camera.x}deg) rotateY(${camera.y}deg)`;
  const readout = document.getElementById("angle-readout");
  if (readout) readout.textContent = `X: ${normDeg(camera.x)}° · Y: ${normDeg(camera.y)}°`;
}

function initCamera() {
  let down = false, sx = 0, sy = 0, startX = 0, startY = 0;

  viewportEl.addEventListener("pointerdown", e => {
    if (e.button !== 0) return;
    down = true;
    state.wasDragged = false;
    sx = e.clientX;
    sy = e.clientY;
    startX = camera.x;
    startY = camera.y;
  });

  window.addEventListener("pointermove", e => {
    if (!down) return;
    const dx = e.clientX - sx, dy = e.clientY - sy;
    if (!state.wasDragged && Math.hypot(dx, dy) > DRAG_THRESHOLD) {
      state.wasDragged = true;
      viewportEl.classList.add("dragging");
      cubeNavEl.classList.add("dragging");
    }
    if (!state.wasDragged) return;
    const flip = Math.cos(startX * Math.PI / 180) >= 0 ? 1 : -1;
    camera.y = startY + dx * DRAG_SPEED * flip;
    camera.x = startX - dy * DRAG_SPEED;
    applyCamera();
  });

  window.addEventListener("pointerup", () => {
    if (!down) return;
    down = false;
    viewportEl.classList.remove("dragging");
    cubeNavEl.classList.remove("dragging");
    setTimeout(() => { state.wasDragged = false; }, 10);
  });

  const nudge = (dx, dy) => () => { camera.x += dx; camera.y += dy; applyCamera(); };
  document.getElementById("nav-left").addEventListener("click", nudge(0, -45));
  document.getElementById("nav-right").addEventListener("click", nudge(0, 45));
  document.getElementById("nav-up").addEventListener("click", nudge(45, 0));
  document.getElementById("nav-down").addEventListener("click", nudge(-45, 0));
  document.getElementById("nav-reset").addEventListener("click", () => {
    camera.x = DEFAULT_VIEW.x;
    camera.y = DEFAULT_VIEW.y;
    applyCamera();
  });

  applyCamera();
}
