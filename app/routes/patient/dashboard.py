
from flask import render_template, session, redirect, url_for, flash
from flask_login import current_user, login_required
from flask_migrate import current
from datetime import date, datetime
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.account import Account
from app.services.patient_cache import get_patient_cache
from . import patient_bp


@patient_bp.route('/dashboard')
@login_required
def patient_dashboard():
    today = date.today()

    patient = Patient.query.filter_by(account_id=current_user.account_id).first()
    if not patient:
        flash("Finish your profile first!","warning")
        return redirect(url_for('patient.create_profile'))
    
    decrypted_patient = get_patient_cache(patient.patient_id)

    appointments = Appointment.query.filter_by(patient_id=patient.patient_id).all()
    doctors = Account.query.filter_by(role='doctor').all()

    upcoming = Appointment.query.filter(Appointment.appointment_date >= today) \
                     .order_by(Appointment.appointment_date.asc())

    return render_template('patient/patient_dashboard.html',
                           patient=decrypted_patient, 
                           appointments=appointments,
                           doctors=doctors,
                           upcoming=upcoming
                           )
