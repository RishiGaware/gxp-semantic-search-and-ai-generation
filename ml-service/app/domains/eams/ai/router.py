from fastapi import APIRouter
from app.domains.eams.ai.service import refine_eams_content, EAMSAIRefineRequest

router = APIRouter()

@router.post("/refine")
def refine_content(payload: EAMSAIRefineRequest):
    """Refinement endpoint for EAMS."""
    generated_text = refine_eams_content(payload)
    return {"success": True, "generatedText": generated_text}
