from sqlalchemy.orm import Session
from .models import FCMToken
from .firebase_config import send_fcm_notification
import logging

logger = logging.getLogger(__name__)

def send_fcm_to_user(db: Session, user_id: int, title: str, body: str):
    """Send FCM push using all stored tokens for a specific user."""
    token_objs = (
        db.query(FCMToken)
        .filter(FCMToken.user_id == user_id)
        .order_by(FCMToken.id.desc())
        .all()
    )
    if not token_objs:
        logger.warning(f"No FCM tokens found for user_id={user_id}")
        return False

    sent_tokens = set()
    success = False

    for token_obj in token_objs:
        if token_obj.token in sent_tokens:
            continue
        token_suffix = token_obj.token[-10:]
        try:
            result = send_fcm_notification(token_obj.token, title, body)
            if result is not None:
                success = True
                sent_tokens.add(token_obj.token)
                logger.info(f"Push sent to user {user_id}, token ...{token_suffix}")
                break
            else:
                logger.warning(f"Push to user {user_id} returned no result for token ...{token_suffix}")
        except Exception as e:
            logger.error(f"Failed to send push to token ...{token_suffix}: {e}")
            try:
                db.delete(token_obj)
                db.commit()
            except Exception:
                db.rollback()

    return success


def send_push_to_user(db: Session, user_id: int, title: str, body: str):
    """Create a DB notification and send push to a specific user."""
    from .models import Notification
    notif = Notification(user_id=user_id, title=title, message=body)
    db.add(notif)
    db.commit()

    return send_fcm_to_user(db, user_id, title, body)


def send_push_to_all_users(db: Session, title: str, body: str, exclude_user_id: int = None):
    """Send ONE notification per account to all users, with optional exclusion."""
    from .models import User, Notification

    query = db.query(User)
    if exclude_user_id is not None:
        query = query.filter(User.id != exclude_user_id)
    users = query.all()

    if not users:
        logger.warning("No users found to notify")
        return False

    for u in users:
        notif = Notification(user_id=u.id, title=title, message=body)
        db.add(notif)
    db.commit()

    success = False
    for u in users:
        if send_fcm_to_user(db, u.id, title, body):
            success = True

    return success

def send_push_to_other_users(db: Session, exclude_user_id: int, title: str, body: str):
    """Send ONE notification per non-admin account to all users EXCEPT the given user."""
    from .models import User, Notification

    users = db.query(User).filter(User.id != exclude_user_id, User.is_admin == False).all()
    if not users:
        logger.warning("No other non-admin users found to notify")
        return False

    for u in users:
        notif = Notification(user_id=u.id, title=title, message=body)
        db.add(notif)
    db.commit()

    success = False
    for u in users:
        if send_fcm_to_user(db, u.id, title, body):
            success = True

    return success

def send_push_to_admins(db: Session, exclude_user_id: int, title: str, body: str):
    """Send ONE notification per admin account EXCEPT the given user."""
    from .models import User, Notification

    admins = db.query(User).filter(User.id != exclude_user_id, User.is_admin == True).all()
    if not admins:
        logger.warning("No admin users found to notify")
        return False

    for admin in admins:
        notif = Notification(user_id=admin.id, title=title, message=body)
        db.add(notif)
    db.commit()

    success = False
    for admin in admins:
        if send_fcm_to_user(db, admin.id, title, body):
            success = True

    return success