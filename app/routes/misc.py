from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import Doctor, Patient
from app.services.patient_cache import get_patient_cache

misc_bp = Blueprint("misc", __name__)

# 🔽 PASTE search(), about(), logout(), unauthorized() ROUTES HERE
@misc_bp.route('/unauthorized')
def unauthorized():
    return "Unauthorized access", 403

@misc_bp.route("/search")
def search():
    q = request.args.get("q")
    print(q)

    if q:
        results = Doctor.query.filter(Doctor.firstname.icontains(q) | Doctor.lastname.icontains(q)) \
        .order_by(Doctor.specialization.asc()).limit(100).all()
    else:
        results = []

    return render_template("search_results.html", results=results)


@misc_bp.route('/about')
@login_required
def about():

    doctor = Doctor.query.first()
    patient = Patient.query.filter_by(account_id=current_user.account_id).first()

    decrypted_patient = get_patient_cache(patient.patient_id)
    return render_template('about.html', doctor=doctor, patient=decrypted_patient)

@misc_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

