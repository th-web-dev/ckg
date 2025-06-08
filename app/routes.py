from .lorenz import encrypt_with_chaos
from flask import Blueprint, render_template, request, jsonify

bp = Blueprint('routes', __name__)

@bp.route('/encrypt', methods=['POST'])
def encrypt():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not password:
        return jsonify({'error': 'No password provided'}), 400

    result = encrypt_with_chaos(password)
    return jsonify(result)

@bp.route('/')
def index():
    return render_template('index.html')