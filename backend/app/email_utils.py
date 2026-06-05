import os
import resend


RESEND_API_KEY = os.getenv("RESEND_API_KEY")
LEAD_TO_EMAIL = os.getenv("LEAD_TO_EMAIL", "unitedhoodcompliance@gmail.com")
LEAD_FROM_EMAIL = os.getenv("LEAD_FROM_EMAIL", "United Code Compliance <onboarding@resend.dev>")


def send_lead_notification(lead_id: int, lead):
    if not RESEND_API_KEY:
        print("Email skipped: RESEND_API_KEY is missing.")
        return False

    resend.api_key = RESEND_API_KEY

    subject = f"New Quote Request #{lead_id} - United Code Compliance"

    text_body = f"""
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

    html_body = f"""
    <h2>New Quote Request</h2>
    <p><strong>Lead ID:</strong> {lead_id}</p>

    <h3>Customer Info</h3>
    <p><strong>Name:</strong> {lead.firstName} {lead.lastName}</p>
    <p><strong>Phone:</strong> {lead.phone}</p>
    <p><strong>Email:</strong> {lead.email}</p>

    <h3>Hood System Info</h3>
    <p><strong>Length of Hood:</strong> {lead.hoodLength}</p>
    <p><strong>Number of Fans:</strong> {lead.fans}</p>
    <p><strong>Last Serviced:</strong> {lead.lastServiced or "Not provided"}</p>
    <p><strong>Service Wanted:</strong> {lead.serviceWanted or "Not selected"}</p>

    <h3>Additional Notes</h3>
    <p>{lead.notes or "No notes provided."}</p>
    """

    try:
        resend.Emails.send({
            "from": LEAD_FROM_EMAIL,
            "to": [LEAD_TO_EMAIL],
            "subject": subject,
            "html": html_body,
            "text": text_body,
            "reply_to": lead.email,
        })

        return True

    except Exception as e:
        print(f"Resend email notification failed: {e}")
        return False