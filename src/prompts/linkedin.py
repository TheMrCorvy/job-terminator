from pathlib import Path
from typing import Any
from src.prompts.base import BasePromptTemplate

class LinkedInPromptTemplate(BasePromptTemplate):
    """Specialized prompt template for LinkedIn (linkedin.com)."""

    @property
    def name(self) -> str:
        return "LinkedInPromptTemplate"

    def matches(self, domain: str) -> bool:
        return "linkedin.com" in domain.lower()

    def build_prompt(
        self,
        req: Any,
        cv_path: Path,
        applicant_context: str,
        is_semi_autonomous: bool
    ) -> str:
        prompt_parts = [
            self._build_header(req),
            self._build_applicant_section(applicant_context),
            f"### LOCAL RESUME / CV FILE (FALLBACK ONLY):\n- Absolute path: {str(cv_path.resolve())}\n\n",
            "### [LINKEDIN RESUME SELECTION RULES]:\n"
            "1. When applying on LinkedIn via Easy Apply / Solicitud sencilla, select the default existing resume already attached to the LinkedIn profile.\n"
            "2. DO NOT click 'Upload resume' / 'Cargar currículum' if a saved resume is already selected.\n\n",
            "### [LINKEDIN APPLICATION STEP-BY-STEP]:\n"
            "1. Navigate to the job URL.\n"
            "2. Click 'Easy Apply' (or 'Solicitud sencilla').\n"
            "3. Confirm contact info (phone, email) and advance with 'Next' / 'Siguiente'.\n"
            "4. Answer any screening questions based on the applicant profile.\n"
            "5. Advance to the final review screen ('Review' / 'Revisar')."
        ]

        if req.cover_letter:
            prompt_parts.append(self._build_cover_letter_section(req.cover_letter))

        if is_semi_autonomous:
            prompt_parts.append(
                "\n### [SEMI-AUTONOMOUS REVIEW INSTRUCTIONS]:\n"
                "- Advance through all steps until you reach the final review screen showing 'Submit application' / 'Enviar solicitud'.\n"
                "- DO NOT click 'Submit application' / 'Enviar solicitud'.\n"
                "- DO NOT dismiss or close the modal.\n"
                "- Stop on that review screen and finish your task stating that the application is waiting for manual submission."
            )
        else:
            prompt_parts.append(
                "\n### [AUTONOMOUS SUBMISSION INSTRUCTIONS]:\n"
                "- Advance through all steps to the final review screen.\n"
                "- Click 'Submit application' (or 'Enviar solicitud').\n"
                "- Verify that the application submitted confirmation screen is displayed."
            )

        prompt_parts.append(self._build_target_validation(req))
        prompt_parts.append(self._build_captcha_rule())

        return "\n".join(prompt_parts)
