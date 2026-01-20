from flask import redirect, url_for, session
from . import auth_bp


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))