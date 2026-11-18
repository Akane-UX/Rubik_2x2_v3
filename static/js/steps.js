// Navigasi langkah solusi: susun frame, label instruksi, dan animasi maju/mundur
function buildFrames(data) {
  const reorient = data.needs_reorientation ? data.reorientation_steps : [];
  state.frames = [copyCorners(state.selections)];
  state.transitions = [];
  state.reorientCount = reorient.length;

  reorient.forEach(step => {
    state.transitions.push({ kind: "reorient", axis: step.axis });
    state.frames.push(copyCorners(step.state));
  });
  data.moves.forEach((move, i) => {
    state.transitions.push({ kind: "move", move });
    state.frames.push(copyCorners(data.states[i + 1]));
  });
  state.frameIdx = 0;
}

function describeMove(move) {
  const face = FACE_LABEL_ID[move[0]], suffix = move.slice(1);
  if (suffix === "2") return `Putar sisi ${face} 180°.`;
  if (suffix === "'") return `Putar sisi ${face} 90° berlawanan jarum jam.`;
  return `Putar sisi ${face} 90° searah jarum jam.`;
}

function labelFor(idx) {
  const t = state.transitions[idx];
  if (!t) return "Selesai. Kubus telah berada pada kondisi terpecahkan.";
  if (t.kind === "reorient") {
    return `Reorientasi: putar seluruh bodi kubus pada sumbu ${t.axis.toUpperCase()} agar sejajar patokan.`;
  }
  return `Langkah ${idx + 1}: ${describeMove(t.move)}`;
}

function updateStepChrome() {
  const idx = state.frameIdx;
  document.getElementById("step-label").textContent = labelFor(idx);
  document.getElementById("step-indicator").textContent = `${idx} / ${state.transitions.length}`;
  document.getElementById("step-prev").disabled = idx === 0 || state.animating;
  document.getElementById("step-next").disabled = idx === state.frames.length - 1 || state.animating;

  const active = idx - state.reorientCount;
  document.querySelectorAll("#result-box .tok").forEach((el, i) => {
    el.classList.toggle("done", i < active);
    el.classList.toggle("active", i === active);
  });
}

function goToFrame(target) {
  if (state.animating || target < 0 || target >= state.frames.length) return;
  const forward = target > state.frameIdx;
  const t = state.transitions[forward ? state.frameIdx : target];
  state.animating = true;
  updateStepChrome();

  animateTransition(t, forward, () => {
    state.frameIdx = target;
    renderCube(state.frames[target]);
    state.animating = false;
    updateStepChrome();
  });
}

function showSteps(visible) {
  document.getElementById("step-controls").classList.toggle("hidden", !visible);
}

function initSteps() {
  document.getElementById("step-next").addEventListener("click", () => goToFrame(state.frameIdx + 1));
  document.getElementById("step-prev").addEventListener("click", () => goToFrame(state.frameIdx - 1));
}
