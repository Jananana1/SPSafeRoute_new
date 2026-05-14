from sqlalchemy.orm import Session
from .models import FCMToken
from .firebase_config import send_fcm_notification
import logging

logger = logging.getLogger(__name__)

def send_push_to_user(db: Session, user_id: int, title: str, body: str):
    """Send notification to a specific user (all tokens of that user)."""
    tokens = db.query(FCMToken).filter(FCMToken.user_id == user_id).all()
    if not tokens:
        logger.warning(f"No FCM tokens found for user_id={user_id}")
        return False
    success = False
    for t in tokens:
        try:
            result = send_fcm_notification(t.token, title, body)
            if result is not None:
                success = True
            logger.info(f"Push sent to user {user_id}, token ...{t.token[-10:]}")
        except Exception as e:
            logger.error(f"Failed to send push to token ...{t.token[-10:]}: {e}")
            # Remove stale/invalid token
            db.delete(t)
            db.commit()
    return success

def send_push_to_other_users(db: Session, exclude_user_id: int, title: str, body: str):
    """Send notification to all users EXCEPT the given user."""
    tokens = db.query(FCMToken).filter(FCMToken.user_id != exclude_user_id).all()
    if not tokens:
        logger.warning("No FCM tokens found for other users")
        return False
    success = False
    for token_obj in tokens:
        try:
            result = send_fcm_notification(token_obj.token, title, body)
            if result is not None:
                success = True
            logger.info(f"Push sent to user {token_obj.user_id}")
        except Exception as e:
            logger.error(f"Failed to send push to token ...{token_obj.token[-10:]}: {e}")
            # Remove stale/invalid token
            db.delete(token_obj)
            db.commit()
    return success
