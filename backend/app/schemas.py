from pydantic import BaseModel, EmailStr, Field, validator  # Added 'Field' here
from typing import Optional, List
from datetime import datetime
from enum import Enum
import re

class AppBaseModel(BaseModel):
    model_config = {"from_attributes": True}

# ---------- Incident schemas (MOVE THIS UP, before User schemas) ----------
class IncidentCreate(AppBaseModel):
    type: str = Field(..., min_length=1)
    description: str = Field(..., min_length=10, max_length=1000)
    lat: float = Field(..., ge=14.0400, le=14.1100)  # San Pablo bounds
    lng: float = Field(..., ge=121.2000, le=121.3800)  # San Pablo bounds
    location_name: str = Field(..., min_length=1)
    image_url: Optional[str] = None
    
    @validator('type')
    def validate_type(cls, v):
        allowed_types = ['accident', 'crime', 'hazard']
        if v.lower() not in allowed_types:
            raise ValueError(f'Type must be one of: {", ".join(allowed_types)}')
        return v.lower()
    
    @validator('description')
    def validate_description(cls, v):
        # Check for XSS patterns
        suspicious = re.compile(r'<script|javascript:|onclick|onerror|alert\(|eval\(', re.IGNORECASE)
        if suspicious.search(v):
            raise ValueError('Description contains invalid content')
        return v.strip()
    
    @validator('image_url')
    def validate_image(cls, v):
        if v:
            # Check base64 size and format
            if len(v) > 5 * 1024 * 1024:  # 5MB limit
                raise ValueError('Image size exceeds 5MB limit')
            if not v.startswith('data:image/'):
                raise ValueError('Invalid image format')
        return v

# ---------- User schemas ----------
class UserCreate(AppBaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    full_name: Optional[str] = None
    captcha_id: str
    captcha_answer: str

class UserOut(AppBaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_admin: bool
    created_at: datetime
    profile_image_url: Optional[str] = None

class Token(AppBaseModel):
    access_token: str
    token_type: str
    mfa_required: Optional[bool] = False

class MFAVerify(AppBaseModel):
    token: str
    otp: str

class ForgotPasswordRequest(AppBaseModel):
    email: EmailStr

class PasswordResetConfirm(AppBaseModel):
    email: EmailStr
    otp: str
    new_password: str
    confirm_password: str

class CaptchaResponse(AppBaseModel):
    captcha_id: str
    question: str

class UnlockAccountRequest(AppBaseModel):
    email: EmailStr
    otp: str

# ---------- Incident output schemas ----------
class IncidentOut(AppBaseModel):
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
class SosCreate(AppBaseModel):
    lat: float
    lng: float

class SosOut(AppBaseModel):
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

class FCMTokenCreate(AppBaseModel):
    token: str

class AnalyticsResponse(AppBaseModel):
    monthly_stats: List[dict]
    area_stats: List[dict]

class NotificationOut(AppBaseModel):
    id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime