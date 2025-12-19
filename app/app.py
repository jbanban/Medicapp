from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import numpy as np
from datetime import datetime
from collections import Counter
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy import Integer, String, ForeignKey, TIMESTAMP, Date, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import json
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'wowixczzzzz'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fernandez_clinic.db'
db = SQLAlchemy(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class Base(DeclarativeBase):
    pass


class Patient(db.Model):
    __tablename__ = "patient"

    patient_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.account_id"), unique=True, nullable=False
    )

    firstname: Mapped[str] = mapped_column(String(50))
    middlename: Mapped[str] = mapped_column(String(50), nullable=True)
    lastname: Mapped[str] = mapped_column(String(50))
    gender: Mapped[str] = mapped_column(String(10))
    birthdate: Mapped[date] = mapped_column(Date)
    age: Mapped[int] = mapped_column(Integer)
    blood_type: Mapped[str] = mapped_column(String(5), nullable=True)
    civil_status: Mapped[str] = mapped_column(String(20), nullable=True)
    current_address: Mapped[str] = mapped_column(String(200))
    permanent_address: Mapped[str] = mapped_column(String(200))
    zipcode: Mapped[str] = mapped_column(String(10), nullable=True)
    phone: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(100), nullable=True)

    ec_name: Mapped[str] = mapped_column(String(100), nullable=True)
    ec_phone: Mapped[str] = mapped_column(String(20), nullable=True)
    ec_relation: Mapped[str] = mapped_column(String(50), nullable=True)
    ec_address: Mapped[str] = mapped_column(String(200), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    account: Mapped["Account"] = relationship(back_populates="patient")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="patient")
    records: Mapped[list["MedicalRecord"]] = relationship(back_populates="patient")

    history: Mapped["PatientHistoryBackground"] = relationship(
        back_populates="patient", uselist=False
    )

class PatientHistoryBackground(db.Model):
    __tablename__ = "patient_history_background"

    phb_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patient.patient_id"), nullable=False
    )
    pastMedicalHistory: Mapped[str] = mapped_column(String(500), nullable=True)
    beenHospitalized: Mapped[str] = mapped_column(String(10), nullable=True)
    hadSurgery: Mapped[str] = mapped_column(String(10), nullable=True)
    allergies: Mapped[str] = mapped_column(String(500), nullable=True)
    ongoingMedications: Mapped[str] = mapped_column(String(500), nullable=True)
    familyHistory: Mapped[str] = mapped_column(String(500), nullable=True)

    patient: Mapped["Patient"] = relationship(back_populates="history")

class Doctor(db.Model):
    __tablename__ = "doctor"

    doctor_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firstname: Mapped[str] = mapped_column(String(50))
    middlename: Mapped[str] = mapped_column(String(50), nullable=True)
    lastname: Mapped[str] = mapped_column(String(50))
    age: Mapped[int] = mapped_column(Integer)
    bloodtype: Mapped[str] = mapped_column(String(5), nullable=True)
    height: Mapped[str] = mapped_column(String, nullable=True)
    weight: Mapped[str] = mapped_column(String, nullable=True)
    specialization: Mapped[str] = mapped_column(String(100))
    gender: Mapped[str] = mapped_column(String(20))
    dob: Mapped[str] = mapped_column(String(10))
    pob: Mapped[str] = mapped_column(String(100), nullable=True)
    civilstatus: Mapped[str] = mapped_column(String(20), nullable=True)
    degree: Mapped[str] = mapped_column(String(100), nullable=True)
    nationality: Mapped[str] = mapped_column(String(50), nullable=True)
    religion: Mapped[str] = mapped_column(String(50), nullable=True)
    phone: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(100))
    account_id: Mapped[int] = mapped_column(ForeignKey("account.account_id"), unique=True)

    account: Mapped["Account"] = relationship(back_populates="doctor")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="doctor")
    records: Mapped[list["MedicalRecord"]] = relationship(back_populates="doctor")
    doctor_schedule = relationship("Doctor_Schedule", back_populates="doctor")


class Appointment(db.Model):
    __tablename__ = "appointment"

    appointment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patient.patient_id"))
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctor.doctor_id"))
    appointment_date: Mapped[str] = mapped_column(String(10))
    appointment_time: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(20))

    patient: Mapped["Patient"] = relationship(back_populates="appointments")
    doctor: Mapped["Doctor"] = relationship(back_populates="appointments")
    payments: Mapped[list["PaymentRecord"]] = relationship(back_populates="appointment")


class MedicalRecord(db.Model):
    __tablename__ = "medical_record"

    record_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patient.patient_id"))
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctor.doctor_id"))
    schedule_id: Mapped[int] = mapped_column(ForeignKey("doctor_schedule.doctor_schedule_id"))
    visit_date: Mapped[str] = mapped_column(String(10))
    diagnosis: Mapped[str] = mapped_column(String)
    notes: Mapped[str] = mapped_column(String)

    patient: Mapped["Patient"] = relationship(back_populates="records")
    doctor: Mapped["Doctor"] = relationship(back_populates="records")
    doctor_schedule: Mapped["Doctor_Schedule"] = relationship(back_populates="record")


class MedicalVisibility(db.Model):
    __tablename__ = "medical_visibility"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, nullable=False, unique=True)
    encrypted_state = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Doctor_Schedule(db.Model):
    __tablename__ = "doctor_schedule"

    doctor_schedule_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctor.doctor_id"))
    vacant_date: Mapped[str] = mapped_column(String(20))
    vacant_time: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))

    doctor = relationship("Doctor", back_populates="doctor_schedule")
    record = relationship("MedicalRecord", back_populates="doctor_schedule")


class PaymentRecord(db.Model):
    __tablename__ = "payment_record"

    payment_record_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointment.appointment_id"))
    amount: Mapped[str] = mapped_column(String(20))
    payment_status: Mapped[str] = mapped_column(String(20))

    appointment: Mapped["Appointment"] = relationship(back_populates="payments")


class Account(db.Model):
    __tablename__ = "account"
    account_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(20))

    patient = relationship("Patient", back_populates="account", uselist=False)
    doctor = relationship("Doctor", back_populates="account", uselist=False)

class User(db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, autoincrement=True) 
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(100))

# appointments = Appointment.query.all()

# APPOINTMENTS_FILE = 'appointments.json'

def load_appointments():
    """Load appointments from file"""
    global appointments
    if os.path.exists(APPOINTMENTS_FILE):
        try:
            with open(APPOINTMENTS_FILE, 'r') as f:
                appointments = json.load(f)
        except:
            appointments = []

def save_appointments():
    """Save appointments to file"""
    with open(APPOINTMENTS_FILE, 'w') as f:
        json.dump(appointments, f, indent=2)

def calculate_appointment_statistics():
    appointments = Appointment.query.all()

    if not appointments:
        return {
            "total_appointments": 0,
            "monthly_counts": {},
            "status_counts": {},
            "average_appointments_per_day": 0,
            "busiest_day_of_week": None
        }

    # Convert string date + time → datetime
    appointment_datetimes = []
    for appt in appointments:
        try:
            dt = datetime.strptime(
                f"{appt.appointment_date} {appt.appointment_time}",
                "%Y-%m-%d %H:%M"
            )
            appointment_datetimes.append(dt)
        except ValueError:
            continue  # skip malformed rows safely

    if not appointment_datetimes:
        return {
            "total_appointments": 0,
            "monthly_counts": {},
            "status_counts": {},
            "average_appointments_per_day": 0,
            "busiest_day_of_week": None
        }

    total_appointments = len(appointment_datetimes)

    # 📅 Monthly counts
    months = [dt.strftime("%Y-%m") for dt in appointment_datetimes]
    monthly_counts = dict(Counter(months))

    # 📌 Status counts
    statuses = [appt.status for appt in appointments if appt.status]
    status_counts = dict(Counter(statuses))

    # 📊 Average per day
    unique_days = set(dt.strftime("%Y-%m-%d") for dt in appointment_datetimes)
    average_per_day = round(total_appointments / len(unique_days), 2)

    # 🔥 Busiest weekday
    weekdays = [dt.strftime("%A") for dt in appointment_datetimes]
    busiest_day = Counter(weekdays).most_common(1)[0][0]

    return {
        "total_appointments": total_appointments,
        "monthly_counts": monthly_counts,
        "status_counts": status_counts,
        "average_appointments_per_day": average_per_day,
        "busiest_day_of_week": busiest_day
    }


@app.route("/api/appointments", methods=["GET"])
def get_appointments():
    appointments = Appointment.query.all()

    return jsonify({
        "success": True,
        "appointments": [
            {
                "appointment_id": appt.appointment_id,
                "patient_id": appt.patient_id,
                "doctor_id": appt.doctor_id,
                "date": appt.appointment_date,
                "time": appt.appointment_time,
                "status": appt.status
            }
            for appt in appointments
        ]
    })



@app.route("/api/appointments", methods=["POST"])
def create_appointment():
    data = request.get_json()

    required = ["patient_id", "doctor_id", "date", "time"]
    for field in required:
        if field not in data:
            return jsonify({
                "success": False,
                "message": f"Missing field: {field}"
            }), 400

    # Conflict check (STRING SAFE)
    conflict = Appointment.query.filter_by(
        appointment_date=data["date"],
        appointment_time=data["time"],
        doctor_id=data["doctor_id"]
    ).first()

    if conflict:
        return jsonify({
            "success": False,
            "message": "This time slot is already booked"
        }), 409

    appointment = Appointment(
        patient_id=data["patient_id"],
        doctor_id=data["doctor_id"],
        appointment_date=data["date"],
        appointment_time=data["time"],
        status="Pending"
    )

    db.session.add(appointment)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Appointment created successfully",
        "appointment_id": appointment.appointment_id
    }), 201



@app.route('/api/appointments/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    """Delete an appointment"""
    global appointments
    appointments = [apt for apt in appointments if apt['id'] != appointment_id]
    save_appointments()
    
    return jsonify({
        'success': True,
        'message': 'Appointment deleted successfully'
    })

@app.route('/api/availability', methods=['GET'])
def check_availability():
    """Check availability for a specific date"""
    date = request.args.get('date')
    if not date:
        return jsonify({
            'success': False,
            'message': 'Date parameter required'
        }), 400
    
    # Get booked slots for the date
    booked_slots = [apt['time'] for apt in appointments if apt['date'] == date]
    
    return jsonify({
        'success': True,
        'booked_slots': booked_slots
    })

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Logged in successfully.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            return render_template('admin/admin_login.html')
    return render_template('admin/admin_login.html')

@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        new_user = User(username=username, password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        flash('Account created!', 'success')
        return redirect(url_for('admin_login'))
    return render_template('admin/admin_register.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = Account.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.account_id
            session['role'] = user.role

            role = session['role'] 

            if role == 'doctor':
                flash('Logged in successfully.', 'success')
                return redirect(url_for('doctor_dashboard'))
            elif role == 'patient':
                flash('Logged in successfully.', 'success')
                patient_profile = db.session.query(Patient).filter_by(account_id=user.account_id).first()
                if patient_profile:
                    return redirect(url_for('patient_dashboard'))
                else:
                    return redirect(url_for('create_profile')) 
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
            return render_template('login.html')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'patient')

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register'))

        existing_user = Account.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists!", "danger")
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password, method='scrypt')
        new_account = Account(email=email, password=hashed_pw, role=role)

        db.session.add(new_account)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect(url_for('register'))

    return render_template('register.html')

@app.route("/admin/dashboard")
def admin_dashboard():
    statistics = calculate_appointment_statistics()
    return render_template(
        "admin/dashboard.html",
        statistics=statistics
    )

@app.route('/admin/patients_list')
def patients_list():
    patients = Patient.query.all()
    return render_template('admin/patients_list.html', patients=patients)

@app.route('/create_doctor_profile/<int:account_id>', methods=['GET', 'POST'])
def create_doctor_profile(account_id):
    selected_account = Account.query.get_or_404(account_id)


    if request.method == 'POST':
        new_doctor = Doctor(
            firstname=request.form['firstname'],
            middlename=request.form.get('middlename'),
            lastname=request.form['lastname'],
            age=request.form.get('age'),
            bloodtype=request.form.get('bloodtype'),
            height=request.form.get('height'),
            weight=request.form.get('weight'),
            specialization=request.form.get('specialization'),
            gender=request.form['gender'],
            dob=request.form['dob'],
            pob=request.form['pob'],
            civilstatus=request.form.get('civilstatus'),
            degree=request.form.get('degree'),
            nationality=request.form['nationality'],
            religion=request.form.get('religion'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            account_id=account_id
        )

        db.session.add(new_doctor)
        db.session.commit()

        flash("Doctor profile created successfully!", "success")
        return redirect(url_for('admin_doctors'))

    return render_template(
        'admin/create_doctor_profile.html',
        selected_account=selected_account
    )

@app.route('/edit_doctor/<int:doctor_id>', methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)

    if request.method == 'POST':

        # Update doctor fields
        doctor.firstname = request.form['firstname']
        doctor.middlename = request.form.get('middlename')
        doctor.lastname = request.form['lastname']
        doctor.age = request.form.get('age')
        doctor.bloodtype = request.form.get('bloodtype')
        doctor.height = request.form.get('height')
        doctor.weight = request.form.get('weight')
        doctor.specialization = request.form.get('specialization')
        doctor.gender = request.form['gender']
        doctor.dob = request.form.get('dob')
        doctor.pob = request.form.get('pob')
        doctor.civilstatus = request.form.get('civilstatus')
        doctor.degree = request.form.get('degree')
        doctor.nationality = request.form.get('nationality')
        doctor.religion = request.form.get('religion')
        doctor.phone = request.form.get('phone')
        doctor.email = request.form.get('email')

        db.session.commit()

        flash("Doctor profile updated successfully!", "success")
        return redirect(url_for('admin_doctors'))

    return render_template(
        'admin/edit_doctor.html',
        doctor=doctor,
    )


@app.route('/admin_reports')
def admin_reports():
    return render_template('admin/admin_reports.html')

@app.route('/admin_doctors', methods=['GET', 'POST'])
def admin_doctors():
    account_id = request.args.get('account_id', type=int)
    edit_account = Account.query.get(account_id) if account_id else None

    if request.method == 'POST':
        account_id = request.form.get('account_id')
        email = request.form['email']
        password = request.form.get('password')

        # EDIT
        if account_id:
            account = Account.query.get(account_id)
            account.email = email
            if password:
                account.password = generate_password_hash(password)
            db.session.commit()
            flash("Account updated successfully!", "success")

        # CREATE
        else:
            if Account.query.filter_by(email=email).first():
                flash("Email already exists!", "danger")
                return redirect(url_for('admin_doctors'))

            new_account = Account(
                email=email,
                password=generate_password_hash(password),
                role='doctor'
            )
            db.session.add(new_account)
            db.session.commit()
            flash("Doctor account created!", "success")

        return redirect(url_for('admin_doctors'))

    accounts = (
        db.session.query(Account)
        .outerjoin(Doctor, Doctor.account_id == Account.account_id)
        .filter(Account.role == 'doctor')
        .all()
    )

    doctors = Doctor.query.all()

    return render_template('admin/admin_doctors.html', 
                           accounts=accounts, 
                           doctors=doctors,
                           edit_account=edit_account
                           )

@app.route('/doctor/dashboard')
def doctor_dashboard():
    if 'role' not in session or session['role'] != 'doctor':
        return redirect(url_for('unauthorized'))
    user_id = session.get('user_id')

    doctor = Doctor.query.filter_by(account_id=user_id).first()
    if not doctor:
        flash("Please complete your doctor profile.", "warning")
        return redirect(url_for('doctor_dashboard'))

    appointments = Appointment.query.filter_by(doctor_id=doctor.doctor_id).all()
    
    return render_template('doctor/doctor_dashboard.html',
                           doctor=doctor,
                           appointments=appointments
                           )

@app.route('/doctor/patients')
def doctor_patients():
    if session.get('role') != 'doctor':
        return redirect(url_for('unauthorized'))

    user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(account_id=user_id).first()

    if not doctor:
        flash("Please complete your doctor profile.", "warning")
        return redirect(url_for('create_doctor_profile'))

    patients = (
        Patient.query
        .join(Appointment)
        .filter(Appointment.doctor_id == doctor.doctor_id)
        .distinct()
        .all()
    )

    return render_template(
        'doctor/doctor_patients.html',
        doctor=doctor,
        patients=patients
    )

@app.route('/doctors/appointment')  
def doctors_appointment():
    if 'role' not in session or session['role'] != 'doctor':
        return redirect(url_for('unauthorized'))

    user_id = session.get('user_id')

    doctor = Doctor.query.filter_by(account_id=user_id).first()
    if not doctor:
        return redirect(url_for('unauthorized'))

    appointments = Appointment.query.filter_by(
        doctor_id=doctor.doctor_id
    ).all()

    return render_template(
        'doctor/doctor_appointment.html', 
        appointments=appointments,
        doctor=doctor
    )


@app.route('/doctors/schedule', methods=['GET', 'POST'])
def doctors_schedule():
    if 'role' not in session or session['role'] != 'doctor':
        return redirect(url_for('unauthorized'))

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    # Get doctor profile
    doctor = Doctor.query.filter_by(account_id=user_id).first()
    if not doctor:
        flash("Please complete your doctor profile first.", "warning")
        return redirect(url_for('unauthorized'))

    if request.method == 'POST':
        preferred_date = request.form['preferred_date']
        preferred_time = request.form['preferred_time']

        new_schedule = Doctor_Schedule(
            doctor_id=doctor.doctor_id,
            vacant_date=preferred_date,
            vacant_time=preferred_time,
            status='Available'
        )
        db.session.add(new_schedule)
        db.session.commit()

        flash("Schedule added successfully.", "success")
        return redirect(url_for('doctors_schedule'))

    schedules = Doctor_Schedule.query.filter_by(
        doctor_id=doctor.doctor_id
    ).all()

    return render_template(
        'doctor/calendar.html',
        schedules=schedules,
        doctor=doctor
    )

@app.route('/available_doctors')
def available_doctors():
    if 'role' not in session or session['role'] != 'patient':
        return redirect(url_for('unauthorized'))
    user_id = session.get('user_id')

    profile = Patient.query.filter_by(account_id=user_id).first()
    doctors = Doctor.query.all()
    return render_template('patient/available_doctors.html', 
                           doctors=doctors,
                           profile=profile)

@app.route('/doctor_profile/<int:doctor_id>', methods=['GET', 'POST'])
def doctor_profile(doctor_id):
    if session.get('role') != 'doctor':
        return redirect(url_for('unauthorized'))

    user_id = session.get('user_id')

    doctor = Doctor.query.get_or_404(doctor_id)

    # 🔒 SECURITY CHECK
    if doctor.account_id != user_id:
        return redirect(url_for('unauthorized'))

    return render_template(
        'doctor/doctor_profile.html',
        doctor=doctor
    )

@app.route('/doctors/accept_appointment/<int:appointment_id>', methods=['POST'])
def accept_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return redirect(url_for('doctors_appointment'))
    appointment.status = 'Accepted'
    db.session.commit()
    return redirect(url_for('doctors_appointment'))

@app.route('/doctors/reject_appointment/<int:appointment_id>', methods=['POST'])
def reject_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return redirect(url_for('doctors_appointment'))
    appointment.status = 'Rejected'
    db.session.commit()
    return redirect(url_for('doctors_appointment'))

@app.route('/doctors/done_appointment/<int:appointment_id>', methods=['POST'])
def done_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return redirect(url_for('doctors_appointment'))
    appointment.status = 'Done'
    db.session.commit()
    return redirect(url_for('doctors_appointment'))

@app.route('/doctors/delete_schedule/<int:doctor_schedule_id>', methods=['POST'])
def delete_doctor_schedule(doctor_schedule_id):
    schedule = Doctor_Schedule.query.get(doctor_schedule_id)
    if not schedule:
        return redirect(url_for('doctors_schedule'))
    db.session.delete(schedule)
    db.session.commit()
    return redirect(url_for('doctors_schedule'))

@app.route('/medical_records', methods=['GET','POST'])
def medical_records():
    pass

@app.route('/patient/dashboard')
def patient_dashboard():
    if 'role' not in session or session['role'] != 'patient':
        return redirect(url_for('unauthorized'))
    user_id = session.get('user_id')

    profile = Patient.query.filter_by(account_id=user_id).first()
    if not profile:
        return redirect(url_for('create_profile'))
    
    appointments = Appointment.query.filter_by(patient_id=user_id).all()
    doctors = Account.query.filter_by(role='doctor').all()

    return render_template('patient/patient_dashboard.html',
                           profile=profile, 
                           appointments=appointments,
                           doctors=doctors
                           )

@app.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    # Check if user already has patient profile
    existing = Patient.query.filter_by(account_id=user_id).first()
    if existing:
        flash("You already created your profile.", "warning")
        return redirect(url_for('patient_profile'))

    if request.method == 'POST':
        # ------------ BASIC PATIENT INFO ------------
        firstname = request.form.get('firstname', "").strip()
        middlename = request.form.get('middlename', "").strip()
        lastname = request.form.get('lastname', "").strip()
        gender = request.form.get('gender', "").strip()
        birthdate_str = request.form.get('birthdate', "").strip()
        age = request.form.get('age', "").strip()
        blood_type = request.form.get('blood_type', "").strip()
        civil_status = request.form.get('civil_status', "").strip()
        current_address = request.form.get('current_address', "").strip()
        permanent_address = request.form.get('permanent_address', "").strip()
        zipcode = request.form.get('zipcode', "").strip()
        phone = request.form.get('phone', "").strip()
        email = request.form.get('email', "").strip()
        
        # ------------ EMERGENCY CONTACT INFO ------------
        ec_name = request.form.get('ec_name', "").strip()
        ec_relation = request.form.get('ec_relation', "").strip()
        ec_phone = request.form.get('ec_phone', "").strip()
        ec_address = request.form.get('ec_address', "").strip()

        # ------------ PATIENT HISTORY QUESTIONS ------------
        pastMedicalHistory = request.form.get('pastMedicalHistory', "").strip()
        beenHospitalized = request.form.get('beenHospitalized', "").strip()
        hadSurgery = request.form.get('hadSurgery', "").strip()
        allergies = request.form.get('allergies', "").strip()
        ongoingMedications = request.form.get('ongoingMedications', "").strip()
        familyHistory = request.form.get('familyHistory', "").strip()

        # Convert birthdate string to date object
        if not birthdate_str:
            flash("Birthdate is required.", "warning")
            return redirect(url_for('create_profile'))

        try:
            birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid birthdate format.", "warning")

        # ------------ REQUIRED FIELD VALIDATION ------------
        missing_fields = []

        required_fields = {
            "First Name": firstname,
            "Last Name": lastname,
            "Phone Number": phone,
            "Birthdate": birthdate,
            "Email": email,
            "Gender": gender,
            "Permanent Address": permanent_address,
            "Past Medical History": pastMedicalHistory,
            "Hospitalized Before": beenHospitalized,
            "Had Surgery": hadSurgery,
            "Allergies": allergies,
            "Ongoing Medications": ongoingMedications,
            "Family History": familyHistory
        }

        for label, value in required_fields.items():
            if not value:
                missing_fields.append(label)

        if missing_fields:
            flash(f"Please complete all required fields: /n. {', '.join(missing_fields)}", "warning")
            return redirect(url_for('create_profile'))

        # ------------ PHONE VALIDATION ------------
        if len(phone) < 10:
            flash("Phone number is too short.", "warning")
            return redirect(url_for('create_profile'))

        if len(phone) > 13:
            flash("Phone number is too long.", "warning")
            return redirect(url_for('create_profile'))

        # ------------ CREATE PATIENT & HISTORY RECORDS ------------
        try:
            patient = Patient(
                firstname=firstname,
                middlename=middlename,
                lastname=lastname,
                gender=gender,
                birthdate=birthdate,
                age=age,
                blood_type=blood_type,
                civil_status=civil_status,
                current_address=current_address,
                permanent_address=permanent_address,
                zipcode=zipcode,
                phone=phone,
                email=email,
                ec_name=ec_name,
                ec_relation=ec_relation,
                ec_phone=ec_phone,
                ec_address=ec_address,
                account_id=user_id
            )

            db.session.add(patient)
            db.session.flush()  # ensures patient_id is available

            history = PatientHistoryBackground(
                patient_id=patient.patient_id,
                pastMedicalHistory=pastMedicalHistory,
                beenHospitalized=beenHospitalized,
                hadSurgery=hadSurgery,
                allergies=allergies,
                ongoingMedications=ongoingMedications,
                familyHistory=familyHistory
            )

            db.session.add(history)
            db.session.commit()

            flash("Profile successfully created!", "success")
            return redirect(url_for('patient_profile'))

        except Exception as e:
            db.session.rollback()
            flash("An error occurred while creating your profile.", "danger")
            print("Error:", e)
            return redirect(url_for('create_profile'))

    return render_template(
        'patient/create_profile.html',
        data=request.form
    )


@app.route('/patient_profile')
def patient_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    profile = Patient.query.filter_by(account_id=user_id).first()
    if not profile:
        return redirect(url_for('create_profile'))
    
    history = PatientHistoryBackground.query.filter_by(
        patient_id=profile.patient_id
    ).first()

    visibility = MedicalVisibility.query.filter_by(
        patient_id=profile.patient_id
    ).first()

    return render_template(
        "patient/patient_profile.html",
        profile=profile,
        history=history,
        encrypted_visibility=visibility.encrypted_state if visibility else None
    )

@app.route('/patient/appointment', methods=['GET', 'POST'])
def patient_appointment():
    if 'role' not in session or session['role'] != 'patient':
        return redirect(url_for('unauthorized'))
    user_id = session.get('user_id')

    profile = Patient.query.filter_by(account_id=user_id).first()
    appointments = Appointment.query.filter_by(patient_id=session.get('user_id')).all()

    return render_template('patient/patient_appointment.html', 
                           appointments=appointments,
                           profile=profile
                           )

@app.route('/doctor/<int:doctor_id>/upload-photo', methods=['POST'])
def upload_doctor_photo(doctor_id):

    user_id = session.get('user_id')

    # Get doctor based on URL (doctor_id), not user_id
    doctor = Doctor.query.get_or_404(doctor_id)

    # Authorization check: ensure logged-in doctor owns this profile
    if doctor.account_id != user_id:
        return redirect(url_for('unauthorized'))

    # -------- FILE VALIDATION --------
    if "photo" not in request.files:
        flash("No file part in request.", "danger")
        return redirect(url_for('doctor_profile', doctor_id=doctor_id))

    file = request.files["photo"]

    if file.filename == '':
        flash("No file selected.", "danger")
        return redirect(url_for('doctor_profile', doctor_id=doctor_id))

    if file and allowed_image(file.filename):

        ext = file.filename.rsplit('.', 1)[1].lower()

        new_filename = f"{doctor.lastname.lower()}_{doctor.firstname.lower()}.{ext}"
        new_filename = secure_filename(new_filename)

        upload_folder = os.path.join('static', 'uploads', 'doctors')
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, new_filename)

        if doctor.profile_image:
            old_path = os.path.join('static', doctor.profile_image)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except:
                    pass

        file.save(file_path)

        doctor.profile_image = f"uploads/doctors/{new_filename}"
        db.session.commit()

        flash("Profile picture updated!", "success")

    else:
        flash("Invalid file type. Only JPG and PNG allowed.", "danger")

    return redirect(url_for('doctor_profile', doctor_id=doctor_id))



@app.route('/doctors/view_available/time_for_<int:doctor_id>')
def view_available_time(doctor_id):
    if 'role' not in session or session['role'] != 'patient':
        return redirect(url_for('unauthorized'))
    user_id = session.get('user_id')

    profile = Patient.query.filter_by(account_id=user_id).first()
    schedules = Doctor_Schedule.query.filter_by(doctor_id=doctor_id).all()
    return render_template('patient/view_available_time.html', 
                           schedules=schedules,
                           profile=profile
                           )

@app.route('/book_appointment/<int:doctor_schedule_id>', methods=['GET', 'POST'])
def book_appointment(doctor_schedule_id):
    if 'role' not in session or session['role'] != 'patient':
        return redirect(url_for('unauthorized'))
    user_id = session.get('user_id')

    schedule = Doctor_Schedule.query.get(doctor_schedule_id)

    if not schedule:
        flash('Schedule not found.', 'error')
        return redirect(url_for('patient_appointment'))

    if request.method == 'POST':
        patient_id = user_id
        preferred_date = request.form['vacant_date']
        preferred_time = request.form['vacant_time']
        doctor_id = request.form['doctor_id']
        status = 'Pending'

        # Create appointment
        new_appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=preferred_date,
            appointment_time=preferred_time,
            status=status
        )
        db.session.add(new_appointment)

        schedule.status = 'Booked'
        print("Before Commit:", schedule.status)
        db.session.commit()
        print("Before Commit:", schedule.status)
        flash('Appointment booked successfully!', 'success')

        return redirect(url_for('patient_appointment'))

    profile = Patient.query.filter_by(account_id=user_id).first()

    return render_template('patient/book_appointment.html', 
                           profile=profile
                           )

@app.route('/patient/reschedule_appointment/<int:appointment_id>', methods=['GET', 'POST'])
def reschedule_appointment(appointment_id):
    if 'role' not in session or session['role'] != 'patient':
        return redirect(url_for('unauthorized'))
    print("request is as follows = ",request.form)  # DEBUG: Print form content
    appointment = Appointment.query.get_or_404(appointment_id)

    if request.method == 'POST':
        preferred_date = request.form['preferred_date']
        preferred_time = request.form['preferred_time']

        if not preferred_date or not preferred_time:
            flash('Missing date or time.')
            return redirect(reschedule_appointment(appointment_id))
        
        appointment.appointment_date = preferred_date
        appointment.appointment_time = preferred_time
        db.session.commit()

        return redirect(url_for('patient_appointment'))

    return render_template('patient/reschedule_appointment.html', appointment=appointment)

@app.route('/patient/cancel_appointment/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return redirect(url_for('patient_appointment'))

    appointment.status = 'Cancelled'
    db.session.commit()

    return redirect(url_for('patient_appointment'))

@app.route('/request_appointment', methods=['GET', 'POST'])
def request_appointment():
    if 'role' not in session or session['role'] != 'patient':
        return redirect(url_for('unauthorized'))
    user_id = session.get('user_id')

    doctors = Doctor.query.all()

    if request.method == 'POST':
        appointment_date = request.form['preferred_date']
        appointment_time = request.form['preferred_time']
        doctor_id = request.form['doctor_id']
        status = 'Pending'

        new_appointment = Appointment(
            patient_id=user_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status=status
        )

        db.session.add(new_appointment)
        db.session.commit()

        return redirect(url_for('request_appointment'))
    
    profile = Patient.query.filter_by(account_id=user_id).first()

    return render_template('patient/request_appointment.html', 
                           doctors=doctors,
                           profile=profile
                           )


@app.route('/api/medical-visibility/save', methods=['POST'])
def save_medical_visibility():
    if 'user_id' not in session or session.get('role') != 'patient':
        return {"error": "Unauthorized"}, 401

    data = request.json
    patient_id = data.get('patient_id')
    encrypted_state = data.get('encrypted_state')

    record = MedicalVisibility.query.filter_by(patient_id=patient_id).first()

    if record:
        record.encrypted_state = encrypted_state
    else:
        record = MedicalVisibility(
            patient_id=patient_id,
            encrypted_state=encrypted_state
        )
        db.session.add(record)

    db.session.commit()
    return {"status": "saved"}


@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/unauthorized')
def unauthorized():
    return "Unauthorized access", 403

@app.route("/search")
def search():
    q = request.args.get("q")
    print(q)

    if q:
        results = Doctor.query.filter(Doctor.firstname.icontains(q) | Doctor.lastname.icontains(q)) \
        .order_by(Doctor.specialization.asc()).limit(100).all()
    else:
        results = []

    return render_template("search_results.html", results=results)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
