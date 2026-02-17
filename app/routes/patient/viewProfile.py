from flask import render_template, abort, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.medical_record import MedicalRecord
from app.models.patient_history_background import PatientHistoryBackground
from app.models.medical_visibility import MedicalVisibility
from app.models.appointment_visibility import AppointmentVisibility
from app.services.patient_cache import get_patient_cache 
from app.security.crypto import decrypt_value, safe_decrypt
from app import db

from . import patient_bp

@patient_bp.route("/viewProfile/<int:patient_id>")
@login_required
def viewProfile(patient_id):

    patient = Patient.query.get_or_404(patient_id)

    doctor = None 

    # ===============================
    # ROLE CHECK
    # ===============================
    if current_user.role == "doctor":
        doctor = Doctor.query.filter_by(
            account_id=current_user.account_id
        ).first()

        if not doctor:
            abort(403)

        # Optional: security check (doctor must have appointment with patient)
        allowed = Appointment.query.filter_by(
            doctor_id=doctor.doctor_id,
            patient_id=patient.patient_id
        ).first()

        if not allowed:
            abort(403)

    elif current_user.role == "patient":
        own_patient = Patient.query.filter_by(
            account_id=current_user.account_id
        ).first()

        if not own_patient or own_patient.patient_id != patient.patient_id:
            abort(403)


    # Get medical history
    history = PatientHistoryBackground.query.filter_by(
        patient_id=patient.patient_id
    ).first()

    # Get current/latest appointment
    appointments = Appointment.query.filter(
        Appointment.patient_id == patient.patient_id,
        Appointment.status.in_(["Done", "Paid"])
    ).order_by(Appointment.appointment_id.desc()).all()

    appointment_visibility = AppointmentVisibility.query.filter_by(
        patient_id=patient.patient_id
    ).first()

    if appointment_visibility and appointment_visibility.visibility_meta:
        appointment_visibility_dict = appointment_visibility.visibility_meta
    else:
        appointment_visibility_dict = {}
        
    # Decrypt main patient fields using your cache
    decrypted_patient = get_patient_cache(patient.patient_id)

    info = patient
    if info:
        decrypted_patient.update({
            "gender": decrypt_value(info.gender),
            "blood_type": safe_decrypt(info.blood_type),
            "civil_status": decrypt_value(info.civil_status),
            "birthdate": info.birthdate,
            "age": info.age,
            # EMERGENCY CONTACT
            "ec_name": decrypt_value(info.ec_name),
            "ec_relation": decrypt_value(info.ec_relation),
            "ec_phone": decrypt_value(info.ec_phone),
            "ec_address": decrypt_value(info.ec_address),
            # CURRENT ADDRESS
            "current_house_no": safe_decrypt(info.current_house_no),
            "current_street": safe_decrypt(info.current_street),
            "current_barangay": decrypt_value(info.current_barangay),
            "current_city": decrypt_value(info.current_city),
            "current_province": decrypt_value(info.current_province),
            "current_zipcode": info.current_zipcode,
            # PERMANENT ADDRESS
            "permanent_house_no": safe_decrypt(info.permanent_house_no),
            "permanent_street": safe_decrypt(info.permanent_street),
            "permanent_barangay": decrypt_value(info.permanent_barangay),
            "permanent_city": decrypt_value(info.permanent_city),
            "permanent_province": decrypt_value(info.permanent_province),
            "permanent_zipcode": info.permanent_zipcode,
        })

    # Decrypt medical history safely
    decrypted_history = None
    if history:
        decrypted_history = {
            "pastMedicalHistory": decrypt_value(history.pastMedicalHistory),
            "beenHospitalized": decrypt_value(history.beenHospitalized),
            "hadSurgery": decrypt_value(history.hadSurgery),
            "allergies": decrypt_value(history.allergies),
            "ongoingMedications": decrypt_value(history.ongoingMedications),
            "familyHistory": decrypt_value(history.familyHistory),
            "socialHistory": safe_decrypt(getattr(history, "socialHistory", None)),
            "immunizations": safe_decrypt(getattr(history, "immunizations", None)),
            "recentTravelHistory": safe_decrypt(getattr(history, "recentTravelHistory", None)),
            "otherRelevantInfo": safe_decrypt(getattr(history, "otherRelevantInfo", None)),
        }

    visibility = MedicalVisibility.query.filter_by(
        patient_id=patient.patient_id
    ).first()

    # Default: everything hidden if no record exists
    default_state = {
        "pastMedicalHistory": False,
        "beenHospitalized": False,
        "hadSurgery": False,
        "allergies": False,
        "ongoingMedications": False,
        "familyHistory": False,
        "socialHistory": False,
        "immunizations": False,
        "recentTravelHistory": False,
        "otherRelevantInfo": False,
    }

    if visibility:
        visibility_dict = {
            "pastMedicalHistory": visibility.pastMedicalHistory,
            "beenHospitalized": visibility.beenHospitalized,
            "hadSurgery": visibility.hadSurgery,
            "allergies": visibility.allergies,
            "ongoingMedications": visibility.ongoingMedications,
            "familyHistory": visibility.familyHistory,
            "socialHistory": visibility.socialHistory,
            "immunizations": visibility.immunizations,
            "recentTravelHistory": visibility.recentTravelHistory,
            "otherRelevantInfo": visibility.otherRelevantInfo,
        }
    else:
        visibility_dict = default_state

    result = []

    for appt in appointments:

        record = appt.record

        if not record:
            result.append({
                "appointment_id": appt.appointment_id,
                "patient_firstname": None,
                "patient_lastname": None,
                "date": None,
                "diagnosis": None,
                "notes": None,
            })
            continue

        result.append({
            "appointment_id": appt.appointment_id,
            "patient_firstname": patient.firstname,
            "patient_lastname": patient.lastname,
            "date": record.visit_date,
            "diagnosis": record.diagnosis,
            "notes": record.notes,
        })

    return render_template(
        "viewProfile.html",
        patient=decrypted_patient,
        doctor=doctor,
        history=decrypted_history,
        appointments=result,
        visibility=visibility_dict,
        appointment_visibility=appointment_visibility_dict
    )


@patient_bp.route('/second_opinion/<int:appointment_id>', methods=['POST'])
def second_opinion(appointment_id):
    
    appointment = Appointment.query.get_or_404(appointment_id)

    record = MedicalRecord.query.filter_by(
        appointment_id=appointment.appointment_id
    ).first()


    if not record:
        flash("No medical record found.", "danger")
        return redirect(url_for('patient.viewProfile',
                                patient_id=appointment.patient_id))
    

    opinion = request.form.get('second_opinion')

    record.second_op = opinion

    db.session.commit()

    flash('Opinion Successfully Added','success')
    return redirect( url_for('patient.viewProfile',patient_id=appointment.patient_id))

