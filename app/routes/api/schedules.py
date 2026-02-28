from flask import jsonify, request
from datetime import date, datetime, timedelta

from flask_login import current_user
from app.models.doctor_schedule import Doctor_Schedule
from app.models.doctor_secretary import Doctor_Secretary
from app.models.doctor import Doctor
from app import db
from . import api_bp

#This is nothing
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

@api_bp.route("/doctor/doctors_schedule", methods=["GET"])
def get_doctor_month_schedule():
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    if not year or not month:
        return jsonify({"error": "year and month are required"}), 400

    # First day of month
    start_date = date(year, month, 1)

    # First day of next month
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    doctor = None

    if current_user.role == "doctor":
        doctor = Doctor.query.filter_by(
            account_id=current_user.account_id
        ).first()

    elif current_user.role == "secretary":
        secretary = Doctor_Secretary.query.filter_by(
            account_id=current_user.account_id
        ).first()

        if secretary:
            doctor = Doctor.query.get(secretary.doctor_id)

    if not doctor:
        return jsonify({"error": "Unauthorized"}), 403


    rows = (
        db.session.query(
            Doctor_Schedule.vacant_date,
            db.func.count().label("slots")
        )
        .filter(
            Doctor_Schedule.doctor_id == doctor.doctor_id,
            Doctor_Schedule.vacant_date >= start_date,
            Doctor_Schedule.vacant_date < end_date,
            Doctor_Schedule.status.in_(["available", "Booked"])
        )
        .group_by(Doctor_Schedule.vacant_date)
        .order_by(Doctor_Schedule.vacant_date)
        .all()
    )

    
    return jsonify([
    {
        "date": row.vacant_date.isoformat(),
        "slots": row.slots
    }
    for row in rows
])

@api_bp.route('/schedules', methods=['GET'])
def get_week_schedules():
    
    week_start_str = request.args.get('week_start')

    if not week_start_str:
        return jsonify({
            "success": False,
            "message": "week_start is required"
        }), 400

    try:
        week_start = datetime.strptime(week_start_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid date format"
        }), 400

    week_end = week_start + timedelta(days=6)

    doctor_id = current_user.doctor_id if hasattr(current_user, 'doctor_id') else None
    if not doctor_id:
        return jsonify({
            "success": False,
            "message": "Doctor not found"
        }), 404

    schedules = Doctor_Schedule.query.filter(
        Doctor_Schedule.doctor_id == doctor_id,
        Doctor_Schedule.vacant_date >= week_start,
        Doctor_Schedule.vacant_date <= week_end
    ).all()

    day_map = defaultdict(list)

    for s in schedules:
        weekday = s.vacant_date.strftime("%A").lower()  # monday, tuesday...

        day_map[weekday].append({
            "id": s.id,
            "date": s.vacant_date.strftime("%Y-%m-%d"),
            "start": s.start_time.strftime("%H:%M"),
            "end": s.end_time.strftime("%H:%M")
        })

    return jsonify({
        "success": True,
        "week_start": week_start_str,
        "schedules": day_map
    })