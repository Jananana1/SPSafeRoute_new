from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ---------- User schemas ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    full_name: Optional[str] = None
    captcha_id: str
    captcha_answer: str

class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_admin: bool
    created_at: datetime
    profile_image_url: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    mfa_required: Optional[bool] = False

class MFAVerify(BaseModel):
    token: str
    otp: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
    confirm_password: str

class CaptchaResponse(BaseModel):
    captcha_id: str
    question: str

# ---------- Incident schemas ----------
class IncidentCreate(BaseModel):
    type: str
    description: str
    lat: float
    lng: float
    location_name: Optional[str] = None
    image_url: Optional[str] = None

class IncidentOut(BaseModel):
    id: int
    type: str
    description: str
    lat: float
    lng: float
    location_name: Optional[str]
    image_url: Optional[str]
    user_id: int
    created_at: datetime

# ---------- SOS schemas ----------
class SosCreate(BaseModel):
    lat: float
    lng: float

class SosOut(BaseModel):
    id: int
    lat: float
    lng: float
    user_id: int
    created_at: datetime

# ---------- Admin / extra schemas ----------
class IncidentStatusEnum(str, Enum):
    REPORTED = "reported"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELETED = "deleted"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

class IncidentOutWithStatus(IncidentOut):
    status: IncidentStatusEnum

class FCMTokenCreate(BaseModel):
    token: str

class AnalyticsResponse(BaseModel):
    monthly_stats: List[dict]
    area_stats: List[dict]