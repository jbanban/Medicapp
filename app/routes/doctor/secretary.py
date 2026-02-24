from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Doctor_Secretary, Account, Doctor

from . import doctor_bp

@doctor_bp.route("/secretary")
@login_required
def list_secretaries():

    if current_user.role != "doctor":
        abort(403)

    doctor = Doctor.query.filter_by(
        account_id=current_user.account_id
    ).first_or_404()

    secretaries = Doctor_Secretary.query.filter_by(
        doctor_id=doctor.doctor_id
    ).all()

    return render_template(
        "doctor/doctor_secretary.html",
        secretaries=secretaries
    )

@doctor_bp.route("/create", methods=["POST"])
@login_required
def create_secretary():

    # 🔐 Allow doctor only
    if current_user.role != "doctor":
        abort(403)

    doctor = Doctor.query.filter_by(
        account_id=current_user.account_id
    ).first_or_404()

    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    username = request.form.get("username")
    password = request.form.get("password")

    # 🛑 Validate required fields
    if not all([first_name, last_name, username, password]):
        flash("All fields are required.", "danger")
        return redirect(url_for("secretary.list_secretaries"))

    # 🛑 Check if username already exists
    existing_user = Account.query.filter_by(username=username).first()
    if existing_user:
        flash("Username already exists.", "danger")
        return redirect(url_for("secretary.list_secretaries"))

    try:
        # ✅ Create Account (Using your model properly)
        account = Account(
            username=username,
            role="secretary",
            active=True  # optional since default=True
        )

        account.set_password(password)

        db.session.add(account)
        db.session.flush()  # get generated account_id

        # ✅ Create Doctor Secretary
        secretary = Doctor_Secretary(
            account_id=account.account_id,
            doctor_id=doctor.doctor_id,
            first_name=first_name,
            last_name=last_name
        )

        db.session.add(secretary)
        db.session.commit()

        flash("Secretary created successfully!", "success")

    except Exception as e:
        db.session.rollback()
        flash("Error creating secretary.", "danger")

    return redirect(url_for("secretary.list_secretaries"))

@doctor_bp.route("/update/<int:id>", methods=["POST"])
@login_required
def update_secretary(id):

    if current_user.role != "doctor":
        abort(403)

    doctor = Doctor.query.filter_by(
        account_id=current_user.account_id
    ).first_or_404()

    secretary = Doctor_Secretary.query.filter_by(
        secretary_id=id,
        doctor_id=doctor.doctor_id
    ).first_or_404()

    secretary.first_name = request.form.get("first_name")
    secretary.last_name = request.form.get("last_name")

    db.session.commit()

    flash("Secretary updated successfully!", "success")
    return redirect(url_for("secretary.list_secretaries"))

@doctor_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_secretary(id):

    if current_user.role != "doctor":
        abort(403)

    doctor = Doctor.query.filter_by(
        account_id=current_user.account_id
    ).first_or_404()

    secretary = Doctor_Secretary.query.filter_by(
        secretary_id=id,
        doctor_id=doctor.doctor_id
    ).first_or_404()

    # delete linked account
    account = Account.query.get(secretary.account_id)

    db.session.delete(secretary)
    db.session.delete(account)
    db.session.commit()

    flash("Secretary deleted successfully!", "success")
    return redirect(url_for("secretary.list_secretaries"))