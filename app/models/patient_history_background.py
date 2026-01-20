from datetime import datetime, date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from app.extensions import db


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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    patient: Mapped["Patient"] = relationship(back_populates="history")
