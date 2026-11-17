// Komunikasi dengan backend Flask (app.py)
async function fetchExample() {
  const res = await fetch(`${API_BASE}/api/example`);
  if (!res.ok) throw new Error("Server error");
  return res.json();
}

async function requestSolve(selections) {
  const corners = {};
  for (let s = 0; s < 8; s++) corners[String(s)] = selections[s];
  const res = await fetch(`${API_BASE}/api/solve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ corners }),
  });
  return { ok: res.ok, data: await res.json() };
}
