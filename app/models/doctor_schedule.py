from datetime import datetime, date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Date, Time, ForeignKey, DateTime, UniqueConstraint
from app.extensions import db



class Doctor_Schedule(db.Model):
    __tablename__ = "doctor_schedule"
    __table_args__ = (
        UniqueConstraint(
            "doctor_id",
            "vacant_date",
            "start_time",
            "end_time",
            name="uq_doctor_slot"
        ),
    )

    doctor_schedule_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctor.doctor_id"), nullable=False
    )

    # ✅ Proper date & time types
    vacant_date: Mapped[Date] = mapped_column(Date, nullable=False)
    start_time: Mapped[Time] = mapped_column(Time, nullable=False)
    end_time: Mapped[Time] = mapped_column(Time, nullable=False)

    status: Mapped[str] = mapped_column(
        String(20), default="available"
    )
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    doctor = relationship("Doctor", back_populates="doctor_schedule")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="schedule",cascade="all, delete-orphan")
