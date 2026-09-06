from pathlib import Path
from typing import Any
from src.prompts.base import BasePromptTemplate

class GenericAtsPromptTemplate(BasePromptTemplate):
    """Fallback prompt template for standard corporate ATS portals (Greenhouse, Lever, Workday, etc.)."""

    @property
    def name(self) -> str:
        return "GenericAtsPromptTemplate"

    def matches(self, domain: str) -> bool:
        # Fallback template matches anything
        return True

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
            f"### [RESUME / CV FILE TO UPLOAD]:\n"
            f"- Absolute path: {str(cv_path.resolve())}\n"
            "Whenever there is an 'Upload Resume' / 'CV' file input element, upload this file.\n\n",
            "### [APPLICATION STEP-BY-STEP]:\n"
            "1. Navigate to the job URL.\n"
            "2. Click the application button (e.g., 'Apply', 'Apply for this job', 'Submit Application').\n"
            "3. Accurately fill in contact details, work history, links, and education matching the applicant profile above.\n"
            "4. Upload the provided resume PDF to the file attachment field.\n"
            "5. To advance between steps, click forward buttons like 'Next', 'Continue', or 'Review'."
        ]

        if req.cover_letter:
            prompt_parts.append(self._build_cover_letter_section(req.cover_letter))

        if is_semi_autonomous:
            prompt_parts.append(
                "\n### [SEMI-AUTONOMOUS REVIEW INSTRUCTIONS]:\n"
                "- Fill out every field on every step.\n"
                "- Proceed until you reach the final review or confirmation screen.\n"
                "- DO NOT click the final 'Submit' or 'Finish' button.\n"
                "- Stop on the final screen so the applicant can visually review the inputs and click submit manually.\n"
                "- Finish your task stating that the application is filled and waiting for manual submission."
            )
        else:
            prompt_parts.append(
                "\n### [AUTONOMOUS SUBMISSION INSTRUCTIONS]:\n"
                "- Review all fields and click the final 'Submit' / 'Submit Application' button to complete the process.\n"
                "- Verify that the confirmation screen appears."
            )

        prompt_parts.append(self._build_target_validation(req))
        prompt_parts.append(self._build_captcha_rule())

        return "\n".join(prompt_parts)
