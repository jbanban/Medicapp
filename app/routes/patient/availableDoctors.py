from flask import render_template, session, redirect, url_for, flash
from app.models.patient import Patient
from app.models.doctor import Doctor
from . import patient_bp

@patient_bp.route('/available_doctors')
def available_doctors():
    if 'role' not in session or session['role'] != 'patient':
        return redirect(url_for('unauthorized'))
    user_id = session.get('user_id')

    profile = Patient.query.filter_by(account_id=user_id).first()
    doctors = Doctor.query.all()
    return render_template('patient/available_doctors.html', 
                           doctors=doctors,
                           profile=profile)
