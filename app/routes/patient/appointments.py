from flask import jsonify, render_template, session, redirect, url_for, request, flash
from flask_login import current_user, login_required
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.doctor_schedule import Doctor_Schedule
from app.services.patient_cache import get_patient_cache
from app import db
from . import patient_bp


@patient_bp.route('/appointment', methods=['GET', 'POST'])
@login_required
def patient_appointment():

    appointments = Appointment.query.filter_by(patient_id=current_user.account_id).all()
    patient = Patient.query.filter_by(account_id=current_user.account_id).first()
    
    decrypted_patient = get_patient_cache(patient.patient_id)

    return render_template('patient/myAppointments.html', 
                           appointments=appointments,
                           patient=decrypted_patient
                           )

@patient_bp.route('/doctors/view_available/time_for_<int:doctor_id>')
@login_required
def viewAvailableTime(doctor_id):

    doctor = Doctor.query.get(doctor_id)
    patient = Patient.query.filter_by(account_id=current_user.account_id).first()
    schedules = Doctor_Schedule.query.filter_by(doctor_id=doctor_id).all()

    selected_date = request.args.get('date')

    if request.method == 'POST':
        preferred_date = request.form['vacant_date']
        preferred_time = request.form['vacant_time']
        status = 'Booked'

        # Create appointment
        new_appointment = Appointment(
            patient_id=patient.patient_id,
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
                           patient=patient,
                           doctor=doctor,
                           doctor_id=doctor_id,
                           selected_date=selected_date 
                           )


@patient_bp.route('/book_appointment', methods=['POST'])
@login_required
def book_appointment():
    schedule_id = request.form.get('doctor_schedule_id')
    reason = request.form.get('reason')

    if not schedule_id or not reason:
        return jsonify({
            "success": False, 
            "error": "Missing required fields"
        }), 400

    schedule = Doctor_Schedule.query.get(schedule_id)
    if not schedule:
        return jsonify({
            "success": False, 
            "error": "Schedule not found"
        }), 404
        
    if schedule.status.lower() != 'available':
        return jsonify({
            "success": False, 
            "error": "This time slot is no longer available"
        }), 400

    patient = Patient.query.filter_by(account_id=current_user.account_id).first()
    if not patient:
        return jsonify({
            "success": False, 
            "error": "Patient profile not found"
        }), 400

    try:
        appointment = Appointment(
            patient_id=patient.patient_id,
            doctor_id=schedule.doctor_id,
            appointment_date=schedule.vacant_date.strftime("%Y-%m-%d"),
            appointment_time=f"{schedule.start_time.strftime('%H:%M')} - {schedule.end_time.strftime('%H:%M')}",
            reason=reason,
            status='Booked'
        )

        # Update schedule status
        schedule.status = 'Booked'

        db.session.add(appointment)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Appointment booked successfully!",
            "appointment_id": appointment.appointment_id
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error booking appointment: {str(e)}")  # For debugging
        return jsonify({
            "success": False,
            "error": "An error occurred while booking the appointment"
        }), 500
    

@patient_bp.route('/cancel_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return redirect(url_for('patient.patient_appointment'))

    appointment.status = 'Cancelled'
    db.session.commit()

    return redirect(url_for('patient.patient_appointment'))
