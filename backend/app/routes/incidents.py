from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models, schemas, auth
import traceback

router = APIRouter(prefix="/incidents", tags=["incidents"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_incidents(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    try:
        incidents = db.query(models.Incident).filter(
            models.Incident.status != 'completed'
        ).order_by(models.Incident.created_at.desc()).all()
        return incidents
    except Exception as e:
        print("GET /incidents error:", e)
        traceback.print_exc()
        return []   # return empty list so frontend doesn't crash

@router.post("/", response_model=schemas.IncidentOut)
def create_incident(
    incident: schemas.IncidentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    try:
        incident_dict = incident.dict()
        # Ensure optional fields are set to None if missing
        incident_dict['location_name'] = incident_dict.get('location_name')
        incident_dict['image_url'] = incident_dict.get('image_url')
        incident_dict['user_id'] = current_user.id

        db_incident = models.Incident(**incident_dict)
        db.add(db_incident)
        db.commit()
        db.refresh(db_incident)

        # Broadcast to all OTHER users (exclude reporter)
        from ..push_service import send_push_to_other_users
        location = incident.location_name or "your area"
        send_push_to_other_users(
            db,
            exclude_user_id=current_user.id,
            title="New Incident Reported",
            body=f"{incident.type.capitalize()} reported at {location}"
        )

        return db_incident
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))