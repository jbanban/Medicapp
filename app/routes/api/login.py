from flask import request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from app.models import Account
from . import api_bp

@api_bp.route('/api/login', methods=['POST'])
def api_login():

    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "Missing JSON"}), 400

    username = data.get('username')
    password = data.get('password')

    user = Account.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    return jsonify({
        "success": True,
        "user": {
            "id": user.account_id,
            "username": user.username,
            "role": user.role
        },
        "tokens": {
            "access": create_access_token(identity=user.account_id),
            "refresh": create_refresh_token(identity=user.account_id)
        }
    }), 200