from sqlalchemy.orm import Session
from .models import FCMToken
from .firebase_config import send_fcm_notification
import logging

logger = logging.getLogger(__name__)

def send_push_to_user(db: Session, user_id: int, title: str, body: str):
    """Create a DB notification and send push to a specific user."""
    # 1. Create DB Notification
    from .models import Notification
    notif = Notification(user_id=user_id, title=title, message=body)
    db.add(notif)
    db.commit()

    # 2. Send FCM Push
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
            db.delete(t)
            db.commit()
    return success

def send_push_to_other_users(db: Session, exclude_user_id: int, title: str, body: str):
    """Send notification to all users EXCEPT the given user."""
    from .models import User, Notification
    
    # 1. Create DB Notifications
    users = db.query(User).filter(User.id != exclude_user_id).all()
    for u in users:
        notif = Notification(user_id=u.id, title=title, message=body)
        db.add(notif)
    db.commit()

    # 2. Send FCM Pushes
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
            db.delete(token_obj)
            db.commit()
    return success
