import os
from pathlib import Path
import warnings

FIREBASE_AVAILABLE = False
messaging = None

try:
    import firebase_admin
    from firebase_admin import credentials, messaging as fb_messaging

    # Search for the credentials file in several likely locations so the
    # server works regardless of which directory it is launched from.
    _this_file = Path(__file__).resolve()
    _candidates = [
        _this_file.parent.parent.parent / "firebase-adminsdk.json",        # SPSafeRoute_new/firebase-adminsdk.json
        _this_file.parent.parent.parent.parent / "firebase-adminsdk.json", # one level higher
        Path.cwd() / "firebase-adminsdk.json",                             # CWD (where run.py is)
        Path.cwd().parent / "firebase-adminsdk.json",
    ]

    cred_path = None
    for candidate in _candidates:
        if candidate.exists():
            cred_path = str(candidate)
            break

    if cred_path:
        # Guard against double-initialization — happens on uvicorn --reload
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print(f"[Firebase] Initialized with {cred_path}")
        else:
            print("[Firebase] Already initialized, reusing existing app.")
        messaging = fb_messaging
        FIREBASE_AVAILABLE = True
    else:
        warnings.warn(
            "[Firebase] Credentials not found (searched: "
            + ", ".join(str(c) for c in _candidates)
            + "). Push notifications disabled."
        )

except ImportError:
    warnings.warn("[Firebase] Admin SDK not installed (pip install firebase-admin). Push disabled.")
except Exception as e:
    warnings.warn(f"[Firebase] Initialization failed: {e}. Push disabled.")


def send_fcm_notification(token: str, title: str, body: str,
                          icon: str = "/static/icons/android-chrome-192x192.png"):
    if not FIREBASE_AVAILABLE or messaging is None:
        print(f"[PUSH SKIPPED - Firebase not configured] {title}: {body}")
        return None
    try:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            android=messaging.AndroidConfig(
                notification=messaging.AndroidNotification(icon=icon)
            ),
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(icon=icon)
            ),
            token=token,
        )
        result = messaging.send(message)
        print(f"[PUSH SENT] '{title}' → ...{token[-10:]}: {result}")
        return result
    except Exception as e:
        print(f"[PUSH ERROR] Failed for token ...{token[-10:]}: {e}")
        return None
  