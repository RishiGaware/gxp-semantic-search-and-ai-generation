from fastapi import APIRouter
from app.domains.eams.ai.router import router as eams_ai_router

router = APIRouter()

router.include_router(
    eams_ai_router,
    prefix="/ai",
    tags=["eams_ai"]
)
