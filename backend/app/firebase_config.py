import os
from pathlib import Path
import warnings

try:
    import firebase_admin
    from firebase_admin import credentials, messaging

    # HARDCODE YOUR FULL PATH (replace with your actual path)
    cred_path = r"C:\Users\Personal Laptop\Desktop\SafeRoute_new\firebase-adminsdk.json"
    
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        FIREBASE_AVAILABLE = True
        print(f"Firebase initialized with {cred_path}")
    else:
        FIREBASE_AVAILABLE = False
        warnings.warn(f"Firebase credentials not found at {cred_path}. Push disabled.")
except ImportError:
    FIREBASE_AVAILABLE = False
    warnings.warn("Firebase Admin SDK not installed. Push disabled.")

def send_fcm_notification(token: str, title: str, body: str, icon: str = "/static/icon.png"):
    if not FIREBASE_AVAILABLE:
        print(f"Push notification would be sent: {title} - {body} (Firebase not configured)")
        return None
    try:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            android=messaging.AndroidConfig(notification=messaging.AndroidNotification(icon=icon)),
            webpush=messaging.WebpushConfig(notification=messaging.WebpushNotification(icon=icon)),
            token=token,
        )
        return messaging.send(message)
    except Exception as e:
        print(f"Error sending push: {e}")
        return None