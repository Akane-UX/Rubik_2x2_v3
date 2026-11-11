"""Konversi input warna pengguna ke CubeState kanonik dan orkestrasi pipeline solusi."""

from typing import Dict, List, Optional, Tuple

from cube_model import (
    CORNER_FACES,
    CORNER_NAMES,
    CubeState,
    DEFAULT_FACE_COLORS,
    is_valid_state,
)
from movements import apply_move
from solver import is_encodable, solve as bfs_solve

# Pemetaan muka berlawanan
OPPOSITE_FACE = {"U": "D", "D": "U", "F": "B", "B": "F", "L": "R", "R": "L"}


class ColorMappingError(ValueError):
    """Pengecualian validasi input warna pengguna."""


def _face_of_color(color_scheme: Dict[str, str], color: str) -> str:
    """Ambil nama muka dari warna tertentu."""
    for face, c in color_scheme.items():
        if c == color:
            return face
    raise ColorMappingError(f"Warna '{color}' tidak dikenal di skema warna.")


def _opposite_color(color_scheme: Dict[str, str], color: str) -> str:
    """Ambil warna dari muka yang berseberangan."""
    return color_scheme[OPPOSITE_FACE[_face_of_color(color_scheme, color)]]


def _rotate3(tup: Tuple, o: int) -> Tuple:
    """Rotasi siklik tuple 3 elemen: hasil[i] = tup[(i+o) % 3]."""
    return tuple(tup[(i + o) % 3] for i in range(3))


def validate_raw_input(
    corners: Dict[int, Tuple[str, str, str]],
    color_scheme: Dict[str, str] = DEFAULT_FACE_COLORS,
) -> None:
    """Validasi integritas fisik input 8 corner, kuota 4 stiker per warna, dan kombinasi muka."""
    if set(corners.keys()) != set(range(8)):
        raise ColorMappingError(
            f"Input harus punya tepat 8 corner (slot 0-7). Ditemukan slot: "
            f"{sorted(corners.keys())}"
        )

    valid_colors = set(color_scheme.values())
    color_counter = {c: 0 for c in valid_colors}
    canonical_sets = {
        i: frozenset(color_scheme[f] for f in CORNER_FACES[i]) for i in range(8)
    }
    seen_corner_sets: Dict[frozenset, int] = {}

    for slot, colors in corners.items():
        name = CORNER_NAMES[slot]
        if len(colors) != 3:
            raise ColorMappingError(f"Corner {name} (slot {slot}) harus punya 3 warna.")

        for c in colors:
            if c not in valid_colors:
                raise ColorMappingError(
                    f"Corner {name}: warna '{c}' tidak dikenal. Pilihan: "
                    f"{sorted(valid_colors)}"
                )
            color_counter[c] += 1

        if len(set(colors)) != 3:
            raise ColorMappingError(
                f"Corner {name}: warnanya tidak boleh ada yang sama "
                f"({colors}) -- satu piece kubus punya 3 warna berbeda."
            )

        for c in colors:
            opp = _opposite_color(color_scheme, c)
            if opp in colors:
                raise ColorMappingError(
                    f"Corner {name}: tidak mungkin punya warna '{c}' dan "
                    f"'{opp}' sekaligus -- keduanya muka berseberangan pada "
                    f"kubus, tidak pernah bertemu di satu corner."
                )

        color_set = frozenset(colors)
        if color_set not in canonical_sets.values():
            raise ColorMappingError(
                f"Corner {name}: kombinasi warna {colors} bukan salah satu "
                f"dari 8 kombinasi corner yang mungkin ada di kubus manapun."
            )
        if color_set in seen_corner_sets:
            other = seen_corner_sets[color_set]
            raise ColorMappingError(
                f"Corner {name} dan corner {CORNER_NAMES[other]} punya "
                f"kombinasi warna yang sama ({colors}) -- tidak mungkin dua "
                f"piece fisik identik."
            )
        seen_corner_sets[color_set] = slot

    for c, n in color_counter.items():
        if n != 4:
            raise ColorMappingError(
                f"Warna '{c}' muncul {n} kali di input, seharusnya tepat 4 "
                f"kali (4 stiker per muka)."
            )


def _canonical_orders(color_scheme: Dict[str, str]) -> Dict[int, Tuple[str, str, str]]:
    """Daftar urutan kanonik warna stiker tiap corner."""
    return {i: tuple(color_scheme[f] for f in CORNER_FACES[i]) for i in range(8)}


def _identify_corner(
    colors: Tuple[str, str, str],
    canonical_orders: Dict[int, Tuple[str, str, str]],
) -> Tuple[int, int]:
    """Identifikasi corner ID asli dan orientasi dari kombinasi 3 warna stiker."""
    obs = tuple(colors)
    obs_set = frozenset(obs)
    for cid, canon in canonical_orders.items():
        if frozenset(canon) != obs_set:
            continue
        for o in range(3):
            if _rotate3(canon, o) == obs:
                return cid, (3 - o) % 3
    raise ColorMappingError(f"Tidak ada corner kanonik yang cocok dengan warna {colors}.")


def raw_state_from_colors(
    corners: Dict[int, Tuple[str, str, str]],
    color_scheme: Dict[str, str] = DEFAULT_FACE_COLORS,
) -> CubeState:
    """Validasi input dan ubah ke CubeState mentah."""
    validate_raw_input(corners, color_scheme)
    canon = _canonical_orders(color_scheme)

    perm: List[Optional[int]] = [None] * 8
    orient: List[Optional[int]] = [None] * 8
    for slot, colors in corners.items():
        cid, o = _identify_corner(colors, canon)
        perm[slot] = cid
        orient[slot] = o

    perm_t, orient_t = tuple(perm), tuple(orient)
    if not is_valid_state(perm_t, orient_t):
        raise ColorMappingError(
            "Kombinasi hasil scan tidak mungkin dicapai secara fisik (total "
            "twist tidak habis dibagi 3). Kemungkinan ada 1 corner yang "
            "urutan warnanya salah arah saat diinput -- coba scan ulang."
        )
    return CubeState(perm_t, orient_t)


# Koordinat geometris 3D tiap slot corner
CORNER_COORD = {
    0: (1, 1, 1), 1: (-1, 1, 1), 2: (-1, 1, -1), 3: (1, 1, -1),
    4: (1, -1, 1), 5: (-1, -1, 1), 6: (-1, -1, -1), 7: (1, -1, -1),
}
COORD_TO_SLOT = {v: k for k, v in CORNER_COORD.items()}

FACE_TO_AXIS_DIR = {
    "U": (0, 1, 0), "D": (0, -1, 0),
    "F": (0, 0, 1), "B": (0, 0, -1),
    "R": (1, 0, 0), "L": (-1, 0, 0),
}

CANONICAL_DIRS = {i: tuple(FACE_TO_AXIS_DIR[f] for f in CORNER_FACES[i]) for i in range(8)}


def _rot_x(v):
    """Rotasi 90 derajat koordinat pada sumbu X."""
    x, y, z = v
    return (x, -z, y)


def _rot_y(v):
    """Rotasi 90 derajat koordinat pada sumbu Y."""
    x, y, z = v
    return (z, y, -x)


def _generate_rotations():
    """Bangun seluruh 24 rotasi ruang kubus kaku (rigid body) beserta jalur token animasi."""
    def compose(f, g):
        return lambda v: f(g(v))

    basis = ((1, 0, 0), (0, 1, 0), (0, 0, 1))

    def sig(f):
        return tuple(f(b) for b in basis)

    identity = lambda v: v
    seen = {sig(identity): identity}
    rotations = [identity]
    paths = [[]]
    frontier = [(identity, [])]
    generators = [("x", _rot_x), ("y", _rot_y)]
    while frontier:
        nxt = []
        for f, path in frontier:
            for token, g in generators:
                h = compose(g, f)
                s = sig(h)
                if s not in seen:
                    seen[s] = h
                    rotations.append(h)
                    paths.append(path + [token])
                    nxt.append((h, path + [token]))
        frontier = nxt
    return rotations, paths


ROTATIONS, ROTATION_PATHS = _generate_rotations()
ROTATION_GENERATOR = {"x": _rot_x, "y": _rot_y}


def apply_rotation(state: CubeState, rot_fn) -> CubeState:
    """Terapkan satu rotasi bodi kubus utuh pada state."""
    new_perm: List[Optional[int]] = [None] * 8
    new_orient: List[Optional[int]] = [None] * 8

    for old_slot in range(8):
        new_slot = COORD_TO_SLOT[rot_fn(CORNER_COORD[old_slot])]

        old_dirs_observed = _rotate3(CANONICAL_DIRS[old_slot], state.orient[old_slot])
        new_dirs_observed = tuple(rot_fn(d) for d in old_dirs_observed)

        target_canon = CANONICAL_DIRS[new_slot]
        o = next(
            cand for cand in range(3)
            if _rotate3(target_canon, cand) == new_dirs_observed
        )

        new_perm[new_slot] = state.perm[old_slot]
        new_orient[new_slot] = o

    return CubeState(tuple(new_perm), tuple(new_orient))


def canonicalize(raw_state: CubeState):
    """Cari rotasi kubus yang menempatkan corner 6 ke slot 6 orientasi 0."""
    original_slot = raw_state.perm.index(6)
    original_orient = raw_state.orient[original_slot]

    for rot, path in zip(ROTATIONS, ROTATION_PATHS):
        candidate = apply_rotation(raw_state, rot)
        if is_encodable(candidate):
            return candidate, original_slot, original_orient, path

    raise RuntimeError("Tidak ditemukan rotasi kanonik yang valid.")


def state_to_colors(
    state: CubeState, color_scheme: Dict[str, str] = DEFAULT_FACE_COLORS
) -> Dict[int, Tuple[str, str, str]]:
    """Konversi CubeState kembali menjadi pemetaan warna per slot."""
    canon = _canonical_orders(color_scheme)
    return {slot: _rotate3(canon[state.perm[slot]], (3 - state.orient[slot]) % 3) for slot in range(8)}


def _states_to_json_colors(states: List[CubeState], color_scheme) -> List[Dict[str, List[str]]]:
    """Konversi daftar CubeState ke serialisasi dictionary warna untuk response JSON."""
    out = []
    for st in states:
        colors = state_to_colors(st, color_scheme)
        out.append({str(slot): list(c) for slot, c in colors.items()})
    return out


def colors_to_solution(
    corners: Dict[int, Tuple[str, str, str]],
    color_scheme: Dict[str, str] = DEFAULT_FACE_COLORS,
) -> Dict[str, object]:
    """Pipeline terpadu: validasi, normalisasi kanonik, pencarian solusi BFS, dan pembuatan frame animasi."""
    raw_state = raw_state_from_colors(corners, color_scheme)

    if raw_state.is_solved():
        return {
            "moves": [],
            "moves_str": "(sudah solved)",
            "needs_reorientation": False,
            "reorientation_steps": [],
            "already_solved": True,
            "states": _states_to_json_colors([raw_state], color_scheme),
        }

    canonical_state, orig_slot, orig_orient, rotation_path = canonicalize(raw_state)
    moves = bfs_solve(canonical_state)

    # Langkah reorientasi seluruh kubus jika diperlukan
    reorientation_steps = []
    cur_raw = raw_state
    for token in rotation_path:
        cur_raw = apply_rotation(cur_raw, ROTATION_GENERATOR[token])
        reorientation_steps.append({
            "axis": token,
            "state": {str(s): list(c) for s, c in state_to_colors(cur_raw, color_scheme).items()},
        })
    needs_reorientation = len(rotation_path) > 0

    # Rangkaian state pergerakan layer solusi (U, R, F)
    states = [canonical_state]
    cur = canonical_state
    for m in moves:
        cur = apply_move(cur, m)
        states.append(cur)

    return {
        "moves": moves,
        "moves_str": " ".join(moves),
        "needs_reorientation": needs_reorientation,
        "reorientation_steps": reorientation_steps,
        "already_solved": False,
        "states": _states_to_json_colors(states, color_scheme),
    }


if __name__ == "__main__":
    import random
    from cube_model import SOLVED_STATE
    from movements import apply_moves

    scramble = "R U2 F' R' U F2 R U'"
    print(f"(Demo) Scramble: {scramble}")
    scrambled = apply_moves(SOLVED_STATE, scramble)

    random.seed(42)
    held = apply_rotation(scrambled, random.choice(ROTATIONS))
    colors = state_to_colors(held)
    result = colors_to_solution(colors)
    print("Solusi:", result["moves_str"])

