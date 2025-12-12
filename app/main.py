from flask import Flask, render_template, redirect, request, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from database import db
from models import Account, Doctor, Patient

app = Flask(__name__)
app.config['SECRET_KEY'] = "yoursecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///system.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return Account.query.get(int(user_id))


# -------------------------------------------------------
# AUTH ROUTES
# -------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = Account.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")

            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))
            elif user.role == "doctor":
                return redirect(url_for("doctor_dashboard"))
            else:
                return redirect(url_for("patient_dashboard"))

        flash("Invalid email or password", "danger")

    return render_template("auth/login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "info")
    return redirect(url_for("login"))


# -------------------------------------------------------
# ADMIN ROUTES
# -------------------------------------------------------

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return "Unauthorized", 403

    return render_template("admin/dashboard.html")


@app.route("/admin/doctors")
@login_required
def admin_doctors():
    if current_user.role != "admin":
        return "Unauthorized", 403

    # Correct query: join Account + Doctor
    doctors = Doctor.query.join(Account).filter(Account.role == "doctor").all()

    return render_template("admin/admin_doctors.html", doctors=doctors)


@app.route("/admin/patients")
@login_required
def admin_patients():
    if current_user.role != "admin":
        return "Unauthorized", 403

    patients = Patient.query.join(Account).filter(Account.role == "patient").all()

    return render_template("admin/admin_patients.html", patients=patients)


# -------------------------------------------------------
# DOCTOR ROUTES
# -------------------------------------------------------

@app.route("/doctor/dashboard")
@login_required
def doctor_dashboard():
    if current_user.role != "doctor":
        return "Unauthorized", 403

    doctor = Doctor.query.filter_by(account_id=current_user.id).first()
    return render_template("doctor/dashboard.html", doctor=doctor)


# -------------------------------------------------------
# PATIENT ROUTES
# -------------------------------------------------------

@app.route("/patient/dashboard")
@login_required
def patient_dashboard():
    if current_user.role != "patient":
        return "Unauthorized", 403

    patient = Patient.query.filter_by(account_id=current_user.id).first()
    return render_template("patient/dashboard.html", patient=patient)


# -------------------------------------------------------
# INITIALIZE DATABASE
# -------------------------------------------------------
@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
