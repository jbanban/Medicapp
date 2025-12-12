from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from flask_login import current_user
from ..utils.decorators import login_required, role_required
from ..extensions import db
from ..models.doctor import Doctor
from ..models.appointment import Appointment

app = Blueprint("doctor", __name__)

@app.route("/dashboard")
@login_required
@role_required("doctor")
def dashboard():
    doctor = Doctor.query.filter_by(account_id=current_user.account_id).first()
    if doctor is None:
        flash("Please complete your profile.", "warning")
        return redirect(url_for("doctor.profile_setup"))
    
    appointments = Appointment.query.filter_by(doctor_id=doctor.doctor_id).all()

    return render_template("doctor/doctor_dashboard.html", 
                           doctor=doctor, 
                           appointments=appointments
                           )

@app.route("/profile_setup", methods=["GET","POST"])
@login_required
@role_required("doctor")
def profile_setup():
    user_id = session.get("user_id")
    if request.method == "POST":
        d = Doctor(
            firstname=request.form.get("firstname"),
            middlename=request.form.get("middlename"),
            lastname=request.form.get("lastname"),
            specialization=request.form.get("specialization"),
            phone=request.form.get("phone"),
            email=request.form.get("email"),
            account_id=user_id
        )
        db.session.add(d)
        db.session.commit()
        flash("Profile saved", "success")
        return redirect(url_for("doctor.dashboard"))
    return render_template("doctor/profile_setup.html")
