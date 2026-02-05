from flask import render_template, session, redirect, url_for, flash
from flask_login import current_user, login_required
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.appointment import Appointment
from . import doctor_bp


@doctor_bp.route('/patients')
@login_required
def doctor_patients():
    doctor = Doctor.query.filter_by(account_id=current_user.account_id).first()

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


