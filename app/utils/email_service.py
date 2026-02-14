from flask_mail import Message
from flask import current_app


def send_email(subject: str, recipients: list, body: str) -> bool:
    mail = current_app.extensions.get("mail")
    if not mail:
        print("Mail extension not found.")
        return False

    msg = Message(
        subject=subject,
        recipients=recipients,
        body=body
    )

    try:
        mail.send(msg)
        return True
    except Exception as e:
        print("Email Error:", e)
        return False