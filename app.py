"""Controller web Flask untuk antarmuka Rubik 2x2x2 Solver."""

import random

from flask import Flask, jsonify, render_template, request

from cube_model import CORNER_NAMES, DEFAULT_FACE_COLORS, SOLVED_STATE
from color_mapping import ColorMappingError, colors_to_solution, state_to_colors, apply_rotation, ROTATIONS
from movements import ALL_MOVES, apply_moves

app = Flask(__name__)


@app.route("/")
def index():
    """Menyajikan halaman antarmuka web 3D."""
    return render_template("index.html")


@app.route("/api/solve", methods=["POST"])
def api_solve():
    """Menerima konfigurasi warna dari frontend, memproses solusi, dan mengembalikan JSON."""
    payload = request.get_json(silent=True) or {}
    raw_corners = payload.get("corners")

    if not isinstance(raw_corners, dict):
        return jsonify({"error": "Format input tidak valid: 'corners' harus berupa objek."}), 400

    try:
        corners = {int(slot): tuple(colors) for slot, colors in raw_corners.items()}
    except (TypeError, ValueError):
        return jsonify({"error": "Format input tidak valid: slot harus angka, warna harus daftar 3 item."}), 400

    try:
        result = colors_to_solution(corners)
    except ColorMappingError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Terjadi kesalahan tak terduga: {e}"}), 500

    return jsonify(result)


@app.route("/api/example", methods=["GET"])
def api_example():
    """Menghasilkan acakan kubus acak untuk pengujian instan pada antarmuka."""
    n = random.randint(3, 12)
    seq = [random.choice(ALL_MOVES) for _ in range(n)]
    scrambled = apply_moves(SOLVED_STATE, " ".join(seq))
    held = apply_rotation(scrambled, random.choice(ROTATIONS))
    colors = state_to_colors(held)
    return jsonify({
        "corners": {str(slot): list(c) for slot, c in colors.items()},
        "scramble_used": " ".join(seq),
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)

