# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Smart API Security Tester - An intelligent, agentic API security scanner built for the Microsoft AI Dev Days Hackathon (February-March 2026). This tool combines traditional OWASP API Security Top 10 testing with AI-powered vulnerability analysis using Azure OpenAI and the Microsoft Agent Framework.

**Key Technologies:**
- Python 3.11+, Azure OpenAI (GPT-4), FastAPI, Semantic Kernel, Azure Container Apps

## Development Commands

### Environment Setup
```bash
# Windows activation
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Interactive CLI scanner (legacy mode)
python main.py

# Run coordinator agent test
python src/agents/coordinator_agent.py

# Run test API server
python test_api_server.py
```

### Testing
```bash
# Run tests
python -m pytest tests/

# Run async tests
python -m pytest tests/ -v
```

### Code Quality
```bash
# Format with Black
black .

# Type checking (when implemented)
mypy src/
```

## Architecture

### Multi-Agent System

The project is transitioning from a traditional scanner to an intelligent multi-agent architecture:

1. **Coordinator Agent** (`src/agents/coordinator_agent.py`) - AI-powered scan planning
   - Analyzes target APIs to understand structure, auth methods, and risk profile
   - Uses Azure OpenAI to intelligently prioritize OWASP tests based on API characteristics
   - Creates execution plans with specific parameters tailored to the target
   - Entry point: `plan_scan(target_url, headers)` → returns comprehensive scan plan

2. **Scanner Agent** (`core/scanner.py`) - Executes security tests
   - Orchestrates test execution using the `SecurityScanner` class
   - Manages `ScanSession` objects that track results, timing, and vulnerabilities
   - Runs tests from the vulnerability test suite
   - Provides interactive CLI workflow via `interactive_scan()`

3. **Report Generators** (root directory modules)
   - `html_generator.py` - Creates interactive HTML reports with charts
   - `pdf_generator.py` - Generates professional PDF reports
   - Both consume `ScanSession.to_dict()` output

**Future agents (in development):**
- Analysis Agent - AI-powered vulnerability assessment and false positive filtering
- Remediation Agent - Code fix generation
- Report Agent - Enhanced AI-driven reporting

### Key Architectural Patterns

**Agent Communication:** Agents are designed to work both standalone and as part of orchestrated workflows. The Coordinator Agent produces structured JSON plans that the Scanner Agent consumes.

**Azure OpenAI Integration:** All agents use consistent patterns:
- Initialize with `AzureOpenAI` client from environment variables
- Use `response_format={"type": "json_object"}` for structured outputs
- Temperature 0.2-0.4 for analysis tasks, 0.6-0.8 for creative tasks
- Wrap all AI calls in try-except with retry logic

**Test Execution:** The scanner imports `ALL_TESTS` from `tests/vulnerability_tests.py` (note: this file may not exist yet in the new structure). Tests implement a common interface with `run(target_url, headers)` method.

**Session Management:** `ScanSession` objects track scan lifecycle, aggregate results by severity, and provide serialization via `to_dict()`.

## Important Files & Locations

- **Environment Config:** `.env` - Azure OpenAI credentials (never commit)
- **Entry Points:** `main.py` (CLI), `src/agents/coordinator_agent.py` (agent test)
- **Legacy Scanner:** `core/scanner.py` - Original non-AI scanner implementation
- **Agent Rules:** `.cursorrules` - Comprehensive project guidelines and patterns
- **Test Server:** `test_api_server.py` - Demo vulnerable API for testing

## Environment Variables Required

```bash
# Azure OpenAI (required for agents)
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Azure Storage (future use for reports)
AZURE_STORAGE_CONNECTION_STRING=...

# Application Settings
ENVIRONMENT=development
```

## Code Style Conventions

**Agent Structure:** All agents follow a template pattern (see `.cursorrules` lines 66-115):
- Constructor initializes Azure OpenAI client from environment
- Async methods for main capabilities
- Google-style docstrings with Args, Returns, Raises
- Proper error handling with logging

**Naming:**
- Classes: `PascalCase` (e.g., `CoordinatorAgent`)
- Functions: `snake_case` (e.g., `plan_scan`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- Agent files: suffix `_agent.py`

**Security Testing:**
- Non-destructive tests when possible (read-only preferred)
- Include rate limiting to avoid DDoS-like behavior
- Return structured results with evidence and remediation
- Severity: CRITICAL (auth bypass, injection) > HIGH (authz, SSRF) > MEDIUM (misconfig) > LOW (info disclosure) > INFO

## Git Workflow

**Branch Strategy:**
- `main` - Production-ready
- `dev` - Integration branch (create PRs here, not main)
- `staging` - Pre-production testing
- `feature/*` - New features (current: `feature/agent-framework-setup`)
- `fix/*` - Bug fixes

**Commit Convention:**
```bash
feat: implement analysis agent with vulnerability assessment
fix: correct Azure OpenAI API version handling
docs: update coordinator agent documentation
test: add integration tests for agent communication
refactor: streamline scan session management
chore: update dependencies for Semantic Kernel
```

**PR Guidelines:** Always create PRs to `dev` branch, include description of changes, reference issues, add testing notes.

## Hackathon Requirements

**Must demonstrate:**
- ✅ Azure OpenAI integration (Coordinator Agent)
- ✅ Microsoft Agent Framework usage (in progress)
- ⏳ Azure deployment (Container Apps)
- ⏳ GitHub Copilot usage
- ⏳ Azure MCP for agent communication
- ✅ Public GitHub repository

**Judging Focus Areas (20% each):**
1. Technological Implementation - Clean code, effective Microsoft tool usage
2. Agentic Design - Multi-agent orchestration sophistication
3. Real-World Impact - Solves actual API security problems
4. User Experience - Clear demo, intuitive interface
5. Category Adherence - "Agentic DevOps" track

## Common Patterns & Anti-Patterns

**DO:**
- Use `async/await` for all agent operations and I/O
- Load environment variables with `python-dotenv`
- Use `rich` for terminal output formatting
- Implement proper error handling with specific exceptions
- Test agents in isolation before integration
- Use `asyncio.gather()` for parallel operations

**DON'T:**
- Commit credentials or API keys
- Use synchronous code for I/O-bound operations
- Skip rate limiting in security tests
- Test APIs without explicit permission
- Use `--no-verify` or force push to main/master
- Add backwards-compatibility hacks for hackathon project

## Testing Security Scanner

When testing the scanner:
1. Always use test/staging environments, never production
2. The `test_api_server.py` provides a safe vulnerable API for testing
3. Review scan results manually - automated tools produce false positives
4. Rate limiting tests may trigger DDoS protection
5. Only test APIs you own or have explicit permission to test

## Known Issues & TODOs

- `vulnerability_tests.py` referenced in `scanner.py` but file location needs verification
- `src/api/` and `src/services/` directories are empty placeholders
- Scanner uses hardcoded path: `/home/claude/api-security-tester` (line 16 of scanner.py)
- Missing integration between Coordinator Agent and Scanner Agent
- Azure MCP integration not yet implemented
- Semantic Kernel integration incomplete

## Debugging Tips

**Azure OpenAI Issues:**
- Check `.env` has all required variables
- Verify API version matches deployment
- Check deployment name exists in Azure portal
- Monitor token usage for cost optimization

**Agent Issues:**
- Test agents standalone with `python src/agents/coordinator_agent.py`
- Check JSON response parsing - add error handling for malformed AI responses
- Use lower temperature (0.2-0.3) if agent outputs are inconsistent

**Scanner Issues:**
- Verify target URL is accessible (test with curl first)
- Check if API requires VPN or specific network
- Review headers format for authentication
- Use `rich` console for debugging output
