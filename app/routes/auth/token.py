from flask import jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token
)
from app.models import Account
from . import auth_bp


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    user = Account.query.get(user_id)

    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    access_token = create_access_token(identity=user.id)

    return jsonify({
        "success": True,
        "access_token": access_token
    }), 200
