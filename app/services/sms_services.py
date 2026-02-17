import random
from datetime import datetime, timedelta
from app.utils.twilio_service import send_sms
from werkzeug.security import generate_password_hash
from app import db


def send_sms_otp(patient, phone_number: str):
    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))

    # Store hashed OTP
    patient.sms_otp = generate_password_hash(otp)
    patient.sms_otp_expiry = datetime.utcnow() + timedelta(minutes=5)
    db.session.commit()

    message = (
        f"MEDICAPP OTP: {otp}\n"
        "Use this code to verify your mobile number.\n"
        "Expires in 5 minutes."
    )

    send_sms(phone_number, message)

    return True


def send_appointment_reminder(phone_number: str, doctor_name: str, date: str, time: str):
    message = (
        f"Reminder: You have an appointment with Dr. {doctor_name} "
        f"on {date} at {time}. Please arrive 10 minutes early."
    )

    return send_sms(phone_number, message)
