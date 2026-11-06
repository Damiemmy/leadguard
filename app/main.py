from fastapi import FastAPI

from app.database import engine, Base
from app import models
from app.routes import router as lead_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LeadGuard API",
    description="Lead recovery and customer follow-up automation",
    version="1.0.0"
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "LeadGuard"
    }


app.include_router(lead_router)