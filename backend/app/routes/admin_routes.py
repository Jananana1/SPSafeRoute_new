from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List
from . import models, schemas, auth, push_service
from .database import SessionLocal

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
    db.delete(inc)
    db.commit()
    return {"message": "Deleted"}

@router.post("/incidents/{incident_id}/complete")
def complete_incident(incident_id: int, db: Session = Depends(get_db), admin: models.User = Depends(auth.get_current_admin)):
    inc = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(404, "Not found")
    inc.status = models.IncidentStatus.COMPLETED
    db.commit()
    push_service.send_push_to_user(
        db, inc.user_id,
        "Incident Resolved",
        f"Your {inc.type} report at {inc.location_name or 'your location'} has been completed."
    )
    return {"message": "Completed & user notified"}

@router.get("/analytics")
def analytics(db: Session = Depends(get_db), admin: models.User = Depends(auth.get_current_admin)):
    try:
        from sqlalchemy import text
        
        # Monthly incident counts
        monthly_sql = text("""
            SELECT DATE_FORMAT(created_at, '%Y-%m') as month, COUNT(*) as count
            FROM incidents
            GROUP BY month
            ORDER BY month
        """)
        monthly_result = db.execute(monthly_sql).fetchall()
        monthly_stats = [{"month": row[0], "count": row[1]} for row in monthly_result]
        
        # Most prone areas
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
        
        return {"monthly_stats": monthly_stats, "area_stats": area_stats}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"monthly_stats": [], "area_stats": []}