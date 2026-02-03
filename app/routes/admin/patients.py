from flask import render_template
from app.models import Patient, Account
from app.services.patient_cache import get_patient_cache
from app.extensions import cache
from . import admin_bp



@admin_bp.route('/patients_list')
def patients_list():
    patient = Patient.query.all()

    decrypted_patients = [get_patient_cache(p.patient_id) for p in patient]

    account = Account.query.all()

    return render_template('admin/patients_list.html', 
                           patient=decrypted_patients,
                           account=account
                           )
