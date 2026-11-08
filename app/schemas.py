from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.models import LeadStatus, LeadUrgency

from app.models import LeadStatus, LeadUrgency, FollowUpStatus

class LeadCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=150)
    phone_number: str = Field(min_length=7, max_length=30)
    email: str | None = None
    service_type: str = Field(min_length=2, max_length=100)
    message: str = Field(min_length=5)
    urgency: LeadUrgency = LeadUrgency.MEDIUM


class LeadResponse(BaseModel):
    id: int
    customer_name: str
    phone_number: str
    email: str | None
    service_type: str
    message: str
    urgency: LeadUrgency
    #intelligence fields start
    customer_intent: str
    recommended_action: str
    requires_human_review: bool
    #intelligence fields end
    status: LeadStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeadStatusUpdate(BaseModel):
    status: LeadStatus


class FollowUpStatusUpdate(BaseModel):
    status: FollowUpStatus


class FollowUpResponse(BaseModel):
    id: int
    lead_id: int
    message: str
    scheduled_for: datetime
    status: FollowUpStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)