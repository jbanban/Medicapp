from flask import render_template, redirect, request, url_for, flash
from flask_login import current_user, login_required
from datetime import date, datetime
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.payment import PaymentRecord
from app.routes.patient import Patient
from app.models.medical_record import MedicalRecord
from app.services.patient_cache import get_patient_cache
from app import db
from . import doctor_bp


@doctor_bp.route('/appointments')
@login_required
def doctors_appointment():
    doctor = Doctor.query.filter_by(account_id=current_user.account_id).first()

    tab = request.args.get('tab', 'all')
    today = date.today().isoformat()

    page = request.args.get('page', 1, type=int)
    per_page = 5

    appointments_query = (
        Appointment.query
        .join(Patient, Appointment.patient_id == Patient.patient_id)
        .filter(Appointment.doctor_id == doctor.doctor_id)
    )

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

    # print("\n=== APPOINTMENTS DEBUG ===")
    # for appt in appointments.items:
    #     print(
    #         f"ID={appt.appointment_id}, "
    #         f"PatientID={appt.patient_id}, "
    #         f"Date={appt.appointment_date}, "
    #         f"Time={appt.appointment_time}, "
    #         f"Status={appt.status}, "
    #         f"ScheduleID={appt.doctor_schedule_id}"
    #     )
    # print("=== END APPOINTMENTS DEBUG ===\n")


    return render_template(
        'doctor/doctor_appointment.html',
        appointments=appointments.items,
        pagination=appointments,
        doctor=doctor,
        tab=tab,
        ongoing_appointment=ongoing_appointment
    )


@doctor_bp.route('/view_profile/<int:patient_id>')
@login_required
def view_profile(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return redirect(url_for('doctor.doctors_appointment'))

    # 🔹 cache patient data
    patient_data = get_patient_cache(patient_id)

    return render_template(
        'patient/viewProfile.html',
        patient=patient,
        patient_data=patient_data
    )

@doctor_bp.route('/accept_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def accept_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return redirect(url_for('doctor.doctors_appointment'))
    appointment.status = 'Booked'
    db.session.commit()
    flash('Appointment Request Successfully Accepted','success')
    return redirect(url_for('doctor.doctors_appointment'))

@doctor_bp.route('/reject_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def reject_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return redirect(url_for('doctor.doctors_appointment'))
    appointment.status = 'Rejected'
    db.session.commit()
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
    flash('Patient is Currently Checked-in.', 'success')
    return redirect(url_for('doctor.doctors_appointment'))

@doctor_bp.route('/done_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def done_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return redirect(url_for('doctor.doctors_appointment'))
    appointment.status = 'Done'
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

    # Ensure appointment belongs to this doctor
    if appointment.doctor_id != doctor.doctor_id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for('doctor.doctors_appointment'))

    # 1️⃣ Free current schedule slot (optional depending on your design)

    # 2️⃣ Find nearest available appointment slot
    nearest_slot = Appointment.query.filter(
        Appointment.doctor_id == doctor.doctor_id,
        Appointment.status == 'Available',
        Appointment.appointment_date >= datetime.today().date()
    ).order_by(
        Appointment.appointment_date.asc(),
        Appointment.appointment_time.asc()
    ).first()

    if nearest_slot:
        # Reschedule current appointment
        appointment.appointment_date = nearest_slot.appointment_date
        appointment.appointment_time = nearest_slot.appointment_time
        appointment.doctor_schedule_id = nearest_slot.doctor_schedule_id
        appointment.status = 'Booked'

        # Mark slot as taken (if needed)
        nearest_slot.status = 'Reserved'

        db.session.commit()

        flash('Appointment automatically rescheduled to nearest available time.', 'success')
    else:
        # If no available slot found
        appointment.status = 'Cancelled'
        db.session.commit()
        flash('No available schedule found. Appointment cancelled.', 'warning')

    return redirect(url_for('doctor.doctors_appointment'))
