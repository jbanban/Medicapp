from flask import render_template, redirect, request, url_for, flash
from flask_login import current_user, login_required
from app.services.email_services import send_email
from datetime import date, datetime
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.doctor_schedule import Doctor_Schedule
from app.models.payment import PaymentRecord
from app.routes.patient import Patient
from app.models.medical_record import MedicalRecord
from app.services.patient_cache import get_patient_cache
from app.services.audit_services import log_activity
from app import db
from . import doctor_bp


@doctor_bp.route('/appointments')
@login_required
def doctors_appointment():
    doctor = Doctor.query.filter_by(account_id=current_user.account_id).first()

    tab = request.args.get('tab', 'all')
    today = date.today()

    page = request.args.get('page', 1, type=int)
    per_page = 5

    appointments_query = (
        Appointment.query
        .join(Patient, Appointment.patient_id == Patient.patient_id)
        .filter(Appointment.doctor_id == doctor.doctor_id)
    )

    missed = Appointment.query.filter_by(
        doctor_id=doctor.doctor_id,
        status = 'Missed',          # adjust to match your actual status string
        appointment_date = today
    ).all()

    if tab == 'today':
        appointments_query = appointments_query.filter(
            Appointment.status.in_(['Booked', 'Paid', 'Ongoing']),
            Appointment.appointment_date == today
        )

    elif tab == 'opened':
        appointments_query = appointments_query.filter(
            Appointment.type == 'availability',
            Appointment.appointment_date == today
        )
    
    elif tab == 'request':
        appointments_query = appointments_query.filter(
            Appointment.type == 'request',
            Appointment.status == 'Pending'
        )

    appointments_query = appointments_query.order_by(
        Appointment.appointment_date.asc(),
        Appointment.appointment_time.asc()
    )

    appointments = appointments_query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    ongoing_appointment = Appointment.query.filter_by(
        doctor_id=doctor.doctor_id,
        status="Ongoing"
    ).first()

    # 🔹 cache patient data
    for appointment in appointments.items:
        appointment.patient_data = get_patient_cache(appointment.patient_id)


    return render_template(
        'doctor/doctor_appointment.html',
        appointments=appointments.items,
        pagination=appointments,
        doctor=doctor,
        tab=tab,
        ongoing_appointment=ongoing_appointment,
        missed_appointments=missed   
    )


@doctor_bp.route('/view_profile/<int:patient_id>')
@login_required
def view_profile(patient_id):
    patient = Patient.query.get(patient_id)
    
    doctor = Doctor.query.filter_by(account_id=current_user.account_id)

    # 🔹 cache patient data
    patient_data = get_patient_cache(patient_id)

    log_activity(
        account_id=current_user.account_id,
        action="Viewed Profile",
        description=f"Dr. {doctor.firstname} {doctor.lastname}, Viewed Patient Profile of {patient_data.full_name}."
    )

    return render_template(
        'patient/viewProfile.html',
        patient=patient,
        patient_data=patient_data
    )


@doctor_bp.route('/appointments')
@login_required
def view_appointments():
    doctor = Doctor.query.filter_by(
        account_id=current_user.account_id
    ).first()

    if not doctor:
        flash("Please complete your doctor profile.", "warning")
        return redirect(url_for('doctor.create_doctor_profile'))

    # Get query parameters
    patient_id = request.args.get("patient_id")
    search = request.args.get("search")

    # Base query (only this doctor's appointments)
    query = db.session.query(Appointment, Patient)\
        .join(Patient, Patient.patient_id == Appointment.patient_id)\
        .filter(Appointment.doctor_id == doctor.doctor_id)

    # Filter by patient_id (when clicking eye icon)
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)

    # Search by patient name
    if search:
        query = query.filter(
            (Patient.firstname.ilike(f"%{search}%")) |
            (Patient.lastname.ilike(f"%{search}%"))
        )

    records = query.order_by(Appointment.appointment_date.desc()).all()

    appointment_list = []

    for appointment, patient in records:
        decrypted = get_patient_cache(patient.patient_id)

        appointment_list.append({
            "appointment": appointment,
            "patient_id": patient.patient_id,
            "firstname": decrypted["firstname"],
            "lastname": decrypted["lastname"],
        })

    return render_template(
        "doctor/doctor_appointments.html",
        appointments=appointment_list,
        search=search
    )




# ACTIONS FOR BUTTON ROUTES
@doctor_bp.route('/accept_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def accept_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return redirect(url_for('doctor.doctors_appointment'))
    appointment.status = 'Booked'
    db.session.commit()
    flash('Appointment Request Successfully Accepted','success')

    log_activity(
        account_id=current_user.account_id,
        action="Accept Appointment",
        description=f"Doctor Accept appointment ID {appointment.appointment_id}"
    )

    send_email(
        subject="Appointment Confirmation – Successfully Booked",
        recipient=appointment.patient.email,
        body=f"""
            Dear {appointment.patient.firstname} {appointment.patient.lastname},

            Good day.

            We are pleased to inform you that your appointment has been successfully scheduled.

            Appointment Details:
            Doctor: Dr. {appointment.doctor.firstname} {appointment.doctor.lastname}
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

    return redirect(url_for('doctor.doctors_appointment'))

@doctor_bp.route('/reject_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def reject_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return redirect(url_for('doctor.doctors_appointment'))
    appointment.status = 'Rejected'
    db.session.commit()

    log_activity(
        account_id=current_user.account_id,
        action="Reject Appointment",
        description=f"Doctor Rejects appointment ID {appointment.appointment_id}"
    )

    flash('Appointment Request Successfully Rejected','success')
    return redirect(url_for('doctor.doctors_appointment'))

@doctor_bp.route('/check-in/<int:appointment_id>', methods=['POST'])
@login_required
def check_in_patient(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return redirect(url_for('doctor.doctors_appointment'))
    appointment.status = 'Ongoing'
    db.session.commit()

    log_activity(
        account_id=current_user.account_id,
        action="Patient Check-in",
        description=f"Patient ID {appointment.patient_id} is currently check-in for his/her appointment {appointment.appointment_id}"
    )

    flash('Patient is Currently Checked-in.', 'success')
    return redirect(url_for('doctor.doctors_appointment'))

@doctor_bp.route('/done_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def done_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return redirect(url_for('doctor.doctors_appointment'))
    appointment.status = 'Done'

    log_activity(
        account_id=current_user.account_id,
        action="Done Appointment",
        description=f"Doctor successfully {appointment.reason} appointment ID {appointment.appointment_id}."
    )

    db.session.commit()
    return redirect(url_for('doctor.doctors_appointment'))

@doctor_bp.route('/diagnosis_record/<int:appointment_id>', methods=['POST'])
@login_required
def appointment_diagnosis(appointment_id):

    appointment = Appointment.query.get_or_404(appointment_id)
    doctor = Doctor.query.filter_by(account_id=current_user.account_id).first()

    diagnosis = request.form.get('diagnosis')
    notes = request.form.get('notes')
    visit_date = request.form.get('visit_date')
    patient_id = request.form.get('patient_id')

    new_record = MedicalRecord(
        patient_id=patient_id,
        doctor_id = doctor.doctor_id,
        appointment_id=appointment_id,
        visit_date=visit_date,
        diagnosis=diagnosis,
        notes=notes
    )

    db.session.add(new_record)
    db.session.commit()

    flash('Medical record saved successfully.', 'success')

    return redirect(url_for('doctor.doctors_appointment'))


@doctor_bp.route('/pay_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def pay_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    if request.method == 'POST':
        amount = float(request.form.get('consultation_fee'))

        if not amount:
            flash('Amount is required.', 'danger')
            return redirect(url_for('doctor.doctors_appointment'))

        # Update appointment status
        appointment.status = 'Paid'

        # Create payment record
        new_payment = PaymentRecord(
            appointment_id=appointment_id,
            amount=amount,
            payment_status='Paid'
        )

        db.session.add(new_payment)
        db.session.commit()

        log_activity(
            account_id=current_user.account_id,
            action="Appointment Paid",
            description=f"Appointment ID: {appointment.appointment_id} has been Successfully Paid."
        )
            
        flash('Appointment Successfully Paid.', 'success')
        return redirect(url_for('doctor.doctors_appointment'))


@doctor_bp.route("/appointment/<int:appointment_id>/update_status/<string:action>", methods=["POST"])
@login_required
def update_appointment_status(appointment_id, action):

    doctor = Doctor.query.filter_by(account_id=current_user.account_id).first_or_404()

    appointment = Appointment.query.get_or_404(appointment_id)

    # Make sure appointment belongs to this doctor
    if appointment.doctor_id != doctor.doctor_id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("doctor.doctor_appointment"))

    # CHECK IF OTHER APPOINTMENT IS ONGOING
    ongoing = Appointment.query.filter(
        Appointment.doctor_id == doctor.doctor_id,
        Appointment.status == "Ongoing",
        Appointment.appointment_id != appointment_id
    ).first()

    if action == "checkin":
        if ongoing:
            flash("Another patient is currently ongoing.", "warning")
            return redirect(url_for("doctor.doctor_appointment"))

        appointment.status = "Ongoing"

    elif action == "done":
        appointment.status = "Done"

    db.session.commit()
    flash("Appointment updated successfully.", "success")
    return redirect(url_for("doctor.doctors_appointment"))



@doctor_bp.route('/cancel_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):

    doctor = Doctor.query.filter_by(
        account_id=current_user.account_id
    ).first_or_404()

    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.doctor_id != doctor.doctor_id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for('doctor.doctors_appointment'))

    today_str = date.today().strftime("%Y-%m-%d")

    # 🔥 FIND AVAILABLE SLOT FROM doctor_schedule TABLE
    nearest_slot = Doctor_Schedule.query.filter(
        Doctor_Schedule.doctor_id == doctor.doctor_id,
        Doctor_Schedule.status == 'available',
        Doctor_Schedule.vacant_date >= today_str
    ).order_by(
        Doctor_Schedule.vacant_date.asc(),
        Doctor_Schedule.start_time.asc()
    ).first()

    if nearest_slot:

        # 🔥 RESCHEDULE APPOINTMENT
        appointment.appointment_date = nearest_slot.vacant_date.strftime("%Y-%m-%d")
        appointment.appointment_time = nearest_slot.start_time.strftime("%H:%M")
        appointment.doctor_schedule_id = nearest_slot.doctor_schedule_id
        appointment.status = 'Booked'

        # 🔥 MARK SLOT AS BOOKED
        nearest_slot.status = 'Cancelled'

        db.session.commit()


        flash('Appointment automatically rescheduled to nearest available time.', 'success')

        log_activity(
            account_id=current_user.account_id,
            action="Appointment automatic Reschedule",
            description=f"Doctor cancelled appointment ID {appointment.appointment_id} and is atomatically Rescheduled."
        )

        send_email(
            subject="Appointment Rescheduled Notice",
            recipient=appointment.patient.email,
            body=f"""
                Dear {appointment.patient.firstname} {appointment.patient.lastname},

                Good day.

                Please be informed that your previously scheduled appointment with 
                Dr. {doctor.firstname} {doctor.lastname} has been rescheduled
                due to unforeseen circumstances.

                New Appointment Details:
                Date: {appointment.appointment_date}
                Time: {appointment.appointment_time}

                We sincerely apologize for any inconvenience this adjustment may cause.
                Your understanding and continued trust in our services are greatly appreciated.

                If the new schedule is not convenient for you, please log in to your
                MEDICAPP account to choose another available time.

                Thank you for your patience and understanding.

                Sincerely,
                MEDICAPP Support Team
                """
            )

    else:
        appointment.status = 'Cancelled'
        db.session.commit()

        flash('No available schedule found. Appointment cancelled.', 'warning')

        log_activity(
            account_id=current_user.account_id,
            action="Cancel Appointment",
            description=f"Doctor cancelled appointment ID {appointment.appointment_id}"
        )
        send_email(
            subject="Notice of Appointment Cancellation",
            recipient=appointment.patient.email,
            body=f"""
                Dear {appointment.patient.firstname} {appointment.patient.lastname},

                Good day.

                We regret to inform you that your scheduled appointment with 
                Dr. {doctor.firstname} {doctor.lastname} on 
                {appointment.appointment_date} at {appointment.appointment_time}
                has been cancelled due to unforeseen circumstances.

                We sincerely apologize for any inconvenience this may have caused.
                Your time and trust are highly valued, and we understand the importance
                of your scheduled consultation.

                We kindly encourage you to log in to your MEDICAPP account to
                reschedule your appointment at your convenience, or you may contact
                the clinic directly for assistance.

                Thank you for your understanding.

                Sincerely,
                MEDICAPP Support Team
                """
            )
        

    return redirect(url_for('doctor.doctors_appointment'))

