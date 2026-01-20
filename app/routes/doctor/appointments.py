from flask import render_template, session, redirect, url_for
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app import db
from . import doctor_bp


@doctor_bp.route('/appointments')  
def doctors_appointment():
    if 'role' not in session or session['role'] != 'doctor':
        return redirect(url_for('unauthorized'))

    user_id = session.get('user_id')

    doctor = Doctor.query.filter_by(account_id=user_id).first()
    if not doctor:
        return redirect(url_for('unauthorized'))

    appointments = Appointment.query.filter_by(
        doctor_id=doctor.doctor_id
    ).all()

    return render_template(
        'doctor/doctor_appointment.html', 
        appointments=appointments,
        doctor=doctor
    )

@doctor_bp.route('/accept_appointment/<int:appointment_id>', methods=['POST'])
def accept_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return redirect(url_for('doctor.doctors_appointment'))
    appointment.status = 'Accepted'
    db.session.commit()
    return redirect(url_for('doctor.doctors_appointment'))

@doctor_bp.route('/reject_appointment/<int:appointment_id>', methods=['POST'])
def reject_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return redirect(url_for('doctor.doctors_appointment'))
    appointment.status = 'Rejected'
    db.session.commit()
    return redirect(url_for('doctor.doctors_appointment'))

@doctor_bp.route('/done_appointment/<int:appointment_id>', methods=['POST'])
def done_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return redirect(url_for('doctor.doctors_appointment'))
    appointment.status = 'Done'
    db.session.commit()
    return redirect(url_for('doctor.doctors_appointment'))