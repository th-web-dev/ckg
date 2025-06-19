from flask import Blueprint, render_template, request, jsonify
from app.ciphers.factory import get_cipher

bp = Blueprint('routes', __name__)


@bp.route('/encrypt', methods=['POST'])
def encrypt():
    data = request.get_json()
    cipher_name = data.get("method", "lorenz")
    password = data.get("password")
    token = data.get("token", "default_token")
    coord = data.get("coord", [0, 0])  # Erwartet [x, y] als Liste

    if not password:
        return jsonify({'error': 'No password provided'}), 400

    try:
        cipher = get_cipher(cipher_name)

        if cipher_name == "lorenz":
            result = cipher.encrypt(password, token=token, coord=tuple(coord))
        else:
            result = cipher.encrypt(password)

        return jsonify({"formatted": result["formatted"]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/')
def index():
    return render_template('index.html')