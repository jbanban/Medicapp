from ..extensions import db

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
