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
        return f"""You are an automated job application agent applying on behalf of Gonzalo Salvador Corvalán.
Target Job URL: {req.job_post_link}
Job Title: {req.job_title or 'Fullstack Engineer'}
Company: EPAM Systems

### APPLICANT DATA:
- First Name: gonzalo salvador
- Last Name: corvalán
- Email: gonzalosalvadorcorvalan@gmail.com
- Mobile Phone Number: 9 223 4567890 (the +54 flag is already selected; do NOT type +54)
- Current City: Mar del Plata
- Preferred Work Countries: Argentina
- Primary Skill: Node.js
- Years of Experience: 7
- English Level: Proficient (C2)
- LinkedIn Profile URL: https://www.linkedin.com/in/gonzalo-salvador-corvalan

### [MANDATORY EXECUTION SEQUENCE - FOLLOW THESE EXACT STEPS IN ORDER]:
0. If you start on Indeed, click the button 'Postularse en la página de la empresa' (or 'Apply on company site') to navigate to the EPAM job page in a new tab, and switch to that tab.
1. If you are on EPAM make sure to click "APPLY" button (id 'cta_job_apply_unauthorized'). A modal form will open and it will contain inputs that you need to fill in order to succeed in your task.
2. First fill my first name in the "Name *" input (id 'name'): type "gonzalo salvador".
3. Then fill my last name in "* Surname" input (id 'surname'): type "corvalán".
4. Then fill my email in "* Email" input (id 'email'): type "gonzalosalvadorcorvalan@gmail.com".
5. Then fill my phone number in "* Mobile phone number" input (id 'phone'): type "9 223 4567890".
6. Then fill "Current city" input (id 'react-select-5-input') with "Mar del Plata" and select it from the dropdown option.
7. Then fill "Argentina" in "* Preferred work countries" input (id 'react-select-6-input') and select "Argentina" from the dropdown option. Then click outside the dropdown to close the dropdown menu.
8. Then fill "Node.js" in "* Primary skill" input (id 'react-select-7-input') and select "Node.js" from the dropdown option.
9. Then scroll all the way down inside the modal so the remaining fields are in view.
10. Then fill "7" in "Years of experience" input (id 'relevantExperience').
11. Then fill "Proficient (C2)" in "English level" input (id 'react-select-8-input') and select it from the dropdown options.
12. Then click on the radio input for "LinkedIn profile" (data-testid 'LinkedIn' or id 'radio-experience-1') inside "* Experience" input, this will create one new text input with the text "https://linkedin.com/in/", make that text into "https://www.linkedin.com/in/gonzalo-salvador-corvalan" (in input id 'linkedin').
13. Then check the "* He leído y acepto el contenido del Aviso de Privacidad del Aspirante a EPAM." checkmark input (id 'apply-isLATAMPrivacyConsentAccepted-field'). If clicking the checkbox element does not toggle it to checked, run:
    evaluate: code: "(function(){{ const cb = document.querySelector('#apply-isLATAMPrivacyConsentAccepted-field input'); if (cb && !cb.checked) cb.click(); return cb ? cb.checked : false; }})()"
    Make sure that this checkbox is marked as checked!
14. Then click on "Submit" button (id 'apply-button').
15. Verify that the application confirmation message appears, then call done.

CRITICAL: Follow steps 1 through 14 IN ORDER. DO NOT skip to step 14 before completing steps 1 through 13!
"""
