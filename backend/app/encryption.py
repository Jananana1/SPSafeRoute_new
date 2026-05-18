import os
from .config import load_project_env
from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy.types import TypeDecorator, VARCHAR

load_project_env()

DB_ENCRYPTION_KEY = os.getenv("DB_ENCRYPTION_KEY")
if not DB_ENCRYPTION_KEY:
    raise RuntimeError("DB_ENCRYPTION_KEY environment variable must be set for database field encryption.")

try:
    _cipher = Fernet(DB_ENCRYPTION_KEY)
except ValueError as exc:
    raise RuntimeError("DB_ENCRYPTION_KEY must be a valid Fernet key.") from exc


class EncryptedString(TypeDecorator):
    impl = VARCHAR
    cache_ok = True

    def __init__(self, length=None, **kwargs):
        super().__init__(length=length or 255, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            return _cipher.encrypt(value.encode('utf-8')).decode('utf-8')
        raise TypeError('EncryptedString only supports string values.')

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return _cipher.decrypt(value.encode('utf-8')).decode('utf-8')
        except InvalidToken:
            # If the value cannot be decrypted, return raw data to avoid breaking reads.
            return value
