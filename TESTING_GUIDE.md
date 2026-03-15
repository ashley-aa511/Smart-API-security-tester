# Smart API Security Tester — Complete Testing Guide

This guide walks through every way to run and test the system — from a quick
30-second smoke test to the full AI-powered scan with Azure OpenAI.

---

## System Overview

| Component | What it does | Needs Azure? |
|-----------|-------------|-------------|
| `test_api_server.py` | Intentionally vulnerable Flask API used as the scan target | No |
| `test_full_scan.py` | Runs all 9 OWASP tests against the test server, one command | No |
| `main.py` | Interactive CLI scanner — prompts you through each step | No |
| `python -m pytest tests/` | 30 unit tests — no server or Azure needed | No |
| `test_helpers.py` | Tests helper utilities (URL parsing, risk scoring) | No |
| `src/agents/coordinator_agent.py` | AI agent that analyzes an API and creates a prioritized test plan | **Yes** |
| `test_integration.py` | End-to-end: AI planning + live scan, 3 scenarios | **Yes** |
| `uvicorn src.api.main:app` | FastAPI REST service exposing the scanner over HTTP | Optional |

---

## 1. Initial Setup

### Clone and install

```bash
git clone https://github.com/ashley-aa511/Smart-API-security-tester.git
cd Smart-API-security-tester

# Windows
python -m venv venv
.\venv\Scripts\Activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### Verify everything installed correctly

```bash
python verify_setup.py
```

**Expected output (without Azure configured):**

```
======================================================================
SMART API SECURITY TESTER - Setup Verification
======================================================================
  ✅ Python 3.12.x (OK)
  ✅ requests             - HTTP client
  ✅ rich                 - Terminal formatting
  ✅ flask                - Test server
  ✅ openai               - Azure OpenAI client
  ✅ python-dotenv        - Environment variables
  ✅ jinja2               - HTML templates
  ✅ reportlab            - PDF generation

  ⚠️  AZURE_OPENAI_ENDPOINT: Not configured (placeholder detected)
  ⚠️  AZURE_OPENAI_API_KEY:  Not configured (placeholder detected)
  ℹ️  Azure OpenAI not configured - AI features won't work
      You can still test: test_api_server.py and test_helpers.py

✅ BASIC SETUP: Complete
⚠️  AZURE AI SETUP: Not configured
```

All green checkmarks on dependencies = ready to test.

---

## 2. Configure Azure OpenAI (for AI features)

> Skip this section if you just want to run scans without AI planning.
> Everything in sections 3–5 works without Azure.

### Step 1 — Create an Azure OpenAI Resource

1. Go to [portal.azure.com](https://portal.azure.com)
2. Search for **"Azure OpenAI"** → click **Create**
3. Choose a region that has quota (Sweden Central and East US are most reliable)
4. Pricing tier: **Standard S0**
5. Click **Review + Create** → **Create**

### Step 2 — Deploy a Model

1. Open your Azure OpenAI resource
2. Click **Go to Azure AI Foundry** (or visit [ai.azure.com](https://ai.azure.com))
3. In the left menu: **Deployments** → **Deploy model** → **Deploy base model**
4. Choose **gpt-4o-mini** (lowest cost, works perfectly for this project)
5. Set a deployment name — e.g. `gpt-4o-mini`
6. SKU: **GlobalStandard**, tokens per minute: set to whatever quota you have
7. Click **Deploy**

### Step 3 — Get Your Credentials

From your Azure OpenAI resource page:
- **Keys and Endpoint** → copy **Key 1** and the **Endpoint URL**
- The endpoint looks like: `https://YOUR-RESOURCE-NAME.openai.azure.com/`

### Step 4 — Configure .env

Edit the `.env` file in the project root:

```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=abc123yourkeyhere
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

> **Never commit this file.** It is in `.gitignore`.

### Step 5 — Verify Azure is connected

```bash
python verify_setup.py
```

Look for:
```
  ✅ AZURE_OPENAI_ENDPOINT: https://your-resource.openai.azure.com/
  ✅ AZURE_OPENAI_API_KEY:  abc123you...here
  ✅ AZURE_OPENAI_DEPLOYMENT_NAME: gpt-4o-mini

✅ AZURE AI SETUP: Complete
```

---

## 3. Start the Vulnerable Test Server

This is a **safe, intentionally broken Flask API** used as the scan target.
Run it in **Terminal 1** and leave it running for all tests below.

```bash
python test_api_server.py
```

**Expected startup output:**
```
╔══════════════════════════════════════════════════════════╗
║  TEST API SERVER - FOR TESTING PURPOSES ONLY             ║
║  Contains intentional vulnerabilities                    ║
║  DO NOT USE IN PRODUCTION                                ║
╚══════════════════════════════════════════════════════════╝

Starting server at http://localhost:5000
 * Running on http://127.0.0.1:5000
 * Debugger is active!
```

### What's vulnerable on this server

| Endpoint | Method | Vulnerability | OWASP Category |
|----------|--------|--------------|----------------|
| `/api/user/1` | GET | Returns any user's data with no auth | API1 — BOLA |
| `/api/user/2` | GET | Same — exposes Bob's data to anyone | API1 — BOLA |
| `/api/admin` | GET | Admin panel with no authentication | API2 — Broken Auth |
| `/api/login` | POST | Accepts weak passwords: `admin/password`, `admin/123456` | API2 — Broken Auth |
| `/api/users` | POST | Accepts `role`, `isAdmin`, `balance` — any user can self-promote | API3 — Mass Assignment |
| `/api/unlimited` | GET | No rate limiting | API4 — Resource Consumption |
| `/api/search?q=` | GET | Returns SQL error on `'` or `--` input | API10 — Injection |
| `/api-docs` | GET | Exposes full API schema publicly | API9 — Inventory |
| All responses | - | Missing security headers (no CORS, no CSP, no X-Frame-Options) | API8 — Misconfiguration |

You can manually verify the server works before scanning:

```bash
# PowerShell
Invoke-RestMethod http://localhost:5000/api/user/1
Invoke-RestMethod http://localhost:5000/api/admin
Invoke-RestMethod -Uri http://localhost:5000/api/login -Method POST -ContentType "application/json" -Body '{"username":"admin","password":"password"}'
```

---

## 4. Quick End-to-End Scan (No Azure needed)

**Terminal 2** — this is the fastest way to see the full scanner in action:

```bash
python test_full_scan.py
```

This non-interactively runs all 9 OWASP tests against `localhost:5000` and
prints a full report.

**Expected output:**

```
╔══════════════════════════════════════╗
║   End-to-End Full Scan Test          ║
╚══════════════════════════════════════╝

Checking test server...
✓ Server reachable at http://localhost:5000

✓ Loaded 9 OWASP test modules

Starting scan against http://localhost:5000...
Running 9 tests

  ⚠ Found 2 potential issue(s)    ← BOLA (accessing user 1 and 2)
  ⚠ Found 3 potential issue(s)    ← Broken Auth (admin panel + weak passwords)
  ⚠ Found 1 potential issue(s)    ← Excessive Data Exposure
  ✓ Passed                         ← Rate Limiting
  ⚠ Found 1 potential issue(s)    ← Function Level Auth
  ✓ Passed                         ← SSRF
  ⚠ Found 1 potential issue(s)    ← Security Misconfiguration
  ⚠ Found 1 potential issue(s)    ← Improper Inventory
  ⚠ Found 2 potential issue(s)    ← Injection

┌─────────────────────────────────┬───────┐
│ Final Summary                         │
├──────────────────────────────────┬────┤
│ Total tests run                  │  9+ │
│ Vulnerabilities found            │  X  │
│   CRITICAL                       │  X  │
│   HIGH                           │  X  │
│   MEDIUM                         │  X  │
│   LOW                            │  0  │
│ Passed (no issues)               │  2  │
└──────────────────────────────────┴────┘

✓ Results saved to: scan_YYYYMMDD_HHMMSS.json

✓ SCAN COMPLETE — X vulnerabilities detected
  (expected for the intentionally vulnerable test server)
```

The exact vulnerability count depends on how the test server responds, but
you should see **at minimum 6–8 VULNERABLE findings**.

---

## 5. Interactive CLI Scanner (No Azure needed)

For a guided, interactive experience:

```bash
python main.py
```

**Step-by-step prompts:**

```
╔═══════════════════════════════════════════════════════╗
║       API Security Tester                             ║
║       OWASP API Security Top 10 Scanner               ║
╚═══════════════════════════════════════════════════════╝

Configure Your Security Scan

Enter target API URL: http://localhost:5000

Add custom headers? (e.g., Authorization, API-Key)
Press Enter to skip, or enter in format 'Key: Value'
Header (or press Enter to continue): [press Enter]

Select Tests to Run
  1. [CRITICAL] API1:2023 - Broken Object Level Authorization
  2. [CRITICAL] API2:2023 - Broken Authentication
  3. [HIGH]     API3:2023 - Excessive Data Exposure
  ...
  10. Run ALL tests (recommended)

Enter your choice: 10

Review Configuration
Target: http://localhost:5000
Tests: 9 test(s)

Proceed with scan? (y/n): y
```

After the scan, you are prompted to export:
```
Export Results
1. JSON
2. HTML Report
3. PDF Report
4. All formats
5. Skip export

Select export option: 2
```

- **JSON** → `scan_YYYYMMDD_HHMMSS.json` — machine-readable full results
- **HTML** → `security_report_YYYYMMDD_HHMMSS.html` — visual report, open in browser
- **PDF** → `security_report_YYYYMMDD_HHMMSS.pdf` — printable report

---

## 6. Unit Tests (No Azure, No server needed)

These run entirely offline with mocked data:

```bash
python -m pytest tests/ -v
```

**Expected output:**

```
collected 30 items

tests/agents/test_coordinator_agent.py::TestCoordinatorAgentInit::test_init_creates_client PASSED
tests/agents/test_coordinator_agent.py::TestCoordinatorAgentInit::test_init_with_missing_env_vars PASSED
tests/agents/test_coordinator_agent.py::TestAnalyzeApi::test_analyze_api_returns_dict PASSED
tests/agents/test_coordinator_agent.py::TestAnalyzeApi::test_analyze_api_passes_headers PASSED
tests/agents/test_coordinator_agent.py::TestCreateScanPlan::test_create_scan_plan_returns_dict PASSED
tests/agents/test_coordinator_agent.py::TestCreateScanPlan::test_create_scan_plan_includes_analysis_context PASSED
tests/agents/test_coordinator_agent.py::TestPlanScan::test_plan_scan_returns_complete_result PASSED
tests/agents/test_coordinator_agent.py::TestPlanScan::test_plan_scan_calls_openai_twice PASSED
tests/agents/test_coordinator_agent.py::TestPlanScan::test_plan_scan_preserves_headers PASSED
tests/test_scanner.py::TestScanSession::test_init_defaults PASSED
... (21 more)

============================== 30 passed in 7s ==============================
```

All 30 must pass. If any fail, run `pip install -r requirements.txt` first.

---

## 7. AI Coordinator Agent (Requires Azure)

The Coordinator Agent uses GPT to analyze an API and produce a prioritized,
reasoned test plan before running a single test.

```bash
python src/agents/coordinator_agent.py
```

**Expected output:**

```
🤖 Coordinator Agent: Analyzing target API...
✓ Analysis complete: User Management API
  Data Sensitivity: Medium
  Auth Method: None

🤖 Coordinator Agent: Creating scan plan...
✓ Plan created: 5 tests prioritized
  Estimated duration: 12 minutes

{
  "api_analysis": {
    "api_type": "REST",
    "auth_method": "None",
    "data_sensitivity": "Medium",
    "domain": "User Management",
    "risk_areas": ["authentication", "authorization", "bola"],
    "reasoning": "No authentication observed — high risk for unauthorized access"
  },
  "scan_plan": {
    "priority_tests": [
      {
        "test_id": "API2",
        "test_name": "Broken Authentication",
        "priority": "CRITICAL",
        "reason": "Admin endpoint accessible without credentials",
        "parameters": { "intensity": "high" }
      },
      ...
    ],
    "recommended_order": ["API2", "API5", "API1", "API10", "API8"],
    "estimated_duration_minutes": 12,
    "special_considerations": ["No rate limiting detected — safe to test aggressively"]
  }
}
```

The AI reasons about *why* certain tests matter for this specific API, not just
running them blindly.

---

## 8. AI + Scanner Integration Test (Requires Azure + Test Server)

Runs the Coordinator Agent against 3 different API scenarios and shows how the
AI adapts its plan each time.

**Terminal 1:** `python test_api_server.py`

**Terminal 2:**
```bash
python test_integration.py
```

**Expected output:**

```
==========================================================
 SMART API SECURITY TESTER - Integration Test
==========================================================

Scenario 1: Public REST API (No Auth)
  Target: http://localhost:5000
  🤖 AI analyzing API...
  ✓ API type: REST  |  Auth: None  |  Sensitivity: Medium
  ✓ Plan: 6 tests prioritized — leads with API2, API1
  🔍 Running scanner with AI guidance...
  ✓ Scan complete — X vulnerabilities found

Scenario 2: Authenticated API
  ...

Scenario 3: High-Sensitivity API
  ...

==========================================================
Integration test PASSED — AI planning + Scanner working end-to-end
==========================================================
```

---

## 9. FastAPI Web Service

Exposes the scanner as a REST API. Useful for CI/CD integration or building
a frontend on top.

### Start the service

```bash
uvicorn src.api.main:app --reload --port 8000
```

**Expected:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

Visit **http://localhost:8000/docs** for the interactive Swagger UI — you can
trigger scans directly from the browser.

### API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/health` | Returns `{"status": "healthy"}` |
| `POST` | `/api/v1/scan` | Start a scan (runs in background) |
| `GET` | `/api/v1/scan/{id}` | Get results for a scan |
| `GET` | `/api/v1/scans` | List all scans |
| `DELETE` | `/api/v1/scan/{id}` | Remove a scan |
| `POST` | `/api/v1/plan` | AI planning only — no scan executed |

### Trigger a scan (PowerShell)

```powershell
# Start a scan (no AI planning)
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/scan" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"target_url": "http://localhost:5000", "use_ai_planning": false}'

$scanId = $response.scan_id
Write-Host "Scan started: $scanId"

# Wait a few seconds, then get results
Start-Sleep -Seconds 10
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/scan/$scanId"
```

### Trigger a scan (bash/curl)

```bash
# Start scan
SCAN_ID=$(curl -s -X POST http://localhost:8000/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{"target_url": "http://localhost:5000", "use_ai_planning": false}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['scan_id'])")

echo "Scan ID: $SCAN_ID"

# Get results
sleep 10
curl -s http://localhost:8000/api/v1/scan/$SCAN_ID | python -m json.tool
```

### Expected scan result (after completion)

```json
{
  "scan_id": "abc-123-...",
  "target_url": "http://localhost:5000",
  "status": "completed",
  "started_at": "2026-03-15T19:00:00",
  "completed_at": "2026-03-15T19:00:45",
  "summary": {
    "total_tests": 12,
    "vulnerabilities_found": 8,
    "critical": 2,
    "high": 3,
    "medium": 2,
    "low": 0,
    "info": 1,
    "passed": 2
  },
  "results": [ ... ],
  "ai_plan": null
}
```

If `use_ai_planning: true` and Azure is configured, `ai_plan` will contain the
full Coordinator Agent analysis.

---

## 10. Recommended Test Order

Run these in sequence to validate the entire system:

```
Step 1 (offline)    python -m pytest tests/ -v              ← 30 tests, no deps
Step 2 (no Azure)   python test_api_server.py               ← start server (keep running)
Step 3 (no Azure)   python test_full_scan.py                ← full scan, simplest
Step 4 (no Azure)   python main.py                          ← interactive scan + reports
Step 5 (Azure)      python src/agents/coordinator_agent.py  ← AI planning
Step 6 (Azure)      python test_integration.py              ← AI + scanner together
Step 7 (optional)   uvicorn src.api.main:app --port 8000    ← REST API
```

---

## Troubleshooting

### `ModuleNotFoundError`
```bash
pip install -r requirements.txt
```

### `✗ Test server not running!` in test_full_scan.py
```bash
# Terminal 1 must be running:
python test_api_server.py
```

### `DeploymentNotFound`
- Your `.env` `AZURE_OPENAI_DEPLOYMENT_NAME` doesn't match the deployment name in Azure AI Foundry
- Go to [ai.azure.com](https://ai.azure.com) → **Deployments** and copy the exact name

### `InsufficientQuota`
- Your subscription has 0 TPM quota for that region
- Try a different region: Sweden Central or East US tend to have the most available quota
- Request an increase: [ai.azure.com](https://ai.azure.com) → **Quotas** → **Request increase**

### `AuthenticationError` / `401`
- Your `AZURE_OPENAI_API_KEY` is wrong or expired
- Copy **Key 1** fresh from Azure portal → your resource → **Keys and Endpoint**

### Virtual environment not active (missing modules)
```bash
.\venv\Scripts\Activate    # Windows
source venv/bin/activate   # Linux/Mac
```

### Port 5000 already in use
```bash
# Windows PowerShell — find and kill the process
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Port 8000 already in use (FastAPI)
```bash
uvicorn src.api.main:app --port 8001
```
