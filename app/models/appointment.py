from datetime import datetime, date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from app.security.encrypted_column import EncryptedColumn
from app.extensions import db


class Appointment(db.Model):
    __tablename__ = "appointment"

    appointment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patient.patient_id"))
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctor.doctor_id"))
    doctor_schedule_id: Mapped[int] = mapped_column(
        ForeignKey("doctor_schedule.doctor_schedule_id"),
        nullable=True
    )
    appointment_date: Mapped[str] = mapped_column(String(10))
    appointment_time: Mapped[str] = mapped_column(String(10))
    reason: Mapped[str] = mapped_column(EncryptedColumn(), nullable=True)
    notes: Mapped[str | None] = mapped_column(EncryptedColumn(), nullable=True)
    status: Mapped[str] = mapped_column(String(20))
    type: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    patient: Mapped["Patient"] = relationship(back_populates="appointments")
    doctor: Mapped["Doctor"] = relationship(back_populates="appointments")
    payments: Mapped[list["PaymentRecord"]] = relationship(back_populates="appointment")
    record: Mapped["MedicalRecord"] = relationship(
        back_populates="appointment",
        uselist=False
    )
    schedule: Mapped["Doctor_Schedule"] = relationship(back_populates="appointments")