from flask import render_template, session, redirect, url_for, request, flash
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.doctor_schedule import Doctor_Schedule
from app.security.crypto import decrypt_value
from app import db
from . import patient_bp


@patient_bp.route('/patient/appointment', methods=['GET', 'POST'])
def patient_appointment():
    if 'role' not in session or session['role'] != 'patient':
        return redirect(url_for('unauthorized'))
    user_id = session.get('user_id')

    appointments = Appointment.query.filter_by(patient_id=session.get('user_id')).all()
    profile = Patient.query.filter_by(account_id=user_id).first()
    decrypted_patient = {
        "patient_id": patient.patient_id,

        "firstname": decrypt_value(patient.firstname),
        "middlename": decrypt_value(patient.middlename),
        "lastname": decrypt_value(patient.lastname),

        "full_name": " ".join(filter(None, [
            decrypt_value(patient.firstname),
            decrypt_value(patient.middlename),
            decrypt_value(patient.lastname)
        ])),
    }

    return render_template('patient/myAppointments.html', 
                           appointments=appointments,
                           patient=decrypted_patient
                           )

@patient_bp.route('/doctors/view_available/time_for_<int:doctor_id>')
def viewAvailableTime(doctor_id):
    if 'role' not in session or session['role'] != 'patient':
        return redirect(url_for('unauthorized'))
    user_id = session.get('user_id')

    profile = Patient.query.filter_by(account_id=user_id).first()
    schedules = Doctor_Schedule.query.filter_by(doctor_id=doctor_id).all()

    if request.method == 'POST':
        preferred_date = request.form['vacant_date']
        preferred_time = request.form['vacant_time']
        status = 'Booked'

        # Create appointment
        new_appointment = Appointment(
            patient_id=user_id,
            doctor_id=doctor_id,
            appointment_date=preferred_date,
            appointment_time=preferred_time,
            status=status
        )
        db.session.add(new_appointment)
        db.session.commit()
        flash('Appointment booked successfully!', 'success')

        return redirect(url_for('patient.patient_appointment'))
    
    return render_template('patient/viewAvailableTime.html', 
                           schedules=schedules,
                           profile=profile
                           )


@patient_bp.route('/book_appointment/<int:doctor_schedule_id>', methods=['GET', 'POST'])
def book_appointment(doctor_schedule_id):

    # 🔐 Patient-only access
    if 'role' not in session or session['role'] != 'patient':
        return redirect(url_for('unauthorized'))

    user_id = session.get('user_id')

    # 🔎 Fetch doctor schedule slot
    schedule = Doctor_Schedule.query.get(doctor_schedule_id)
    if not schedule:
        flash('Schedule slot not found.', 'error')
        return redirect(url_for('patient.patient_appointment'))

    # ❌ Prevent double booking
    if schedule.status.lower() != 'available':
        flash('This schedule is no longer available.', 'error')
        return redirect(url_for('patient.patient_appointment'))

    if request.method == 'POST':
        patient = Patient.query.filter_by(account_id=user_id).first()
        if not patient:
            flash('Patient profile not found.', 'error')
            return redirect(url_for('patient.patient_appointment'))

        # ✅ COPY schedule → appointment
        new_appointment = Appointment(
            patient_id=patient.patient_id,
            doctor_id=schedule.doctor_id,
            appointment_date=schedule.vacant_date.strftime("%Y-%m-%d"),
            appointment_time=f"{schedule.start_time.strftime('%H:%M')} - {schedule.end_time.strftime('%H:%M')}",
            status='Booked'
        )

        # ✅ Mark doctor schedule as booked
        schedule.status = 'Booked'

        db.session.add(new_appointment)
        db.session.commit()

        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('patient.patient_appointment'))

    profile = Patient.query.filter_by(account_id=user_id).first()

    return render_template(
        'patient/book_appointment.html',
        profile=profile,
        schedule=schedule
    )


@patient_bp.route('/patient/cancel_appointment/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return redirect(url_for('patient.patient_appointment'))

    appointment.status = 'Cancelled'
    db.session.commit()

    return redirect(url_for('patient.patient_appointment'))
