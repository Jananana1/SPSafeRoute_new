from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ---------- User schemas ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_admin: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

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

class IncidentOutWithStatus(IncidentOut):
    status: IncidentStatusEnum

class FCMTokenCreate(BaseModel):
    token: str

class AnalyticsResponse(BaseModel):
    monthly_stats: List[dict]
    area_stats: List[dict]