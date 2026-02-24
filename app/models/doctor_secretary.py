from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from app.extensions import db

class Doctor_Secretary(db.Model):
    __tablename__ = "doctor_secretary"

    secretary_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    account_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("account.account_id"),
        nullable=False,
        unique=True
    )

    doctor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("doctor.doctor_id"),
        nullable=False
    )

    firstname: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    lastname: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    account = relationship("Account")
    doctor = relationship("Doctor", back_populates="secretary")