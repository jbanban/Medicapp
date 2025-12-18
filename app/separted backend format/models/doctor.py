from ..extensions import db

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
    account_id = db.Column(db.Integer, db.ForeignKey("account.account_id"), unique=True, nullable=True)

    account = db.relationship("Account", back_populates="doctor")
    appointments = db.relationship("Appointment", back_populates="doctor", cascade="all, delete-orphan")
    records = db.relationship("MedicalRecord", back_populates="doctor", cascade="all, delete-orphan")
    doctor_schedule = db.relationship("Doctor_Schedule", back_populates="doctor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Doctor {self.firstname} {self.lastname}>"
