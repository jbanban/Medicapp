from flask import Blueprint, render_template, redirect, url_for, session
from flask_login import login_required, current_user
from app.models import Doctor, Patient
from app.services.patient_cache import get_patient_cache

misc_bp = Blueprint("misc", __name__)


@misc_bp.route('/unauthorized')
def unauthorized():
    return "Unauthorized access", 403


@misc_bp.route('/about')
@login_required
def about():

    doctor = Doctor.query.first()
    patient = Patient.query.filter_by(account_id=current_user.account_id).first()

    decrypted_patient = get_patient_cache(patient.patient_id)
    return render_template('about.html', doctor=doctor, patient=decrypted_patient)

@misc_bp.route('/forbidden')
def forbidden():
    doctor = Doctor.query.filter_by(account_id=current_user.account_id).first()
    
    return render_template('403.html',
                           doctor=doctor
                           )

@misc_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

