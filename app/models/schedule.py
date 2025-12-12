from ..extensions import db

class Doctor_Schedule(db.Model):
    __tablename__ = "doctor_schedule"
    doctor_schedule_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.doctor_id"))
    vacant_date = db.Column(db.String(50))
    vacant_time = db.Column(db.String(50))
    status = db.Column(db.String(20), default="Available")

    doctor = db.relationship("Doctor", back_populates="doctor_schedule")
    record = db.relationship("MedicalRecord", back_populates="doctor_schedule")

    def __repr__(self):
        return f"<Doctor_Schedule {self.doctor_schedule_id}>"
