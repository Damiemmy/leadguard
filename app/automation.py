from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import (
    Lead,
    FollowUp,
    FollowUpStatus
)


def create_lead_automation(
    db: Session,
    lead: Lead
):
    follow_up = FollowUp(
        lead_id=lead.id,
        message=(
            f"Follow up with {lead.customer_name} "
            f"about their {lead.service_type} enquiry."
        ),
        scheduled_for=datetime.now(timezone.utc)
        + timedelta(hours=1),
        status=FollowUpStatus.PENDING
    )

    db.add(follow_up)
    db.flush()

    return follow_up


def send_acknowledgement(lead: Lead):
    message = (
        f"Hello {lead.customer_name}, "
        f"we received your {lead.service_type} enquiry. "
        "Our team will contact you shortly."
    )

    # Temporary simulation; later we integrate an SMS provider.
    print(f"[SIMULATED SMS] To: {lead.phone_number}")
    print(f"[SIMULATED SMS] Message: {message}")


    