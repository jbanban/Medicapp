from datetime import datetime, timedelta

def generate_and_save_slots(
    doctor_id,
    selected_date,       # '2025-01-15'
    start_time,          # '09:00'
    end_time,            # '17:00'
    duration_minutes     # 30
):
    """
    Generates time slots based on availability and duration
    and saves them to the database.
    """

    # Convert strings to datetime objects
    date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
    start_dt = datetime.strptime(f"{selected_date} {start_time}", "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(f"{selected_date} {end_time}", "%Y-%m-%d %H:%M")

    slots = []

    while start_dt + timedelta(minutes=duration_minutes) <= end_dt:
        slot_end = start_dt + timedelta(minutes=duration_minutes)

        slot = DoctorSchedule(
            doctor_id=doctor_id,
            date=date_obj,
            start_time=start_dt.time(),
            end_time=slot_end.time(),
            status='available'
        )

        slots.append(slot)
        start_dt = slot_end  # move to next slot

    db.session.bulk_save_objects(slots)
    db.session.commit()

    return len(slots)
