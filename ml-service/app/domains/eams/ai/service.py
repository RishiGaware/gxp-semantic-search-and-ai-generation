from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.domains.eams.ai.prompts import SYSTEM_PROMPT, build_eams_refinement_prompt
from app.domains.ai_enhancement.services.engine import call_ai_engine, enforce_word_count
from app.domains.common.service import robust_text_extraction

class EAMSAIRefineRequest(BaseModel):
    """EAMS-specific refinement request."""
    fieldType: str = Field(..., description="The name of the field to refine")
    value: str = Field(default="", description="Existing field content or keywords")
    prompt: str = Field(..., min_length=1, description="User intent or instruction for refinement")
    observationText: Optional[str] = None
    referenceClause: Optional[str] = None

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Prompt cannot be empty or whitespace only.")
        return normalized

def refine_eams_content(payload: EAMSAIRefineRequest) -> str:
    """
    EAMS-specific refinement logic.
    """
    processed_value = payload.value
    # Apply text extraction for description field if it contains HTML/RTF
    if payload.fieldType == "observationDescription":
        processed_value = robust_text_extraction(payload.value)

    full_user_prompt = build_eams_refinement_prompt(
        field_type=payload.fieldType,
        user_input=processed_value,
        user_prompt=payload.prompt,
        observation_text=payload.observationText,
        reference_clause=payload.referenceClause,
    )

    generated_text = call_ai_engine(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=full_user_prompt
    )

    return enforce_word_count(generated_text, payload.prompt)
