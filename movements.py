"""Logika gerakan layer kubus 2x2x2 (U, R, F) dan manipulasi urutan gerakan."""

from typing import Dict, List, Sequence, Union

from cube_model import CubeState

# Indeks slot corner sebagai alias konstan
URF, UFL, ULB, UBR, DFR, DLF, DBL, DRB = range(8)

# Tabel transisi 3 putaran dasar 90 derajat searah jarum jam
_BASE_TURNS: Dict[str, CubeState] = {
    "U": CubeState(
        perm=(UBR, URF, UFL, ULB, DFR, DLF, DBL, DRB),
        orient=(0, 0, 0, 0, 0, 0, 0, 0),
    ),
    "R": CubeState(
        perm=(DFR, UFL, ULB, URF, DRB, DLF, DBL, UBR),
        orient=(2, 0, 0, 1, 1, 0, 0, 2),
    ),
    "F": CubeState(
        perm=(UFL, DLF, ULB, UBR, URF, DFR, DBL, DRB),
        orient=(1, 2, 0, 0, 2, 1, 0, 0),
    ),
}


def _apply_table(state: CubeState, table: CubeState) -> CubeState:
    """Terapkan satu tabel mutasi gerakan pada state kubus."""
    perm = tuple(state.perm[table.perm[i]] for i in range(8))
    orient = tuple(
        (state.orient[table.perm[i]] + table.orient[i]) % 3 for i in range(8)
    )
    return CubeState(perm, orient)


def _build_moves() -> Dict[str, CubeState]:
    """Bangun tabel 9 variasi gerakan dari 3 putaran dasar (X, X2, X')."""
    moves: Dict[str, CubeState] = {}
    for face, quarter in _BASE_TURNS.items():
        half = _apply_table(quarter, quarter)      # 180 derajat
        three = _apply_table(half, quarter)        # 270 derajat (invers 90)
        moves[face] = quarter
        moves[face + "2"] = half
        moves[face + "'"] = three
    return moves


MOVES: Dict[str, CubeState] = _build_moves()

# 9 gerakan resmi yang digunakan dalam pencarian solusi BFS
ALL_MOVES = ("U", "U'", "U2", "R", "R'", "R2", "F", "F'", "F2")


def apply_move(state: CubeState, move: str) -> CubeState:
    """Terapkan satu gerakan legal pada state kubus."""
    if move not in MOVES:
        raise ValueError(f"Gerakan tidak dikenal: {move!r}. Pilihan: {ALL_MOVES}")
    return _apply_table(state, MOVES[move])


def parse_moves(sequence: str) -> List[str]:
    """Parse string urutan gerakan menjadi daftar token gerakan."""
    normalized = sequence.replace("\u2019", "'").replace("\u2018", "'")
    tokens = normalized.split()
    for token in tokens:
        if token not in MOVES:
            raise ValueError(
                f"Gerakan tidak dikenal: {token!r}. Pilihan: {ALL_MOVES}"
            )
    return tokens


def apply_moves(state: CubeState, sequence: Union[str, Sequence[str]]) -> CubeState:
    """Terapkan serangkaian gerakan secara berurutan pada state."""
    moves = parse_moves(sequence) if isinstance(sequence, str) else list(sequence)
    for move in moves:
        state = apply_move(state, move)
    return state


def inverse_move(move: str) -> str:
    """Invers satu gerakan (misal R -> R', R' -> R, R2 -> R2)."""
    if move not in MOVES:
        raise ValueError(f"Gerakan tidak dikenal: {move!r}")
    if move.endswith("2"):
        return move
    if move.endswith("'"):
        return move[:-1]
    return move + "'"


def inverse_moves(sequence: Union[str, Sequence[str]]) -> str:
    """Balik urutan seluruh gerakan dan invers setiap gerakannya."""
    moves = parse_moves(sequence) if isinstance(sequence, str) else list(sequence)
    return " ".join(inverse_move(m) for m in reversed(moves))


if __name__ == "__main__":
    from cube_model import SOLVED_STATE

    s = apply_moves(SOLVED_STATE, "R U2 F' R'")
    print("Setelah R U2 F' R':", s)
    print("Balik lagi        :", apply_moves(s, inverse_moves("R U2 F' R'")).is_solved())

