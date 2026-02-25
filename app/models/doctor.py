from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from app.extensions import db

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.appointment import Appointment
    from app.models.medical_record import MedicalRecord
    from app.models.doctor_schedule import Doctor_Schedule
    from app.models.doctor_secretary import Doctor_Secretary

class Doctor(db.Model):
    __tablename__ = "doctor"

    doctor_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("account.account_id"), unique=True)
    firstname: Mapped[str] = mapped_column(String(50), nullable=False)
    middlename: Mapped[str] = mapped_column(String(50), nullable=True)
    lastname: Mapped[str] = mapped_column(String(50), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    bloodtype: Mapped[str] = mapped_column(String(10), nullable=True)
    height: Mapped[str] = mapped_column(String(10), nullable=True)
    weight: Mapped[str] = mapped_column(String(10), nullable=True)
    specialization: Mapped[str] = mapped_column(String(100), nullable=True)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    dob: Mapped[str] = mapped_column(String(10), nullable=False)
    pob: Mapped[str] = mapped_column(String(100), nullable=False)
    civilstatus: Mapped[str] = mapped_column(String(20), nullable=False)
    degree: Mapped[str] = mapped_column(String(100), nullable=False)
    nationality: Mapped[str] = mapped_column(String(100), nullable=False)
    religion: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    profile_image: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    account: Mapped["Account"] = relationship(back_populates="doctor")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="doctor")
    records: Mapped[list["MedicalRecord"]] = relationship(back_populates="doctor")
    doctor_schedule: Mapped["Doctor_Schedule"] = relationship(back_populates="doctor")
    secretary: Mapped["Doctor_Secretary"] = relationship(back_populates="doctor")
