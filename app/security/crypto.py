# app/security/crypto.py
import os
import json
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# 🔐 In production:
# - Load this from ENV or KMS (AWS KMS, GCP KMS, Azure Key Vault)
MASTER_KEY = os.environ.get("MASTER_ENCRYPTION_KEY", "dev-master-key").encode()

PBKDF2_ITERATIONS = 310_000


def derive_key(master_key: bytes, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # AES-256
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(master_key)


def encrypt_value(plaintext: str) -> str:
    if plaintext is None:
        return None

    salt = os.urandom(16)
    nonce = os.urandom(12)  # GCM recommended size

    key = derive_key(MASTER_KEY, salt)
    aesgcm = AESGCM(key)

    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)

    payload = {
        "alg": "AES-256-GCM",
        "kdf": "PBKDF2-HMAC-SHA256",
        "iterations": PBKDF2_ITERATIONS,
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode(),
    }

    return json.dumps(payload)


def decrypt_value(payload: str | None) -> str | None:
    # 1️⃣ Handle NULL / empty values
    if not payload:
        return None

    # 2️⃣ Payload must be a string
    if not isinstance(payload, str):
        return payload

    # 3️⃣ Try to parse JSON (encrypted format)
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        # Not JSON → assume already plain text
        return payload

    # 4️⃣ Validate expected encryption keys
    required_keys = {"salt", "nonce", "ciphertext"}
    if not required_keys.issubset(data):
        # Not encrypted in expected format
        return payload

    try:
        salt = base64.b64decode(data["salt"])
        nonce = base64.b64decode(data["nonce"])
        ciphertext = base64.b64decode(data["ciphertext"])

        key = derive_key(MASTER_KEY, salt)
        aesgcm = AESGCM(key)

        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode()

    except Exception:
        # Any crypto failure → fail safely
        return None
        

def safe_decrypt(value):
    if not value:
        return value
    try:
        return decrypt_value(value)
    except Exception:
        return value  # fallback for non-encrypted/legacy data

