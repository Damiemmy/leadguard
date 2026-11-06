from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Lead, LeadStatus
from app.schemas import LeadCreate, LeadResponse

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.post("/", response_model=LeadResponse, status_code=201)
def create_lead(
    lead_data: LeadCreate,
    db: Session = Depends(get_db)
):
    new_lead = Lead(**lead_data.model_dump())

    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)

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