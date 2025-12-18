from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from app import app
from utils.decorators import login_required, role_required
from extensions import db
from models import Account, Doctor
from werkzeug.security import generate_password_hash


def admin_required(fn):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            return redirect(url_for("unauthorized"))
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper


@app.route("/dashboard")
@login_required
@admin_required
def dashboard():
    total_doctors = Doctor.query.count()
    total_accounts = Account.query.count()
    return render_template("admin/admin_dashboard.html", total_doctors=total_doctors, total_accounts=total_accounts)

@app.route("/doctors", methods=["GET","POST"])
@login_required
@admin_required
def doctors():
    if request.method == "POST":
        email = request.form.get("email")
        pw = request.form.get("password")
        if Account.query.filter_by(email=email).first():
            flash("Email exists", "danger")
            return redirect(url_for("admin.doctors"))
        acc = Account(email=email, password=generate_password_hash(pw), role="doctor")
        db.session.add(acc)
        db.session.commit()
        flash("Doctor account created", "success")
        return redirect(url_for("admin.doctors"))
    doctors = Doctor.query.all()
    return render_template("admin/admin_doctors.html", doctors=doctors)

@app.route('/admin/doctors')
@login_required
@admin_required
def admin_doctors():
    doctors = Doctor.query.all()
    return render_template("admin/admin_doctors.html", doctors=doctors)

@app.route('/admin/accounts')
@login_required
@admin_required
def admin_accounts():
    accounts = Account.query.all()
    return render_template("admin/admin_accounts.html", accounts=accounts)
