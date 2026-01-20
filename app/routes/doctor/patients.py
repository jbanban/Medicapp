from flask import render_template, session, redirect, url_for, flash
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.appointment import Appointment
from . import doctor_bp


@doctor_bp.route('/patients')
def doctor_patients():
    if session.get('role') != 'doctor':
        return redirect(url_for('unauthorized'))

    user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(account_id=user_id).first()

    if not doctor:
        flash("Please complete your doctor profile.", "warning")
        return redirect(url_for('doctor.create_doctor_profile'))

    patients = (
        Patient.query
        .join(Appointment)
        .filter(Appointment.doctor_id == doctor.doctor_id)
        .distinct()
        .all()
    )

    return render_template(
        'doctor/doctor_patients.html',
        doctor=doctor,
        patients=patients
    )
