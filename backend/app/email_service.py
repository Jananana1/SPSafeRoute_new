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


def _build_otp_html(otp_code: str, email_type: str = "verification") -> str:
    """Build a beautiful HTML email template for SP SafeRoute OTP emails."""

    if email_type == "registration":
        headline = "Welcome to SP SafeRoute!"
        subheading = "Complete your registration by verifying your email address."
        action_label = "Registration Verification Code"
        footer_note = "You are receiving this because you recently created an SP SafeRoute account."
    elif email_type == "login":
        headline = "Login Verification"
        subheading = "Use the code below to complete your sign-in."
        action_label = "Login Verification Code"
        footer_note = "You are receiving this because a login was attempted on your SP SafeRoute account."
    elif email_type == "reset":
        headline = "Password Reset Request"
        subheading = "Use the code below to reset your password."
        action_label = "Password Reset Code"
        footer_note = "You are receiving this because a password reset was requested for your account."
    else:
        headline = "Your Verification Code"
        subheading = "Use the code below to verify your identity."
        action_label = "Verification Code"
        footer_note = "You are receiving this from SP SafeRoute."

    digits = list(str(otp_code))
    digit_boxes = "".join(
        f'<td style="padding:0 6px;">'
        f'<div style="width:48px;height:60px;background:#f0f6ff;border:2px solid #1a56db;'
        f'border-radius:10px;font-size:32px;font-weight:800;color:#1a3a8f;'
        f'text-align:center;line-height:60px;font-family:monospace;">{d}</div></td>'
        for d in digits
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>SP SafeRoute</title>
</head>
<body style="margin:0;padding:0;background:#e8f0fe;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#e8f0fe;padding:40px 0;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0"
             style="background:#ffffff;border-radius:18px;overflow:hidden;
                    box-shadow:0 8px 32px rgba(26,86,219,0.13);max-width:560px;">

        <!-- Header -->
        <tr>
          <td style="background:linear-gradient(135deg,#1a3a8f 0%,#1a56db 60%,#3b82f6 100%);
                     padding:36px 40px 32px;text-align:center;">
            <div style="margin-bottom:14px;">
              <span style="display:inline-block;background:rgba(255,255,255,0.15);
                           border-radius:50%;width:64px;height:64px;line-height:64px;
                           font-size:30px;text-align:center;">&#128737;</span>
            </div>
            <h1 style="margin:0;color:#ffffff;font-size:26px;font-weight:700;letter-spacing:-0.5px;">
              SP SafeRoute
            </h1>
            <p style="margin:6px 0 0;color:#bfdbfe;font-size:13px;
                      letter-spacing:1.5px;text-transform:uppercase;font-weight:500;">
              Safe. Smart. Secure.
            </p>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:40px 40px 32px;">
            <h2 style="margin:0 0 10px;color:#1a3a8f;font-size:22px;font-weight:700;">
              {headline}
            </h2>
            <p style="margin:0 0 28px;color:#475569;font-size:15px;line-height:1.6;">
              {subheading}
            </p>

            <p style="margin:0 0 12px;color:#64748b;font-size:12px;font-weight:600;
                      text-transform:uppercase;letter-spacing:1.2px;">
              {action_label}
            </p>

            <table cellpadding="0" cellspacing="0" style="margin:0 auto 28px;">
              <tr>{digit_boxes}</tr>
            </table>

            <hr style="border:none;border-top:1px solid #e2e8f0;margin:0 0 24px;"/>

            <table width="100%" cellpadding="0" cellspacing="0"
                   style="background:#eff6ff;border-left:4px solid #1a56db;
                          border-radius:0 8px 8px 0;margin-bottom:20px;">
              <tr>
                <td style="padding:14px 16px;">
                  <p style="margin:0;color:#1e40af;font-size:13px;line-height:1.6;">
                    &#9200; <strong>This code expires in 5 minutes.</strong>
                    If you did not request this, please ignore this email.
                  </p>
                </td>
              </tr>
            </table>

            <p style="margin:0;color:#94a3b8;font-size:12px;line-height:1.7;">
              Never share this code with anyone. SP SafeRoute staff will
              <strong>never</strong> ask for your OTP.
            </p>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#f8faff;border-top:1px solid #e2e8f0;
                     padding:20px 40px;text-align:center;">
            <p style="margin:0 0 6px;color:#94a3b8;font-size:12px;">
              {footer_note}
            </p>
            <p style="margin:0;color:#cbd5e1;font-size:11px;">
              &copy; 2025 SP SafeRoute &nbsp;|&nbsp; All rights reserved
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


def send_email(to_email: str, subject: str, body: str, is_html: bool = False,
               otp_code: str = None, email_type: str = "verification"):
    """
    Send an email via Gmail SMTP.

    Pass `otp_code` and `email_type` to use the branded HTML OTP template.
    email_type options: 'registration', 'login', 'reset', 'verification'
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"SP SafeRoute <{SMTP_USERNAME}>"
        msg["To"] = to_email
        msg["Subject"] = subject

        if otp_code:
            html_body = _build_otp_html(otp_code, email_type)
            msg.attach(MIMEText(f"Your OTP code is: {otp_code}. It expires in 5 minutes.", "plain"))
            msg.attach(MIMEText(html_body, "html"))
        else:
            content_type = "html" if is_html else "plain"
            msg.attach(MIMEText(body, content_type))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()

        print("Email sent successfully!")
        return True

    except Exception as e:
        print("Failed to send email:")
        print(e)
        return False
