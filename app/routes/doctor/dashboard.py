from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from . import doctor_bp


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

    return render_template(
        'doctor/doctor_dashboard.html',
        doctor=doctor,
        appointments=appointments
    )
