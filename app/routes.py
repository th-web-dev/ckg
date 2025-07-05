import numpy as np
from flask import Blueprint, render_template, request, jsonify
from flask import session
from app.memory import generate_noise_field_opensimplex
from app.memory import store_noise_field
from app.memory import get_noise_field
import hashlib
from app.ciphers.lorenz import LorenzCipher
from chaoscrypto_noise import rotate_token_py

bp = Blueprint('routes', __name__)


@bp.route('/set-cipher', methods=['POST'])
def set_cipher():
    cipher = request.form.get('cipher', 'lorenz')

    lines = [
        f"> Request arrived at endpoint /set-cipher with data: {{'cipher': '{cipher}'}}",
        f"> Ready to receive using {cipher.upper()} cipher"
    ]

    return jsonify({
        "receiver_log": lines
    })

@bp.route("/set-token", methods=["POST"])
def set_token():
    token = request.form.get("token")
    session["token"] = token

    log_lines = [
        {"type": "line", "text": f"> Request arrived at endpoint /set-token with data:"},
        {"type": "log", "text": f"{{'token': '{token}'}}"},
        {"type": "line", "text": "> Token received securely..."},
        {"type": "line", "text": f"> Noise field will be generated based on token..."},
    ]

    # Generate Noise Field
    field = generate_noise_field_opensimplex(token)

    user_id = session.get("user_id", "default")
    store_noise_field(user_id, field)

    first_row = field[0]
    formatted_row = "[" + ", ".join(f"{v:.8f}" for v in first_row) + "]"
    field_log = f"Field shape: {field.shape}\nFirst row:\n{formatted_row}"

    row_bytes = b"".join(v.tobytes() for v in first_row.astype(np.float64))
    hash_digest = hashlib.sha256(row_bytes).hexdigest()

    log_lines.append({"type": "log", "text": field_log})
    log_lines.append({"type": "line", "text": f"> Calculating and returning noise field hash for validation..."})

    return jsonify({
        "receiver_log": log_lines,
        "noise_hash": hash_digest
    })

@bp.route("/message", methods=["POST"])
def message():
    enc_message = request.form.get("enc_message")
    coords = request.form.get("coords")
    coord = tuple(map(int, coords.split(",")))

    log_lines = [
        {"type": "line", "text": f"> Request arrived at endpoint /message with data:"},
        {"type": "log", "text": f"{{'encrypted_message': '{enc_message}'}}"},
        {"type": "log", "text": f"{{'coordinates': '{coord}'}}"},
    ]

    user_id = session.get("user_id", "default")
    old_token = session.get("token")

    if old_token is None:
        log_lines.append({"type": "log", "text": f"⚠No token found in session!"})
        return jsonify({"receiver_log": log_lines}), 400

    noise = get_noise_field(user_id)
    if noise is None:
        log_lines.append({"type": "log", "text": f"⚠No noise field found for user {user_id}!"})
        return jsonify({"receiver_log": log_lines}), 400

    # Entschlüsselung mit altem Token
    cipher = LorenzCipher(noise=noise, steps_per_char=100)
    result = cipher.decrypt(enc_message, coord=coord)
    log_lines.extend(result["formatted"])

    decrypted = result["decrypted"]

    # Token-Rotation
    message_bytes = enc_message.encode("utf-8")
    message_hash_bytes = hashlib.sha256(message_bytes).digest()
    message_hash_hex = message_hash_bytes.hex()
    new_token = rotate_token_py(old_token, message_hash_hex)
    log_lines.append({"type": "line", "text": f"> Token rotated (server): {new_token}"})

    # Neues Noise-Feld berechnen
    new_noise = generate_noise_field_opensimplex(new_token)

    # Speichern
    store_noise_field(user_id, new_noise)
    session["token"] = new_token

    return jsonify({
        "receiver_log": log_lines,
        "decrypted_message": decrypted,
        "new_token": new_token
    })


@bp.route('/')
def index():
    return render_template('index.html')