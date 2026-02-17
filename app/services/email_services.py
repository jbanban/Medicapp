# services/email_service.py

from flask_mail import Message
from app.extensions import mail
from flask import current_app


def send_email(subject, recipient, body):
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            body=body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print("Email sending error:", e)
        return False