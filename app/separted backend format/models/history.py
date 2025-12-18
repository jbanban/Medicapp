from ..extensions import db

class PatientHistoryBackground(db.Model):
    __tablename__ = "patient_history_background"
    phb_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.patient_id"), nullable=False)

    pastMedicalHistory = db.Column(db.String(500), nullable=True)
    beenHospitalized = db.Column(db.String(10), nullable=True)
    hadSurgery = db.Column(db.String(10), nullable=True)
    allergies = db.Column(db.String(500), nullable=True)
    ongoingMedications = db.Column(db.String(500), nullable=True)
    familyHistory = db.Column(db.String(500), nullable=True)

    patient = db.relationship("Patient", back_populates="history")

    def __repr__(self):
        return f"<PatientHistory {self.patient_id}>"
