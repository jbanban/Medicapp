from app import create_app
from app.services.scheduler import (
    scheduler,
    check_appointments,
    expire_old_schedule_slots,
    check_missed_appointments
)


app = create_app()

scheduler.add_job(
    func=check_appointments,
    trigger="interval",
    minutes=10,
    args=[app]
)
scheduler.add_job(
    func=expire_old_schedule_slots,
    trigger="interval",
    minutes=15,
    args=[app]
)
scheduler.add_job(
    func=check_missed_appointments,
    trigger="interval",
    minutes=5,
    args=[app]
)
scheduler.start()

if __name__ == "__main__":
    app.run(debug=True)

