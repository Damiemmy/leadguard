from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import ForeignKey

from sqlalchemy import (
    String,
    Text,
    DateTime,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    BOOKED = "booked"
    LOST = "lost"


class LeadUrgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    customer_name: Mapped[str] = mapped_column(
        String(150), nullable=False
    )

    phone_number: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True
    )

    email: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    service_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    message: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    urgency: Mapped[LeadUrgency] = mapped_column(
        SQLEnum(LeadUrgency),
        default=LeadUrgency.MEDIUM,
        nullable=False
    )

    status: Mapped[LeadStatus] = mapped_column(
        SQLEnum(LeadStatus),
        default=LeadStatus.NEW,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

class FollowUpStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id: Mapped[int] = mapped_column(primary_key=True)

    lead_id: Mapped[int] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    scheduled_for: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    status: Mapped[FollowUpStatus] = mapped_column(
        SQLEnum(FollowUpStatus),
        default=FollowUpStatus.PENDING,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )