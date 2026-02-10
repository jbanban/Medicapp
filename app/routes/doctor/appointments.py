from flask import render_template, redirect, request, url_for
from flask_login import current_user, login_required
from datetime import date
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.routes.patient import Patient
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
            Appointment.status == 'Booked',
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
        tab=tab
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
    appointment.status = 'Accepted'
    db.session.commit()
    return redirect(url_for('doctor.doctors_appointment'))

@doctor_bp.route('/reject_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def reject_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return redirect(url_for('doctor.doctors_appointment'))
    appointment.status = 'Rejected'
    db.session.commit()
    return redirect(url_for('doctor.doctors_appointment'))

@doctor_bp.route('/cancel_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return redirect(url_for('doctor.doctors_appointment'))
    appointment.status = 'Cancelled'
    db.session.commit()
    return redirect(url_for('doctor.doctors_appointment'))

@doctor_bp.route('/check-in/<int:appointment_id>', methods=['POST'])
@login_required
def check_in_patient(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return redirect(url_for('doctor.doctors_appointment'))
    appointment.status = 'Checked-in'
    db.session.commit()
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