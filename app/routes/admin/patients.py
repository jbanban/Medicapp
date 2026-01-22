from flask import render_template
from app.models import Patient, Account
from app.security.crypto import decrypt_value, safe_decrypt
from . import admin_bp


@admin_bp.route('/admin/patients_list')
def patients_list():
    patients = Patient.query.all()

    decrypted_patients = [
        {
            "patient_id": patient.patient_id,   # ✅ ADD THIS

            "firstname": decrypt_value(patient.firstname),
            "middlename": safe_decrypt(patient.middlename),
            "lastname": decrypt_value(patient.lastname),
            "phone": decrypt_value(patient.phone),
            "permanent_address": " ".join(filter(None, [
                safe_decrypt(patient.permanent_house_no),
                safe_decrypt(patient.permanent_barangay),
                safe_decrypt(patient.permanent_city),
                safe_decrypt(patient.permanent_province)
            ])),

            "full_name": " ".join(filter(None, [
                decrypt_value(patient.firstname),
                safe_decrypt(patient.middlename),
                decrypt_value(patient.lastname)
            ])),
        }  for patient in patients
    ]

    account = Account.query.all()

    return render_template('admin/patients_list.html', 
                           patients=decrypted_patients,
                           account=account
                           )
