from flask import jsonify, request
from datetime import datetime
from app.models.appointment import Appointment
from app.models.doctor_schedule import Doctor_Schedule
from app import db
from . import api_bp

@api_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    """Delete a booked appointment and free the doctor's schedule slot"""

    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({
            'success': False,
            'message': 'Appointment not found'
        }), 404

    # 🔎 Find the matching doctor schedule slot
    schedule = Doctor_Schedule.query.filter_by(
        doctor_id=appointment.doctor_id,
        vacant_date=datetime.strptime(
            appointment.appointment_date, "%Y-%m-%d"
        ).date(),
        status='booked'
    ).filter(
        Doctor_Schedule.start_time <= datetime.strptime(
            appointment.appointment_time.split(' - ')[0], "%H:%M"
        ).time(),
        Doctor_Schedule.end_time >= datetime.strptime(
            appointment.appointment_time.split(' - ')[1], "%H:%M"
        ).time()
    ).first()

    # ✅ Free the slot if found
    if schedule:
        schedule.status = 'available'

    # ✅ Delete appointment
    db.session.delete(appointment)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Appointment deleted and schedule restored'
    })


@api_bp.route("/appointments", methods=["GET"])
def get_appointments():
    appointments = Appointment.query.all()

    return jsonify({
        "success": True,
        "appointments": [
            {
                "appointment_id": appt.appointment_id,
                "patient_id": appt.patient_id,
                "doctor_id": appt.doctor_id,
                "date": appt.appointment_date,
                "time": appt.appointment_time,
                "status": appt.status
            }
            for appt in appointments
        ]
    })


@api_bp.route("/appointments", methods=["POST"])
def create_appointment():
    data = request.get_json()

    required = ["patient_id", "doctor_id", "date", "time"]
    for field in required:
        if field not in data:
            return jsonify({
                "success": False,
                "message": f"Missing field: {field}"
            }), 400

    # Conflict check (STRING SAFE)
    conflict = Appointment.query.filter_by(
        appointment_date=data["date"],
        appointment_time=data["time"],
        doctor_id=data["doctor_id"]
    ).first()

    if conflict:
        return jsonify({
            "success": False,
            "message": "This time slot is already booked"
        }), 409

    appointment = Appointment(
        patient_id=data["patient_id"],
        doctor_id=data["doctor_id"],
        appointment_date=data["date"],
        appointment_time=data["time"],
        status="Pending"
    )

    db.session.add(appointment)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Appointment created successfully",
        "appointment_id": appointment.appointment_id
    }), 201
