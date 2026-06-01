import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

from app.database import get_connection, init_db
from app.email_utils import send_lead_notification


app = FastAPI(title="United Code Compliance Leads API")


FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "*")
ADMIN_KEY = os.getenv("ADMIN_KEY")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN] if FRONTEND_ORIGIN != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LeadCreate(BaseModel):
    firstName: str = Field(..., min_length=1)
    lastName: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)
    email: EmailStr
    hoodLength: str = Field(..., min_length=1)
    fans: int = Field(..., ge=0)
    lastServiced: Optional[str] = None
    serviceWanted: Optional[str] = None
    notes: Optional[str] = None


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/health")
def health():
    return {"ok": True, "message": "United Code Compliance backend is running."}


@app.post("/api/leads")
def create_lead(lead: LeadCreate):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO leads (
                        first_name,
                        last_name,
                        phone,
                        email,
                        hood_length,
                        fans,
                        last_serviced,
                        service_wanted,
                        notes
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (
                        lead.firstName.strip(),
                        lead.lastName.strip(),
                        lead.phone.strip(),
                        str(lead.email).strip(),
                        lead.hoodLength.strip(),
                        lead.fans,
                        lead.lastServiced.strip() if lead.lastServiced else None,
                        lead.serviceWanted.strip() if lead.serviceWanted else None,
                        lead.notes.strip() if lead.notes else None,
                    ),
                )

                lead_id = cursor.fetchone()["id"]

            conn.commit()

        email_sent = send_lead_notification(lead_id, lead)

        return {
            "ok": True,
            "message": "Quote request submitted successfully.",
            "lead_id": lead_id,
            "email_sent": email_sent,
        }

    except Exception as e:
        print(f"Lead creation failed: {e}")
        raise HTTPException(status_code=500, detail="Could not save quote request.")


@app.get("/api/leads")
def get_leads(admin_key: str = Query(...)):
    if not ADMIN_KEY or admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key.")

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM leads
                ORDER BY created_at DESC;
                """
            )
            leads = cursor.fetchall()

    return {"ok": True, "leads": leads}