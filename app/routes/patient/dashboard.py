
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from datetime import date, timedelta
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.payment import PaymentRecord
from sqlalchemy import func
from app.services.patient_cache import get_patient_cache
from app import db

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
    doctors = Doctor.query.all()

    
    five_days_ahead = today + timedelta(days=5)

    upcoming = Appointment.query \
            .filter(
                Appointment.patient_id == patient.patient_id,
                Appointment.appointment_date >= today,
                Appointment.appointment_date <= five_days_ahead
            ) \
            .order_by(Appointment.appointment_date.asc()) \
            .all()

    total_payment = db.session.query(func.sum(PaymentRecord.amount)) \
        .join(Appointment, PaymentRecord.appointment_id == Appointment.appointment_id) \
        .filter(Appointment.patient_id == patient.patient_id) \
        .scalar()

    total_payment = total_payment or 0  # Handle None if no payments found

    return render_template('patient/patient_dashboard.html',
                           patient=decrypted_patient, 
                           appointments=appointments,
                           doctors=doctors,
                           upcoming=upcoming,
                           payment=total_payment
                           )
