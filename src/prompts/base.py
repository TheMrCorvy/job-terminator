from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Any

class BasePromptTemplate(ABC):
    """Abstract base class for platform-specific prompt templates."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of this prompt template."""
        pass

    @abstractmethod
    def matches(self, domain: str) -> bool:
        """Returns True if this template handles the given domain."""
        pass

    @abstractmethod
    def build_prompt(
        self,
        req: Any,
        cv_path: Path,
        applicant_context: str,
        is_semi_autonomous: bool
    ) -> str:
        """Builds the complete task instructions for browser-use."""
        pass

    def _build_header(self, req: Any) -> str:
        return (
            f"You are an automated job application agent. Your goal is to apply for the following job posting:\n"
            f"- Job URL: {req.job_post_link}\n"
            f"- Job Title: {req.job_title or 'N/A'}\n"
            f"- Company: {req.company_name or 'N/A'}\n"
        )

    def _build_applicant_section(self, applicant_context: str) -> str:
        return f"### APPLICANT INFORMATION:\n{applicant_context}\n"

    def _build_cover_letter_section(self, cover_letter: Optional[str]) -> str:
        if not cover_letter:
            return ""
        return (
            f"### COVER LETTER TO USE:\n{cover_letter}\n"
            "If there is a Cover Letter text area, message field, or upload field, provide or paste this content.\n\n"
        )

    def _build_target_validation(self, req: Any) -> str:
        return (
            f"\n### [TARGET COMPANY VALIDATION]:\n"
            f"- You are applying to: '{req.job_title or 'Job'}' at '{req.company_name or 'the company'}' ({req.job_post_link}).\n"
            f"- NEVER call 'done' based on an old or leftover confirmation page for a different company or past job!\n"
            f"- You must actively navigate to {req.job_post_link} and complete the application specifically for '{req.company_name or 'the company'}'.\n"
        )

    def _build_captcha_rule(self) -> str:
        return (
            "\n### [SECURITY & CAPTCHA RULE]:\n"
            "- If a CAPTCHA, Cloudflare challenge, or 2FA verification appears, DO NOT try to bypass it. "
            "Stop immediately and state clearly that a CAPTCHA was encountered."
        )
