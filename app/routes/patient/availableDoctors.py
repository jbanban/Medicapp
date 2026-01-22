from flask import render_template, session, redirect, url_for, flash
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.security.crypto import decrypt_value, safe_decrypt
from . import patient_bp

@patient_bp.route('/available_doctors')
def available_doctors():
    if 'role' not in session or session['role'] != 'patient':
        return redirect(url_for('unauthorized'))
    user_id = session.get('user_id')

    doctors = Doctor.query.all()
    patient = Patient.query.filter_by(account_id=user_id).first()
    decrypted_patient = {
        "patient_id": patient.patient_id,

        "firstname": decrypt_value(patient.firstname),
        "middlename": safe_decrypt(patient.middlename),
        "lastname": decrypt_value(patient.lastname),

        "full_name": " ".join(filter(None, [
            decrypt_value(patient.firstname),
            safe_decrypt(patient.middlename),
            decrypt_value(patient.lastname)
        ])),
    }


    return render_template('patient/available_doctors.html', 
                           doctors=doctors,
                           patient=decrypted_patient)
