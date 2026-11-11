"""Solver optimal kubus 2x2x2 berbasis tabel lookup BFS (Breadth-First Search)."""

import os
from array import array
from typing import List, Optional

from cube_model import CubeState, SOLVED_STATE, is_valid_state
from movements import ALL_MOVES, apply_move

# Konfigurasi encoding slot bebas (slot 6 / DBL difiksasi)
FREE_POS = (0, 1, 2, 3, 4, 5, 7)
N_FREE = len(FREE_POS)
FREE_CORNER_IDS = tuple(sorted(FREE_POS))
_CORNER_RANK = {cid: i for i, cid in enumerate(FREE_CORNER_IDS)}

# Faktorial untuk perhitungan Lehmer code
_FACT = [1] * (N_FREE + 1)
for _i in range(1, N_FREE + 1):
    _FACT[_i] = _FACT[_i - 1] * _i

PERM_TABLE_SIZE = _FACT[N_FREE]              # 5040 permutasi (7!)
ORIENT_TABLE_SIZE = 3 ** (N_FREE - 1)        # 729 kombinasi orientasi (3^6)
TABLE_SIZE = PERM_TABLE_SIZE * ORIENT_TABLE_SIZE  # 3.674.160 state total


def _lehmer_encode(ranks: List[int]) -> int:
    """Encode permutasi berperingkat 0..N-1 ke integer menggunakan Lehmer code."""
    ranks = list(ranks)
    n = len(ranks)
    code = 0
    for i in range(n):
        smaller = sum(1 for j in range(i + 1, n) if ranks[j] < ranks[i])
        code += smaller * _FACT[n - 1 - i]
    return code


def _lehmer_decode(code: int, n: int) -> List[int]:
    """Decode integer Lehmer code kembali ke deretan peringkat permutasi."""
    elements = list(range(n))
    result = []
    for i in range(n, 0, -1):
        f = _FACT[i - 1]
        idx, code = divmod(code, f)
        result.append(elements.pop(idx))
    return result


def encode_state(state: CubeState) -> int:
    """Konversi CubeState ke indeks integer unik (0 .. 3.674.159)."""
    ranks = [_CORNER_RANK[state.perm[p]] for p in FREE_POS]
    perm_code = _lehmer_encode(ranks)

    orient_code = 0
    for p in FREE_POS[:-1]:
        orient_code = orient_code * 3 + state.orient[p]

    return perm_code * ORIENT_TABLE_SIZE + orient_code


def decode_state(index: int) -> CubeState:
    """Konversi indeks integer kembali menjadi objek CubeState."""
    perm_code, orient_code = divmod(index, ORIENT_TABLE_SIZE)
    ranks = _lehmer_decode(perm_code, N_FREE)

    perm = [0] * 8
    perm[6] = 6
    for pos, rank in zip(FREE_POS, ranks):
        perm[pos] = FREE_CORNER_IDS[rank]

    digits = []
    c = orient_code
    for _ in range(N_FREE - 1):
        c, d = divmod(c, 3)
        digits.append(d)
    digits.reverse()

    orient = [0] * 8
    total = 0
    for pos, d in zip(FREE_POS[:-1], digits):
        orient[pos] = d
        total += d
    orient[FREE_POS[-1]] = (-total) % 3

    return CubeState(tuple(perm), tuple(orient))


def is_encodable(state: CubeState) -> bool:
    """Cek apakah state valid fisik dan slot 6 (DBL) berada di posisi kanonik 6 orientasi 0."""
    if not is_valid_state(state.perm, state.orient):
        return False
    if state.perm[6] != 6 or state.orient[6] != 0:
        return False
    return True


# Prapemetaan indeks gerakan invers
_INVERSE_INDEX = {}
for _i, _m in enumerate(ALL_MOVES):
    if _m.endswith("2"):
        _inv = _m
    elif _m.endswith("'"):
        _inv = _m[:-1]
    else:
        _inv = _m + "'"
    _INVERSE_INDEX[_m] = ALL_MOVES.index(_inv)

UNVISITED = -1
SOLVED_MARK = -2

DEFAULT_TABLE_PATH = os.path.join(os.path.dirname(__file__), "bfs_table.bin")


def build_bfs_table(verbose: bool = True) -> array:
    """Bangun tabel lookup BFS 1-byte per state (total 3.674.160 state)."""
    table = array("b", (UNVISITED for _ in range(TABLE_SIZE)))
    table[encode_state(SOLVED_STATE)] = SOLVED_MARK

    frontier = [SOLVED_STATE]
    total = 1
    depth = 0
    if verbose:
        print(f"  depth {depth}: total = {total}")

    while frontier:
        next_frontier = []
        for state in frontier:
            for move in ALL_MOVES:
                new_state = apply_move(state, move)
                enc = encode_state(new_state)
                if table[enc] == UNVISITED:
                    table[enc] = _INVERSE_INDEX[move]
                    next_frontier.append(new_state)
        if not next_frontier:
            break
        depth += 1
        total += len(next_frontier)
        if verbose:
            print(f"  depth {depth}: total = {total} (+{len(next_frontier)})")
        frontier = next_frontier

    if total != TABLE_SIZE:
        raise RuntimeError(
            f"BFS hanya menemukan {total} state, seharusnya {TABLE_SIZE}."
        )
    if verbose:
        print(f"Selesai. Total state = {total} (kedalaman maksimum = {depth})")
    return table


def save_table(table: array, path: str = DEFAULT_TABLE_PATH) -> None:
    """Simpan tabel BFS ke file biner."""
    with open(path, "wb") as f:
        table.tofile(f)


def load_table(path: str = DEFAULT_TABLE_PATH) -> array:
    """Muat tabel BFS dari file biner."""
    table = array("b")
    with open(path, "rb") as f:
        table.fromfile(f, TABLE_SIZE)
    return table


_TABLE_CACHE: Optional[array] = None


def get_table(path: str = DEFAULT_TABLE_PATH, verbose: bool = True) -> array:
    """Ambil tabel BFS via cache memori, file disk, atau bangun otomatis jika belum ada."""
    global _TABLE_CACHE
    if _TABLE_CACHE is not None:
        return _TABLE_CACHE
    if os.path.exists(path):
        _TABLE_CACHE = load_table(path)
    else:
        _TABLE_CACHE = build_bfs_table(verbose=verbose)
        save_table(_TABLE_CACHE, path)
    return _TABLE_CACHE


MAX_SOLVE_LEN = 20  # Batas aman pencegah infinite loop


def solve(state: CubeState, table: Optional[array] = None) -> List[str]:
    """Cari solusi langkah optimal (minimum) menuju solved state menggunakan tabel BFS."""
    if table is None:
        table = get_table(verbose=False)

    if not is_encodable(state):
        raise ValueError(
            "State tidak bisa diselesaikan: pastikan valid secara fisik dan "
            "corner DBL telah dinormalisasi ke slot 6 orientasi 0."
        )

    moves: List[str] = []
    current = state
    for _ in range(MAX_SOLVE_LEN):
        enc = encode_state(current)
        code = table[enc]
        if code == UNVISITED:
            raise RuntimeError("State valid tidak ditemukan pada tabel BFS.")
        if code == SOLVED_MARK:
            return moves
        move = ALL_MOVES[code]
        moves.append(move)
        current = apply_move(current, move)

    raise RuntimeError("Pencarian solusi melebihi batas langkah maksimum.")


def solve_to_string(state: CubeState, table: Optional[array] = None) -> str:
    """Format solusi gerakan menjadi string ringkas."""
    moves = solve(state, table)
    return " ".join(moves) if moves else "(sudah solved)"


if __name__ == "__main__":
    from movements import apply_moves

    print("Membangun/memuat tabel BFS...")
    t = get_table()

    scramble = "R U2 F' R' U F2 R U'"
    scrambled = apply_moves(SOLVED_STATE, scramble)
    solution = solve_to_string(scrambled, t)
    print(f"Scramble : {scramble}")
    print(f"Solusi   : {solution}")
    print(f"Terverifikasi solved: {apply_moves(scrambled, solution or '').is_solved()}")

