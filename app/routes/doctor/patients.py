from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.services.patient_cache import get_patient_cache
from . import doctor_bp
from app import db


@doctor_bp.route('/patients')
@login_required
def doctor_patients():
    doctor = Doctor.query.filter_by(account_id=current_user.account_id).first()

    if not doctor:
        flash("Please complete your doctor profile.", "warning")
        return redirect(url_for('doctor.create_doctor_profile'))
    
    patients = (
        db.session.query(Patient, Appointment)
        .join(Appointment, Appointment.patient_id == Patient.patient_id)
        .filter(Appointment.doctor_id == doctor.doctor_id)
        .all()
    )

    decrypted_patients = {}

    for patient, _ in patients:
        if patient.patient_id not in decrypted_patients:
            decrypted_patients[patient.patient_id] = get_patient_cache(patient.patient_id)

    return render_template(
        "doctor/doctor_patients.html",
        doctor=doctor,
        patients=patients,
        decrypted_patients=decrypted_patients
    )



