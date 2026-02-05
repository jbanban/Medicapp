from flask import render_template, request, session, redirect, url_for, flash
from flask_login import current_user, login_required
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.services.patient_cache import get_patient_cache
from app import db
from . import patient_bp


@patient_bp.route('/request_appointment', methods=['GET', 'POST'])
@login_required
def request_appointment():
    user_id = current_user.account_id
    doctors = Doctor.query.all()

    if request.method == 'POST':
        appointment_date = request.form['preferred_date']
        appointment_time = request.form['preferred_time']
        doctor_id = request.form['doctor_id']
        status = 'Pending'

        new_appointment = Appointment(
            patient_id=user_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status=status
        )

        db.session.add(new_appointment)
        db.session.commit()

        return redirect(url_for('patient.request_appointment'))
    
    patient = Patient.query.filter_by(account_id=user_id).first()
    
    decrypted_patient = get_patient_cache(patient.patient_id)

    return render_template('patient/request_appointment.html', 
                           doctors=doctors,
                           patient=decrypted_patient
                           )


@patient_bp.route('/patient/reschedule_appointment/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def reschedule_appointment(appointment_id):
    if 'role' not in session or session['role'] != 'patient':
        return redirect(url_for('unauthorized'))
    print("request is as follows = ",request.form)  # DEBUG: Print form content
    appointment = Appointment.query.get_or_404(appointment_id)

    if request.method == 'POST':
        preferred_date = request.form['preferred_date']
        preferred_time = request.form['preferred_time']

        if not preferred_date or not preferred_time:
            flash('Missing date or time.')
            return redirect(reschedule_appointment(appointment_id))
        
        appointment.appointment_date = preferred_date
        appointment.appointment_time = preferred_time
        db.session.commit()

        return redirect(url_for('patient.patient_appointment'))

    return render_template('patient/reschedule_appointment.html', appointment=appointment)