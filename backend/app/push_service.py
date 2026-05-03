from sqlalchemy.orm import Session
from .models import FCMToken
from .firebase_config import send_fcm_notification

def send_push_to_user(db: Session, user_id: int, title: str, body: str):
    """Send notification to a specific user (all tokens of that user)."""
    tokens = db.query(FCMToken).filter(FCMToken.user_id == user_id).all()
    if not tokens:
        return False
    for t in tokens:
        try:
            send_fcm_notification(t.token, title, body)
        except Exception as e:
            print(f"Failed to send to {t.token}: {e}")
    return True

def send_push_to_other_users(db: Session, exclude_user_id: int, title: str, body: str):
    """Send notification to all users EXCEPT the given user."""
    tokens = db.query(FCMToken).filter(FCMToken.user_id != exclude_user_id).all()
    if not tokens:
        return False
    for token_obj in tokens:
        try:
            send_fcm_notification(token_obj.token, title, body)
        except Exception as e:
            print(f"Failed to send to {token_obj.token}: {e}")
    return True