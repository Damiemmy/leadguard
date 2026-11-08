
from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database import get_db

from app.models import (
    Lead,
    LeadStatus,
    LeadUrgency,
    FollowUp,
    FollowUpStatus,
)

from app.schemas import (
    LeadCreate,
    LeadResponse,
    LeadStatusUpdate,
    FollowUpStatusUpdate,
    FollowUpResponse,
)

from app.automation import (
    create_lead_automation,
    send_acknowledgement,
)

from app.intelligence import analyze_lead


router = APIRouter(
    prefix="/leads",
    tags=["Leads"],
)


# ==========================================================
# 1. CREATE A NEW LEAD
# ==========================================================

@router.post(
    "/",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_lead(
    lead_data: LeadCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    new_lead = Lead(**lead_data.model_dump())

    try:
        # Analyse the customer's enquiry.
        analysis = analyze_lead(
            new_lead.message,
            new_lead.service_type,
        )

        # Preserve explicitly supplied higher urgency.
        urgency_rank = {
            LeadUrgency.LOW: 1,
            LeadUrgency.MEDIUM: 2,
            LeadUrgency.HIGH: 3,
        }

        detected_urgency = analysis["urgency"]

        if (
            urgency_rank[detected_urgency]
            > urgency_rank[new_lead.urgency]
        ):
            new_lead.urgency = detected_urgency

        # Store intelligence results.
        new_lead.customer_intent = analysis["customer_intent"]
        new_lead.recommended_action = analysis["recommended_action"]
        new_lead.requires_human_review = analysis["requires_human_review"]

        # Save the lead and obtain its database ID.
        db.add(new_lead)
        db.flush()

        # Automatically create a follow-up task.
        create_lead_automation(db, new_lead)

        # Commit lead and follow-up together.
        db.commit()
        db.refresh(new_lead)

    except Exception:
        db.rollback()

        # Log the actual error on the server.
        import logging
        logging.exception("Unable to process lead")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process lead",
        )

    # Send simulated acknowledgement after successful commit.
    # Pass primitive values, not the SQLAlchemy object.
    background_tasks.add_task(
        send_acknowledgement,
        new_lead.customer_name,
        new_lead.phone_number,
        new_lead.service_type,
    )

    return new_lead


# ==========================================================
# 2. RETRIEVE ALL LEADS
# ==========================================================

@router.get(
    "/",
    response_model=list[LeadResponse],
)
def get_leads(
    db: Session = Depends(get_db),
):
    return (
        db.query(Lead)
        .order_by(Lead.created_at.desc())
        .all()
    )


# ==========================================================
# 3. UPDATE LEAD STATUS
# ==========================================================

@router.patch(
    "/{lead_id}/status",
    response_model=LeadResponse,
)
def update_lead_status(
    lead_id: int,
    status_data: LeadStatusUpdate,
    db: Session = Depends(get_db),
):
    lead = db.get(Lead, lead_id)

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )

    lead.status = status_data.status

    try:
        db.commit()
        db.refresh(lead)

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update lead status",
        )

    return lead


# ==========================================================
# 4. RETRIEVE OVERDUE FOLLOW-UPS
# ==========================================================

@router.get(
    "/follow-ups/due",
    response_model=list[FollowUpResponse],
)
def get_due_followups(
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)

    return (
        db.query(FollowUp)
        .filter(
            FollowUp.scheduled_for <= now,
            FollowUp.status == FollowUpStatus.PENDING,
        )
        .order_by(FollowUp.scheduled_for.asc())
        .all()
    )


# ==========================================================
# 5. RETRIEVE ALL FOLLOW-UPS
# ==========================================================

@router.get(
    "/follow-ups",
    response_model=list[FollowUpResponse],
)
def get_followups(
    db: Session = Depends(get_db),
):
    return (
        db.query(FollowUp)
        .order_by(FollowUp.scheduled_for.asc())
        .limit(100)
        .all()
    )


# ==========================================================
# 6. UPDATE FOLLOW-UP STATUS
# ==========================================================

@router.patch(
    "/follow-ups/{followup_id}/status",
    response_model=FollowUpResponse,
)
def update_followup_status(
    followup_id: int,
    status_data: FollowUpStatusUpdate,
    db: Session = Depends(get_db),
):
    followup = db.get(FollowUp, followup_id)

    if not followup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up not found",
        )

    followup.status = status_data.status

    try:
        db.commit()
        db.refresh(followup)

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update follow-up",
        )

    return followup


# ==========================================================
# 7. RETRIEVE A SINGLE LEAD
# IMPORTANT: KEEP THIS ROUTE LAST.
# ==========================================================

@router.get(
    "/{lead_id}",
    response_model=LeadResponse,
)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
):
    lead = db.get(Lead, lead_id)

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )

    return lead
