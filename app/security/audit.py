# app/security/audit.py
import logging

audit_logger = logging.getLogger("crypto_audit")
audit_logger.setLevel(logging.INFO)

handler = logging.FileHandler("crypto_audit.log")
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)
handler.setFormatter(formatter)

audit_logger.addHandler(handler)


def log_encryption_event(user_id: int, field_name: str):
    audit_logger.info(f"User {user_id} encrypted field '{field_name}'.")