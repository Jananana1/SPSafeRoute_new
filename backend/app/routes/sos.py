from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth

router = APIRouter(prefix="/sos", tags=["sos"])

@router.post("/", response_model=schemas.SosOut)
def create_sos(alert: schemas.SosCreate, db: Session = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_alert = models.SosAlert(**alert.dict(), user_id=current_user.id)
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.get("/", response_model=List[schemas.SosOut])
def get_sos_alerts(db: Session = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    alerts = db.query(models.SosAlert).order_by(models.SosAlert.created_at.desc()).all()
    return alerts