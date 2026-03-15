# Testing Guide - What Works Right Now

This guide shows you how to test the **working components** of the Smart API Security Tester.

## Quick Start

### 1. Setup Environment

```bash
# Activate virtual environment (Windows)
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Azure OpenAI

Edit `.env` file with your actual Azure credentials:

```bash
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com/
AZURE_OPENAI_API_KEY=YOUR-ACTUAL-KEY
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

**Don't have Azure OpenAI?** You can still test the vulnerable API server (Step 3).

---

## What You Can Test

### ✅ Test 1: Helper Functions (No Azure Required)

Tests utility functions for URL validation, risk scoring, etc.

```bash
python test_helpers.py
```

**Expected Output:**
```
Testing Helper Functions
==================================================

1. URL Validation:
   Valid URL: True
   Invalid URL: False

2. URL Sanitization:
   Original: https://api.example.com/users?token=secret123
   Sanitized: https://api.example.com/users

3. Risk Score Calculation:
   Summary: {'critical': 2, 'high': 3, 'medium': 5, 'low': 2}
   Risk Score: 99/100
   Risk Level: CRITICAL

4. Group Results by Severity:
   CRITICAL: 2 finding(s)
   HIGH: 1 finding(s)

✓ All helper functions working!
```

---

### ✅ Test 2: Vulnerable Test Server (No Azure Required)

Starts a Flask server with intentional security vulnerabilities.

**Terminal 1 - Start server:**
```bash
python test_api_server.py
```

**Terminal 2 - Test endpoints:**
```bash
# Test BOLA (Broken Object Level Authorization)
curl http://localhost:5000/api/user/1
curl http://localhost:5000/api/user/admin

# Test unprotected admin endpoint
curl http://localhost:5000/api/admin

# Test weak password authentication
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"password\"}"

# Test SQL injection
curl "http://localhost:5000/api/search?q=test' OR '1'='1"

# Test mass assignment
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Hacker\",\"role\":\"admin\",\"balance\":999999}"

# View API documentation
curl http://localhost:5000/api-docs
```

**What to expect:** You'll see responses demonstrating various vulnerabilities.

---

### ✅ Test 3: AI Coordinator Agent (Requires Azure)

Tests the intelligent scan planning agent using Azure OpenAI.

```bash
python src/agents/coordinator_agent.py
```

**Expected Output:**
```
🤖 Coordinator Agent: Analyzing target API...
✓ Analysis complete: [API Type] API
  Data Sensitivity: [Level]
  Auth Method: Bearer Token

🤖 Coordinator Agent: Creating scan plan...
✓ Plan created: X tests prioritized
  Estimated duration: Y minutes

============================================================
SCAN PLAN RESULTS
============================================================
{
  "api_analysis": {
    "api_type": "REST",
    "auth_method": "Bearer Token",
    "data_sensitivity": "High",
    ...
  },
  "scan_plan": {
    "priority_tests": [...],
    "recommended_order": [...],
    ...
  }
}
```

---

### ✅ Test 4: Integration Test (Requires Both)

Demonstrates AI agent analyzing the vulnerable test server.

**Prerequisites:**
1. Test server running: `python test_api_server.py` (Terminal 1)
2. Azure credentials configured in `.env`

**Run test (Terminal 2):**
```bash
python test_integration.py
```

**What it does:**
- AI agent analyzes the test server endpoints
- Identifies API type, authentication methods, risk areas
- Creates intelligent scan plans for different scenarios
- Shows how AI prioritizes tests based on vulnerability likelihood

**Expected Output:**
```
======================================================================
INTEGRATION TEST: AI Coordinator + Vulnerable Test Server
======================================================================

SCENARIO 1: Anonymous User Access
======================================================================
Target: http://localhost:5000/api/user/1
Headers: None

🤖 Coordinator Agent: Analyzing target API...
✓ Analysis complete: REST API
  Data Sensitivity: Medium
  Auth Method: None

----------------------------------------------------------------------
AI ANALYSIS RESULTS:
----------------------------------------------------------------------

API Type: REST
Auth Method: None
Data Sensitivity: Medium
Domain: User Management
Key Risk Areas:
  • authentication
  • authorization
  • data_exposure

Reasoning: Endpoint allows unauthenticated access to user data...

----------------------------------------------------------------------
RECOMMENDED SCAN PLAN:
----------------------------------------------------------------------

Priority Tests (5):
  [CRITICAL] Broken Object Level Authorization
  Reason: No authentication detected, high BOLA risk

  [CRITICAL] Broken Authentication
  Reason: Unauthenticated endpoint accessing sensitive data

...
```

---

## What Does NOT Work (Yet)

❌ **Main CLI Scanner** - `python main.py` will fail
- Missing `tests/vulnerability_tests.py` file
- No OWASP test implementations exist

❌ **Actual Security Scanning** - Cannot run real vulnerability tests
- Only AI planning works, not execution

❌ **Report Generation** - No scan data to generate reports from

---

## Troubleshooting

### Import Errors

```
ModuleNotFoundError: No module named 'rich'
```

**Fix:** Install dependencies
```bash
pip install -r requirements.txt
```

### Azure OpenAI Errors

```
openai.AuthenticationError: Incorrect API key provided
```

**Fix:** Update `.env` with valid Azure credentials

### Test Server Not Running

```
Failed to connect to localhost:5000
```

**Fix:** Start test server in another terminal
```bash
python test_api_server.py
```

### Environment Not Activated

```
python: command not found (or wrong Python version)
```

**Fix:** Activate virtual environment
```bash
.\venv\Scripts\Activate  # Windows
source venv/bin/activate  # Linux/Mac
```

---

## Summary of Working Components

| Component | Status | Requires Azure | Command |
|-----------|--------|---------------|---------|
| Helper Functions | ✅ Working | No | `python test_helpers.py` |
| Test API Server | ✅ Working | No | `python test_api_server.py` |
| AI Coordinator Agent | ✅ Working | Yes | `python src/agents/coordinator_agent.py` |
| Integration Demo | ✅ Working | Yes | `python test_integration.py` |
| Main Scanner | ❌ Broken | - | `python main.py` (fails) |
| Vulnerability Tests | ❌ Missing | - | Not implemented |

---

## Next Steps for Development

To make the full scanner work, you need to:

1. **Create vulnerability test implementations** (`tests/vulnerability_tests.py`)
2. **Integrate Coordinator Agent with Scanner** (connect AI planning to test execution)
3. **Add Scanner Agent** (executes tests from AI-generated plans)
4. **Connect report generators** (use actual scan results)

For now, the **integration test** (`test_integration.py`) shows the best demonstration of working AI-powered capabilities.
