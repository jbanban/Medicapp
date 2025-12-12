from ..extensions import db
from datetime import datetime

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
