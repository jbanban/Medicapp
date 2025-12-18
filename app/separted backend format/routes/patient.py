from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from flask_login import current_user
from models import Account, Patient, PatientHistoryBackground
from extensions import db
from utils.decorators import login_required, role_required
from datetime import datetime

app = Blueprint("patient", __name__)

def patient_required(fn):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "patient":
            return redirect(url_for("unauthorized"))
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

@app.route("/dashboard")
@login_required
@role_required("patient")
def dashboard():
    profile = Patient.query.filter_by(account_id=current_user.account_id).first()
    return render_template("patient/patient_dashboard.html", profile=profile)

@app.route("/create_profile", methods=["GET","POST"])
@login_required
@patient_required
def create_profile():
    user_id = session.get("user_id")
    existing = Patient.query.filter_by(account_id=user_id).first()
    if existing:
        flash("Profile exists", "warning")
        return redirect(url_for("patient.dashboard"))

    if request.method == "POST":
        # parse form (same as your earlier logic)
        try:
            birthdate = datetime.strptime(request.form.get("birthdate"), "%Y-%m-%d").date()
        except:
            flash("Invalid birthdate", "warning")
            return redirect(url_for("patient.create_profile"))

        patient = Patient(
            account_id=user_id,
            firstname=request.form.get("firstname"),
            middlename=request.form.get("middlename"),
            lastname=request.form.get("lastname"),
            gender=request.form.get("gender"),
            birthdate=birthdate,
            age=int(request.form.get("age") or 0),
            current_address=request.form.get("current_address"),
            permanent_address=request.form.get("permanent_address"),
            phone=request.form.get("phone"),
            email=request.form.get("email")
        )
        db.session.add(patient)
        db.session.flush()

        history = PatientHistoryBackground(
            patient_id=patient.patient_id,
            pastMedicalHistory=request.form.get("pastMedicalHistory"),
            beenHospitalized=request.form.get("beenHospitalized"),
            hadSurgery=request.form.get("hadSurgery"),
            allergies=request.form.get("allergies"),
            ongoingMedications=request.form.get("ongoingMedications"),
            familyHistory=request.form.get("familyHistory"),
        )
        db.session.add(history)
        db.session.commit()
        flash("Profile created", "success")
        return redirect(url_for("patient.dashboard"))

    return render_template("patient/create_profile.html")
