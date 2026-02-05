from flask import render_template
from flask_login import current_user, login_required
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.services.patient_cache import get_patient_cache
from . import patient_bp

@patient_bp.route('/available_doctors')
@login_required
def available_doctors():

    patient = Patient.query.filter_by(account_id=current_user.account_id).first()
    doctors = Doctor.query.all()
   
    decrypted_patient = get_patient_cache(patient.patient_id)

    return render_template('patient/available_doctors.html', 
                           doctors=doctors,
                           patient=decrypted_patient)
