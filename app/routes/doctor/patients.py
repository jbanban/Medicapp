from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from sqlalchemy import func
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

    latest_subquery = (
        db.session.query(
            Appointment.patient_id,
            func.max(Appointment.appointment_id).label("latest_id")
        )
        .filter(Appointment.doctor_id == doctor.doctor_id)
        .group_by(Appointment.patient_id)
        .subquery()
    )


    # Main query: join patient + appointment using latest date
    records = (
        db.session.query(Patient, Appointment)
        .join(Appointment, Appointment.patient_id == Patient.patient_id)
        .join(
            latest_subquery,
            Appointment.appointment_id == latest_subquery.c.latest_id
        )
        .all()
    )


    patient_list = []

    for patient, appointment in records:
        decrypted = get_patient_cache(patient.patient_id)

        patient_list.append({
            "patient_id": patient.patient_id,
            "firstname": decrypted["firstname"],
            "lastname": decrypted["lastname"],
            "appointment": appointment
        })

    return render_template(
        "doctor/doctor_patients.html",
        doctor=doctor,
        patients=patient_list
    )


