from datetime import datetime
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, DateTime, ForeignKey, JSON
from app.extensions import db


class AppointmentVisibility(db.Model):
    __tablename__ = "appointment_visibility"

    # ---------------- PRIMARY KEY ----------------
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # ---------------- FOREIGN KEY ----------------
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patient.patient_id"),
        nullable=False
    )

    # ---------------- VISIBILITY METADATA ----------------
    visibility_meta: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSON),
        nullable=False,
        default=dict
    )

    # ---------------- METADATA ----------------
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


    # ---------------- RELATIONSHIP ----------------
    patient: Mapped["Patient"] = relationship(
        back_populates="appointment_visibility"
    )
