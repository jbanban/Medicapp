from flask import request, jsonify
from flask_login import login_required, current_user
from app.models.medical_visibility import MedicalVisibility
from app.extensions import db
from . import api_bp


@api_bp.route("/medical-visibility", methods=["POST"])
@login_required
def update_medical_visibility():
    data = request.get_json()
    patient_id = current_user.account_id   # adjust if needed

    visibility = MedicalVisibility.query.filter_by(
        patient_id=patient_id
    ).first()

    if not visibility:
        visibility = MedicalVisibility(patient_id=patient_id)
        db.session.add(visibility)

    # Update dynamically
    for key, value in data.items():
        if hasattr(visibility, key):
            setattr(visibility, key, bool(value))

    db.session.commit()

    return jsonify({"message": "Visibility updated successfully"}), 200
