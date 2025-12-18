from .auth import auth_bp
from .patient import patient_bp
from .doctor import doctor_bp
from .admin import admin_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(patient_bp, url_prefix="/patient")
    app.register_blueprint(doctor_bp, url_prefix="/doctor")
    app.register_blueprint(admin_bp, url_prefix="/admin")
