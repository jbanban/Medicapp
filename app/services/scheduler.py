from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from app.extensions import db
from app.models import Doctor_Schedule
from app.models import Appointment
from app.services.email_services import send_email


scheduler = BackgroundScheduler()


def parse_appointment_datetime(appointment):
    try:
        return datetime.strptime(
            f"{appointment.appointment_date} {appointment.appointment_time}",
            "%Y-%m-%d %H:%M"
        )
    except Exception as e:
        print("Datetime parsing error:", e)
        return None


def check_appointments(app):  # ✅ receive app

    with app.app_context():  # ✅ use real app

        now = datetime.now()

        appointments = Appointment.query.filter(
            Appointment.status == "Booked"
        ).all()

        for appointment in appointments:

            appointment_datetime = parse_appointment_datetime(appointment)

            if not appointment_datetime:
                continue

            patient = appointment.patient

            if not patient or not patient.email_verified:
                continue

            # 1 Hour Before
            one_hour_before = appointment_datetime - timedelta(hours=1)

            if (
                one_hour_before <= now < appointment_datetime
                and not appointment.reminder_1hr_sent
            ):

                send_email(
                    subject="Reminder: Upcoming Appointment in 1 Hour",
                    recipient=patient.email,
                    body=f"""
                        Dear {patient.firstname} {patient.lastname},

                        Good day.

                        This is a friendly reminder that you have a scheduled appointment in one (1) hour.

                        Appointment Details:
                        Doctor: Dr. {appointment.doctor.firstname} {appointment.doctor.lastname}
                        Date: {appointment.appointment_date}
                        Time: {appointment.appointment_time}

                        Kindly ensure that you arrive at least 10–15 minutes before your scheduled time to allow for proper check-in and preparation.

                        If you are unable to attend, please inform the clinic as soon as possible.

                        Thank you for choosing MEDICAPP.

                        Sincerely,
                        MEDICAPP Support Team
                        """
                    )


                appointment.reminder_1hr_sent = True
                db.session.commit()

            # On-Time Reminder
            if (
                appointment_datetime <= now < appointment_datetime + timedelta(minutes=10)
                and not appointment.reminder_ontime_sent
            ):

                send_email(
                    subject="Appointment Reminder: Your Scheduled Consultation is Now",
                    recipient=patient.email,
                    body=f"""
                        Dear {patient.firstname} {patient.lastname},

                        Good day.

                        This is to inform you that your scheduled appointment is now due.

                        Appointment Details:
                        Doctor: Dr. {appointment.doctor.firstname} {appointment.doctor.lastname}
                        Date: {appointment.appointment_date}
                        Time: {appointment.appointment_time}

                        Kindly proceed to the clinic or join your consultation session as scheduled.

                        If you are unable to attend, please notify the clinic as soon as possible to avoid inconvenience.

                        Thank you for choosing MEDICAPP.

                        Sincerely,
                        MEDICAPP Support Team
                        """
                    )

                appointment.reminder_ontime_sent = True
                db.session.commit()


def expire_old_schedule_slots(app):

    with app.app_context():

        now = datetime.now()

        slots = Doctor_Schedule.query.filter(
            Doctor_Schedule.status == "available"
        ).all()

        for slot in slots:
            slot_datetime = datetime.combine(slot.vacant_date, slot.start_time)

            if slot_datetime < now:
                slot.status = "unavailable"

        db.session.commit()

