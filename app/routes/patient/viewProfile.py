from flask import render_template
from flask_login import login_required
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.patient_history_background import PatientHistoryBackground
from app.models.medical_visibility import MedicalVisibility
from app.services.patient_cache import get_patient_cache 
from app.security.crypto import decrypt_value, safe_decrypt

from . import patient_bp

@patient_bp.route("/viewProfile/<int:patient_id>")
@login_required
def viewProfile(patient_id):

    # Get patient
    patient = Patient.query.get_or_404(patient_id)

    # Get medical history
    history = PatientHistoryBackground.query.filter_by(
        patient_id=patient.patient_id
    ).first()

    appointment = Appointment.query.filter_by(
        patient_id=patient.patient_id
    ).first()

    # Decrypt main patient fields using your cache
    decrypted_patient = get_patient_cache(patient.patient_id)

    info = Patient.query.get(patient.patient_id)
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
            "current_zipcode": decrypt_value(info.current_zipcode),
            # PERMANENT ADDRESS
            "permanent_house_no": safe_decrypt(info.permanent_house_no),
            "permanent_street": safe_decrypt(info.permanent_street),
            "permanent_barangay": decrypt_value(info.permanent_barangay),
            "permanent_city": decrypt_value(info.permanent_city),
            "permanent_province": decrypt_value(info.permanent_province),
            "permanent_zipcode": decrypt_value(info.permanent_zipcode),
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

    return render_template(
        "viewProfile.html",
        patient=decrypted_patient,
        history=decrypted_history,
        appointment=appointment,
        visibility=visibility_dict
    )
