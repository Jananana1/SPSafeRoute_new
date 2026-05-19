from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import validates
from .database import Base
from .encryption import EncryptedString
import enum
import re

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(EncryptedString(255), nullable=True)
    is_admin = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    profile_image_url = Column(String(500), nullable=True)

    @validates('email')
    def validate_email(self, key, address):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", address):
            raise ValueError("Invalid email format")
        return address

class IncidentStatus(str, enum.Enum):
    REPORTED = "reported"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELETED = "deleted"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    location_name = Column(String(255), nullable=True)
    image_url = Column(String(500), nullable=True)
    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default='reported')

class SosAlert(Base):
    __tablename__ = "sos_alerts"
    id = Column(Integer, primary_key=True, index=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# For Firebase: store FCM registration token
class FCMToken(Base):
    __tablename__ = "fcm_tokens"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_fcm_tokens_user_id"),
    )
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Security related models
class LoginHistory(Base):
    __tablename__ = "login_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ip_address = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False) # 'success' or 'failed'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OTPToken(Base):
    __tablename__ = "otp_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    otp_code = Column(String(6), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class IncidentHistory(Base):
    __tablename__ = "incident_history"
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, nullable=False)   # original incident ID
    action = Column(String(20), nullable=False)     # 'resolved' or 'deleted'
    inc_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    location_name = Column(String(255), nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    user_id = Column(Integer, nullable=True)
    image_url = Column(String(500), nullable=True)
    reported_at = Column(DateTime(timezone=True), nullable=True)
    actioned_at = Column(DateTime(timezone=True), server_default=func.now())

class CaptchaChallenge(Base):
    __tablename__ = "captcha_challenges"
    id = Column(String(36), primary_key=True, index=True)
    answer = Column(String(20), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())