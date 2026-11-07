from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import (
    Lead,
    LeadStatus,
    LeadUrgency,
    FollowUp,
    FollowUpStatus,
)
from app.schemas import LeadResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):

    now = datetime.now(timezone.utc)

    total_leads = (
        db.query(func.count(Lead.id)).scalar() or 0
    )

    new_leads = (
        db.query(func.count(Lead.id))
        .filter(Lead.status == LeadStatus.NEW)
        .scalar() or 0
    )

    urgent_leads = (
        db.query(func.count(Lead.id))
        .filter(Lead.urgency == LeadUrgency.HIGH)
        .scalar() or 0
    )

    booked_leads = (
        db.query(func.count(Lead.id))
        .filter(Lead.status == LeadStatus.BOOKED)
        .scalar() or 0
    )

    leads_requiring_review = (
        db.query(func.count(Lead.id))
        .filter(Lead.requires_human_review.is_(True))
        .scalar() or 0
    )

    pending_followups = (
        db.query(func.count(FollowUp.id))
        .filter(FollowUp.status == FollowUpStatus.PENDING)
        .scalar() or 0
    )

    overdue_followups = (
        db.query(func.count(FollowUp.id))
        .filter(
            FollowUp.status == FollowUpStatus.PENDING,
            FollowUp.scheduled_for <= now
        )
        .scalar() or 0
    )

    recent_leads = (
        db.query(Lead)
        .order_by(Lead.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "total_leads": total_leads,
        "new_leads": new_leads,
        "urgent_leads": urgent_leads,
        "booked_leads": booked_leads,
        "leads_requiring_review": leads_requiring_review,
        "pending_followups": pending_followups,
        "overdue_followups": overdue_followups,
        "recent_leads": [
            LeadResponse.model_validate(lead).model_dump(mode="json")
            for lead in recent_leads
        ],
    }