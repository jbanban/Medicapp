from app import db
from datetime import datetime

class DoctorsBackground(db.Model):
    __tablename__ = 'doctors_background'

    id = db.Column(db.Integer, primary_key=True)

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey('doctor.doctor_id', ondelete='CASCADE'),
        nullable=False
    )

    # qualification | experience | award | clinic
    type = db.Column(db.String(50), nullable=False)

    title = db.Column(db.String(150), nullable=False)
    organization = db.Column(db.String(150))
    year = db.Column(db.String(20))
    description = db.Column(db.Text)

    clinic_name = db.Column(db.String(150), nullable=True)
    clinic_address = db.Column(db.String(255), nullable=True)
    clinic_days = db.Column(db.String(100), nullable=True)
    clinic_hours_from = db.Column(db.String(100), nullable=True)
    clinic_hours_to = db.Column(db.String(100), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctor = db.relationship(
        'Doctor',
        backref=db.backref(
            'backgrounds',
            cascade='all, delete-orphan',
            lazy=True
        )
    )


