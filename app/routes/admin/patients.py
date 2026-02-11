from flask import render_template
from app.models import Patient, Account
from app.services.patient_cache import get_patient_cache
from app.utils.admin_only import admin_required
from . import admin_bp



@admin_bp.route('/patients_list')
@admin_required
def patients_list():

    patients = (
        Patient.query
        .join(Account, Patient.account_id == Account.account_id)
        .all()
    )

    decrypted_patients = [get_patient_cache(p.patient_id) for p in patients]

    return render_template('admin/patients.html', 
                           patients=decrypted_patients,
                           )
