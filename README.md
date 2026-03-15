# Smart API Security Tester

An intelligent, agentic API security scanner built for the **Microsoft AI Dev Days Hackathon (2026)**.
Combines OWASP API Security Top 10 testing with AI-powered analysis using Azure OpenAI.

---

## What It Does

1. **Scans** any REST API for the OWASP API Security Top 10 (2023) vulnerabilities
2. **AI Planning** — an Azure OpenAI agent analyzes the target API first and creates a prioritized, reasoned test plan
3. **Reports** — exports findings as JSON, HTML (interactive), or PDF
4. **REST API** — exposes the scanner as a FastAPI service for CI/CD integration

---

## Quick Start

```bash
git clone https://github.com/ashley-aa511/Smart-API-security-tester.git
cd Smart-API-security-tester

python -m venv venv
.\venv\Scripts\Activate        # Windows
source venv/bin/activate       # macOS / Linux

pip install -r requirements.txt
python verify_setup.py         # check everything is installed
```

### Run the scanner (no Azure needed)

```bash
# Terminal 1 — start the vulnerable test target
python test_api_server.py

# Terminal 2 — run a full scan
python test_full_scan.py
```

### Run the interactive CLI

```bash
python main.py
# Enter target URL, optional headers, select tests, export report
```

---

## Multi-Agent Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User / REST API                      │
└───────────────────────┬─────────────────────────────────┘
                        │
            ┌───────────▼────────────┐
            │   Coordinator Agent    │  ← Azure OpenAI (GPT-4o-mini)
            │  Analyzes target API   │    Reasons about risk profile,
            │  Creates test plan     │    auth method, and domain
            └───────────┬────────────┘
                        │ prioritized plan
            ┌───────────▼────────────┐
            │    Security Scanner    │  ← core/scanner.py
            │  Executes OWASP tests  │    9 test categories
            └───────────┬────────────┘
                        │ results
            ┌───────────▼────────────┐
            │    Report Generator    │  ← JSON / HTML / PDF
            └────────────────────────┘
```

---

## OWASP Coverage

| # | Category | Severity | What It Tests |
|---|----------|----------|---------------|
| API1:2023 | Broken Object Level Authorization | CRITICAL | Accessing other users' data without ownership check |
| API2:2023 | Broken Authentication | CRITICAL | Admin endpoints without auth, weak passwords |
| API3:2023 | Excessive Data Exposure | HIGH | Responses leaking more fields than needed |
| API4:2023 | Unrestricted Resource Consumption | MEDIUM | Missing rate limiting |
| API5:2023 | Broken Function Level Authorization | HIGH | Admin functions accessible to regular users |
| API7:2023 | Server Side Request Forgery | HIGH | API fetching attacker-controlled URLs |
| API8:2023 | Security Misconfiguration | MEDIUM | Missing security headers, verbose errors |
| API9:2023 | Improper Inventory Management | MEDIUM | Exposed API docs, deprecated endpoints |
| API10:2023 | Injection | CRITICAL | SQL injection patterns in query parameters |

---

## Project Structure

```
Smart-API-security-tester/
├── main.py                          # Interactive CLI scanner
├── test_api_server.py               # Intentionally vulnerable Flask API (scan target)
├── test_full_scan.py                # Non-interactive end-to-end scan script
├── test_helpers.py                  # Utility function tests
├── test_integration.py              # AI + scanner integration test
├── verify_setup.py                  # Environment verification script
│
├── core/
│   └── scanner.py                   # SecurityScanner + ScanSession engine
│
├── src/
│   ├── agents/
│   │   └── coordinator_agent.py     # Azure OpenAI AI planning agent
│   ├── api/
│   │   └── main.py                  # FastAPI REST service
│   └── services/
│       └── azure_openai_service.py  # Shared Azure OpenAI wrapper
│
├── tests/
│   ├── vulnerability_tests.py       # All 9 OWASP test implementations
│   └── agents/
│       └── test_coordinator_agent.py # Unit tests (mocked Azure)
│
├── tests/test_scanner.py            # Unit tests for scanner engine
│
├── html_generator.py                # HTML report builder
├── pdf_generator.py                 # PDF report builder
└── reports/                         # Report package (re-exports generators)
```

---

## Azure OpenAI Setup

For the AI planning features:

1. Create an **Azure OpenAI** resource in [portal.azure.com](https://portal.azure.com)
2. Deploy **gpt-4o-mini** via [ai.azure.com](https://ai.azure.com) → Deployments
3. Copy your endpoint and key into `.env`:

```bash
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

4. Test the connection:
```bash
python src/agents/coordinator_agent.py
```

See **TESTING_GUIDE.md** for the full step-by-step setup walkthrough.

---

## Running Tests

```bash
# All unit tests — no Azure or server needed
python -m pytest tests/ -v     # 30 tests, all should pass
```

---

## FastAPI Web Service

```bash
uvicorn src.api.main:app --reload --port 8000
```

- Swagger UI: **http://localhost:8000/docs**
- Start a scan: `POST /api/v1/scan`
- Get results: `GET /api/v1/scan/{id}`
- AI plan only: `POST /api/v1/plan`

---

## Severity Levels

| Level | Examples |
|-------|---------|
| CRITICAL | Auth bypass, SQL injection, BOLA giving access to any user |
| HIGH | SSRF, function-level authorization bypass, data over-exposure |
| MEDIUM | Missing rate limiting, security header gaps, public API docs |
| LOW | Server version disclosure, verbose errors |
| INFO | API documentation found, informational notes |

---

## Report Formats

| Format | Contents |
|--------|---------|
| **JSON** | Full machine-readable results — use for CI/CD or further analysis |
| **HTML** | Visual report with charts, color-coded by severity, opens in browser |
| **PDF** | Professional printable report for stakeholders |

---

## Important

> Only test APIs you own or have explicit written permission to test.
> The test server (`test_api_server.py`) is safe — it is an intentionally
> vulnerable demo application designed for this purpose.

---

## Tech Stack

- **Python 3.11+**, Flask, FastAPI, Uvicorn
- **Azure OpenAI** (GPT-4o-mini) — AI planning agent
- **Rich** — terminal UI
- **ReportLab** — PDF generation
- **Jinja2** — HTML templating
- **pytest** — unit testing

Built for the **Microsoft AI Dev Days Hackathon — Agentic DevOps track**.
