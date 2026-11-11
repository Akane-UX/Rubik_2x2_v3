"""Model representasi state dan validasi fisik Rubik 2x2x2 (Pocket Cube)."""

from dataclasses import dataclass
from typing import Tuple

# Daftar nama 8 slot corner (indeks 0..7)
CORNER_NAMES = ("URF", "UFL", "ULB", "UBR", "DFR", "DLF", "DBL", "DRB")

# Pemetaan tiap slot corner ke 3 muka fisiknya (arah U/D lalu berlawanan jarum jam)
CORNER_FACES = {
    0: ("U", "R", "F"),  # URF
    1: ("U", "F", "L"),  # UFL
    2: ("U", "L", "B"),  # ULB
    3: ("U", "B", "R"),  # UBR
    4: ("D", "F", "R"),  # DFR
    5: ("D", "L", "F"),  # DLF
    6: ("D", "B", "L"),  # DBL
    7: ("D", "R", "B"),  # DRB
}

# Skema warna standar Western (U: Putih, D: Kuning, F: Hijau, B: Biru, L: Oranye, R: Merah)
DEFAULT_FACE_COLORS = {
    "U": "White",
    "D": "Yellow",
    "F": "Green",
    "B": "Blue",
    "L": "Orange",
    "R": "Red",
}

SOLVED_PERM: Tuple[int, ...] = tuple(range(8))
SOLVED_ORIENT: Tuple[int, ...] = tuple([0] * 8)


@dataclass(frozen=True)
class CubeState:
    """State kubus 2x2x2: permutasi dan orientasi 8 corner (immutable)."""

    perm: Tuple[int, ...] = SOLVED_PERM
    orient: Tuple[int, ...] = SOLVED_ORIENT

    def is_solved(self) -> bool:
        """Cek apakah kubus berada dalam kondisi solved."""
        return self.perm == SOLVED_PERM and self.orient == SOLVED_ORIENT

    def as_key(self) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
        """Kunci tuple hashable untuk indexing tabel/set."""
        return (self.perm, self.orient)

    def __str__(self) -> str:
        parts = [
            f"{CORNER_NAMES[i]}:{CORNER_NAMES[self.perm[i]]}(+{self.orient[i]})"
            for i in range(8)
        ]
        return " ".join(parts)


SOLVED_STATE = CubeState(SOLVED_PERM, SOLVED_ORIENT)


def is_valid_state(perm: Tuple[int, ...], orient: Tuple[int, ...]) -> bool:
    """Validasi fisik: permutasi 0..7 lengkap, orientasi valid, dan sum(orient) % 3 == 0."""
    if sorted(perm) != list(range(8)):
        return False
    if any(o not in (0, 1, 2) for o in orient):
        return False
    if sum(orient) % 3 != 0:
        return False
    return True


if __name__ == "__main__":
    print("Solved state:", SOLVED_STATE)
    print("Is solved   :", SOLVED_STATE.is_solved())
    print("Valid?      :", is_valid_state(SOLVED_PERM, SOLVED_ORIENT))

