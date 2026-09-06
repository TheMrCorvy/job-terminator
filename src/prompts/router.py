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

    def get_template(self, url: str) -> BasePromptTemplate:
        """Finds and returns the best matching prompt template for the given URL."""
        domain = self.extract_domain(url)
        
        for template in self.templates:
            if template.matches(domain):
                print(f"[PromptRouter] Matched domain '{domain}' -> Using template: {template.name}")
                return template

        # Safe fallback
        fallback = GenericAtsPromptTemplate()
        print(f"[PromptRouter] No specific match for '{domain}' -> Using fallback: {fallback.name}")
        return fallback

prompt_router = PromptRouter()
