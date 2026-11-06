from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.models import LeadStatus, LeadUrgency


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
    status: LeadStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)