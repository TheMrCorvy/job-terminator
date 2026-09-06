# Job Terminator 🤖💼

> Autonomous Job Application Agent orchestrated via **n8n**, powered by **browser-use**, integrated with **Strapi V5**, and driven by your authenticated Google Chrome session.

---

## 📌 Overview

**Job Terminator** is an end-to-end intelligent automation system designed to eliminate repetitive job application tasks. It connects your existing scrapers, headless CMS, workflow automation engine, and a live web browser agent:

1. **Webhook & Manual Triggers**: Initiated automatically via a Strapi V5 webhook or manually on demand.
2. **Strapi V5 Ingestion**: Queries pending jobs from `J - Job Radar` (`j-job-radar`) and automatically detects custom CV attachments (`custom_cv`) or specific `cover_letter` texts.
3. **Dynamic Applicant Profile & Fallback**: Pulls your complete profile (experience, education, links) from Strapi's `updated-resume` endpoint (`/api/updated-resume?populate=*`) and falls back to your default PDF resume if no job-specific CV is attached.
4. **Live Chrome Session Control (CDP Port 9222)**: Attaches `browser-use` directly to a dedicated, persistent Chrome profile with all your logged-in credentials (LinkedIn, Indeed, Glassdoor, Greenhouse, Lever, Workday, etc.).
5. **Intelligent Form Completion & PDF Uploads**: Uses OpenAI `gpt-4o` to navigate portals, fill multi-step forms, map experience/contact data, and upload the resume PDF.
6. **Semi-Autonomous Guardrail (Human-in-the-Loop)**: Accurately prepares the application and pauses right before the final submission screen so you can inspect before sending.

---

## 🖥️ Target Host Environment & System Architecture

This project is tailored to run on:
- **Host PC**: Mac Mini 2018 (Intel Core i5 6-Core, x86_64, 32GB RAM)
- **Host OS**: macOS Sequoia (macOS 15+)
- **Container Engine**: [OrbStack](https://orbstack.dev/) (Lightweight, fast Docker & Linux engine for macOS)
- **Orchestration**: Self-hosted n8n running in Docker via OrbStack

```mermaid
sequenceDiagram
    autonumber
    participant Strapi as Strapi V5 (Chaldea Foundation Center)
    participant n8n as n8n Container (OrbStack)
    participant Agent as Job Terminator (Host macOS Python)
    participant Chrome as Chrome (Host macOS CDP Port 9222)
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
        Note over n8n, Agent: 3. Dispatch via OrbStack Host Bridge
        n8n->>Agent: POST http://host.docker.internal:8000/apply
        
        Note over Agent: 4. Resume & Profile Preparation
        Agent->>Strapi: GET /api/updated-resume?populate=*
        Agent->>Agent: Download PDF CV (custom or default) to ./temp_resumes
        
        Note over Agent, Chrome: 5. Browser Automation (CDP)
        Agent->>Chrome: Connect via CDP (ws://localhost:9222)
        Chrome->>Portal: Navigate to job application URL
        Agent->>Chrome: Analyze DOM, fill inputs & upload PDF
        Agent->>Chrome: Stop on final review screen (Semi-Autonomous mode)
        
        Note over Agent, n8n: 6. Execution Outcome
        Agent-->>n8n: 200 OK (Status: ready_for_review / submitted / captcha_detected)
        n8n->>n8n: Update internal n8n data table with application status
        n8n->>n8n: Wait 5s before proceeding to next job
    end
```

---

## 📦 Host PC Dependencies (macOS Sequoia on Intel Mac Mini)

All required dependencies must be installed directly on the macOS host (outside containers) so the agent can interface with the desktop display server and the Chrome GUI.

### 1. Install Homebrew (Package Manager)
If not already installed on your Mac Mini, install Homebrew (for Intel Macs, installs to `/usr/local`):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Core Host Packages
Run the following brew command to install Python, Git, and Google Chrome:
```bash
# 1. Install Python 3.12 (or 3.11)
brew install python@3.12

# 2. Install Git
brew install git

# 3. Install Google Chrome (GUI browser for CDP control)
brew install --cask google-chrome

# 4. Install OrbStack (if not already installed)
brew install --cask orbstack
```

### 3. Verify Installations
```bash
python3 --version     # Should report Python 3.11.x or 3.12.x
git --version         # Should report git version 2.x
which "Google Chrome" # App exists in /Applications/Google Chrome.app
```

---

## 🚀 Setup Guide (Step-by-Step)

### Step 1: Clone or Navigate to the Repository
```bash
cd ~/Desktop/localhost/job-terminator
```

### Step 2: Set Up Python Virtual Environment
```bash
# Create virtual environment using host Python
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip and install all project dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browser dependencies for Chromium
playwright install chromium
```

> [!NOTE]
> On macOS, `playwright install chromium` downloads the headless shell and browser engines used internally by Playwright. For live automated sessions, `job-terminator` connects directly to your installed `/Applications/Google Chrome.app` via CDP port 9222.

---

### Step 3: Configure Environment Variables (`.env`)

Copy the example template:
```bash
cp .env.example .env
```

Edit `.env` and set your credentials:

```env
# ===================================================================
# Job Terminator Configuration
# ===================================================================

# OpenAI API Key (Required for browser-use agent with gpt-4o)
OPENAI_API_KEY=sk-proj-your_openai_api_key_here

# Chrome Remote Debugging (CDP) URL
CHROME_CDP_URL=http://localhost:9222

# Service Binding
PORT=8000
HOST=0.0.0.0

# Strapi V5 Configuration
STRAPI_API_URL=https://admin.chaldea.foundation
STRAPI_API_TOKEN=your_strapi_api_token_here

# Default Resume Configuration (fallback when job has no custom_cv)
DEFAULT_RESUME_JSON_ENDPOINT=https://admin.chaldea.foundation/api/updated-resume?populate=*
DEFAULT_RESUME_PDF_URL=https://admin.chaldea.foundation/uploads/gonzalo_salvador_corvalan_Resume_fe85477412.pdf

# Autonomy Level
# "semi-autonomous" (Recommended): Fills forms & uploads CV, pauses on final review screen
# "autonomous": Submits applications directly without human confirmation
AUTONOMY_MODE=semi-autonomous

# Temp directory to store downloaded CVs for browser-use upload
TEMP_DIR=./temp_resumes
```

#### Environment Variables Reference:
| Variable | Required | Description |
| :--- | :--- | :--- |
| `OPENAI_API_KEY` | **Yes** | OpenAI API key with access to `gpt-4o`. |
| `STRAPI_API_TOKEN` | **Yes** | Strapi API Token with Read permissions for `updated-resume` and `j-job-radars`. |
| `STRAPI_API_URL` | **Yes** | Base URL of your Strapi instance (`https://admin.chaldea.foundation`). |
| `CHROME_CDP_URL` | No | CDP listener URL (defaults to `http://localhost:9222`). |
| `HOST` | No | Defaults to `0.0.0.0` so containers inside OrbStack can reach the service. |
| `PORT` | No | Defaults to `8000`. |
| `AUTONOMY_MODE` | No | `semi-autonomous` (stops at review screen) or `autonomous` (clicks Submit). |

---

### Step 4: Launch Chrome with CDP & Persistent Profile

Modern Chrome blocks remote debugging against the standard default profile to prevent infostealers from extracting credentials. We launch Chrome pointing to a persistent automation profile at `$HOME/.chrome-job-terminator`.

#### On macOS:
Make the helper script executable and run it:
```bash
chmod +x scripts/launch-chrome.sh scripts/manual-trigger.sh
./scripts/launch-chrome.sh
```

#### On Windows (if running on Windows host):
```powershell
.\scripts\launch-chrome.ps1
```

> [!IMPORTANT]
> **One-Time Manual Login**:
> The first time this dedicated Chrome window opens, log into your job search accounts (LinkedIn, Indeed, Glassdoor, Greenhouse, Lever, etc.).
> Because the user data directory is persistent (`~/.chrome-job-terminator`), your login cookies and sessions will remain permanently saved for all future automated runs. You will **not** need to log in again.

---

### Step 5: Start the Job Terminator FastAPI Service

```bash
# Ensure venv is activated
source venv/bin/activate

# Start the server
python -m src.main
```

The service will be listening on `http://0.0.0.0:8000`. You can inspect:
- **Interactive Swagger Documentation**: `http://localhost:8000/docs`
- **Service & CDP Health Check**: `http://localhost:8000/health`
- **Candidate Profile JSON Check**: `http://localhost:8000/profile`

---

## 🎮 Manual Trigger & Testing CLI

Before triggering full batch runs from n8n or Strapi webhooks, verify each component individually:

### 1. Test Strapi Connection & Resume Ingestion
Tests fetching your profile JSON and querying the latest job from `j-job-radars`:
```bash
# macOS
./scripts/manual-trigger.sh --test-strapi

# Windows
.\scripts\manual-trigger.ps1 -TestStrapi
```

### 2. Test Chrome CDP Navigation
Opens a test tab in your Chrome instance via `browser-use` to verify the AI has control:
```bash
# macOS
./scripts/manual-trigger.sh --test-browser

# Windows
.\scripts\manual-trigger.ps1 -TestBrowser
```

### 3. Apply to the Latest Job from Strapi
Pulls the newest job entry from Strapi `j-job-radars` and runs the application flow:
```bash
# macOS
./scripts/manual-trigger.sh --latest-strapi

# Windows
.\scripts\manual-trigger.ps1 -LatestStrapi
```

### 4. Apply to Any Arbitrary Job URL Directly
```bash
# macOS
./scripts/manual-trigger.sh --url "https://jobs.lever.co/company/example" --title "Senior Backend Engineer"

# Windows
.\scripts\manual-trigger.ps1 -Url "https://jobs.lever.co/company/example" -Title "Senior Backend Engineer"
```

### 5. Interactive Swagger UI (One-Click Testing)
1. Open **`http://localhost:8000/docs`** in your browser.
2. Expand **`POST /trigger/latest-strapi`**.
3. Click **"Try it out"** > **"Execute"**.

---

## 🔄 Detailed n8n Integration Guide (with OrbStack)

The repository provides an importable workflow file at [`workflows/n8n-job-terminator-workflow.json`](file:///C:/Users/gonza/OneDrive/Desktop/localhost/job-terminator/workflows/n8n-job-terminator-workflow.json).

### How to Import into n8n

1. Open your n8n web dashboard (`http://localhost:5678`).
2. Navigate to **Workflows** on the left navigation sidebar.
3. Click the **`...` (Options menu)** in the upper-right corner of the canvas and select **"Import from File..."**.
4. Upload `workflows/n8n-job-terminator-workflow.json`.
5. The pipeline will appear on your canvas.

---

### Step-by-Step Node Walkthrough

```
[Strapi Webhook] ────┐
                     ├───> [Fetch Jobs] ───> [Format Items] ───> [Loop (Batches: 1)] ───> [Trigger Agent] ───> [Pause] ───┐
[Manual Trigger] ────┘                                                                                               │
                               ▲                                                                                     │
                               └─────────────────────────────────────────────────────────────────────────────────────┘
```

#### Node 1: `Strapi Webhook Trigger`
- **Type**: `n8n-nodes-base.webhook`
- **HTTP Method**: `POST`
- **Path**: `job-terminator-trigger`
- **Webhook URL**: `http://localhost:5678/webhook/job-terminator-trigger`
- **Configuring in Strapi Admin**:
  1. Open Strapi Admin (`https://admin.chaldea.foundation/admin`).
  2. Go to **Settings > Webhooks > Create new Webhook**.
  3. Set Name to `Job Terminator Trigger`.
  4. Set URL to your n8n webhook URL.
  5. Select Events: `entry.create` or `entry.publish` under `J - Job Radar`.

#### Node 2: `When clicking 'Test workflow'`
- **Type**: `n8n-nodes-base.manualTrigger`
- Connected alongside the Webhook node to allow one-click testing inside the n8n canvas without sending real webhooks.

#### Node 3: `Fetch Jobs From Strapi`
- **Type**: `n8n-nodes-base.httpRequest`
- **URL**: `https://admin.chaldea.foundation/api/j-job-radars?populate=*`
- **Headers**:
  - `Authorization`: `Bearer YOUR_STRAPI_TOKEN_HERE`
- Pulls all recorded job opportunities, complete with media attachments (`custom_cv`) and cover letter texts.

#### Node 4: `Format Job Items`
- **Type**: `n8n-nodes-base.code` (JavaScript)
- Flattens the Strapi V5 schema structure and prepares a clean JSON object containing:
  - `id`: Unique Job ID
  - `job_title`: Title of the role
  - `company_name`: Target company
  - `job_post_link`: URL of the application page
  - `custom_cv_url`: Media file URL (if attached)
  - `cover_letter`: Job-specific cover letter (if present)

#### Node 5: `Loop Over Each Job`
- **Type**: `n8n-nodes-base.splitInBatches`
- **Batch Size**: `1`
- **Purpose**: Essential to ensure the browser processes jobs sequentially. Running multiple browser automations concurrently against a single Chrome session would cause focus and input collisions.

#### Node 6: `Trigger Job Terminator Agent`
- **Type**: `n8n-nodes-base.httpRequest`
- **HTTP Method**: `POST`
- **URL**: `http://host.docker.internal:8000/apply` (or `http://mac.orb.local:8000/apply`)
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
- **Timeout**: Set to `300000` ms (5 minutes) so the request doesn't drop while the agent navigates, fills fields, and uploads files.

#### Node 7: `Pause Between Applications`
- **Type**: `n8n-nodes-base.wait`
- **Amount**: `5 seconds`
- **Purpose**: Provides a short interval between consecutive applications before the loop proceeds to the next job.

#### Node 8: Connecting Your Custom n8n Data Table
- Add your custom n8n Data Table node immediately after **`Trigger Job Terminator Agent`**.
- Map the status values returned by the agent:
  - `job_id`: `{{ $json.details.job_id }}`
  - `status`: `{{ $json.status }}` (`ready_for_review`, `submitted`, `captcha_detected`, `failed`)
  - `message`: `{{ $json.message }}`
  - `cv_file_used`: `{{ $json.details.cv_file_used }}`

---

## 🌐 OrbStack & Docker Networking Specifics

When running n8n inside Docker using **OrbStack** on macOS, container-to-host networking behaves as follows:

1. **Host Reachability**:
   - Containers in OrbStack can reach host services via **`http://host.docker.internal:8000`** or **`http://mac.orb.local:8000`**.
   - Because `job-terminator` binds to `0.0.0.0:8000`, it listens on all network interfaces, allowing OrbStack's container bridge to communicate seamlessly.
2. **Port Forwarding**:
   - OrbStack exposes container ports (like n8n on `5678`) directly on your Mac host without additional configuration.
3. **Intel Mac Mini Performance**:
   - Because the 2018 Mac Mini has an Intel Core i5 (x86_64), all Docker images run in native `linux/amd64` architecture with zero emulation overhead.

---

## 💡 Important Things to Know & Troubleshooting

### 1. macOS Sequoia Sleep Prevention
On a headless or standalone Mac Mini, macOS Sequoia may attempt to put system sleep or display sleep into effect:
- Go to **System Settings > Energy Saver**.
- Enable **"Prevent automatic sleeping when the display is off"**.
- Alternatively, run `caffeinate -dis` in a background terminal if needed.

### 2. macOS Accessibility / Automation Permissions
macOS Sequoia enforces strict privacy controls. If Playwright or Chrome displays a permission dialog:
- Go to **System Settings > Privacy & Security > Accessibility** (and **Screen Recording** if requested).
- Allow **Terminal** (or iTerm2 / Python) access.

### 3. Dedicated Chrome Profile vs Main Profile (Chrome 136+)
- If you see `Cannot connect to port 9222`, ensure `./scripts/launch-chrome.sh` is running and that no orphaned Chrome instance is holding the port.
- Check active listeners on macOS:
  ```bash
  lsof -i :9222
  ```

### 4. CAPTCHAs, Cloudflare Turnstile & 2FA
- If a Cloudflare challenge or 2FA verification appears, `browser-use` pauses and returns `status: "captcha_detected"`.
- Because Chrome is running as a regular desktop window on your Mac Mini, you can access the display (via VNC / Screen Sharing) and solve the puzzle manually.

### 5. Resume & Document Fallback Logic
- If `custom_cv` is attached in Strapi for that job, it is downloaded to `temp_resumes/` and uploaded to the application form.
- If `custom_cv` is null, it falls back to your default resume PDF URL specified in `.env`.
- Form text fields (experience, skills, email, website, GitHub) are dynamically populated using the JSON resume from Strapi.

---

## 📂 Project Structure

```
job-terminator/
├── .env.example                         # Environment variables template
├── .gitignore                           # Excludes venv, Chrome profile, temp PDFs
├── README.md                            # Comprehensive documentation & guide
├── requirements.txt                     # Python dependencies
├── run_manual.py                        # CLI testing & manual trigger runner
├── scripts/
│   ├── launch-chrome.sh                 # macOS Chrome CDP launcher (Mac Mini / Sequoia)
│   ├── launch-chrome.ps1                # Windows Chrome CDP launcher
│   ├── manual-trigger.sh                # macOS CLI manual trigger wrapper
│   └── manual-trigger.ps1               # Windows CLI manual trigger wrapper
├── src/
│   ├── __init__.py
│   ├── config.py                        # Settings & environment parser
│   ├── resume_loader.py                 # Strapi resume JSON fetcher & PDF downloader
│   ├── agent.py                         # browser-use agent with gpt-4o & guardrails
│   └── main.py                          # FastAPI endpoints (/apply, /health, /trigger)
└── workflows/
    └── n8n-job-terminator-workflow.json # Ready-to-import n8n workflow
```
