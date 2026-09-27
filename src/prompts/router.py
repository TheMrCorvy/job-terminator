from urllib.parse import urlparse
from typing import List
from src.prompts.base import BasePromptTemplate
from src.prompts.indeed import IndeedPromptTemplate
from src.prompts.epam import EpamPromptTemplate
from src.prompts.linkedin import LinkedInPromptTemplate
from src.prompts.generic import GenericAtsPromptTemplate

class PromptRouter:
    """Selects the appropriate prompt template based on the target job URL domain."""

    def __init__(self):
        # Specific platform templates registered first; Generic fallback registered last
        self.templates: List[BasePromptTemplate] = [
            IndeedPromptTemplate(),
            EpamPromptTemplate(),
            LinkedInPromptTemplate(),
            GenericAtsPromptTemplate(),  # Fallback
        ]

    def extract_domain(self, url: str) -> str:
        """Extracts the network domain from a given URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path.split("/")[0]
            # Strip port if present
            return domain.split(":")[0].lower()
        except Exception:
            return ""

    def get_template(self, url: str, company_name: str = "") -> BasePromptTemplate:
        """Finds and returns the best matching prompt template for the given URL and company."""
        domain = self.extract_domain(url)
        company_lower = (company_name or "").lower()

        # If the target employer is EPAM (even if accessed via Indeed or another aggregator), use EpamPromptTemplate
        if "epam" in company_lower or "epam" in domain:
            print(f"[PromptRouter] Target company '{company_name}' / domain '{domain}' -> Using EpamPromptTemplate")
            return EpamPromptTemplate()
        
        for template in self.templates:
            if template.matches(domain):
                print(f"[PromptRouter] Matched domain '{domain}' -> Using template: {template.name}")
                return template

        # Safe fallback
        fallback = GenericAtsPromptTemplate()
        print(f"[PromptRouter] No specific match for '{domain}' -> Using fallback: {fallback.name}")
        return fallback

prompt_router = PromptRouter()
