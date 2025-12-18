from flask_login import UserMixin
from datetime import datetime
from database import db

class Account(UserMixin, db.Model):
    __tablename__ = 'accounts'

    account_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fullname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    doctor_profile = db.relationship('Doctor', backref='account', uselist=False)
    patient_profile = db.relationship('Patient', backref='account', uselist=False)

    # Flask-Login required ID getter
    def get_id(self):
        return str(self.id)
    
    def __repr__(self):
        return f"<Account {self.email} ({self.role})>"

class Doctor(db.Model):
    __tablename__ = "doctor"

    doctor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(50), nullable=False)
    middlename = db.Column(db.String(50), nullable=True)
    lastname = db.Column(db.String(50), nullable=False)

    age = db.Column(db.Integer, nullable=True)
    bloodtype = db.Column(db.String(5), nullable=True)
    height = db.Column(db.String(20), nullable=True)
    weight = db.Column(db.String(20), nullable=True)

    specialization = db.Column(db.String(100), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    dob = db.Column(db.Date, nullable=True)
    pob = db.Column(db.String(100), nullable=True)
    civilstatus = db.Column(db.String(20), nullable=True)

    degree = db.Column(db.String(100), nullable=True)
    nationality = db.Column(db.String(50), nullable=True)
    religion = db.Column(db.String(50), nullable=True)

    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)

    profile_image = db.Column(db.String(255), nullable=True)

    account_id = db.Column(db.Integer, db.ForeignKey("account.account_id"), unique=True, nullable=True)

    account = db.relationship("Account", back_populates="doctor")
    appointments = db.relationship("Appointment", back_populates="doctor", cascade="all, delete-orphan")
    records = db.relationship("MedicalRecord", back_populates="doctor", cascade="all, delete-orphan")
    doctor_schedule = db.relationship("Doctor_Schedule", back_populates="doctor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Doctor {self.firstname} {self.lastname}>"


class Patient(db.Model):
    __tablename__ = "patient"
    patient_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account_id = db.Column(db.Integer, db.ForeignKey("account.account_id"), unique=True, nullable=False)

    firstname = db.Column(db.String(50), nullable=False)
    middlename = db.Column(db.String(50), nullable=True)
    lastname = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    age = db.Column(db.Integer, nullable=True)
    blood_type = db.Column(db.String(5), nullable=True)
    civil_status = db.Column(db.String(20), nullable=True)
    current_address = db.Column(db.String(200), nullable=True)
    permanent_address = db.Column(db.String(200), nullable=True)
    zipcode = db.Column(db.String(10), nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=True)

    ec_name = db.Column(db.String(100), nullable=True)
    ec_phone = db.Column(db.String(20), nullable=True)
    ec_relation = db.Column(db.String(50), nullable=True)
    ec_address = db.Column(db.String(200), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    account = db.relationship("Account", back_populates="patient")
    appointments = db.relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    records = db.relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")
    history = db.relationship("PatientHistoryBackground", back_populates="patient", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient {self.firstname} {self.lastname}>"


class PatientHistoryBackground(db.Model):
    __tablename__ = "patient_history_background"
    history_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.patient_id"))
    medical_history = db.Column(db.String)
    surgical_history = db.Column(db.String)
    family_history = db.Column(db.String)
    social_history = db.Column(db.String)

    patient = db.relationship("Patient", back_populates="history")

    def __repr__(self):
        return f"<PatientHistoryBackground {self.history_id}>"


class Appointment(db.Model):
    __tablename__ = "appointment"
    appointment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.patient_id"))
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.doctor_id"))
    appointment_date = db.Column(db.String(20))
    appointment_time = db.Column(db.String(20))
    status = db.Column(db.String(20), default="Pending")

    patient = db.relationship("Patient", back_populates="appointments")
    doctor = db.relationship("Doctor", back_populates="appointments")

    def __repr__(self):
        return f"<Appointment {self.appointment_id} {self.status}>"


class MedicalRecord(db.Model):
    __tablename__ = "medical_record"
    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.patient_id"))
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.doctor_id"))
    schedule_id = db.Column(db.Integer, db.ForeignKey("doctor_schedule.doctor_schedule_id"))
    visit_date = db.Column(db.String(20))
    diagnosis = db.Column(db.String)
    notes = db.Column(db.String)

    patient = db.relationship("Patient", back_populates="records")
    doctor = db.relationship("Doctor", back_populates="records")
    doctor_schedule = db.relationship("Doctor_Schedule", back_populates="record")

    def __repr__(self):
        return f"<MedicalRecord {self.record_id}>"


class Doctor_Schedule(db.Model):
    __tablename__ = "doctor_schedule"
    doctor_schedule_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.doctor_id"))
    schedule_date = db.Column(db.String(20))
    start_time = db.Column(db.String(20))
    end_time = db.Column(db.String(20))

    doctor = db.relationship("Doctor", back_populates="doctor_schedule")
    record = db.relationship("MedicalRecord", back_populates="doctor_schedule", uselist=False)

    def __repr__(self):
        return f"<Doctor_Schedule {self.doctor_schedule_id} {self.schedule_date}>"


class Payment(db.Model):
    __tablename__ = "payment"
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointment.appointment_id"))
    amount = db.Column(db.Float)
    payment_date = db.Column(db.String(20))
    payment_method = db.Column(db.String(50))

    appointment = db.relationship("Appointment", back_populates="payments")

    def __repr__(self):
        return f"<Payment {self.payment_id} Amount: {self.amount}>"

