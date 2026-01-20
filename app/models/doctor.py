from datetime import datetime, date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from app.extensions import db


class Doctor(db.Model):
    __tablename__ = "doctor"

    doctor_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("account.account_id"), unique=True)
    firstname: Mapped[str] = mapped_column(String(50))
    middlename: Mapped[str] = mapped_column(String(50), nullable=True)
    lastname: Mapped[str] = mapped_column(String(50))
    age: Mapped[int] = mapped_column(Integer)
    bloodtype: Mapped[str] = mapped_column(String(5), nullable=True)
    height: Mapped[str] = mapped_column(String, nullable=True)
    weight: Mapped[str] = mapped_column(String, nullable=True)
    specialization: Mapped[str] = mapped_column(String(100))
    gender: Mapped[str] = mapped_column(String(20))
    dob: Mapped[str] = mapped_column(String(10))
    pob: Mapped[str] = mapped_column(String(100), nullable=True)
    civilstatus: Mapped[str] = mapped_column(String(20), nullable=True)
    degree: Mapped[str] = mapped_column(String(100), nullable=True)
    nationality: Mapped[str] = mapped_column(String(50), nullable=True)
    religion: Mapped[str] = mapped_column(String(50), nullable=True)
    phone: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(100))
    profile_image: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    account: Mapped["Account"] = relationship(back_populates="doctor")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="doctor")
    records: Mapped[list["MedicalRecord"]] = relationship(back_populates="doctor")
    doctor_schedule = relationship("Doctor_Schedule", back_populates="doctor")
