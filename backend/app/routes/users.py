from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import re
import uuid
from .. import schemas, models, auth

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@router.get("/", response_model=List[schemas.UserOut])
def get_users(db: Session = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    users = db.query(models.User).all()
    return users

# ========== NOTIFICATIONS ENDPOINTS ==========
@router.get("/notifications", response_model=List[schemas.NotificationOut])
def get_notifications(db: Session = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id
    ).order_by(models.Notification.created_at.desc()).limit(50).all()

@router.put("/notifications/{notif_id}/read")
def mark_notification_read(notif_id: int, db: Session = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_user)):
    notif = db.query(models.Notification).filter(
        models.Notification.id == notif_id,
        models.Notification.user_id == current_user.id
    ).first()
    if notif and not notif.is_read:
        notif.is_read = True
        db.commit()
    return {"status": "ok"}


# ========== FCM TOKEN ENDPOINT ==========
@router.post("/fcm-token")
def save_fcm_token(
    data: schemas.FCMTokenCreate,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Keep exactly one active token per account, and remove any stale duplicate token rows.
    db.query(models.FCMToken).filter(
        (models.FCMToken.user_id == current_user.id) |
        (models.FCMToken.token == data.token)
    ).delete(synchronize_session=False)
    new_token = models.FCMToken(
        user_id=current_user.id,
        token=data.token
    )
    db.add(new_token)
    db.commit()
    return {"message": "FCM token saved"}

# ========== PROFILE UPDATE ENDPOINT ==========
@router.put("/profile", response_model=schemas.UserOut)
async def update_profile(
    full_name: Optional[str] = Form(None),
    current_password: Optional[str] = Form(None),
    new_password: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None),
    remove_profile_image: Optional[bool] = Form(False),
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if new_password:
        if not current_password:
            raise HTTPException(400, "Current password required to set a new password")
        if not auth.verify_password(current_password, current_user.hashed_password):
            raise HTTPException(400, "Incorrect current password")
        
        strength = auth.check_password_strength(new_password)
        if strength in ["Too Short", "Weak"]:
            raise HTTPException(400, "New password is too weak. Must be at least 8 characters and contain uppercase, lowercase, and numbers.")
            
        current_user.hashed_password = auth.get_password_hash(new_password)
        
    if full_name is not None:
        normalized_full_name = full_name.strip()
        if normalized_full_name == "":
            current_user.full_name = None
        else:
            if len(normalized_full_name) < 2 or len(normalized_full_name) > 100:
                raise HTTPException(400, "Full name must be between 2 and 100 characters.")
            suspicious_pattern = re.compile(r"<script|javascript:|onclick|onerror|alert\(|eval\(|<[^>]+>", re.IGNORECASE)
            if suspicious_pattern.search(normalized_full_name):
                raise HTTPException(400, "Full name contains invalid characters.")
            current_user.full_name = normalized_full_name
        
    if remove_profile_image:
        current_user.profile_image_url = None
    elif profile_image:
        allowed_types = {"image/jpeg", "image/png", "image/gif"}
        allowed_extensions = {"jpg", "jpeg", "png", "gif"}
        content_type = profile_image.content_type.lower() if profile_image.content_type else ""
        if content_type not in allowed_types:
            raise HTTPException(400, "Only JPEG, PNG, or GIF profile images are allowed.")

        filename_ext = os.path.splitext(profile_image.filename)[1].lower().lstrip('.')
        if filename_ext not in allowed_extensions:
            raise HTTPException(400, "Invalid profile image file extension.")

        content = await profile_image.read()
        max_size = 2 * 1024 * 1024
        if len(content) > max_size:
            raise HTTPException(400, "Profile image must be 2MB or smaller.")

        filename = f"{uuid.uuid4()}.{filename_ext}"
        filepath = os.path.join("uploads", "profiles", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(content)
        current_user.profile_image_url = f"/uploads/profiles/{filename}"
        
    db.commit()
    db.refresh(current_user)
    return current_user