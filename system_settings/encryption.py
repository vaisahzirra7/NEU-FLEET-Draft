"""
Field encryption for sensitive SystemSettings values (currently: SMTP password).

Design:
- Uses Fernet symmetric encryption (authenticated, base64-encoded).
- The encryption key is read from Django settings: SETTINGS_ENCRYPTION_KEY.
- If the key is missing, encryption falls back to a stable default derived
  from SECRET_KEY — this is BETTER THAN PLAINTEXT but worse than a dedicated
  key. We log a warning at decrypt time so the operator knows to set one.
- Encrypted values are stored as base64 strings (Fernet's default output).
- Empty strings stay empty (never encrypted) — this lets the migration
  default work without needing the key on first apply.

Key generation (run once, save the result to .env or settings.py):
    from cryptography.fernet import Fernet
    print(Fernet.generate_key().decode())

Key rotation:
    1. Read all encrypted values with the OLD key.
    2. Re-encrypt with the NEW key.
    3. Replace the key in settings.
    Not automated — operator must script it. See migration helpers if needed.
"""
import base64
import hashlib
import logging

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

logger = logging.getLogger(__name__)


def _resolve_key():
    """
    Return the Fernet key as bytes. Order of preference:
      1. settings.SETTINGS_ENCRYPTION_KEY (explicit, recommended)
      2. Derived from settings.SECRET_KEY (fallback, logs a warning)
    """
    key = getattr(settings, "SETTINGS_ENCRYPTION_KEY", None)
    if key:
        if isinstance(key, str):
            key = key.encode("utf-8")
        return key

    # Fallback: derive a 32-byte key from SECRET_KEY using SHA-256,
    # then base64-encode it (Fernet's required format).
    logger.warning(
        "SETTINGS_ENCRYPTION_KEY not set; falling back to SECRET_KEY-derived "
        "key. Set SETTINGS_ENCRYPTION_KEY in settings.py for stronger isolation."
    )
    secret = settings.SECRET_KEY.encode("utf-8") if isinstance(settings.SECRET_KEY, str) else settings.SECRET_KEY
    digest = hashlib.sha256(secret).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt(value):
    """
    Encrypt a string and return a base64 token (also a string).
    Empty/None returns an empty string — empty values are never encrypted.
    """
    if not value:
        return ""
    if not isinstance(value, str):
        value = str(value)
    f = Fernet(_resolve_key())
    return f.encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt(token):
    """
    Decrypt a base64 token back to the original string.
    Returns empty string for empty input or any decryption failure.
    """
    if not token:
        return ""
    try:
        f = Fernet(_resolve_key())
        return f.decrypt(token.encode("utf-8") if isinstance(token, str) else token).decode("utf-8")
    except (InvalidToken, ValueError, TypeError) as e:
        logger.warning("Failed to decrypt SystemSettings field: %s", e)
        return ""


def is_encrypted(value):
    """
    Cheap check whether a value LOOKS like a Fernet token. Used by migrations
    to avoid double-encrypting on re-runs. Not authoritative — a real check
    requires the key. False positives are possible but harmless (decrypt
    will detect and return empty).
    """
    if not value or not isinstance(value, str):
        return False
    # Fernet tokens start with "gAAAAA" (version byte 0x80 in URL-safe base64)
    return value.startswith("gAAAAA")
