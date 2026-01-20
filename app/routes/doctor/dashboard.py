from flask import render_template, session, redirect, url_for, flash
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from . import doctor_bp


@doctor_bp.route('/dashboard')
def doctor_dashboard():
    if 'role' not in session or session['role'] != 'doctor':
        return redirect(url_for('misc.unauthorized'))

    user_id = session.get('user_id')

    doctor = Doctor.query.filter_by(account_id=user_id).first()

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
