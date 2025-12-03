from flask import Flask, render_template, request, redirect, url_for, session, flash
import numpy as np
from datetime import datetime
from collections import Counter
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy import Integer, String, ForeignKey, TIMESTAMP, Date, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wowixczzzzz'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fernandez_clinic.db'
db = SQLAlchemy(app)


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
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="appointment")


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


class Doctor_Schedule(db.Model):
    __tablename__ = "doctor_schedule"

    doctor_schedule_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctor.doctor_id"))
    vacant_date: Mapped[str] = mapped_column(String(20))
    vacant_time: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))

    doctor = relationship("Doctor", back_populates="doctor_schedule")
    record = relationship("MedicalRecord", back_populates="doctor_schedule")


class Service(db.Model):
    __tablename__ = "service"

    service_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String)
    fee: Mapped[str] = mapped_column(String(20))


class Invoice(db.Model):
    __tablename__ = "invoice"

    invoice_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointment.appointment_id"))
    service_id: Mapped[int] = mapped_column(ForeignKey("service.service_id"))
    amount: Mapped[str] = mapped_column(String(20))
    payment_status: Mapped[str] = mapped_column(String(20))

    appointment: Mapped["Appointment"] = relationship(back_populates="invoices")
    service: Mapped["Service"] = relationship()


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

def calculate_appointment_statistics():
    appointments = db.session.query(Appointment).all()

    if not appointments:
        return {
            'total_appointments': 0,
            'monthly_counts': {},
            'status_counts': {},
            'average_appointments_per_day': 0,
            'busiest_day_of_week': None
        }

    appointment_datetimes = np.array([
        datetime.strptime(f"{appt.appointment_date} {appt.appointment_time}", '%Y-%m-%d %H:%M')
        for appt in appointments
    ])

    # Total number of appointments
    total_appointments = len(appointments)

    # Monthly appointment counts
    months = [date.strftime('%Y-%m') for date in appointment_datetimes]
    monthly_counts = Counter(months)

    # Appointment status counts
    statuses = [appt.status for appt in appointments]
    status_counts = Counter(statuses)

    # Average appointments per day
    if appointment_datetimes.size > 0:
        unique_days = np.unique(appointment_datetimes.astype('datetime64[D]'))
        average_appointments_per_day = total_appointments / len(unique_days)
    else:
        average_appointments_per_day = 0

    # Busiest day of the week
    if appointment_datetimes.size > 0:
        days_of_week = [date.strftime('%A') for date in appointment_datetimes]
        day_counts = Counter(days_of_week)
        busiest_day = day_counts.most_common(1)[0][0]
    else:
        busiest_day = None

    return {
        'total_appointments': total_appointments,
        'monthly_counts': dict(monthly_counts),
        'status_counts': dict(status_counts),
        'average_appointments_per_day': round(average_appointments_per_day, 2),
        'busiest_day_of_week': busiest_day
    }

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

@app.route('/admin/dashboard')
def admin_dashboard():
    statistics = calculate_appointment_statistics()
    return render_template('admin/admin_dashboard.html', statistics=statistics)

@app.route('/patients_list')
def patients_list():
    patients = Patient.query.all()
    return render_template('admin/patients_list.html', patients=patients)

@app.route('/view_doctor', methods=['GET', 'POST'])
def view_doctor():
    account_id = request.args.get('account_id', type=int)
    selected_account = None

    if account_id:
        selected_account = Account.query.get(account_id)
        
    accounts = (
        db.session.query(Account)
        .outerjoin(Doctor, Doctor.account_id == Account.account_id)
        .filter(Account.role == 'doctor', Doctor.account_id.is_(None))
        .all()
    )
    selected_account = None

    if request.method == 'POST':
        account_id = request.form['account_id']
        selected_account = Account.query.get(account_id)

        new_doctor = Doctor(
            firstname=request.form['firstname'],
            middlename=request.form['middlename'],
            lastname=request.form['lastname'],
            age=request.form['age'],
            bloodtype=request.form['bloodtype'],
            height=request.form['height'],
            weight=request.form['weight'],
            specialization=request.form['specialization'],
            gender=request.form['gender'],
            dob=request.form['dob'],
            pob=request.form['pob'],
            civilstatus=request.form.get('civilstatus'),
            degree=request.form.get('degree'),
            nationality=request.form['nationality'],
            religion=request.form['religion'],
            phone=request.form['phone'],
            email=request.form['email'],
            account_id=account_id
        )

        db.session.add(new_doctor)
        db.session.commit()

        return redirect(url_for('admin_doctors'))
    return render_template('admin/view_doctor.html', 
                           accounts=accounts, 
                           selected_account=selected_account)

@app.route('/admin_reports')
def admin_reports():
    return render_template('admin/admin_reports.html')

@app.route('/admin_doctors', methods=['GET', 'POST'])
def admin_doctors():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = 'doctor'

        if Account.query.filter_by(email=email).first():
            flash("Email already exists!", "danger")
            return redirect(url_for('admin_doctors'))

        hashed_pw = generate_password_hash(password)
        new_account = Account(email=email, password=hashed_pw, role=role)
        db.session.add(new_account)
        db.session.commit()

        flash("Doctor account created!", "success")
        return redirect(url_for('admin_doctors'))

    doctors = Account.query.filter_by(role='doctor').all()
    return render_template('admin/admin_doctors.html', doctors=doctors)

@app.route('/doctor/dashboard')
def doctor_dashboard():
    if 'role' not in session or session['role'] != 'doctor':
        return redirect(url_for('unauthorized'))
    return render_template('doctor/doctor_dashboard.html')

@app.route('/doctors/patients')
def doctors_patient():
    if 'role' not in session or session['role'] != 'doctor':
        return redirect(url_for('unauthorized'))
    user_id = session.get('user_id')
    
    patients = db.session.query(Patient).join(Appointment).filter(Appointment.doctor_id == user_id,Appointment.status == 'Accepted').all()
    return render_template('doctor/doctor_patients.html', patients=patients)

@app.route('/doctors/appointment')  
def doctors_appointment():
    if 'role' not in session or session['role'] != 'doctor':
        return redirect(url_for('unauthorized'))
    user_id = session.get('user_id')

    # appointments = db.session.query(Appointment).\
    #     join(Doctor, Appointment.doctor_id == Doctor.doctor_id).\
    #     join(Account, Doctor.account_id == Account.account_id).\
    #     filter(Account.account_id == user_id).all()

    appointments = Appointment.query.filter_by(doctor_id=user_id).all()
    return render_template('doctor/doctor_appointment.html', appointments=appointments)

@app.route('/doctors/schedule', methods=['GET', 'POST'])
def doctors_schedule():
    if 'role' not in session or session['role'] != 'doctor':
        return redirect(url_for('unauthorized'))
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    if request.method == 'POST':
        doctor_id = session.get('user_id')
        preferred_date = request.form['preferred_date']
        preferred_time = request.form['preferred_time']
        status = 'Available'

        new_schedule = Doctor_Schedule(doctor_id=doctor_id, 
                                       vacant_date=preferred_date,
                                       vacant_time=preferred_time, 
                                       status=status)
        db.session.add(new_schedule)
        db.session.commit()
        return redirect(url_for('doctors_schedule'))
    
    schedules = Doctor_Schedule.query.filter_by(doctor_id=user_id).all()

    return render_template('doctor/open_schedule.html', schedules=schedules)

@app.route('/available_doctors')
def available_doctors():
    doctors = Doctor.query.all()
    return render_template('patient/available_doctors.html', doctors=doctors)

@app.route('/doctors/profile')
def doctors_profile():
    if 'role' not in session or session['role'] != 'doctor':
        return redirect(url_for('unauthorized'))
    user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(account_id=user_id).first()
    return render_template('doctor/doctor_profile.html', doctor=doctor)

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

    return render_template('patient/patient_dashboard.html',profile=profile, appointments=appointments)

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
    
    history = PatientHistoryBackground.query.filter_by(patient_id=Patient.patient_id).first()

    return render_template('patient/patient_profile.html', 
                           profile=profile, 
                           history=history
    )

@app.route('/patient/appointment', methods=['GET', 'POST'])
def patient_appointment():
    if 'role' not in session or session['role'] != 'patient':
        return redirect(url_for('unauthorized'))
    appointments = Appointment.query.filter_by(patient_id=session.get('user_id')).all()

    return render_template('patient/patient_appointment.html', appointments=appointments)

@app.route('/doctors/view_available/time_for_<int:doctor_id>')
def view_available_time(doctor_id):
    if 'role' not in session or session['role'] != 'patient':
        return redirect(url_for('unauthorized'))
    schedules = Doctor_Schedule.query.filter_by(doctor_id=doctor_id).all()
    return render_template('patient/view_available_time.html', schedules=schedules)

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

    return render_template('patient/book_appointment.html')

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

@app.route('/create_appointment', methods=['GET', 'POST'])
def create_appointment():
    if 'role' not in session or session['role'] != 'patient':
        return redirect(url_for('unauthorized'))
    doctors = Doctor.query.all()

    user_id = session.get('user_id')

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

        return redirect(url_for('create_appointment'))
    
    return render_template('patient/create_appointment.html', doctors=doctors)

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/unauthorized')
def unauthorized():
    return "Unauthorized access", 403

@app.route('/profile/<int:user_id>', methods=['GET'])
def profile(user_id):
    user = User.query.get(user_id)
    return render_template('profile.html',user=user)

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
