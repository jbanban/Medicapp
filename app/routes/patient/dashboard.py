
from flask import render_template, session, redirect, url_for, flash
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.account import Account
from app.services.patient_cache import get_patient_cache
from . import patient_bp


@patient_bp.route('/dashboard')
def patient_dashboard():
    if 'role' not in session or session['role'] != 'patient':
        return redirect(url_for('unauthorized'))
    user_id = session.get('user_id')

    patient = Patient.query.filter_by(account_id=user_id).first()
    if not patient:
        flash("Finish your profile first!","warning")
        return redirect(url_for('patient.create_profile'))
    
    decrypted_patient = get_patient_cache(patient.patient_id)

    appointments = Appointment.query.filter_by(patient_id=user_id).all()
    doctors = Account.query.filter_by(role='doctor').all()

    return render_template('patient/patient_dashboard.html',
                           patient=decrypted_patient, 
                           appointments=appointments,
                           doctors=doctors
                           )
