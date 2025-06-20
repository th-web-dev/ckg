from flask import Blueprint, render_template, request, jsonify
from app.ciphers.factory import get_cipher
from flask import session
from app.memory import generate_noise_field_opensimplex

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
    field = generate_noise_field_opensimplex(token, size=100, scale=0.1)
    first_row = field[0]
    field_log = f"Field shape: {field.shape}\nFirst row:\n{first_row}"

    log_lines.append({"type": "log", "text": field_log})

    return jsonify({"receiver_log": log_lines})


@bp.route('/')
def index():
    return render_template('index.html')