from flask import Blueprint, render_template, request, jsonify
from app.ciphers.factory import get_cipher

bp = Blueprint('routes', __name__)


@bp.route('/encrypt', methods=['POST'])
def encrypt():
    data = request.get_json()

    cipher_name = data.get("method", "lorenz")
    password = data.get("password")

    if not password:
        return jsonify({'error': 'No password provided'}), 400

    try:
        cipher = get_cipher(cipher_name)
        result = cipher.encrypt(password)

        # Wenn nur 'formatted' existiert, sende nur diesen
        if "formatted" in result:
            return jsonify({"formatted": result["formatted"]})

        # Fallback: komplette Struktur zurücksenden
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/')
def index():
    return render_template('index.html')