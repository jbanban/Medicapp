from flask import jsonify, request
from app.models.doctor_schedule import Doctor_Schedule
from app.routes.patient import appointments
from . import api_bp


@api_bp.route('/availability/check', methods=['GET'])
def check_availability():
    date = request.args.get('date')
    if not date:
        return jsonify({
            'success': False,
            'message': 'Date parameter required'
        }), 400

    booked_slots = [
        apt['time'] for apt in appointments
        if apt['date'] == date
    ]

    return jsonify({
        'success': True,
        'booked_slots': booked_slots
    })

@api_bp.route('/availability', methods=['GET', 'POST'])
def availability():
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'availability': {
                "sunday": {"available": False},
                "monday": {"start": "09:00", "end": "17:00", "available": True},
                "tuesday": {"start": "09:00", "end": "17:00", "available": True},
                "wednesday": {"start": "09:00", "end": "17:00", "available": True},
                "thursday": {"start": "09:00", "end": "17:00", "available": True},
                "friday": {"start": "09:00", "end": "17:00", "available": True},
                "saturday": {"available": False}
            }
        })

    # POST — save weekly availability
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            'success': False,
            'message': 'No availability data provided'
        }), 400

    # TODO: persist data (db, file, user profile)
    return jsonify({'success': True})



@api_bp.route("/day/<date>")
def get_day_schedule(date):
    slots = Doctor_Schedule.query.filter_by(vacant_date=date).all()
    return jsonify([
        {
            "time": s.vacant_time,
            "status": s.status
        } for s in slots
    ])