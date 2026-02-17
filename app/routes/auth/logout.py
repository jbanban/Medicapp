from flask import jsonify, url_for, redirect
from . import auth_bp
from flask_login import logout_user

def response_logout():
    logout_user()
    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    }), 200

@auth_bp.route('/logout')
def logout():
    response_logout()
    return redirect(url_for('auth.login'))