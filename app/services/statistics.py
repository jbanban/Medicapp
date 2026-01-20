from collections import Counter
from datetime import datetime
from app.models import Appointment

def calculate_appointment_statistics():
    appointments = Appointment.query.all()

    if not appointments:
        return {
            "total_appointments": 0,
            "monthly_counts": {},
            "status_counts": {},
            "average_appointments_per_day": 0,
            "busiest_day_of_week": None
        }

    # Convert string date + time → datetime
    appointment_datetimes = []
    for appt in appointments:
        try:
            dt = datetime.strptime(
                f"{appt.appointment_date} {appt.appointment_time}",
                "%Y-%m-%d %H:%M"
            )
            appointment_datetimes.append(dt)
        except ValueError:
            continue  # skip malformed rows safely

    if not appointment_datetimes:
        return {
            "total_appointments": 0,
            "monthly_counts": {},
            "status_counts": {},
            "average_appointments_per_day": 0,
            "busiest_day_of_week": None
        }

    total_appointments = len(appointment_datetimes)

    # 📅 Monthly counts
    months = [dt.strftime("%Y-%m") for dt in appointment_datetimes]
    monthly_counts = dict(Counter(months))

    # 📌 Status counts
    statuses = [appt.status for appt in appointments if appt.status]
    status_counts = dict(Counter(statuses))

    # 📊 Average per day
    unique_days = set(dt.strftime("%Y-%m-%d") for dt in appointment_datetimes)
    average_per_day = round(total_appointments / len(unique_days), 2)

    # 🔥 Busiest weekday
    weekdays = [dt.strftime("%A") for dt in appointment_datetimes]
    busiest_day = Counter(weekdays).most_common(1)[0][0]

    return {
        "total_appointments": total_appointments,
        "monthly_counts": monthly_counts,
        "status_counts": status_counts,
        "average_appointments_per_day": average_per_day,
        "busiest_day_of_week": busiest_day
    }


