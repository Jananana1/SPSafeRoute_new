from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List
from . import models, schemas, auth, push_service
from .database import SessionLocal
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, current_user: models.User = Depends(auth.get_current_admin)):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "user": current_user})

@router.get("/incidents", response_model=List[schemas.IncidentOutWithStatus])
def get_incidents(db: Session = Depends(get_db), admin: models.User = Depends(auth.get_current_admin)):
    return db.query(models.Incident).order_by(models.Incident.created_at.desc()).all()

@router.delete("/incidents/{incident_id}")
def delete_incident(incident_id: int, db: Session = Depends(get_db), admin: models.User = Depends(auth.get_current_admin)):
    inc = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(404, "Not found")
    inc.status = 'deleted'
    db.commit()

    try:
        history = models.IncidentHistory(
            incident_id=inc.id,
            action="deleted",
            inc_type=inc.type,
            description=inc.description,
            location_name=inc.location_name,
            lat=inc.lat,
            lng=inc.lng,
            user_id=inc.user_id,
            image_url=inc.image_url,
            reported_at=inc.created_at,
            actioned_at=datetime.utcnow()
        )
        db.add(history)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to save incident history: {e}")

    return {"message": "Deleted"}

@router.post("/incidents/{incident_id}/complete")
def complete_incident(incident_id: int, db: Session = Depends(get_db), admin: models.User = Depends(auth.get_current_admin)):
    inc = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(404, "Not found")
    inc.status = 'completed'
    db.commit()

    try:
        history = models.IncidentHistory(
            incident_id=inc.id,
            action="resolved",
            inc_type=inc.type,
            description=inc.description,
            location_name=inc.location_name,
            lat=inc.lat,
            lng=inc.lng,
            user_id=inc.user_id,
            image_url=inc.image_url,
            reported_at=inc.created_at,
            actioned_at=datetime.utcnow()
        )
        db.add(history)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to save incident history: {e}")

    try:
        push_service.send_push_to_user(
            db, inc.user_id,
            "Incident Resolved",
            f"Your {inc.type} report at {inc.location_name or 'your location'} has been completed."
        )
    except Exception as e:
        print(f"Failed to send push notification: {e}")

    return {"message": "Completed & user notified"}

@router.get("/history")
def get_history(db: Session = Depends(get_db), admin: models.User = Depends(auth.get_current_admin)):
    history = db.query(models.IncidentHistory).order_by(models.IncidentHistory.actioned_at.desc()).all()
    result = []
    for h in history:
        user = db.query(models.User).filter(models.User.id == h.user_id).first()
        full_name = user.full_name if user and user.full_name else (user.email if user else f"User #{h.user_id}")
        result.append({
            "id": h.id,
            "incident_id": h.incident_id,
            "action": h.action,
            "type": h.inc_type,
            "description": h.description,
            "location_name": h.location_name,
            "lat": h.lat,
            "lng": h.lng,
            "reported_by": full_name,
            "reported_at": h.reported_at.isoformat() if h.reported_at else None,
            "actioned_at": h.actioned_at.isoformat() if h.actioned_at else None,
        })
    return result

@router.get("/analytics")
def analytics(db: Session = Depends(get_db), admin: models.User = Depends(auth.get_current_admin)):
    try:
        # Detect database type
        db_url = str(db.get_bind().url)
        
        # Monthly incident counts - database agnostic
        if 'postgresql' in db_url or 'postgres' in db_url:
            monthly_sql = text("""
                SELECT TO_CHAR(created_at, 'YYYY-MM') as month, COUNT(*) as count
                FROM incidents
                GROUP BY month
                ORDER BY month
            """)
        elif 'mysql' in db_url:
            monthly_sql = text("""
                SELECT DATE_FORMAT(created_at, '%Y-%m') as month, COUNT(*) as count
                FROM incidents
                GROUP BY month
                ORDER BY month
            """)
        else:  # SQLite or other
            monthly_sql = text("""
                SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count
                FROM incidents
                GROUP BY month
                ORDER BY month
            """)
        
        monthly_result = db.execute(monthly_sql).fetchall()
        monthly_stats = [{"month": row[0], "count": row[1]} for row in monthly_result]

        # Most prone areas - works across all databases
        area_sql = text("""
            SELECT location_name, COUNT(*) as count
            FROM incidents
            WHERE location_name IS NOT NULL AND location_name != ''
            GROUP BY location_name
            ORDER BY count DESC
            LIMIT 10
        """)
        area_result = db.execute(area_sql).fetchall()
        area_stats = [{"area": row[0], "count": row[1]} for row in area_result]

        # If no data, return empty arrays
        if not monthly_stats:
            # Try a simpler query to check if there's any data at all
            count_sql = text("SELECT COUNT(*) FROM incidents")
            total_count = db.execute(count_sql).scalar()
            print(f"Total incidents in database: {total_count}")
            
            if total_count == 0:
                print("No incidents found in database")
            else:
                print(f"Found {total_count} incidents but monthly query returned nothing")

        return {"monthly_stats": monthly_stats, "area_stats": area_stats}
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Return empty data instead of failing
        return {"monthly_stats": [], "area_stats": []}