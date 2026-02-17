from typing import TYPE_CHECKING
from datetime import datetime, date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Date, DateTime, ForeignKey
from app.extensions import db
from app.security.encrypted_column import EncryptedColumn

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.appointment import Appointment
    from app.models.medical_record import MedicalRecord
    from app.models.patient_history_background import PatientHistoryBackground
    from app.models.medical_visibility import MedicalVisibility
    from app.models.appointment_visibility import AppointmentVisibility


class Patient(db.Model):
    __tablename__ = "patient"

    patient_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.account_id"),
        unique=True,
        nullable=False
    )

    # ---------------- BASIC INFORMATION ----------------
    firstname: Mapped[str] = mapped_column(String(50), nullable=False)
    middlename: Mapped[str | None] = mapped_column(String(50), nullable=True)
    lastname: Mapped[str] = mapped_column(String(50), nullable=False)
    gender: Mapped[str] = mapped_column(EncryptedColumn(), nullable=False)

    birthdate: Mapped[date] = mapped_column(Date, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)

    blood_type: Mapped[str | None] = mapped_column(EncryptedColumn(), nullable=True)
    civil_status: Mapped[str | None] = mapped_column(EncryptedColumn(), nullable=True)

    # ---------------- CURRENT ADDRESS ----------------
    current_house_no: Mapped[str | None] = mapped_column(EncryptedColumn(), nullable=True)
    current_street: Mapped[str | None] = mapped_column(EncryptedColumn(), nullable=True)
    current_barangay: Mapped[str | None] = mapped_column(EncryptedColumn(), nullable=True)
    current_city: Mapped[str | None] = mapped_column(EncryptedColumn(), nullable=True)
    current_province: Mapped[str | None] = mapped_column(EncryptedColumn(), nullable=True)
    current_zipcode: Mapped[str | None] = mapped_column(EncryptedColumn(), nullable=True)

    # ---------------- PERMANENT ADDRESS ----------------
    permanent_house_no: Mapped[str] = mapped_column(EncryptedColumn(), nullable=False)
    permanent_street: Mapped[str | None] = mapped_column(EncryptedColumn(), nullable=True)
    permanent_barangay: Mapped[str] = mapped_column(EncryptedColumn(), nullable=False)
    permanent_city: Mapped[str] = mapped_column(EncryptedColumn(), nullable=False)
    permanent_province: Mapped[str] = mapped_column(EncryptedColumn(), nullable=False)
    permanent_zipcode: Mapped[str] = mapped_column(EncryptedColumn(), nullable=False)

    # ---------------- CONTACT INFORMATION ----------------
    phone: Mapped[str] = mapped_column(nullable=False)
    phone_otp: Mapped[str | None] = mapped_column(EncryptedColumn(), nullable=True)
    phone_otp_expiry: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    phone_verified: Mapped[bool] = mapped_column(default=False, nullable=False)

    email: Mapped[str | None] = mapped_column(nullable=True)
    email_otp: Mapped[str | None] = mapped_column(EncryptedColumn(), nullable=True)
    email_otp_expiry: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    email_verified: Mapped[bool] = mapped_column(default=False, nullable=False)

    # ---------------- EMERGENCY CONTACT ----------------
    ec_name: Mapped[str | None] = mapped_column(EncryptedColumn(), nullable=True)
    ec_phone: Mapped[str | None] = mapped_column(EncryptedColumn(), nullable=True)
    ec_relation: Mapped[str | None] = mapped_column(EncryptedColumn(), nullable=True)
    ec_address: Mapped[str | None] = mapped_column(EncryptedColumn(), nullable=True)

    # ---------------- FILES ----------------
    profile_image: Mapped[str | None] = mapped_column(nullable=True)

    # ---------------- METADATA ----------------
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # ---------------- RELATIONSHIPS ----------------
    account: Mapped["Account"] = relationship(back_populates="patient")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="patient")
    records: Mapped[list["MedicalRecord"]] = relationship(back_populates="patient")

    history: Mapped["PatientHistoryBackground"] = relationship(
        back_populates="patient",
        uselist=False,
        cascade="all, delete-orphan"
    )
    medical_visibility: Mapped["MedicalVisibility"] = relationship(
        back_populates="patient",
        uselist=False,
        cascade="all, delete-orphan"
    )
    appointment_visibility: Mapped[list["AppointmentVisibility"]] = relationship(
        back_populates="patient",
        cascade="all, delete-orphan"
    )



    # ---------------- HELPERS ----------------
    @property
    def full_current_address(self) -> str:
        return ", ".join(filter(None, [
            self.current_house_no,
            self.current_street,
            self.current_barangay,
            self.current_city,
            self.current_province,
            self.current_zipcode,
        ]))

    @property
    def full_permanent_address(self) -> str:
        return ", ".join(filter(None, [
            self.permanent_house_no,
            self.permanent_street,
            self.permanent_barangay,
            self.permanent_city,
            self.permanent_province,
            self.permanent_zipcode,
        ]))

    @property
    def full_name(self) -> str:
        return " ".join(filter(None, [
            self.firstname,
            self.middlename,
            self.lastname
        ]))
