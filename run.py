from app import create_app
from app.services.scheduler import scheduler, check_appointments, expire_old_schedule_slots

app = create_app()

scheduler.add_job(
    func=check_appointments,
    trigger="interval",
    minutes=5,
    args=[app]
)
scheduler.add_job(
    func=expire_old_schedule_slots,
    trigger="interval",
    minutes=10,
    args=[app]
)

scheduler.start()

if __name__ == "__main__":
    app.run(debug=True)
