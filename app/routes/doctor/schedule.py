from flask import render_template
from flask import session, redirect, url_for, flash, request
from app.models.doctor import Doctor
from app.models.doctor_schedule import Doctor_Schedule
from app import db
from . import doctor_bp


@doctor_bp.route('/schedule', methods=['GET', 'POST'])
def doctors_schedule():
    if 'role' not in session or session['role'] != 'doctor':
        return redirect(url_for('misc.unauthorized'))

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    doctor = Doctor.query.filter_by(account_id=user_id).first()
    if not doctor:
        flash("Please complete your doctor profile first.", "warning")
        return redirect(url_for('misc.unauthorized'))

    if request.method == 'POST':
        selected_date = request.form['preferred_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        duration = int(request.form['duration'])

        slots_created = generate_and_save_slots(
            doctor_id=doctor.doctor_id,
            selected_date=selected_date,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration
        )

        flash(f"{slots_created} slots successfully created.", "success")
        return redirect(url_for('doctor.doctors_schedule'))

    schedules = Doctor_Schedule.query.filter_by(
        doctor_id=doctor.doctor_id
    ).order_by(
        Doctor_Schedule.date,
        Doctor_Schedule.start_time
    ).all()

    return render_template(
        'doctor/calendar.html',
        schedules=schedules,
        doctor=doctor
    )


@doctor_bp.route('/scheduler')
def scheduler():
    if 'role' not in session or session['role'] != 'doctor':
        return redirect(url_for('misc.unauthorized'))

    user_id = session.get('user_id')

    doctor = Doctor.query.filter_by(account_id=user_id).first_or_404()

    selected_date = request.args.get('date')

    return render_template(
        'doctor/scheduler.html',
        doctor=doctor,
        selected_date=selected_date
    )


@doctor_bp.route('/delete_schedule/<int:doctor_schedule_id>', methods=['POST'])
def delete_doctor_schedule(doctor_schedule_id):
    schedule = Doctor_Schedule.query.get(doctor_schedule_id)
    if not schedule:
        return redirect(url_for('doctor.doctors_schedule'))
    db.session.delete(schedule)
    db.session.commit()
    flash("Schedule deleted successfully.", "success")
    return redirect(url_for('doctor.doctors_schedule'))