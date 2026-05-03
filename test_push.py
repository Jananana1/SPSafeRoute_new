from backend.app.firebase_config import send_fcm_notification

# Replace with your actual token from the database
token = "da4vyEWsAgsI1EtWcufsJN:APA91bGX1IV9KIWlsC5LznIYHe1gu5BAMeKS0rD061liGv74cVUCwtPIxcw48_JukWDLIPTrzZgnaP-UHlGclfUm66_URPGRIsSaLO0MwFE2mArGTAVk6CY"
send_fcm_notification(token, "Test Title", "Test body")
print("Sent")