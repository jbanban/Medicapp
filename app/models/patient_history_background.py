from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, DateTime, ForeignKey
from app.extensions import db
from app.security.encrypted_column import EncryptedColumn


class PatientHistoryBackground(db.Model):
    __tablename__ = "patient_history_background"

    phb_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patient.patient_id"),
        nullable=False
    )

    # ---------------- MEDICAL HISTORY (ENCRYPTED) ----------------
    pastMedicalHistory: Mapped[str] = mapped_column(EncryptedColumn, nullable=True)
    beenHospitalized: Mapped[str] = mapped_column(EncryptedColumn, nullable=True)
    hadSurgery: Mapped[str] = mapped_column(EncryptedColumn, nullable=True)
    allergies: Mapped[str] = mapped_column(EncryptedColumn, nullable=True)
    ongoingMedications: Mapped[str] = mapped_column(EncryptedColumn, nullable=True)
    familyHistory: Mapped[str] = mapped_column(EncryptedColumn, nullable=True)

    # ---------------- METADATA ----------------
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # ---------------- RELATIONSHIPS ----------------
    patient: Mapped["Patient"] = relationship(back_populates="history")
