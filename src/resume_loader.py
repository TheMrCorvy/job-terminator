import os
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
import httpx
from src.config import settings

class ResumeLoader:
    def __init__(self):
        self._cached_resume_json: Optional[Dict[str, Any]] = None

    async def get_applicant_profile_text(self) -> str:
        """
        Fetches the updated resume JSON from Strapi and converts it
        into a clear, structured Markdown context block for the LLM agent.
        """
        data = await self.fetch_resume_json()
        if not data:
            return "No applicant profile available from Strapi. Fallback to general details."

        attributes = data.get("data", {}).get("attributes", data.get("data", {}))
        
        name = attributes.get("name", "Gonzalo Corvalan")
        title = attributes.get("title", "Software Engineer")
        email = attributes.get("email", "")
        website = attributes.get("website", "https://www.corvalangonzalo.com")
        github = attributes.get("github_profile_link", "")
        background = attributes.get("background_rich_text", "")
        
        experience_items = attributes.get("experience_list_items", [])
        education_items = attributes.get("education_list_items", [])

        lines = [
            "### APPLICANT PROFILE SUMMARY",
            f"- **Full Name:** {name}",
            f"- **Job Title:** {title}",
            f"- **Email:** {email}",
            f"- **Portfolio Website:** {website}",
            f"- **GitHub:** {github}",
            "",
            "### WORK EXPERIENCE:"
        ]
        
        for exp in experience_items:
            comp = exp.get("company", exp.get("company_name", ""))
            role = exp.get("role", exp.get("position", ""))
            period = exp.get("period", exp.get("dates", ""))
            desc = exp.get("description", "")
            lines.append(f"- **{role}** at **{comp}** ({period})\n  {desc}")

        lines.append("\n### EDUCATION:")
        for edu in education_items:
            inst = edu.get("institution", edu.get("school", ""))
            degree = edu.get("degree", "")
            period = edu.get("period", edu.get("dates", ""))
            lines.append(f"- **{degree}** - {inst} ({period})")

        if background:
            lines.append(f"\n### SUMMARY / BACKGROUND:\n{background}")

        return "\n".join(lines)

    async def fetch_resume_json(self) -> Optional[Dict[str, Any]]:
        """Fetches the raw JSON from Strapi updated-resume endpoint."""
        headers = {}
        if settings.STRAPI_API_TOKEN:
            headers["Authorization"] = f"Bearer {settings.STRAPI_API_TOKEN}"

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(settings.DEFAULT_RESUME_JSON_ENDPOINT, headers=headers)
                if res.status_code == 200:
                    self._cached_resume_json = res.json()
                    return self._cached_resume_json
                else:
                    print(f"[ResumeLoader] Warning: Received status {res.status_code} from Strapi: {res.text}")
        except Exception as e:
            print(f"[ResumeLoader] Error fetching resume JSON: {e}")

        return self._cached_resume_json

    async def get_resume_pdf_path(self, custom_cv_url: Optional[str] = None, job_id: Optional[str] = None) -> Path:
        """
        Downloads either the job-specific custom CV or the default resume PDF to a local file
        and returns its absolute Path for Playwright / browser-use file upload.
        """
        target_url = custom_cv_url or settings.DEFAULT_RESUME_PDF_URL
        
        # Resolve relative URLs from Strapi
        if target_url.startswith("/"):
            target_url = f"{settings.STRAPI_API_URL.rstrip('/')}{target_url}"

        # Generate unique local filename
        url_hash = hashlib.md5(target_url.encode("utf-8")).hexdigest()[:8]
        prefix = f"job_{job_id}_" if job_id else "default_"
        filename = f"{prefix}cv_{url_hash}.pdf"
        local_path = settings.TEMP_DIR / filename

        # Return cached if already downloaded
        if local_path.exists() and local_path.stat().st_size > 0:
            return local_path.resolve()

        print(f"[ResumeLoader] Downloading CV from {target_url} -> {local_path}...")
        headers = {}
        if settings.STRAPI_API_TOKEN and settings.STRAPI_API_URL in target_url:
            headers["Authorization"] = f"Bearer {settings.STRAPI_API_TOKEN}"

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            res = await client.get(target_url, headers=headers)
            res.raise_for_status()
            with open(local_path, "wb") as f:
                f.write(res.content)

        return local_path.resolve()

    async def fetch_latest_job(self) -> Optional[Dict[str, Any]]:
        """Fetches the most recent job posting from Strapi V5 j-job-radars."""
        url = f"{settings.STRAPI_API_URL.rstrip('/')}/api/j-job-radars?sort[0]=createdAt:desc&pagination[limit]=1&populate=*"
        headers = {}
        if settings.STRAPI_API_TOKEN:
            headers["Authorization"] = f"Bearer {settings.STRAPI_API_TOKEN}"

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    data = res.json().get("data", [])
                    if data:
                        item = data[0]
                        attrs = item.get("attributes", item)
                        custom_cv = attrs.get("custom_cv") or {}
                        cv_url = None
                        if isinstance(custom_cv, dict):
                            cv_url = custom_cv.get("url") or (
                                custom_cv.get("data", {}).get("attributes", {}).get("url")
                                if isinstance(custom_cv.get("data"), dict) else None
                            )
                        return {
                            "job_id": str(item.get("id") or item.get("documentId")),
                            "job_title": attrs.get("job_title"),
                            "company_name": attrs.get("company_name"),
                            "job_post_link": attrs.get("job_post_link"),
                            "cover_letter": attrs.get("cover_letter"),
                            "custom_cv_url": cv_url,
                            "platform": attrs.get("platform")
                        }
                    else:
                        print("[ResumeLoader] No job entries found in Strapi j-job-radars.")
                else:
                    print(f"[ResumeLoader] Received status {res.status_code} from Strapi: {res.text}")
        except Exception as e:
            print(f"[ResumeLoader] Error fetching latest job: {e}")

        return None

resume_loader = ResumeLoader()

