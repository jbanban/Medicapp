import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = "AC237bafcb49340a9114aa43204b38e49e"
TWILIO_AUTH_TOKEN = "41b7a25176ca824e4cf39a6bd8e123b6"
TWILIO_PHONE_NUMBER = "+18059198336"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_sms(to: str, message: str) -> str | None:
    """
    Send SMS using Twilio.
    Returns message SID if successful, otherwise None.
    """
    try:
        msg = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to
        )
        return msg.sid
    except Exception as e:
        print("Twilio Error:", e)
        return None
