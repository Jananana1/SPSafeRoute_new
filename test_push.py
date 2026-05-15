# test_push.py
import firebase_admin
from firebase_admin import credentials

# Use raw string (r"") with correct path
cred_path = r"C:\Users\Personal Laptop\Downloads\SPSafeRoute_new\SPSafeRoute_new\firebase-adminsdk.json"
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
print("✅ Firebase initialized successfully!")