from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Boolean, DateTime, ForeignKey
from app.extensions import db


class MedicalVisibility(db.Model):
    __tablename__ = "medical_visibility"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patient.patient_id"),
        unique=True,
        nullable=False
    )

    # ---------------- VISIBILITY FIELDS ----------------
    pastMedicalHistory: Mapped[bool] = mapped_column(Boolean, default=False)
    beenHospitalized: Mapped[bool] = mapped_column(Boolean, default=False)
    hadSurgery: Mapped[bool] = mapped_column(Boolean, default=False)
    allergies: Mapped[bool] = mapped_column(Boolean, default=False)
    ongoingMedications: Mapped[bool] = mapped_column(Boolean, default=False)
    familyHistory: Mapped[bool] = mapped_column(Boolean, default=False)
    socialHistory: Mapped[bool] = mapped_column(Boolean, default=False)
    immunizations: Mapped[bool] = mapped_column(Boolean, default=False)
    recentTravelHistory: Mapped[bool] = mapped_column(Boolean, default=False)
    otherRelevantInfo: Mapped[bool] = mapped_column(Boolean, default=False)

    # ---------------- METADATA ----------------
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # ---------------- RELATIONSHIP ----------------
    patient: Mapped["Patient"] = relationship(
        back_populates="medical_visibility"
    )
