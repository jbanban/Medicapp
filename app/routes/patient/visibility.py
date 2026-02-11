from flask import request, jsonify
from flask_login import login_required, current_user
from app.models.medical_visibility import MedicalVisibility
from app.models.patient import Patient
from app.extensions import db
from . import patient_bp
import json


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

