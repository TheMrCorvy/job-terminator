# Job Terminator 🤖💼

> Autonomous Job Application Agent orchestrated via **n8n**, powered by **browser-use**, integrated with **Strapi V5**, and driven by your authenticated Google Chrome session.
>
> **Dual-Host Support**: Fully supported on both **macOS Sequoia (Mac Mini 2018 Intel / OrbStack)** and **Windows 11 (Docker Desktop / WSL 2)**.

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

## 🖥️ Dual-Host Architecture Matrix

Job Terminator is designed from the ground up to run seamlessly across both host environments:

| Feature | 🍎 macOS Host | 🪟 Windows 11 Host |
| :--- | :--- | :--- |
| **Target Hardware** | Mac Mini 2018 (Intel Core i5, 32GB RAM) | Desktop / Laptop (x86_64, 16GB+ RAM) |
| **Operating System** | macOS Sequoia (macOS 15+) | Windows 11 (22H2 / 23H2+) |
| **Container Engine** | [OrbStack](https://orbstack.dev/) | [Docker Desktop](https://www.docker.com/products/docker-desktop/) (WSL 2) |
| **Container-to-Host URL** | `http://host.docker.internal:8000` (or `mac.orb.local`) | `http://host.docker.internal:8000` |
| **Package Manager** | Homebrew (`brew`) | winget / python.org |
| **Python Version** | Python 3.11 or 3.12 | Python 3.11, 3.12, or 3.14 |
| **Chrome Executable** | `/Applications/Google Chrome.app/...` | `C:\Program Files\Google\Chrome\Application\chrome.exe` |
| **Chrome Launcher** | [`./scripts/launch-chrome.sh`](file:///C:/Users/gonza/OneDrive/Desktop/localhost/job-terminator/scripts/launch-chrome.sh) | [`.\scripts\launch-chrome.ps1`](file:///C:/Users/gonza/OneDrive/Desktop/localhost/job-terminator/scripts/launch-chrome.ps1) |
| **CLI Trigger** | [`./scripts/manual-trigger.sh`](file:///C:/Users/gonza/OneDrive/Desktop/localhost/job-terminator/scripts/manual-trigger.sh) | [`.\scripts\manual-trigger.ps1`](file:///C:/Users/gonza/OneDrive/Desktop/localhost/job-terminator/scripts/manual-trigger.ps1) |

---

## 🏗️ System Workflow

```mermaid
sequenceDiagram
    autonumber
    participant Strapi as Strapi V5 (Chaldea Foundation Center)
    participant n8n as n8n Container (OrbStack or Docker Desktop)
    participant Agent as Job Terminator (Host Python Service)
    participant Chrome as Chrome GUI (Host CDP Port 9222)
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
        Note over n8n, Agent: 3. Dispatch via Host Gateway
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

## 📦 Host Setup & Dependencies

Choose the tab corresponding to your host operating system:

### 🍎 Option A: macOS Sequoia Setup (Mac Mini Intel / OrbStack)

#### 1. Install Host Packages via Homebrew
```bash
# Install Homebrew if missing
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python, Git, Google Chrome, and OrbStack
brew install python@3.12 git
brew install --cask google-chrome
brew install --cask orbstack
```

#### 2. Virtual Environment & Playwright
```bash
cd ~/Desktop/localhost/job-terminator

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
chmod +x scripts/*.sh
```

#### 3. Launch Chrome with CDP
```bash
./scripts/launch-chrome.sh
```
*(Log in to your job portals once in the opened window; cookies remain saved permanently in `~/.chrome-job-terminator`)*

#### 4. Start the Service
```bash
source venv/bin/activate
python -m src.main
```

---

### 🪟 Option B: Windows 11 Setup (Docker Desktop / WSL 2)

#### 1. Install Host Prerequisites
- **Python 3.11+**: Install via [python.org](https://www.python.org/) or PowerShell:
  ```powershell
  winget install Python.Python.3.12
  ```
- **Google Chrome**:
  ```powershell
  winget install Google.Chrome
  ```
- **Git for Windows**:
  ```powershell
  winget install Git.Git
  ```
- **Docker Desktop with WSL 2 backend**:
  ```powershell
  winget install Docker.DockerDesktop
  ```

#### 2. Virtual Environment & Playwright
Open PowerShell in the project directory:
```powershell
cd C:\Users\gonza\OneDrive\Desktop\localhost\job-terminator

python -m venv venv
.\venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
```

#### 3. Launch Chrome with CDP
```powershell
.\scripts\launch-chrome.ps1
```
*(Log in to your job portals once in the opened window; cookies remain saved permanently in `$HOME\.chrome-job-terminator`)*

#### 4. Start the Service
```powershell
.\venv\Scripts\python.exe -m src.main
```

> [!TIP]
> **Windows Firewall Prompt**: When starting the service, Windows Defender Firewall may prompt you to allow Python access. Check **Private Networks** to allow Docker Desktop containers (via WSL 2 vEthernet) to reach port `8000`.

---

## ⚙️ Environment Configuration (`.env`)

Copy the example template on either OS:
```bash
# macOS
cp .env.example .env

# Windows
copy .env.example .env
```

Edit `.env` and fill in your keys:

```env
# OpenAI API Key (Required for browser-use agent with gpt-4o)
OPENAI_API_KEY=sk-proj-your_openai_api_key_here

# Chrome Remote Debugging (CDP) URL
CHROME_CDP_URL=http://localhost:9222

# Service Binding (0.0.0.0 is mandatory for Docker containers to connect)
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

# Temp directory for downloaded CVs
TEMP_DIR=./temp_resumes
```

---

## 🎮 Manual Trigger & Testing CLI

Before launching automated batches from n8n, test each subsystem individually:

| Purpose | 🍎 macOS Command | 🪟 Windows Command |
| :--- | :--- | :--- |
| **Verify Strapi Token & Resume** | `./scripts/manual-trigger.sh --test-strapi` | `.\scripts\manual-trigger.ps1 -TestStrapi` |
| **Verify Chrome CDP Control** | `./scripts/manual-trigger.sh --test-browser` | `.\scripts\manual-trigger.ps1 -TestBrowser` |
| **Apply to Latest Strapi Job** | `./scripts/manual-trigger.sh --latest-strapi` | `.\scripts\manual-trigger.ps1 -LatestStrapi` |
| **Apply to Custom Job Link** | `./scripts/manual-trigger.sh --url "https://..."` | `.\scripts\manual-trigger.ps1 -Url "https://..."` |
| **Interactive Swagger UI** | `http://localhost:8000/docs` | `http://localhost:8000/docs` |

---

## 🔄 Detailed n8n Integration Guide

The workflow definition is located at [`workflows/n8n-job-terminator-workflow.json`](file:///C:/Users/gonza/OneDrive/Desktop/localhost/job-terminator/workflows/n8n-job-terminator-workflow.json).

### How to Import into n8n (OrbStack or Docker Desktop)

1. Open your n8n web dashboard (`http://localhost:5678`).
2. Navigate to **Workflows** on the left sidebar.
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
- **URL**: `http://host.docker.internal:8000/apply` (works identically on both OrbStack and Docker Desktop)
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

## 🌐 Container-to-Host Networking (OrbStack vs Docker Desktop)

Both container environments support reaching the host machine using the exact same standard URL:

```
http://host.docker.internal:8000
```

1. **Docker Desktop (Windows 11)**:
   - `host.docker.internal` is baked into the WSL 2 DNS resolver. Any container can reach Windows host ports directly.
2. **OrbStack (macOS Sequoia)**:
   - OrbStack natively resolves `host.docker.internal` as well as `mac.orb.local` to the Mac host.
3. **Binding Requirement**:
   - `src/main.py` binds to `0.0.0.0` (all interfaces) rather than `127.0.0.1`. This allows the virtual network adapter of either container engine to reach the host application.

---

## 💡 Operational Notes & Troubleshooting

### 1. Dedicated Automation Profile vs Main Profile (Chrome 136+)
- Starting in Chrome 136, Chrome prohibits remote debugging flags on the default user profile directory.
- `job-terminator` uses an isolated automation directory (`~/.chrome-job-terminator` on macOS, `$HOME\.chrome-job-terminator` on Windows).
- If port 9222 is busy:
  - **macOS**: `lsof -i :9222` to find the process ID.
  - **Windows**: `Get-NetTCPConnection -LocalPort 9222` to check active listeners.

### 2. Semi-Autonomous vs Autonomous Modes
- **`semi-autonomous` (Default & Recommended)**: The agent fills every form field, uploads the CV, proceeds to the review screen, and stops. It takes a screenshot and alerts you so you can give it a 5-second human review and click Submit.
- **`autonomous`**: The agent clicks "Submit" automatically. Set `AUTONOMY_MODE=autonomous` in `.env` to enable.

### 3. CAPTCHAs, Cloudflare Turnstile & 2FA
- When bot challenges or 2FA prompts appear, the agent pauses and sets `status: "captcha_detected"`.
- Because Chrome runs in standard GUI mode on your desktop, you can solve the puzzle manually in the open window, and the agent will continue.

### 4. macOS Sequoia Energy Settings
- If running on a headless or background Mac Mini, enable **"Prevent automatic sleeping when the display is off"** under *System Settings > Energy Saver* or run `caffeinate -dis` in a background terminal.

---

## 🧩 Modular Prompt Templates (Domain-Driven Routing)

The agent dynamically selects custom prompt templates tailored to the target job portal based on the URL domain:

| Domain Match | Template | Custom Strategy & Rules |
| :--- | :--- | :--- |
| `*.indeed.com` | `IndeedPromptTemplate` | Prioritizes *"Usa tu CV de Indeed"*, blacklists *"Guardar y cerrar"*, enforces scrolling to bottom for *"Enviá tu postulación"*. |
| `*.epam.com` | `EpamPromptTemplate` | Mandatory PDF resume upload, English C1/Advanced selection, checks mandatory GDPR/privacy consent boxes, submits via *"Submit application"*. |
| `*.linkedin.com` | `LinkedInPromptTemplate` | Uses saved LinkedIn profile resume, handles Easy Apply (*"Solicitud sencilla"*), advances via *"Next"*, submits via *"Enviar solicitud"*. |
| *All others* | `GenericAtsPromptTemplate` | Fallback for standard corporate ATS portals (Greenhouse, Lever, Workday, SmartRecruiters, etc.) with file upload and form filling. |

### How to Add a New Custom Site Template
1. Create a new file in `src/prompts/<site_name>.py` subclassing `BasePromptTemplate`.
2. Implement `matches(self, domain: str) -> bool` and `build_prompt(...)`.
3. Register your new template in `src/prompts/router.py` inside `PromptRouter.__init__()`.

---

## 📂 Project Structure

```
job-terminator/
├── .env.example                         # Environment variables template
├── .gitignore                           # Excludes venv, Chrome profile, temp PDFs
├── README.md                            # Complete dual-host documentation
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
│   ├── agent.py                         # browser-use agent with tab cleanup & CDP control
│   ├── main.py                          # FastAPI endpoints (/apply, /health, /trigger)
│   └── prompts/                         # Domain-driven modular prompt templates
│       ├── __init__.py
│       ├── base.py                      # BasePromptTemplate abstract class & helpers
│       ├── router.py                    # Domain router & template matcher
│       ├── indeed.py                    # Indeed-specific prompt template
│       ├── epam.py                      # EPAM Careers-specific prompt template
│       ├── linkedin.py                  # LinkedIn Easy Apply prompt template
│       └── generic.py                   # Fallback ATS prompt template (Greenhouse, etc.)
└── workflows/
    └── n8n-job-terminator-workflow.json # Ready-to-import n8n workflow
```
