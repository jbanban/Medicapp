from flask import request, jsonify
from flask_login import login_required, current_user
from app.models.medical_visibility import MedicalVisibility
from app.models.appointment_visibility import AppointmentVisibility
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.extensions import db
from . import patient_bp


def sync_done_paid_appointments(patient_id, visibility):
    appointments = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        Appointment.status.in_(["Done", "Paid"])
    ).all()

    updated = False

    for appt in appointments:
        appt_id_str = str(appt.appointment_id)

        if appt_id_str not in visibility.visibility_meta:
            visibility.visibility_meta[appt_id_str] = False
            updated = True

    return updated




@patient_bp.route("/medical-visibility/<int:patient_id>", methods=["POST"])
@login_required
def update_medical_visibility(patient_id):
    """Update medical field visibility settings"""
    
    # Get the patient and verify ownership
    patient = Patient.query.filter_by(
        patient_id=patient_id,
        account_id=current_user.account_id
    ).first_or_404()
    
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON"}), 400
    
    # Get or create visibility record
    visibility = MedicalVisibility.query.filter_by(
        patient_id=patient_id
    ).first()

    if not visibility:
        visibility = MedicalVisibility(patient_id=patient_id)
        db.session.add(visibility)
    
    for field in [
        "pastMedicalHistory",
        "beenHospitalized",
        "hadSurgery",
        "allergies",
        "ongoingMedications",
        "familyHistory",
        "socialHistory",
        "immunizations",
        "recentTravelHistory",
        "otherRelevantInfo",
    ]:
        if field in data:
            setattr(visibility, field, bool(data[field]))
  
    db.session.commit()

    return jsonify({"message": "Visibility updated successfully"}), 200
        


@patient_bp.route("/medical-visibility/<int:patient_id>", methods=["GET"])
@login_required
def get_medical_visibility(patient_id):
    """Get medical field visibility settings"""
    
    # Get the patient and verify ownership
    patient = Patient.query.filter_by(
        patient_id=patient_id,
        account_id=current_user.account_id
    ).first_or_404()
    
    visibility = MedicalVisibility.query.filter_by(
        patient_id=patient_id
    ).first()
    
    # Default visibility state (all fields hidden initially)
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
    
    
    if not visibility:
        return jsonify(default_state), 200

    return jsonify({
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
    }), 200




# ---------------- APPOINTMENT VISIBILITY ----------------

@patient_bp.route("/update_appointment_visibility/<int:patient_id>", methods=["POST"])
@login_required
def update_appointment_visibility(patient_id):

    patient = Patient.query.filter_by(
        patient_id=patient_id,
        account_id=current_user.account_id
    ).first_or_404()

    data = request.get_json(silent=True)

    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON format"}), 400

    visibility = AppointmentVisibility.query.filter_by(
        patient_id=patient_id
    ).first()

    if not visibility:
        visibility = AppointmentVisibility(
            patient_id=patient_id,
            visibility_meta={}
        )
        db.session.add(visibility)

    if not visibility.visibility_meta:
        visibility.visibility_meta = {}

    # 1️⃣ Auto-sync Done & Paid
    sync_done_paid_appointments(patient_id, visibility)

    # 2️⃣ Apply frontend updates
    for appointment_id_str, status in data.items():

        if not appointment_id_str.isdigit():
            continue

        appointment = Appointment.query.filter_by(
            appointment_id=int(appointment_id_str),
            patient_id=patient_id
        ).first()

        if not appointment:
            continue

        visibility.visibility_meta[str(appointment.appointment_id)] = bool(status)

    db.session.commit()

    return jsonify({
        "message": "Appointment visibility updated",
        "updated": visibility.visibility_meta
    }), 200


@patient_bp.route("/appointment-visibility/<int:patient_id>", methods=["GET"])
@login_required
def get_appointment_visibility(patient_id):

    patient = Patient.query.filter_by(
        patient_id=patient_id,
        account_id=current_user.account_id
    ).first_or_404()

    visibility = AppointmentVisibility.query.filter_by(
        patient_id=patient_id
    ).first()

    if not visibility:
        return jsonify({}), 200

    return jsonify(visibility.visibility_meta), 200

