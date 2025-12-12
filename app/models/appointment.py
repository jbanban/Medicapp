from ..extensions import db

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
    invoices = db.relationship("Invoice", back_populates="appointment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Appointment {self.appointment_id} {self.status}>"
