from pathlib import Path
from typing import Any
from src.prompts.base import BasePromptTemplate

class EpamPromptTemplate(BasePromptTemplate):
    """Specialized prompt template for EPAM Careers (epam.com, careers.epam.com)."""

    @property
    def name(self) -> str:
        return "EpamPromptTemplate"

    def matches(self, domain: str) -> bool:
        domain_lower = domain.lower()
        return "epam.com" in domain_lower or "epam" in domain_lower

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
            f"### [RESUME / CV FILE TO UPLOAD - MANDATORY FOR EPAM]:\n"
            f"- Absolute path: {str(cv_path.resolve())}\n"
            "EPAM requires uploading a CV file. When prompted or when a file upload area appears, upload this PDF.\n\n",
            "### [EPAM CAREERS APPLICATION STEP-BY-STEP]:\n"
            "1. Navigate to the EPAM job posting page.\n"
            "2. Locate and click the primary application button (e.g., 'Apply', 'Apply now', 'Apply for this job').\n"
            "3. If a modal or form appears:\n"
            "   - Upload the provided resume PDF to the 'Resume / CV' file input or upload zone.\n"
            "   - Fill in First Name, Last Name, Email, and Phone matching the applicant profile.\n"
            "   - Fill in Location / Country (select 'Argentina') and City if requested.\n"
            "   - Provide LinkedIn URL, GitHub, or Portfolio website where relevant.\n"
            "4. Language / English Proficiency Question:\n"
            "   - If EPAM asks for English level / proficiency, select 'C1 - Advanced', 'Fluent', or 'Proficient'.\n"
            "5. Mandatory Privacy & Data Consent Checkboxes:\n"
            "   - EPAM requires checking mandatory consent checkboxes (e.g., 'I agree to the processing of my personal data...', 'I accept the Candidate Privacy Policy').\n"
            "   - Check all mandatory consent checkboxes required to enable the submit button."
        ]

        if req.cover_letter:
            prompt_parts.append(self._build_cover_letter_section(req.cover_letter))

        if is_semi_autonomous:
            prompt_parts.append(
                "\n### [SEMI-AUTONOMOUS REVIEW INSTRUCTIONS]:\n"
                "- Fill all required form fields, upload the resume PDF, and check the mandatory consent boxes.\n"
                "- Stop right before clicking the final 'Submit' / 'Submit application' button.\n"
                "- Leave the completed form open on screen for human review.\n"
                "- Finish your task stating that the EPAM application is filled and ready for review."
            )
        else:
            prompt_parts.append(
                "\n### [AUTONOMOUS SUBMISSION INSTRUCTIONS]:\n"
                "- Fill all required form fields, upload the resume PDF, and check the mandatory consent boxes.\n"
                "- Click the final submission button (e.g., 'Submit', 'Submit application', 'Apply').\n"
                "- Verify that the success / 'Application received' confirmation screen is displayed."
            )

        prompt_parts.append(self._build_target_validation(req))
        prompt_parts.append(self._build_captcha_rule())

        return "\n".join(prompt_parts)
