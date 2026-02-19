from flask import render_template, jsonify
from flask import redirect, url_for, flash, request
from flask_login import current_user, login_required
from datetime import date, timedelta
from app.models.doctor import Doctor
from app.models.doctor_schedule import Doctor_Schedule
from app.services.generateSaveSlot import generate_and_save_slots
from app import db
from . import doctor_bp


@doctor_bp.route('/doctors_schedule', methods=['GET', 'POST'])
@login_required
def doctors_schedule():
    
    doctor = Doctor.query.filter_by(account_id=current_user.account_id).first()
    
    schedules = Doctor_Schedule.query.filter_by(doctor_id=doctor.doctor_id).first()

    return render_template(
        'doctor/calendar.html',
        schedules=schedules,
        doctor=doctor,
        today=date.today()
    )

@doctor_bp.route('/scheduler', methods=['POST'])
@login_required
def scheduler():

    doctor = Doctor.query.filter_by(
        account_id=current_user.account_id
    ).first()

    if not doctor:
        return jsonify(success=False, error="Doctor not found"), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify(success=False, error="Invalid JSON"), 400

    try:
        slots_created = generate_and_save_slots(
            doctor_id=doctor.doctor_id,
            selected_date=data['date'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            duration_minutes=int(data['duration'])
        )
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

    return jsonify(
        success=True,
        slots_created=slots_created
    )



@doctor_bp.route('/delete_schedule/<int:doctor_schedule_id>', methods=['POST'])
@login_required
def delete_doctor_schedule(doctor_schedule_id):
    schedule = Doctor_Schedule.query.get(doctor_schedule_id)
    if not schedule:
        return redirect(url_for('doctor.doctors_schedule'))
    db.session.delete(schedule)
    db.session.commit()
    flash("Schedule deleted successfully.", "success")
    return redirect(url_for('doctor.doctors_schedule'))



@doctor_bp.route('/schedule')
@login_required
def day_schedule():

    today=date.today()

    selected_date_str = request.args.get('date', date.today().isoformat())
    selected_date = date.fromisoformat(selected_date_str)
    prev_date = (selected_date - timedelta(days=1)).isoformat()
    next_date = (selected_date + timedelta(days=1)).isoformat()

    appointments = Appointment.query\
        .filter_by(doctor_id=current_user.doctor_id)\
        .filter(Appointment.appointment_date == selected_date)\
        .order_by(Appointment.appointment_time)\
        .all()

    ongoing_appointment = next(
        (a for a in appointments if a.status == 'Ongoing'), None
    )

    return render_template('doctor/daySchedule.html',
        doctor=current_user,
        appointments=appointments,
        ongoing_appointment=ongoing_appointment,
        selected_date=selected_date,
        selected_date_str=selected_date_str,
        prev_date=prev_date,
        next_date=next_date,
        today=today
    )