import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Gmail SMTP Settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Your Gmail
SMTP_USERNAME = "santosjanna858@gmail.com"

# Gmail App Password
SMTP_PASSWORD = "frft ktez rzmo cxgp"


def send_email(to_email: str, subject: str, body: str, is_html: bool = False):
    try:
        # Create email message
        msg = MIMEMultipart()
        msg["From"] = SMTP_USERNAME
        msg["To"] = to_email
        msg["Subject"] = subject

        # Attach message body
        msg.attach(MIMEText(body, "html" if is_html else "plain"))

        # Connect to Gmail SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()

        # Login to Gmail
        server.login(SMTP_USERNAME, SMTP_PASSWORD)

        # Send email
        server.send_message(msg)

        # Close connection
        server.quit()

        print("Email sent successfully!")
        return True

    except Exception as e:
        print("Failed to send email:")
        print(e)
        return False
