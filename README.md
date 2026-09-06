# Job Terminator 🤖💼

> Autonomous Job Application Agent orchestrated via **n8n**, powered by **browser-use**, integrated with **Strapi V5**, and driven by your authenticated Google Chrome session.

---

## 📌 Overview

**Job Terminator** is an end-to-end intelligent automation system designed to eliminate repetitive job application work. It connects your existing scrapers, headless CMS, workflow automation engine, and a live web browser agent:

1. **Webhook & Manual Triggers**: Initiated either automatically via a Strapi V5 webhook or manually on demand.
2. **Strapi V5 Ingestion**: Queries pending jobs from `J - Job Radar` (`j-job-radar`) and automatically checks for custom CV attachments (`custom_cv`) or specific `cover_letter` texts.
3. **Dynamic Applicant Profile & Fallback**: Pulls your complete profile (experience, education, links) from Strapi's `updated-resume` endpoint (`/api/updated-resume?populate=*`) and falls back to your default PDF resume if no job-specific CV is attached.
4. **Live Chrome Session Control (CDP Port 9222)**: Attaches `browser-use` directly to a dedicated, persistent Chrome profile with all your logged-in credentials (LinkedIn, Indeed, Glassdoor, Greenhouse, Lever, Workday, etc.).
5. **Intelligent Form Completion & PDF Uploads**: Uses OpenAI `gpt-4o` to navigate portals, fill multi-step forms, map experience/contact data, and upload the resume PDF.
6. **Semi-Autonomous Guardrail (Human-in-the-Loop)**: Accurately prepares the application and pauses right before the final submission screen so you can inspect before sending.

---

## 🏗️ Architecture & Component Flow

```mermaid
sequenceDiagram
    autonumber
    participant Strapi as Strapi V5 (Chaldea Foundation Center)
    participant n8n as n8n Workflow Engine (Docker)
    participant Agent as Job Terminator Service (FastAPI / Windows Host)
    participant Chrome as Chrome (CDP Port 9222 / Automation Profile)
    participant Portal as Job Board / Employer Portal

    Note over Strapi, n8n: 1. Workflow Initiation
    alt Webhook Trigger
        Strapi->>n8n: POST /webhook/job-terminator-trigger
    else Manual Trigger
        n8n->>n8n: Click "Test workflow" button in n8n canvas
    end

    Note over n8n, Strapi: 2. Data Retrieval
    n8n->>Strapi: GET /api/j-job-radars?populate=*
    Strapi-->>n8n: List of jobs (links, company, cover letters, custom CVs)

    loop For each job (Split In Batches: 1)
        Note over n8n, Agent: 3. Dispatch to Agent
        n8n->>Agent: POST http://host.docker.internal:8000/apply
        
        Note over Agent: 4. Resume & Profile Preparation
        Agent->>Strapi: GET /api/updated-resume?populate=*
        Agent->>Agent: Download PDF CV (custom or default) to ./temp_resumes
        
        Note over Agent, Chrome: 5. Browser Automation
        Agent->>Chrome: Connect via CDP (ws://localhost:9222)
        Chrome->>Portal: Navigate to job application URL
        Agent->>Chrome: Analyze DOM, fill text/select fields & upload PDF
        Agent->>Chrome: Stop on final review screen (Semi-Autonomous mode)
        
        Note over Agent, n8n: 6. Execution Outcome
        Agent-->>n8n: 200 OK (Status: ready_for_review / submitted / captcha_detected)
        n8n->>n8n: Update internal n8n data table with application status
        n8n->>n8n: Wait 5s before proceeding to next job
    end
```

---

## 🚀 Setup Guide

### 1. Prerequisites

- **Operating System**: Windows 10/11
- **Python**: Version 3.11 or higher (Python 3.14 supported)
- **Google Chrome**: Installed at default location (`C:\Program Files\Google\Chrome\Application\chrome.exe`)
- **Docker & n8n**: Running self-hosted n8n instance (e.g., at `localhost:5678`)
- **OpenAI API Key**: Access to `gpt-4o`

---

### 2. Installation & Virtual Environment

Open PowerShell, navigate to the `job-terminator` directory, and set up your virtual environment:

```powershell
cd C:\Users\gonza\OneDrive\Desktop\localhost\job-terminator

# 1. Create Python virtual environment
python -m venv venv

# 2. Activate virtual environment
.\venv\Scripts\activate

# 3. Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Install Playwright browser dependencies
playwright install chromium
```

---

### 3. Environment Configuration (`.env`)

Copy the template configuration file:

```powershell
cp .env.example .env
```

Open `.env` in your editor and configure the variables:

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `OPENAI_API_KEY` | **Required**. Your OpenAI API key for `gpt-4o` | `sk-proj-...` |
| `STRAPI_API_URL` | Base URL of your Strapi V5 instance | `https://admin.chaldea.foundation` |
| `STRAPI_API_TOKEN` | Strapi API Token with Read access to `updated-resume` and `j-job-radars` | `your_token_here` |
| `CHROME_CDP_URL` | Chrome DevTools Protocol URL | `http://localhost:9222` |
| `PORT` | Local FastAPI service port | `8000` |
| `HOST` | Bind address (`0.0.0.0` allows Docker containers to connect) | `0.0.0.0` |
| `DEFAULT_RESUME_JSON_ENDPOINT` | Strapi endpoint for applicant structured JSON resume | `https://admin.chaldea.foundation/api/updated-resume?populate=*` |
| `DEFAULT_RESUME_PDF_URL` | Fallback URL to download default resume PDF | `https://admin.chaldea.foundation/uploads/...Resume.pdf` |
| `AUTONOMY_MODE` | `semi-autonomous` (stops at review screen) or `autonomous` (submits) | `semi-autonomous` |

---

### 4. Launching Chrome with CDP & Persistent Profile

Modern Chrome blocks remote debugging when run against your standard user profile. We use a dedicated automation profile at `$HOME\.chrome-job-terminator`. 

Run the launcher script:

```powershell
.\scripts\launch-chrome.ps1
```

> [!IMPORTANT]
> **One-Time Login**: The first time this Chrome window opens, manually log into your target job accounts (LinkedIn, Indeed, Glassdoor, etc.). Because the profile directory is persistent, your login cookies and sessions will remain permanently saved for all future automated runs!

---

### 5. Running the Service

Start the FastAPI HTTP service:

```powershell
.\venv\Scripts\python.exe -m src.main
```

The server will start on `http://0.0.0.0:8000`. You can verify:
- **Interactive Swagger Documentation**: `http://localhost:8000/docs`
- **Health Check & CDP Connection**: `http://localhost:8000/health`
- **Applicant Profile Preview**: `http://localhost:8000/profile`

---

## 🎮 Manual Trigger & Testing (Before Full Loop)

Before running a full workflow from n8n, you can test every individual subsystem using the CLI tool:

### 1. Test Strapi Token & Connection
Verify that your Strapi token works and your profile JSON and latest job are fetched properly:
```powershell
.\scripts\manual-trigger.ps1 -TestStrapi
```

### 2. Test Chrome CDP Control
Verify that `browser-use` can take control of your open Chrome browser window:
```powershell
.\scripts\manual-trigger.ps1 -TestBrowser
```

### 3. Apply to the Latest Job from Strapi
Fetch the most recent entry from `j-job-radars` and let the agent navigate and fill the form:
```powershell
.\scripts\manual-trigger.ps1 -LatestStrapi
```

### 4. Apply to a Custom Job Link Directly
Test application handling on any arbitrary job posting link:
```powershell
.\scripts\manual-trigger.ps1 -Url "https://www.linkedin.com/jobs/view/12345678" -Title "Senior Fullstack Engineer"
```

### 5. One-Click Test via Swagger UI
1. Navigate to **`http://localhost:8000/docs`** in your browser.
2. Expand **`POST /trigger/latest-strapi`**.
3. Click **"Try it out"** > **"Execute"**.

---

## 🔄 Detailed n8n Integration Guide

The repository includes a ready-to-import workflow located at [`workflows/n8n-job-terminator-workflow.json`](file:///C:/Users/gonza/OneDrive/Desktop/localhost/job-terminator/workflows/n8n-job-terminator-workflow.json).

### How to Import into n8n

1. Open your self-hosted n8n web dashboard (`http://localhost:5678`).
2. Click **Workflows** on the left navigation sidebar.
3. Click the **three dots menu (`...`)** in the top-right corner of the canvas and select **"Import from File..."**.
4. Browse and select `C:\Users\gonza\OneDrive\Desktop\localhost\job-terminator\workflows\n8n-job-terminator-workflow.json`.
5. The complete pipeline will render on your canvas.

---

### Step-by-Step Node Walkthrough

```
[Strapi Webhook] ────┐
                     ├───> [Fetch Jobs] ───> [Format Items] ───> [Loop (Batches)] ───> [Trigger Agent] ───> [Pause] ───┐
[Manual Trigger] ────┘                                                                                          │
                               ▲                                                                                │
                               └────────────────────────────────────────────────────────────────────────────────┘
```

#### 1. `Strapi Webhook Trigger` (Node ID: `1`)
- **Type**: `n8n-nodes-base.webhook`
- **Method**: `POST`
- **Path**: `job-terminator-trigger`
- **Full Webhook URL**: `http://localhost:5678/webhook/job-terminator-trigger`
- **In Strapi Admin**: Go to **Settings > Webhooks > Create new Webhook**:
  - Name: `Trigger Job Terminator`
  - URL: `http://localhost:5678/webhook/job-terminator-trigger` (or internal container URL if both are on Docker bridge)
  - Events: Select `Entry Create` or `Publish` under `J - Job Radar`.

#### 2. `When clicking 'Test workflow'` (Node ID: `0`)
- **Type**: `n8n-nodes-base.manualTrigger`
- Allows you to test the entire pipeline with one click directly inside the n8n canvas without waiting for an incoming webhook event.

#### 3. `Fetch Jobs From Strapi` (Node ID: `2`)
- **Type**: `n8n-nodes-base.httpRequest`
- **URL**: `https://admin.chaldea.foundation/api/j-job-radars?populate=*`
- **Headers**:
  - `Authorization`: `Bearer YOUR_STRAPI_TOKEN_HERE`
- **Purpose**: Fetches the list of saved job offers, including custom CV media relations and cover letters.

#### 4. `Format Job Items` (Node ID: `3`)
- **Type**: `n8n-nodes-base.code` (JavaScript)
- **Purpose**: Normalizes the Strapi V5 response schema. Extracts `id`, `job_title`, `company_name`, `job_post_link`, `cover_letter`, and resolves the media URL for `custom_cv`.

#### 5. `Loop Over Each Job` (Node ID: `4`)
- **Type**: `n8n-nodes-base.splitInBatches`
- **Batch Size**: `1`
- **Purpose**: Feeds job applications to the browser agent one at a time so your browser doesn't attempt to handle multiple conflicting sessions simultaneously.

#### 6. `Trigger Job Terminator Agent` (Node ID: `5`)
- **Type**: `n8n-nodes-base.httpRequest`
- **Method**: `POST`
- **URL**: `http://host.docker.internal:8000/apply`
- **Headers**: `Content-Type: application/json`
- **JSON Body**:
  ```json
  {
    "job_id": "={{ $json.id }}",
    "job_title": "={{ $json.job_title }}",
    "company_name": "={{ $json.company_name }}",
    "job_post_link": "={{ $json.job_post_link }}",
    "custom_cv_url": "={{ $json.custom_cv_url }}",
    "cover_letter": "={{ $json.cover_letter }}",
    "autonomy_mode": "semi-autonomous"
  }
  ```
- **Timeout**: Set to `300000` ms (5 minutes) to give `browser-use` enough time to navigate, fill forms, and upload files.

> [!IMPORTANT]
> **Docker to Host Networking**: Because n8n runs inside a Docker container while Chrome and `job-terminator` run on the Windows host, the URL must use `host.docker.internal:8000` instead of `localhost:8000`.

#### 7. `Pause Between Applications` (Node ID: `6`)
- **Type**: `n8n-nodes-base.wait`
- **Duration**: `5 seconds`
- **Purpose**: Provides a brief cooldown between applications, looping back to the next item in `Loop Over Each Job`.

#### 8. Integrating Your Custom n8n Data Table
- Add your custom n8n Data Table node immediately following the **`Trigger Job Terminator Agent`** node.
- Map the execution result:
  - `Status`: `{{ $json.status }}` (e.g. `ready_for_review`, `submitted`, `captcha_detected`, `failed`)
  - `Message`: `{{ $json.message }}`
  - `Job ID`: `{{ $json.details.job_id }}`

---

## 💡 Important Things to Know & Troubleshooting

### 1. Dedicated Chrome Profile vs Main Profile
- Chrome 136+ prevents remote debugging against your primary user data directory to block malicious infostealers.
- If you see `Cannot connect to port 9222`, ensure you ran `.\scripts\launch-chrome.ps1` and that no rogue Chrome instance is holding port 9222.
- To check active listeners:
  ```powershell
  Get-NetTCPConnection -LocalPort 9222 -ErrorAction SilentlyContinue
  ```

### 2. Autonomy Modes
- **`semi-autonomous` (Default & Recommended)**: The agent navigates, fills every single field, uploads your CV and cover letter, and **stops on the final review page**. It notifies you so you can give it a 5-second human glance and click "Submit".
- **`autonomous`**: The agent clicks the final "Submit" button automatically. You can switch this in `.env` (`AUTONOMY_MODE=autonomous`) or per request.

### 3. CAPTCHAs, Cloudflare Turnstile & 2FA
- `browser-use` has instructions to pause and return `status: "captcha_detected"` if a bot challenge or 2FA screen is detected.
- Because Chrome runs in non-headless mode on your desktop, you can simply interact with the open Chrome window to solve the puzzle, and the agent will continue.

### 4. Resume & Document Matching Logic
- If `custom_cv` is present in Strapi for that specific job, the agent downloads that custom PDF to `temp_resumes/` and uploads it.
- If `custom_cv` is null/empty, it automatically falls back to your default resume PDF URL specified in `.env`.
- Form text fields (experience, skills, email, website, GitHub) are dynamically populated using the JSON resume from Strapi.

---

## 📂 Project Structure

```
job-terminator/
├── .env.example                       # Environment variables template
├── .gitignore                         # Excludes venv, Chrome profile, temp PDFs
├── README.md                          # Comprehensive documentation
├── requirements.txt                   # Python dependencies
├── run_manual.py                      # CLI testing & manual trigger runner
├── scripts/
│   ├── launch-chrome.ps1              # Launch Chrome with CDP & dedicated profile
│   └── manual-trigger.ps1             # PowerShell wrapper for manual runs
├── src/
│   ├── __init__.py
│   ├── config.py                      # Settings & environment parser
│   ├── resume_loader.py               # Strapi resume JSON fetcher & PDF downloader
│   ├── agent.py                       # browser-use agent with gpt-4o & guardrails
│   └── main.py                        # FastAPI endpoints (/apply, /health, /trigger)
└── workflows/
    └── n8n-job-terminator-workflow.json # Ready-to-import n8n workflow
```
