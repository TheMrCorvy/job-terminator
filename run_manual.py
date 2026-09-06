#!/usr/bin/env python3
"""
Job Terminator - Manual Trigger & Testing CLI

Usage examples:
  # 1. Test Chrome CDP connectivity
  python run_manual.py --test-browser

  # 2. Test Strapi connection and display profile + latest job
  python run_manual.py --test-strapi

  # 3. Apply to the most recent job saved in Strapi
  python run_manual.py --latest-strapi

  # 4. Apply to a specific custom job URL directly
  python run_manual.py --url "https://jobs.example.com/apply/123" --title "Frontend Engineer"
"""

import sys
import asyncio
import argparse
from pathlib import Path

# Force UTF-8 encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure root directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from src.config import settings
from src.agent import JobApplicationRequest, job_agent
from src.resume_loader import resume_loader
from browser_use import Browser, Agent, ChatOpenAI

async def run_test_browser():
    print("\n========================================================")
    print(" 🧪 Testing Chrome CDP Connection & Browser-Use Control")
    print(f" Target CDP URL: {settings.CHROME_CDP_URL}")
    print("========================================================\n")
    
    try:
        browser = Browser(cdp_url=settings.CHROME_CDP_URL)
        llm = ChatOpenAI(model="gpt-4o", api_key=settings.OPENAI_API_KEY)
        
        test_task = (
            "Open a new tab, navigate to 'https://www.google.com', "
            "verify the page has loaded, and return the page title."
        )
        print("[Test] Launching test agent...")
        agent = Agent(task=test_task, llm=llm, browser=browser)
        history = await agent.run()
        print("\n✅ SUCCESS: Chrome CDP controlled successfully by browser-use!")
        if history and hasattr(history, "final_result"):
            print(f"Result: {history.final_result()}")
    except Exception as e:
        print(f"\n❌ FAILED to control Chrome: {e}")
        print("\nPlease ensure Chrome is running with CDP enabled:")
        print("Run: .\\scripts\\launch-chrome.ps1")

async def run_test_strapi():
    print("\n========================================================")
    print(" 🔍 Testing Strapi V5 API Connection")
    print(f" Strapi URL: {settings.STRAPI_API_URL}")
    print(f" Resume JSON: {settings.DEFAULT_RESUME_JSON_ENDPOINT}")
    print("========================================================\n")

    print("[1] Fetching Candidate Profile...")
    profile_text = await resume_loader.get_applicant_profile_text()
    print("---------------- Candidate Profile ----------------")
    print(profile_text[:600] + ("..." if len(profile_text) > 600 else ""))
    print("---------------------------------------------------\n")

    print("[2] Fetching Latest Job from 'j-job-radars'...")
    latest = await resume_loader.fetch_latest_job()
    if latest:
        print("✅ Found Latest Job:")
        print(f" - ID: {latest.get('job_id')}")
        print(f" - Title: {latest.get('job_title')}")
        print(f" - Company: {latest.get('company_name')}")
        print(f" - Link: {latest.get('job_post_link')}")
        print(f" - Custom CV: {latest.get('custom_cv_url') or 'None (will use default resume)'}")
        print(f" - Cover Letter: {'Provided' if latest.get('cover_letter') else 'None'}")
    else:
        print("⚠️ Could not fetch jobs from j-job-radars or list is empty.")

async def run_apply(args):
    print("\n========================================================")
    print(" 🎯 Job Terminator - Manual Application Trigger")
    print("========================================================\n")

    req = None

    if args.latest_strapi:
        print("[1] Querying Strapi for the latest job in j-job-radars...")
        latest = await resume_loader.fetch_latest_job()
        if not latest or not latest.get("job_post_link"):
            print("❌ No valid job found in Strapi to apply to.")
            return

        print(f"Applying to: {latest.get('job_title')} at {latest.get('company_name')}")
        print(f"Link: {latest.get('job_post_link')}\n")

        req = JobApplicationRequest(
            job_id=latest.get("job_id"),
            job_title=latest.get("job_title"),
            company_name=latest.get("company_name"),
            job_post_link=latest.get("job_post_link"),
            custom_cv_url=latest.get("custom_cv_url"),
            cover_letter=latest.get("cover_letter"),
            autonomy_mode=args.mode
        )
    elif args.url:
        req = JobApplicationRequest(
            job_post_link=args.url,
            job_title=args.title,
            company_name=args.company,
            cover_letter=args.cover_letter,
            autonomy_mode=args.mode
        )
    else:
        print("Please specify either --url <link> or --latest-strapi.")
        print("Run with --help to view all available options.")
        return

    print(f"Autonomy Mode: {req.autonomy_mode or settings.AUTONOMY_MODE}")
    print("Starting agent execution...\n")

    result = await job_agent.apply_to_job(req)

    print("\n========================================================")
    print(f" Execution Outcome: {'✅ SUCCESS' if result.success else '❌ FAILED'}")
    print(f" Status: {result.status}")
    print(f" Message: {result.message}")
    print("========================================================\n")

def main():
    parser = argparse.ArgumentParser(description="Job Terminator Manual Trigger CLI")
    parser.add_argument("--test-browser", action="store_true", help="Test Chrome CDP connectivity and agent navigation")
    parser.add_argument("--test-strapi", action="store_true", help="Test fetching candidate resume and latest job from Strapi")
    parser.add_argument("--latest-strapi", action="store_true", help="Fetch and apply to the most recent job in Strapi j-job-radars")
    parser.add_argument("--url", type=str, help="Specific job posting URL to apply to")
    parser.add_argument("--title", type=str, default="Software Engineer", help="Job title (optional)")
    parser.add_argument("--company", type=str, default="", help="Company name (optional)")
    parser.add_argument("--cover-letter", type=str, default=None, help="Cover letter text (optional)")
    parser.add_argument("--mode", type=str, choices=["semi-autonomous", "autonomous"], default="semi-autonomous", help="Autonomy mode")

    args = parser.parse_args()

    if args.test_browser:
        asyncio.run(run_test_browser())
    elif args.test_strapi:
        asyncio.run(run_test_strapi())
    elif args.latest_strapi or args.url:
        asyncio.run(run_apply(args))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
