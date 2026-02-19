from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from app.extensions import db
from app.models import Doctor_Schedule
from app.models import Appointment
from app.services.email_services import send_email


scheduler = BackgroundScheduler()


def parse_appointment_datetime(appointment):
    try:
        start_time = appointment.appointment_time.split(" - ")[0].strip()  # extracts "09:00"
        return datetime.strptime(
            f"{appointment.appointment_date} {start_time}",
            "%Y-%m-%d %H:%M"
        )
    except Exception as e:
        print(f"Datetime parsing error for appointment {appointment.appointment_id}: {e}")
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


def check_missed_appointments(app):
    with app.app_context():
        now = datetime.now()

        try:
            appointments = Appointment.query.filter(
                Appointment.status == "Booked"
            ).all()

            updated = 0

            for appointment in appointments:
                appointment_datetime = parse_appointment_datetime(appointment)

                if not appointment_datetime:
                    continue

                if appointment_datetime + timedelta(minutes=10) >= now:
                    continue

                appointment.status = "Missed"
                updated += 1

                patient = appointment.patient

                # Guard against None patient
                if not patient:
                    print(f"No patient found for appointment {appointment.appointment_id}, skipping.")
                    continue

                # Fix NoneType error — treat NULL as 0
                if patient.missed_appointments is None:
                    patient.missed_appointments = 0

                patient.missed_appointments += 1
                count = patient.missed_appointments

                if count == 1:
                    try:
                        send_email(
                            subject="Missed Appointment Reminder – MEDICAPP",
                            recipient=patient.email,
                            body=f"""
                                Dear {patient.firstname} {patient.lastname},

                                We noticed that you missed your appointment on {appointment.appointment_date}
                                with Dr. {appointment.doctor.firstname} {appointment.doctor.lastname}.

                                This is a friendly reminder that missing appointments affects your care
                                and the availability of slots for other patients.

                                Please make sure to attend your future appointments or cancel in advance
                                if you are unable to make it.

                                Sincerely,
                                MEDICAPP Support Team
                            """
                        )
                    except Exception as e:
                        print(f"Failed to send 1st miss reminder: {e}")

                elif count == 2:
                    try:
                        send_email(
                            subject="⚠️ Warning – 2nd Missed Appointment",
                            recipient=patient.email,
                            body=f"""
                                Dear {patient.firstname} {patient.lastname},

                                This is a warning notice that you have now missed 2 appointments on MEDICAPP.

                                Latest missed appointment:
                                Doctor: Dr. {appointment.doctor.firstname} {appointment.doctor.lastname}
                                Date: {appointment.appointment_date}

                                Please be advised that missing one more appointment will result in
                                the suspension of your MEDICAPP account.

                                Sincerely,
                                MEDICAPP Support Team
                            """
                        )
                    except Exception as e:
                        print(f"Failed to send 2nd miss warning: {e}")

                elif count >= 3 and not patient.is_suspended:
                    patient.is_suspended = True
                    patient.suspended_at = datetime.now()

                    try:
                        send_email(
                            subject="Account Suspended – Missed Appointments",
                            recipient=patient.email,
                            body=f"""
                                Dear {patient.firstname} {patient.lastname},

                                Your MEDICAPP account has been suspended due to 3 missed appointments.

                                Latest missed appointment:
                                Doctor: Dr. {appointment.doctor.firstname} {appointment.doctor.lastname}
                                Date: {appointment.appointment_date}

                                If you believe this is an error or would like to appeal,
                                please contact our support team.

                                Sincerely,
                                MEDICAPP Support Team
                            """
                        )
                    except Exception as e:
                        print(f"Failed to send suspension email: {e}")

            if updated:
                db.session.commit()
                print(f"[Scheduler] Marked {updated} appointment(s) as Missed.")

        except Exception as e:
            db.session.rollback()
            print(f"[Scheduler] check_missed_appointments failed: {e}")