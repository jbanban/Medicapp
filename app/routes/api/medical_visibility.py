from flask import request, session
from app import db
from app.models.medical_visibility import MedicalVisibility
from . import api_bp


@api_bp.route('/medical-visibility/save', methods=['POST'])
def save_medical_visibility():
    if 'user_id' not in session or session.get('role') != 'patient':
        return {"error": "Unauthorized"}, 401

    data = request.json
    patient_id = data.get('patient_id')
    encrypted_state = data.get('encrypted_state')

    record = MedicalVisibility.query.filter_by(patient_id=patient_id).first()

    if record:
        record.encrypted_state = encrypted_state
    else:
        record = MedicalVisibility(
            patient_id=patient_id,
            encrypted_state=encrypted_state
        )
        db.session.add(record)

    db.session.commit()
    return {"status": "saved"}

@api_bp.route('/medical-visibility/get/<int:patient_id>', methods=['GET'])
def get_medical_visibility(patient_id):
    if 'user_id' not in session or session.get('role') != 'patient':
        return {"error": "Unauthorized"}, 401

    record = MedicalVisibility.query.filter_by(patient_id=patient_id).first()

    if record:
        return {"encrypted_state": record.encrypted_state}
    else:
        return {"encrypted_state": None}
    

