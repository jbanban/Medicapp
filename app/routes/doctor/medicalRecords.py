from flask import jsonify, render_template, redirect, request, url_for
from flask_login import current_user, login_required
from datetime import date
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.routes.patient import Patient
from app.services.patient_cache import get_patient_cache
from app import db
from . import doctor_bp

@doctor_bp.route('/medical_records')
@login_required
def medical_records():
    doctor = Doctor.query.filter_by(account_id=current_user.account_id).first()

    page = request.args.get('page', 1, type=int)
    per_page = 5

    appointments_query = (
        Appointment.query
        .join(Patient, Appointment.patient_id == Patient.patient_id)
        .filter(Appointment.doctor_id == doctor.doctor_id)
        .filter(Appointment.status == 'Completed')
        .order_by(Appointment.appointment_date.desc())
    )

    appointments = appointments_query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    # 🔹 cache patient data
    for appointment in appointments.items:
        appointment.patient_data = get_patient_cache(appointment.patient_id)

    return render_template(
        'doctor/medical_records.html',
        doctor=doctor,
        appointments=appointments
    )


@doctor_bp.route('/medical_records/<int:appointment_id>')
@login_required
def medical_record_detail(appointment_id):
    doctor = Doctor.query.filter_by(account_id=current_user.account_id).first()
    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.doctor_id != doctor.doctor_id:
        flash("You do not have permission to view this medical record.", "danger")
        return redirect(url_for('doctor.medical_records'))

    patient_data = get_patient_cache(appointment.patient_id)

    return render_template(
        'doctor/medical_record_detail.html',
        doctor=doctor,
        appointment=appointment,
        patient=patient_data
    )

@doctor_bp.route('/medical_records', methods=['POST'])
@login_required
def postMedicalRecord():
    doctor = Doctor.query.filter_by(account_id=current_user.account_id).first()
    data = request.get_json()

    patient_id = data.get("patient_id")
    doctor_id = doctor.doctor_id
    appointment_id = data.get("appointment_id")
    visit_date = date.today().strftime("%Y-%m-%d")
    diagnosis = data.get("diagnosis")
    prescription = data.get("prescription")

    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.doctor_id != doctor.doctor_id:
        return jsonify(success=False, error="You do not have permission to update this medical record."), 403

    appointment.diagnosis = diagnosis
    appointment.prescription = prescription
    db.session.commit()

    return jsonify(success=True, message="Medical record updated successfully.")