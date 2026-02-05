from flask import Blueprint, render_template, redirect, url_for, session, request
from app.models import Doctor, Patient

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
def about():

    doctor = Doctor.query.first()
    patient = Patient.query.first()

    return render_template('about.html', doctor=doctor, patient=patient)

@misc_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

