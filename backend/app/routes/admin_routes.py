from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from datetime import datetime
import logging

from . import models, schemas, auth, push_service
from .database import SessionLocal

router = APIRouter(prefix="/admin", tags=["admin"])

# Setup logging
logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def sanitize_image_url(image_url: str | None) -> str | None:
    """
    If the image_url is a base64 data URI (e.g. 'data:image/png;base64,...'),
    return None instead — we don't store raw base64 blobs in the history table.
    Regular URLs (http/https paths) are kept as-is.
    """
    if image_url and image_url.startswith("data:"):
        return None
    return image_url


@router.get("/dashboard", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    current_user: models.User = Depends(auth.get_current_admin)
):
    try:
        return templates.TemplateResponse(
            "admin_dashboard.html",
            {"request": request, "user": current_user}
        )
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        return HTMLResponse(content=f"<h1>Error loading dashboard: {str(e)}</h1>", status_code=500)


@router.get("/incidents", response_model=List[schemas.IncidentOutWithStatus])
def get_incidents(
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.get_current_admin)
):
    try:
        incidents = (
            db.query(models.Incident)
            .order_by(models.Incident.created_at.desc())
            .all()
        )
        return incidents
    except Exception as e:
        logger.error(f"Get incidents error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/incidents/{incident_id}")
def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.get_current_admin)
):
    try:
        inc = (
            db.query(models.Incident)
            .filter(models.Incident.id == incident_id)
            .first()
        )

        if not inc:
            raise HTTPException(status_code=404, detail="Incident not found")

        # Save history before deleting
        history = models.IncidentHistory(
            incident_id=inc.id,
            action="deleted",
            inc_type=inc.type,
            description=inc.description,
            location_name=inc.location_name,
            lat=inc.lat,
            lng=inc.lng,
            user_id=inc.user_id,
            image_url=sanitize_image_url(inc.image_url),
            reported_at=inc.created_at,
            actioned_at=datetime.utcnow()
        )

        db.add(history)

        # Soft delete
        inc.status = "deleted"

        db.commit()
        
        return JSONResponse(content={"message": "Incident deleted successfully"})

    except Exception as e:
        db.rollback()
        logger.error(f"Delete incident error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/incidents/{incident_id}/complete")
def complete_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.get_current_admin)
):
    try:
        inc = (
            db.query(models.Incident)
            .filter(models.Incident.id == incident_id)
            .first()
        )

        if not inc:
            raise HTTPException(status_code=404, detail="Incident not found")

        # Update status
        inc.status = "completed"

        # Save to history
        history = models.IncidentHistory(
            incident_id=inc.id,
            action="resolved",
            inc_type=inc.type,
            description=inc.description,
            location_name=inc.location_name,
            lat=inc.lat,
            lng=inc.lng,
            user_id=inc.user_id,
            image_url=sanitize_image_url(inc.image_url),
            reported_at=inc.created_at,
            actioned_at=datetime.utcnow()
        )

        db.add(history)
        db.commit()

        # Send push notification (don't let notification failure break the operation)
        try:
            push_service.send_push_to_user(
                db,
                inc.user_id,
                "Incident Resolved",
                f"Your {inc.type} report at {inc.location_name or 'your location'} has been completed."
            )
        except Exception as notify_error:
            logger.error(f"Push notification error: {str(notify_error)}")
            # Continue even if notification fails

        return JSONResponse(content={"message": "Completed and user notified"})

    except Exception as e:
        db.rollback()
        logger.error(f"Complete incident error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.get_current_admin)
):
    try:
        history = (
            db.query(models.IncidentHistory)
            .order_by(models.IncidentHistory.actioned_at.desc())
            .all()
        )

        result = []

        for h in history:
            user = (
                db.query(models.User)
                .filter(models.User.id == h.user_id)
                .first()
            )

            full_name = (
                user.full_name
                if user and user.full_name
                else (user.email if user else f"User #{h.user_id}")
            )

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
                "reported_at": (
                    h.reported_at.isoformat()
                    if h.reported_at else None
                ),
                "actioned_at": (
                    h.actioned_at.isoformat()
                    if h.actioned_at else None
                ),
            })

        return result

    except Exception as e:
        logger.error(f"Get history error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics")
def analytics(
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.get_current_admin)
):
    try:
        # Monthly incident statistics for MySQL
        monthly_sql = text("""
            SELECT DATE_FORMAT(created_at, '%%Y-%%m') AS month,
                   COUNT(*) AS count
            FROM incidents
            WHERE status != 'deleted'
            GROUP BY DATE_FORMAT(created_at, '%%Y-%%m')
            ORDER BY month DESC
            LIMIT 12
        """)

        monthly_result = db.execute(monthly_sql).fetchall()

        monthly_stats = [
            {
                "month": row[0],
                "count": row[1]
            }
            for row in monthly_result
        ]

        # Most incident-prone areas
        area_sql = text("""
            SELECT location_name,
                   COUNT(*) AS count
            FROM incidents
            WHERE location_name IS NOT NULL
              AND location_name != ''
              AND status != 'deleted'
            GROUP BY location_name
            ORDER BY count DESC
            LIMIT 10
        """)

        area_result = db.execute(area_sql).fetchall()

        area_stats = [
            {
                "area": row[0],
                "count": row[1]
            }
            for row in area_result
        ]

        return JSONResponse(content={
            "monthly_stats": monthly_stats,
            "area_stats": area_stats
        })

    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return JSONResponse(
            content={
                "monthly_stats": [],
                "area_stats": [],
                "error": str(e)
            },
            status_code=500
        )