from functools import wraps
from flask import abort
from flask_login import current_user, login_required

def role_required(role):
    def decorator(f):
        @wraps(f)
        @login_required
        def wrapper(*args, **kwargs):
            if current_user.role != role:
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator
