import uvicorn
from fastapi import FastAPI, HTTPException
import httpx
from src.config import settings
from src.agent import JobApplicationRequest, JobApplicationResult, job_agent
from src.resume_loader import resume_loader

app = FastAPI(
    title="Job Terminator API",
    description="Autonomous Job Application Agent powered by browser-use, CDP & Strapi V5",
    version="1.0.0"
)

@app.get("/health")
async def health():
    """Checks service health and tests CDP connection to Chrome."""
    cdp_alive = False
    cdp_details = {}
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            res = await client.get(f"{settings.CHROME_CDP_URL.rstrip('/')}/json/version")
            if res.status_code == 200:
                cdp_alive = True
                cdp_details = res.json()
    except Exception as e:
        cdp_details = {"error": str(e)}

    return {
        "status": "online",
        "autonomy_mode": settings.AUTONOMY_MODE,
        "chrome_cdp_connected": cdp_alive,
        "chrome_info": cdp_details,
        "strapi_configured": bool(settings.STRAPI_API_URL)
    }

@app.get("/profile")
async def get_profile():
    """Fetches and displays the applicant profile as parsed from Strapi V5."""
    profile_text = await resume_loader.get_applicant_profile_text()
    return {
        "profile_markdown": profile_text
    }

@app.post("/apply", response_model=JobApplicationResult)
async def apply_to_job(req: JobApplicationRequest):
    """
    Triggers the browser-use agent to navigate to the job link,
    fill application form fields, upload resume PDF, and either stop for review or submit.
    """
    if not req.job_post_link:
        raise HTTPException(status_code=400, detail="job_post_link is required.")

    result = await job_agent.apply_to_job(req)
    return result

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
