from flask import jsonify, request
from app.models.doctor_schedule import Doctor_Schedule
from app import db
from . import api_bp


@api_bp.route("/open-slot", methods=["POST"])
def open_slot():
    data = request.json
    date = data["date"]
    time = data["time"]

    existing = Doctor_Schedule.query.filter_by(
        vacant_date=date,
        vacant_time=time
    ).first()

    if existing:
        return jsonify({"error": "Slot already exists"}), 400

    slot = Doctor_Schedule(
        doctor_id=1,
        vacant_date=date,
        vacant_time=time,
        status="pending"
    )

    db.session.add(slot)
    db.session.commit()

    return jsonify({"success": True})
