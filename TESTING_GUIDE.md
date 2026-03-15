# Smart API Security Tester — Testing Guide

Full system is implemented. The only external requirement is **Azure OpenAI quota**.

---

## 1. Setup

```bash
# Clone the repo
git clone https://github.com/ashley-aa511/Smart-API-security-tester.git
cd Smart-API-security-tester

# Create and activate virtual environment (Windows)
python -m venv venv
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt
```

---

## 2. Configure Environment

Copy the `.env` file and fill in your Azure OpenAI credentials:

```bash
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com/
AZURE_OPENAI_API_KEY=YOUR-API-KEY
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini   # use your actual deployment name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

Then verify your setup:

```bash
python verify_setup.py
```

All items should show ✅ before proceeding.

---

## 3. Start the Vulnerable Test Server

This is a safe, intentionally vulnerable Flask API used as the scan target.
Run this in **Terminal 1** and leave it running.

```bash
python test_api_server.py
```

Server runs at `http://localhost:5000` with these vulnerable endpoints:

| Endpoint | Vulnerability |
|----------|--------------|
| `GET /api/user/1` | BOLA — no ownership check |
| `GET /api/admin` | No authentication required |
| `POST /api/login` | Accepts weak passwords |
| `POST /api/users` | Mass assignment |
| `GET /api/search?q=` | SQL injection simulation |
| `GET /api-docs` | Public API documentation |

---

## 4. Run the Full CLI Scanner

**Terminal 2** — runs all 9 OWASP tests against the test server:

```bash
python main.py
```

**When prompted:**
- Target URL: `http://localhost:5000`
- Headers: press Enter to skip
- Tests: enter the number for "Run ALL tests"
- Confirm: `y`

**Expected output:**
```
╔═══════════════════════════════════════════════════════╗
║       API Security Tester                             ║
║       OWASP API Security Top 10 Scanner               ║
╚═══════════════════════════════════════════════════════╝

Starting Security Scan
Target: http://localhost:5000
Tests: 9

  ⚠ Found 3 potential issue(s)   ← BOLA
  ⚠ Found 2 potential issue(s)   ← Broken Auth
  ✓ Passed                        ← SSRF
  ...

SCAN RESULTS
======================================================================
Vulnerabilities Found: X
  CRITICAL: X
  HIGH: X
  MEDIUM: X
```

At the end, choose an export format:
- `1` → JSON
- `2` → HTML report (opens in browser)
- `3` → PDF report
- `4` → All formats

---

## 5. Run the AI Coordinator Agent  *(Requires Azure)*

Uses Azure OpenAI to intelligently analyze the API and create a prioritized test plan.

```bash
python src/agents/coordinator_agent.py
```

**Expected output:**
```
🤖 Coordinator Agent: Analyzing target API...
✓ Analysis complete: User Management REST API
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
    "risk_areas": ["authentication", "authorization", "bola"]
  },
  "scan_plan": {
    "priority_tests": [...],
    "recommended_order": ["API1", "API2", "API5", "API10", "API8"],
    "estimated_duration_minutes": 12
  }
}
```

---

## 6. Run the Integration Test  *(Requires Azure + Test Server)*

Demonstrates AI planning + scanner working together end-to-end.

**Terminal 1:** `python test_api_server.py`

**Terminal 2:**
```bash
python test_integration.py
```

This runs the Coordinator Agent against 3 different scenarios on the test server
and shows how AI adapts its scan plan based on what it finds.

---

## 7. Run the FastAPI Web Service

Exposes the scanner as a REST API for programmatic access.

```bash
uvicorn src.api.main:app --reload --port 8000
```

**Endpoints:**

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/scan` | Start a scan (async) |
| `GET` | `/api/v1/scan/{id}` | Get scan results |
| `GET` | `/api/v1/scans` | List all scans |
| `POST` | `/api/v1/plan` | AI planning only (no scan) |
| `GET` | `/docs` | Swagger UI |

**Start a scan via API:**
```bash
# PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/scan" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"target_url": "http://localhost:5000", "use_ai_planning": false}'
```

**Get results:**
```bash
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/scan/YOUR-SCAN-ID"
```

Or visit `http://localhost:8000/docs` for the interactive Swagger UI.

---

## 8. Run Tests

```bash
# All tests
python -m pytest tests/ -v

# Helpers only
python test_helpers.py
```

---

## What's Implemented

| Component | Status | Requires Azure |
|-----------|--------|---------------|
| 9 OWASP API Security Top 10 tests | ✅ | No |
| CLI interactive scanner (`main.py`) | ✅ | No |
| HTML report generator | ✅ | No |
| PDF report generator | ✅ | No |
| Vulnerable test server | ✅ | No |
| AI Coordinator Agent | ✅ | **Yes** |
| FastAPI web service | ✅ | Optional |
| Azure OpenAI service wrapper | ✅ | **Yes** |

---

## Troubleshooting

**`ModuleNotFoundError`**
```bash
pip install -r requirements.txt
```

**`DeploymentNotFound` or `InsufficientQuota`**
- Check your deployment name in Azure AI Foundry
- Request quota increase at [ai.azure.com](https://ai.azure.com) → Management → Quota

**`Connection refused` on localhost:5000**
```bash
python test_api_server.py  # must be running in another terminal
```

**Virtual environment not active** — you'll see missing module errors
```bash
.\venv\Scripts\Activate   # Windows
source venv/bin/activate  # Linux/Mac
```
