from typing import TYPE_CHECKING
from datetime import datetime, date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from app.extensions import db
from app.security.encrypted_column import EncryptedColumn

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.appointment import Appointment
    from app.models.medical_record import MedicalRecord
    from app.models.doctor_schedule import Doctor_Schedule

class Doctor(db.Model):
    __tablename__ = "doctor"

    doctor_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("account.account_id"), unique=True)
    firstname: Mapped[str] = mapped_column(EncryptedColumn, nullable=False)
    middlename: Mapped[str] = mapped_column(EncryptedColumn, nullable=True)
    lastname: Mapped[str] = mapped_column(EncryptedColumn, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    bloodtype: Mapped[str] = mapped_column(EncryptedColumn, nullable=True)
    height: Mapped[str] = mapped_column(EncryptedColumn, nullable=True)
    weight: Mapped[str] = mapped_column(EncryptedColumn, nullable=True)
    specialization: Mapped[str] = mapped_column(EncryptedColumn, nullable=True)
    gender: Mapped[str] = mapped_column(EncryptedColumn, nullable=False)
    dob: Mapped[str] = mapped_column(EncryptedColumn, nullable=False)
    pob: Mapped[str] = mapped_column(EncryptedColumn, nullable=False)
    civilstatus: Mapped[str] = mapped_column(EncryptedColumn, nullable=False)
    degree: Mapped[str] = mapped_column(EncryptedColumn, nullable=False)
    nationality: Mapped[str] = mapped_column(EncryptedColumn, nullable=False)
    religion: Mapped[str] = mapped_column(EncryptedColumn, nullable=False)
    phone: Mapped[str] = mapped_column(EncryptedColumn, nullable=False)
    email: Mapped[str] = mapped_column(EncryptedColumn, nullable=False)
    profile_image: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    account: Mapped["Account"] = relationship(back_populates="doctor")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="doctor")
    records: Mapped[list["MedicalRecord"]] = relationship(back_populates="doctor")
    doctor_schedule: Mapped["Doctor_Schedule"] = relationship(back_populates="doctor")
