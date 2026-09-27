import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
import httpx
from pydantic import BaseModel
from browser_use import Agent, Browser, ChatOpenAI

from src.config import settings
from src.resume_loader import resume_loader
from src.prompts import prompt_router

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

    async def prepare_clean_tab(self, target_url: str):
        """
        Ensures Chrome starts on a clean tab loaded with the target job URL,
        closing any lingering tabs from previous jobs (e.g. past confirmation screens).
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                base = settings.CHROME_CDP_URL.rstrip("/")
                res = await client.get(f"{base}/json/list")
                if res.status_code != 200:
                    return

                targets = res.json()
                old_page_ids = [t["id"] for t in targets if t.get("type") == "page"]

                # Open fresh tab navigating directly to the new job
                new_tab_res = await client.put(f"{base}/json/new?{target_url}")
                if new_tab_res.status_code == 200:
                    new_tab_id = new_tab_res.json().get("id")
                    await client.get(f"{base}/json/activate/{new_tab_id}")

                    # Close previously open page tabs so the agent doesn't see old confirmation screens
                    for old_id in old_page_ids:
                        if old_id != new_tab_id:
                            try:
                                await client.get(f"{base}/json/close/{old_id}")
                            except Exception:
                                pass
        except Exception as e:
            print(f"[Agent] Note: Could not prepare clean tab via CDP: {e}")

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

        # 4. Formulate task instruction prompt using domain/company-matched template
        template = prompt_router.get_template(req.job_post_link, company_name=req.company_name or "")
        instructions = template.build_prompt(
            req=req,
            cv_path=cv_path,
            applicant_context=applicant_context,
            is_semi_autonomous=is_semi_autonomous
        )

        # 5. Ensure Chrome is clean and focused on a single tab with the target job URL
        await self.prepare_clean_tab(req.job_post_link)

        # 6. Initialize LLM and browser-use Agent
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
            max_actions_per_step=1
        )

        try:
            print(f"[Agent] Starting application run for {req.job_post_link} (Mode: {mode}, Template: {template.name})...")
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
                    "template_used": template.name,
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
        """Delegates prompt construction to the modular prompt_router."""
        template = prompt_router.get_template(req.job_post_link, company_name=req.company_name or "")
        return template.build_prompt(
            req=req,
            cv_path=cv_path,
            applicant_context=applicant_context,
            is_semi_autonomous=is_semi_autonomous
        )

job_agent = JobApplicationAgent()
