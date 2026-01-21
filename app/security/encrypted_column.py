# app/security/encrypted_column.py
from sqlalchemy.types import TypeDecorator, TEXT
from app.security.crypto import encrypt_value, decrypt_value
from app.security.audit import audit_logger


class EncryptedColumn(TypeDecorator):
    impl = TEXT
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Encrypt before storing in DB"""
        if value is None:
            return value
        return encrypt_value(value)

    def process_result_value(self, value, dialect):
        """Decrypt automatically when accessed"""
        if value is None:
            return value

        try:
            plaintext = decrypt_value(value)

            # 🔍 Audit log
            audit_logger.info(
                "Decryption event | column=EncryptedColumn"
            )

            return plaintext

        except Exception:
            # fallback for legacy plaintext data
            return value
