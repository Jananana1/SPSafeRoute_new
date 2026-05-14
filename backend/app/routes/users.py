from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
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

# ========== ADD THIS ENDPOINT ==========
@router.post("/fcm-token")
def save_fcm_token(
    data: schemas.FCMTokenCreate,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Delete existing token for this user (optional – replace old token)
    db.query(models.FCMToken).filter(
        models.FCMToken.user_id == current_user.id
    ).delete()
    # Save the new token
    new_token = models.FCMToken(
        user_id=current_user.id,
        token=data.token
    )
    db.add(new_token)
    db.commit()
    return {"message": "FCM token saved"}