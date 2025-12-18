from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required
from extensions import db, login_manager
from models import Account

@login_manager.user_loader
def load_user(user_id):
    return Account.query.get(int(user_id))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = Account.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            # ROLE-BASED REDIRECT
            if user.role == "doctor":
                return redirect(url_for("doctor_dashboard"))
            elif user.role == "patient":
                return redirect(url_for("patient_dashboard"))
            elif user.role == "admin":
                return redirect(url_for("admin_dashboard"))

        flash("Invalid credentials.", "danger")

    return render_template("auth/login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out", "success")
    return redirect(url_for("auth.login"))

@app.route("/unauthorized")
def unauthorized():
    return render_template("errors/unauthorized.html")
