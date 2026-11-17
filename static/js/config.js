// Geometri kubus, warna, dan arah putaran (harus sama dengan backend Python)
const CORNER_NAMES = ["URF", "UFL", "ULB", "UBR", "DFR", "DLF", "DBL", "DRB"];
const CORNER_COORD = {
  0: [1, 1, 1], 1: [-1, 1, 1], 2: [-1, 1, -1], 3: [1, 1, -1],
  4: [1, -1, 1], 5: [-1, -1, 1], 6: [-1, -1, -1], 7: [1, -1, -1],
};
const CORNER_FACES = {
  0: ["U", "R", "F"], 1: ["U", "F", "L"], 2: ["U", "L", "B"], 3: ["U", "B", "R"],
  4: ["D", "F", "R"], 5: ["D", "L", "F"], 6: ["D", "B", "L"], 7: ["D", "R", "B"],
};

const COLORS = ["White", "Yellow", "Green", "Blue", "Orange", "Red"];
const MAX_PER_COLOR = 4;
const COLOR_HEX = {
  White: "#E8E8E3", Yellow: "#EAB308", Green: "#16A34A",
  Blue: "#2563EB", Orange: "#EA580C", Red: "#DC2626",
};
const COLOR_LABEL_ID = {
  White: "Putih", Yellow: "Kuning", Green: "Hijau",
  Blue: "Biru", Orange: "Oranye", Red: "Merah",
};

const CUBIE = 82, OFFSET = 43, H = CUBIE / 2;
const FACE_LOCAL_TRANSFORM = {
  F: `translateZ(${H}px)`,
  B: `rotateY(180deg) translateZ(${H}px)`,
  R: `rotateY(90deg) translateZ(${H}px)`,
  L: `rotateY(-90deg) translateZ(${H}px)`,
  U: `rotateX(90deg) translateZ(${H}px)`,
  D: `rotateX(-90deg) translateZ(${H}px)`,
};

const FACE_LABEL_ID = { U: "ATAS (U)", R: "KANAN (R)", F: "DEPAN (F)" };
const LAYER_SLOTS = { U: [0, 1, 2, 3], R: [0, 3, 4, 7], F: [0, 1, 4, 5] };
const LAYER_AXIS = { U: "Y", R: "X", F: "Z" };
const BASE_ANGLE = { U: -90, R: 90, F: 90 };
const REORIENT_AXIS_ANGLE = {
  x: { axis: "X", angle: -90 },
  y: { axis: "Y", angle: 90 },
};

const TURN_MS = 400;
const DEFAULT_VIEW = { x: -24, y: -35 };

const API_BASE = (window.location.protocol === "file:" || (window.location.port && window.location.port !== "5000"))
  ? "http://127.0.0.1:5000"
  : "";
