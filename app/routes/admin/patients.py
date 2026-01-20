from flask import render_template
from app.models import Patient
from . import admin_bp


@admin_bp.route('/admin/patients_list')
def patients_list():
    patients = Patient.query.all()
    return render_template('admin/patients_list.html', patients=patients)
