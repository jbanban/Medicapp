# services/otp_service.py

import random
from datetime import datetime, timedelta
from app.utils.twilio_service import send_sms

# Temporary in-memory storage (use Redis or DB in production)
otp_storage = {}


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


def send_otp(phone_number: str) -> bool:
    otp = generate_otp()

    # Store OTP with expiration (5 minutes)
    otp_storage[phone_number] = {
        "otp": otp,
        "expires_at": datetime.utcnow() + timedelta(minutes=5)
    }

    message = f"Your MEDICAPP OTP is {otp}. It expires in 5 minutes."

    result = send_sms(phone_number, message)
    return result is not None


def verify_otp(phone_number: str, user_otp: str) -> bool:
    record = otp_storage.get(phone_number)

    if not record:
        return False

    if datetime.utcnow() > record["expires_at"]:
        del otp_storage[phone_number]
        return False

    if record["otp"] == user_otp:
        del otp_storage[phone_number]
        return True

    return False
