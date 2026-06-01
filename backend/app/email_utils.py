import os
import smtplib
from email.message import EmailMessage


SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

LEAD_TO_EMAIL = os.getenv("LEAD_TO_EMAIL", "unitedhoodcompliance@gmail.com")
LEAD_FROM_EMAIL = os.getenv("LEAD_FROM_EMAIL", SMTP_USER)


def send_lead_notification(lead_id: int, lead):
    if not SMTP_USER or not SMTP_PASSWORD:
        print("Email skipped: SMTP_USER or SMTP_PASSWORD is missing.")
        return False

    subject = f"New Quote Request #{lead_id} - United Code Compliance"

    body = f"""
New quote request received.

Lead ID: {lead_id}

Name: {lead.firstName} {lead.lastName}
Phone: {lead.phone}
Email: {lead.email}

Length of Hood: {lead.hoodLength}
Number of Fans: {lead.fans}
Last Serviced: {lead.lastServiced or "Not provided"}
Service Wanted: {lead.serviceWanted or "Not selected"}

Additional Notes:
{lead.notes or "No notes provided."}
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = LEAD_FROM_EMAIL
    msg["To"] = LEAD_TO_EMAIL
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        return True

    except Exception as e:
        print(f"Email notification failed: {e}")
        return False