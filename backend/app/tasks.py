from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from .database import SessionLocal
from .models import Incident

def delete_expired_incidents():
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        db.query(Incident).filter(Incident.type == "accident", Incident.created_at <= now - timedelta(days=5)).delete()
        db.query(Incident).filter(Incident.type == "hazard", Incident.created_at <= now - timedelta(days=5)).delete()
        db.query(Incident).filter(Incident.type == "crime", Incident.created_at <= now - timedelta(days=5)).delete()
        db.commit()
    finally:
        db.close()

scheduler = BackgroundScheduler()
scheduler.add_job(delete_expired_incidents, 'interval', hours=1)