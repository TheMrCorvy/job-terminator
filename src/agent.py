import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel
from browser_use import Agent, Browser, ChatOpenAI

from src.config import settings
from src.resume_loader import resume_loader

class JobApplicationRequest(BaseModel):
    job_id: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    job_post_link: str
    custom_cv_url: Optional[str] = None
    cover_letter: Optional[str] = None
    autonomy_mode: Optional[str] = None

class JobApplicationResult(BaseModel):
    success: bool
    status: str  # "ready_for_review", "submitted", "captcha_detected", "failed"
    message: str
    details: Dict[str, Any] = {}

class JobApplicationAgent:
    def __init__(self):
        self.browser: Optional[Browser] = None

    def get_browser(self) -> Browser:
        # Re-use or connect to the existing Chrome instance over CDP
        return Browser(cdp_url=settings.CHROME_CDP_URL)

    async def apply_to_job(self, req: JobApplicationRequest) -> JobApplicationResult:
        if not settings.OPENAI_API_KEY:
            return JobApplicationResult(
                success=False,
                status="failed",
                message="OPENAI_API_KEY is not configured in .env"
            )

        # 1. Download/resolve resume PDF
        try:
            cv_path: Path = await resume_loader.get_resume_pdf_path(
                custom_cv_url=req.custom_cv_url,
                job_id=req.job_id
            )
        except Exception as e:
            return JobApplicationResult(
                success=False,
                status="failed",
                message=f"Failed to fetch resume PDF: {str(e)}"
            )

        # 2. Get applicant profile JSON context
        applicant_context = await resume_loader.get_applicant_profile_text()

        # 3. Determine autonomy mode
        mode = req.autonomy_mode or settings.AUTONOMY_MODE
        is_semi_autonomous = (mode == "semi-autonomous")

        # 4. Formulate task instruction prompt
        instructions = self._build_prompt(req, cv_path, applicant_context, is_semi_autonomous)

        # 5. Initialize LLM and browser-use Agent
        llm = ChatOpenAI(
            model="gpt-4o",
            api_key=settings.OPENAI_API_KEY,
            temperature=0.1
        )

        browser = self.get_browser()

        agent = Agent(
            task=instructions,
            llm=llm,
            browser=browser,
            available_file_paths=[str(cv_path.resolve())],
            max_actions_per_step=3
        )

        try:
            print(f"[Agent] Starting application run for {req.job_post_link} (Mode: {mode})...")
            history = await agent.run()

            # Parse completion status from agent history
            last_action_text = ""
            if history and hasattr(history, "final_result"):
                last_action_text = str(history.final_result())

            final_status = "ready_for_review" if is_semi_autonomous else "submitted"
            
            # Check if captcha was reported
            if "captcha" in last_action_text.lower() or "cloudflare" in last_action_text.lower():
                final_status = "captcha_detected"

            return JobApplicationResult(
                success=True,
                status=final_status,
                message=last_action_text or "Application process completed.",
                details={
                    "job_id": req.job_id,
                    "job_post_link": req.job_post_link,
                    "autonomy_mode": mode,
                    "cv_file_used": str(cv_path)
                }
            )
        except Exception as e:
            print(f"[Agent] Error during application run: {e}")
            return JobApplicationResult(
                success=False,
                status="failed",
                message=f"Agent execution error: {str(e)}",
                details={"job_id": req.job_id}
            )

    def _build_prompt(
        self,
        req: JobApplicationRequest,
        cv_path: Path,
        applicant_context: str,
        is_semi_autonomous: bool
    ) -> str:
        prompt_parts = [
            f"You are an automated job application agent. Your goal is to apply for the following job posting:\n"
            f"- Job URL: {req.job_post_link}",
            f"- Job Title: {req.job_title or 'N/A'}",
            f"- Company: {req.company_name or 'N/A'}\n",
            "### APPLICANT INFORMATION:",
            applicant_context,
            f"\n### RESUME / CV FILE TO UPLOAD:",
            f"- Absolute path: {str(cv_path.resolve())}",
            "Whenever there is an 'Upload Resume' / 'CV' file input element, upload this file.\n"
        ]

        if req.cover_letter:
            prompt_parts.append(
                f"### COVER LETTER TO USE:\n{req.cover_letter}\n"
                "If there is a Cover Letter text area or upload field, provide or paste this content.\n"
            )

        prompt_parts.append("### STEP-BY-STEP INSTRUCTIONS:")
        prompt_parts.append("1. Navigate to the job URL.")
        prompt_parts.append("2. If the page presents an 'Apply', 'Easy Apply', or application form button, click it.")
        prompt_parts.append("3. Accurately fill in the contact details, work history, links, and education matching the applicant profile above.")
        prompt_parts.append("4. Upload the provided resume PDF to the file attachment field.")
        
        if is_semi_autonomous:
            prompt_parts.append(
                "\n### 🛑 CRITICAL HUMAN-IN-THE-LOOP RULE:\n"
                "- Fill out every field on every step.\n"
                "- Proceed until you reach the final review or confirmation screen.\n"
                "- DO NOT CLICK THE FINAL 'Submit', 'Submit Application', or 'Finish' BUTTON.\n"
                "- Stop on the final screen so the applicant can visually review the inputs and click submit manually.\n"
                "- Finish the task with a summary of the fields filled and note that it is waiting for manual submission."
            )
        else:
            prompt_parts.append(
                "\n### AUTONOMOUS SUBMISSION RULE:\n"
                "- Review all fields and click the final 'Submit Application' button to complete the process."
            )

        prompt_parts.append(
            "\n### SECURITY & CAPTCHA RULE:\n"
            "- If a CAPTCHA, Cloudflare challenge, or 2FA verification appears, DO NOT try to bypass it. "
            "Stop immediately and state clearly that a CAPTCHA was encountered."
        )

        return "\n".join(prompt_parts)

job_agent = JobApplicationAgent()
