from fastapi import FastAPI

from app.database import engine, Base
from app import models
from app.routes import router as lead_router

from app.dashboard import router as dashboard_router

Base.metadata.create_all(bind=engine)

#frontend start import
from pathlib import Path
from fastapi.staticfiles import StaticFiles
#frontend end import

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
app.include_router(dashboard_router)


#frontend start

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app.mount(
    "/",
    StaticFiles(directory=FRONTEND_DIR, html=True),
    name="frontend"
)

#frontend end