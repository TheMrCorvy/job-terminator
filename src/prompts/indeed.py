from pathlib import Path
from typing import Any
from src.prompts.base import BasePromptTemplate

class IndeedPromptTemplate(BasePromptTemplate):
    """Specialized prompt template for Indeed (indeed.com, ar.indeed.com, etc.)."""

    @property
    def name(self) -> str:
        return "IndeedPromptTemplate"

    def matches(self, domain: str) -> bool:
        domain_lower = domain.lower()
        return "indeed.com" in domain_lower or "indeed" in domain_lower

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
            "### [INDEED APPLICATION TYPES - CRITICAL]:\n"
            "There are two types of jobs on Indeed:\n"
            "A) DIRECT INDEED APPLY ('Postularse', 'Postularme ahora', 'Apply now'):\n"
            "   - The entire process happens within Indeed.\n"
            "   - ALWAYS look for and select the radio option 'Usa tu CV de Indeed' (DO NOT upload PDF).\n"
            "   - Advance through the steps using 'Continuar' / 'Siguiente'.\n"
            "B) EXTERNAL COMPANY SITE ('Postularse en la página de la empresa' / 'Apply on company site'):\n"
            "   - Clicking this opens the employer's external website in a new tab (e.g. EPAM Careers, Greenhouse, Lever).\n"
            "   - Switch to the external tab immediately.\n"
            "   - CRITICAL: DO NOT look for 'Usa tu CV de Indeed' or Indeed-specific buttons on the external company site!\n"
            "   - Fill the application form on the company's site using the APPLICANT PROFILE SUMMARY.\n"
            "   - If the company is EPAM (epam.com): click 'apply' to open modal, fill contact info, current city ('Mar del Plata'), select 'Node.js' as primary skill, click 'LinkedIn profile' radio (never CV) and type handle 'gonzalo-salvador-corvalan', check the Privacy Notice checkbox, and locate the 'Submit' button.\n"
        ]

        if req.cover_letter:
            prompt_parts.append(self._build_cover_letter_section(req.cover_letter))

        prompt_parts.append(
            "### [INDEED APPLICATION NAVIGATION]:\n"
            "1. Navigate to the job URL.\n"
            "2. Click the initial application button (e.g. 'Postularse', 'Postularme', 'Postularse en la página de la empresa', 'Apply now').\n"
            "3. If an external tab opens, switch to it and complete the company form.\n"
            "4. Answer contact details, questions, years of experience, and links matching the applicant profile above.\n"
            "5. To advance between steps on Indeed, click forward buttons like 'Continuar', 'Siguiente', 'Next', 'Continue', or 'Revisar tu postulación' / 'Review'."
        )

        prompt_parts.append(
            "\n### [STRICT FORBIDDEN ACTIONS - NEVER CLICK THESE]:\n"
            "- DO NOT CLICK 'Guardar y cerrar' (Save and close).\n"
            "- DO NOT CLICK 'Guardar y salir' (Save and exit).\n"
            "- DO NOT CLICK 'Guardar para más tarde' (Save for later).\n"
            "- DO NOT CLICK 'Cancelar' or the 'X' modal close button.\n"
            "- REASON: Clicking 'Guardar y cerrar' aborts the application flow, returns to the job posting URL, and DOES NOT submit the application! It is strictly prohibited."
        )

        prompt_parts.append(
            "\n### [SCROLLING & SUBMIT BUTTON VERIFICATION]:\n"
            "- On Indeed's final review screen (100% progress), the real submit button ('Enviá tu postulación' or 'Enviar postulación') is located at the VERY BOTTOM of the page/modal, beneath the application summary.\n"
            "- At the top of the modal, Indeed displays a 'Guardar y cerrar' button. DO NOT CLICK IT!\n"
            "- If 'Enviá tu postulación' is not in your visible interactive elements, YOU MUST CALL 'scroll_down' (scroll down 1-2 times) to reach the bottom of the page.\n"
            "- BEFORE CLICKING ANY SUBMIT BUTTON, VERIFY ITS TEXT:\n"
            "  * The button must explicitly say 'Enviá tu postulación', 'Enviar postulación', or 'Postularme'.\n"
            "  * If the element index corresponds to 'Guardar y cerrar' or 'Cerrar', DO NOT CLICK IT. Scroll down instead."
        )

        if is_semi_autonomous:
            prompt_parts.append(
                "\n### [SEMI-AUTONOMOUS REVIEW INSTRUCTIONS]:\n"
                "- Advance through all questions until you reach the final review / confirmation screen (100%).\n"
                "- Scroll down to verify all filled fields and bring 'Enviá tu postulación' into view.\n"
                "- DO NOT click 'Guardar y cerrar' or close the window.\n"
                "- DO NOT click the final 'Enviá tu postulación' button yet.\n"
                "- Simply STOP on that review screen with all fields filled and leave the page intact for the user to review and submit manually.\n"
                "- Finish your task stating that the application is filled and waiting on the final submit screen."
            )
        else:
            prompt_parts.append(
                "\n### [AUTONOMOUS SUBMISSION INSTRUCTIONS]:\n"
                "- Advance through all questions to the final review screen (100%).\n"
                "- SCROLL DOWN to the bottom of the page to locate the blue 'Enviá tu postulación' (or 'Enviar postulación') button.\n"
                "- Click 'Enviá tu postulación' to complete the application.\n"
                "- Verify that the success / confirmation screen appears."
            )

        prompt_parts.append(self._build_target_validation(req))
        prompt_parts.append(self._build_captcha_rule())

        return "\n".join(prompt_parts)
