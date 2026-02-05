from flask import jsonify
from flask_login import login_required
from app.models.doctor_schedule import Doctor_Schedule
from . import api_bp

@api_bp.route('/<int:doctor_id>/availability')
@login_required
def patient_doctor_availability(doctor_id):
    schedules = Doctor_Schedule.query.filter_by(
        doctor_id=doctor_id,
        status='Available'
    ).all()

    availability = {}
    for s in schedules:
        date = s.vacant_date.strftime('%Y-%m-%d')
        availability[date] = availability.get(date, 0) + 1

    return jsonify([
        {"date": date, "slots": slots}
        for date, slots in availability.items()
    ])
