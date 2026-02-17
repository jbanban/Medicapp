from datetime import date
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.payment import PaymentRecord
from app.services.patient_cache import get_patient_cache
from . import doctor_bp
from app import db


from sqlalchemy import func

def get_doctor_dashboard_counts(doctor_id):
    
    today = date.today()
    current_year = today.year
    current_month = today.month

    total_patients = (
        db.session.query(func.count(func.distinct(Appointment.patient_id)))
        .filter(Appointment.doctor_id == doctor_id)
        .scalar()
    )

    total_booked_appointments = (
        db.session.query(func.count(Appointment.appointment_id))
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status == "Booked"
        )
        .scalar()
    )

    total_amount = (
        db.session.query(func.coalesce(func.sum(PaymentRecord.amount), 0))
        .scalar()
    )

    total_amount_this_month = (
        db.session.query(func.coalesce(func.sum(PaymentRecord.amount), 0))
        .join(Appointment)
        .filter(Appointment.doctor_id == doctor_id)
        .scalar()
    )

    return {
        "total_patients": total_patients or 0,
        "total_booked_appointments": total_booked_appointments or 0,
        "total_amount": total_amount or 0,
        "total_amount_month": total_amount_this_month or 0
    }


@doctor_bp.route('/dashboard')
@login_required
def doctor_dashboard():

    doctor = Doctor.query.filter_by(account_id=current_user.account_id).first()
    if not doctor:
        flash("Please complete your doctor profile.", "warning")
        return redirect(url_for('auth.login'))


    appointments = Appointment.query.filter_by(
        doctor_id=doctor.doctor_id
    ).all()

    patients = []
    total_amount = 0

    for appt in appointments:
        decrypted_patient = get_patient_cache(appt.patient_id)

        if decrypted_patient:
            patients.append(decrypted_patient)

        if appt.payments:
            total_amount += sum(p.amount for p in appt.payments)


    dashboard_card_totals = get_doctor_dashboard_counts(doctor.doctor_id)

    return render_template(
        'doctor/doctor_dashboard.html',
        doctor=doctor,
        appointments=appointments,
        patients=patients,
        total_amount=total_amount,
        totals=dashboard_card_totals
    )
