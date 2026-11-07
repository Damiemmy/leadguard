from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Lead, LeadStatus
from app.schemas import LeadCreate, LeadResponse
from app.models import Lead, LeadStatus, LeadUrgency, FollowUp, FollowUpStatus

from fastapi import BackgroundTasks
from datetime import datetime, timezone

from app.models import FollowUp
from app.automation import (
    create_lead_automation,
    send_acknowledgement
)
from app.intelligence import analyze_lead


router = APIRouter(prefix="/leads", tags=["Leads"])


# @router.post("/", response_model=LeadResponse, status_code=201)
# def create_lead(
#     lead_data: LeadCreate,
#     background_tasks: BackgroundTasks,
#     db: Session = Depends(get_db)
# ):
#     new_lead = Lead(**lead_data.model_dump())

#     try:
#         db.add(new_lead)
#         db.flush()

#         create_lead_automation(db, new_lead)

#         db.commit()
#         db.refresh(new_lead)

#     except Exception:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail="Unable to process lead"
#         )

#     background_tasks.add_task(
#         send_acknowledgement,
#         new_lead
#     )

#     return new_lead

@router.post("/", response_model=LeadResponse, status_code=201)
def create_lead(
    lead_data: LeadCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    new_lead = Lead(**lead_data.model_dump())

    try:
        # Analyse the customer's message
        analysis = analyze_lead(
            new_lead.message,
            new_lead.service_type
        )

        # Preserve any higher urgency explicitly supplied by the user
        urgency_rank = {
            LeadUrgency.LOW: 1,
            LeadUrgency.MEDIUM: 2,
            LeadUrgency.HIGH: 3,
        }

        if urgency_rank[analysis["urgency"]] > urgency_rank[new_lead.urgency]:
            new_lead.urgency = analysis["urgency"]

        # Store intelligence results
        new_lead.customer_intent = analysis["customer_intent"]
        new_lead.recommended_action = analysis["recommended_action"]
        new_lead.requires_human_review = analysis["requires_human_review"]

        # Save lead and create follow-up in one transaction
        db.add(new_lead)
        db.flush()

        create_lead_automation(db, new_lead)

        db.commit()
        db.refresh(new_lead)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to process lead"
        )

    background_tasks.add_task(
        send_acknowledgement,
        new_lead.customer_name,
        new_lead.phone_number,
        new_lead.service_type
    )

    return new_lead

@router.get("/", response_model=list[LeadResponse])
def get_leads(db: Session = Depends(get_db)):
    return db.query(Lead).order_by(Lead.created_at.desc()).all()


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    return lead

@router.get("/follow-ups/due")
def get_due_followups(
    db: Session = Depends(get_db)
):
    now = datetime.now(timezone.utc)

    followups = (
        db.query(FollowUp)
        .filter(
            FollowUp.scheduled_for <= now,
            FollowUp.status == "pending"
        )
        .all()
    )

    return followups