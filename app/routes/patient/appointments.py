from flask import jsonify, render_template, redirect, url_for, request, flash
from datetime import date, datetime
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.doctor_schedule import Doctor_Schedule
from app.models.doctors_background import DoctorsBackground
from app.services.patient_cache import get_patient_cache
from app.services.email_services import send_email
from app import db
from . import patient_bp

@patient_bp.route('/appointment', methods=['GET', 'POST'])
@login_required
def patient_appointment():

    patient = Patient.query.filter_by(account_id=current_user.account_id).first()
    decrypted_patient = get_patient_cache(patient.patient_id)

    tab = request.args.get("tab", "upcoming")  # upcoming | past
    today = date.today()

    query = (
        db.session.query(Appointment)
        .options(
            joinedload(Appointment.patient),
            joinedload(Appointment.doctor),
            joinedload(Appointment.payments),
        )
        .filter(Appointment.patient_id == patient.patient_id)
    )

    if tab == "past":
        query = query.filter(Appointment.appointment_date < today) \
                     .order_by(Appointment.appointment_date.desc())
    else:
        query = query.filter(Appointment.appointment_date >= today) \
                     .order_by(Appointment.appointment_date.asc())

    appointments = query.all()

    doctor_ids = {appt.doctor.doctor_id for appt in appointments if appt.doctor}

    doctors_background = DoctorsBackground.query.filter(
        DoctorsBackground.doctor_id.in_(doctor_ids)
    ).all()

    background_by_doctor = {
        bg.doctor_id: bg for bg in doctors_background
    }

    return render_template('patient/myAppointments.html', 
                            appointments=appointments,
                            patient=decrypted_patient,
                            background_by_doctor=background_by_doctor,
                            tab=tab
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
        type = 'availability'

        # Create appointment
        new_appointment = Appointment(
            patient_id=patient.patient_id,
            doctor_id=doctor_id,
            appointment_date=preferred_date,
            appointment_time=preferred_time,
            status=status,
            type=type
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


@patient_bp.route('/book_appointment', methods=['POST','PATCH'])
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
            status='Booked',
            type='availability'
        )

        # Update schedule status
        schedule.status = 'Booked'

        db.session.add(appointment)
        db.session.commit()

        send_email(
            subject="Appointment Confirmation – Successfully Booked",
            recipient=appointment.patient.email,
            body=f"""
                Dear {appointment.patient.first_name} {appointment.patient.last_name},

                Good day.

                We are pleased to inform you that your appointment has been successfully scheduled.

                Appointment Details:
                Doctor: Dr. {appointment.doctor.first_name} {appointment.doctor.last_name}
                Date: {appointment.appointment_date}
                Time: {appointment.appointment_time}
                Type: {appointment.type}

                Please ensure that you arrive at least 10–15 minutes before your scheduled time for proper check-in.

                If you need to reschedule or cancel your appointment, you may do so through your MEDICAPP account.

                Thank you for choosing MEDICAPP. We look forward to serving you.

                Sincerely,
                MEDICAPP Support Team
                """
            )


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
    

@patient_bp.route('/cancel_appointment/<int:appointment_id>', methods=['PATCH'])
@login_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    appointment.status = 'Cancelled'

    if appointment.type == 'availability':
        try:
            start_str, end_str = appointment.appointment_time.split(' - ')
            start_time = datetime.strptime(start_str, "%H:%M").time()
            end_time = datetime.strptime(end_str, "%H:%M").time()
        except Exception as e:
            print("Time parse error:", e)
            start_time = None
            end_time = None

        if start_time and end_time:
            schedule = Doctor_Schedule.query.filter_by(
                doctor_id=appointment.doctor_id,
                vacant_date=appointment.appointment_date,
                start_time=start_time,
                end_time=end_time
            ).first()

            if schedule:
                schedule.status = 'available'
            else:
                print("Warning: No schedule found for appointment", appointment_id)

    db.session.commit()
    return redirect(url_for('patient.patient_appointment'))


@patient_bp.route('/reschedule/<int:appointment_id>', methods=['GET','POST'])
@login_required
def reschedule(appointment_id):

    appointment = Appointment.query.get_or_404(appointment_id)

    if request.method == 'POST':
        
        new_date = request.form.get('appointment_date')
        new_time = request.form.get('appointment_time')  # if you have time
        new_reason = request.form.get('reason')  # optional

        try:
            # Convert string to date/datetime if needed
            # Adjust format to match your input type="date" or "datetime-local"
            appointment.appointment_date = datetime.strptime(new_date, "%Y-%m-%d").date()

            if hasattr(appointment, "appointment_time") and new_time:
                appointment.appointment_time = datetime.strptime(new_time, "%H:%M").time()

            if hasattr(appointment, "reason") and new_reason is not None:
                appointment.reason = new_reason

            db.session.commit()
            flash("Appointment rescheduled successfully!", "success")
            return redirect(url_for('patient.patient_dashboard'))

        except Exception as e:
            db.session.rollback()
            flash("Failed to reschedule appointment. Please try again.", "danger")

    return render_template(
        'patient/reschedule.html',
        appointment=appointment
    )
