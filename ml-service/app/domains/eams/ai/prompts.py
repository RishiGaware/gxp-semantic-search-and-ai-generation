from typing import Dict

SYSTEM_PROMPT = """
You are a highly specialized Pharmaceutical Quality Assurance and Regulatory Affairs expert focused on External Regulatory Audit Management Systems (EAMS).

Your role is to generate or refine content strictly related to health authority inspection observations (e.g., FDA Form 483, MHRA, EMA, WHO audits), audit responses, compliance declarations, and Corrective and Preventive Actions (CAPA) in compliance with cGMP, FDA 21 CFR Part 210/211, and EudraLex guidelines.

Your response MUST adhere to the principle of "LITERAL INTEGRITY":
- Follow GMP-compliant, audit-ready language.
- Be strictly based ONLY on the provided input content.
- NEVER assume, modify, reinterpret, or infer technical values (numbers, quantities, layers, IDs).
- CRITICAL: Technical specifications (e.g., "three layers", "04 nos", "Batch No") MUST be mirrored exactly. 
- Do NOT simplify technical data.
- Maintain 100% traceability of all facts from input.

STRICT FORMAT RULE:
- Default response is ALWAYS professional text paragraphs.
- Tables are ONLY permitted if explicitly requested in the User Requirement.
- If the user specifies structure (e.g., "5 paragraphs", "2 tables"), it MUST be followed EXACTLY.

OUTPUT RULES:
- No explanations, no extra commentary.
- Return ONLY the final formatted content.
- Ensure response is suitable for regulatory audit review.
""".strip()

FIELD_INSTRUCTIONS: Dict[str, str] = {
    "observationDescription": (
        "Generate a precise technical audit observation from health authorities.\n\n"
        "DEFAULT FORMAT (FALLBACK): Professional text paragraphs.\n\n"
        "CRITICAL DATA INTEGRITY (LITERAL MIRRORING):\n"
        "- Highlight the regulatory standard breached (if mentioned) and document the observed gap without emotional language.\n"
        "- Preserve ALL input data exactly (numbers, IDs, references, counts).\n"
    ),
    "observationResponse": (
        "Draft a professional, data-backed audit response.\n\n"
        "DEFAULT FORMAT (FALLBACK): Professional text paragraphs.\n\n"
        "CRITICAL DATA INTEGRITY (LITERAL MIRRORING):\n"
        "- State the immediate correction, the summary of root cause analysis, and the commitment to prevent recurrence.\n"
        "- Preserve ALL IDs, serial numbers, and technical references exactly.\n"
    ),
}

FEW_SHOT_EXAMPLES: Dict[str, str] = {
    "observationDescription": """
Example:
Input Content:
incubator 10 temperature was 38C instead of 37C for 5 hours
 
Output:
During the facility audit, the temperature inside Incubator 10 was observed at 38°C, which exceeds the validated operating specification of 37°C for a continuous duration of approximately 5 hours.
""".strip(),
    "observationResponse": """
Example:
Input Content:
recalibrated incubator 10 and checked old batch data
 
Output:
Immediate corrective action was taken to recalibrate Incubator 10. A retrospective review of historical batch records processed in the unit was performed, confirming no adverse impact on product quality.
""".strip(),
}

def build_eams_refinement_prompt(field_type: str, user_input: str, user_prompt: str, observation_text: str = None, reference_clause: str = None) -> str:
    field_instruction = FIELD_INSTRUCTIONS.get(field_type, "Refine the content to be highly professional, GMP-compliant, and audit-ready.")
    few_shot_example = FEW_SHOT_EXAMPLES.get(field_type, "")
    normalized_user_prompt = (user_prompt or "").strip()

    # Detect structure requirements
    structure_hint = ""
    table_requested = "table" in normalized_user_prompt.lower()
    para_requested = "paragraph" in normalized_user_prompt.lower()

    if table_requested:
        structure_hint += "- Include a Markdown table as requested.\n"
    if para_requested:
        structure_hint += "- Follow the requested paragraph count.\n"

    context_info = ""
    if field_type == "observationResponse" and observation_text:
        context_info = f"\nAssociated Observation Details:\n{observation_text.strip()}\n"
    elif field_type == "observationDescription" and reference_clause:
        context_info = f"\nAssociated Reference Clause Details:\n{reference_clause.strip()}\n"

    return f"""
Task:
{field_instruction}

User Requirement:
{normalized_user_prompt if normalized_user_prompt else "Refine the content as professional text paragraphs."}
{context_info}
Input Content:
{user_input}

Rules:
- THE USER REQUIREMENT IS THE ABSOLUTE HIGHEST PRIORITY.
- Return ONLY the relevant text content.
- Preserve all numbers, IDs, and technical details exactly.
{structure_hint}

Reference Example:
{few_shot_example}
""".strip()
