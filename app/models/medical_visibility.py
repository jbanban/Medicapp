from datetime import datetime, date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from app.extensions import db


class MedicalVisibility(db.Model):
    __tablename__ = "medical_visibility"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, nullable=False, unique=True)
    encrypted_state = db.Column(db.Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
