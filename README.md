# 🛡️ API Security Tester

An interactive, intelligent API security scanner that automatically tests APIs for common vulnerabilities based on the OWASP API Security Top 10 and generates comprehensive security reports in multiple formats.

## Features

### 🎯 Comprehensive Security Testing
- **OWASP API Security Top 10 Coverage**
  - API1:2023 - Broken Object Level Authorization (BOLA)
  - API2:2023 - Broken Authentication
  - API3:2023 - Broken Object Property Level Authorization
  - API4:2023 - Unrestricted Resource Consumption
  - API5:2023 - Broken Function Level Authorization
  - API7:2023 - Server Side Request Forgery (SSRF)
  - API8:2023 - Security Misconfiguration
  - API9:2023 - Improper Inventory Management
  - API10:2023 - Injection Vulnerabilities (SQL, NoSQL)

### 🤖 Interactive Agent
- Guides you through the testing process
- Configurable scan parameters
- Custom header support (API keys, authentication tokens)
- Selective test execution
- Real-time progress feedback

### 📊 Multi-Format Reporting
- **JSON** - Structured data for integration with other tools
- **HTML** - Interactive, visual reports with charts
- **PDF** - Professional reports for stakeholders
- Severity-based color coding
- Detailed remediation recommendations

### 🔍 Smart Detection
- SQL Injection testing
- NoSQL Injection testing
- Authentication bypass attempts
- Authorization flaw detection
- SSRF vulnerability scanning
- Security header verification
- Rate limiting checks
- Mass assignment testing

## Installation

```bash
# Clone or download the project
cd api-security-tester

# Install dependencies
pip install -r requirements.txt --break-system-packages
```

## Quick Start

### Basic Usage

```bash
python3 main.py
```

The tool will guide you through:
1. **Target Configuration** - Enter your API URL
2. **Authentication** - Add custom headers (API keys, tokens)
3. **Test Selection** - Choose specific tests or run all
4. **Scan Execution** - Watch real-time progress
5. **Report Generation** - Export in your preferred format(s)

### Example Session

```
╔═══════════════════════════════════════════════════════╗
║       API Security Tester                             ║
║       OWASP API Security Top 10 Scanner               ║
╚═══════════════════════════════════════════════════════╝

Configure Your Security Scan

Enter target API URL: https://api.example.com

Add custom headers? (e.g., Authorization, API-Key)
Press Enter to skip, or enter in format 'Key: Value'
Header (or press Enter to continue): Authorization: Bearer token123
Header (or press Enter to continue): 

Select Tests to Run
Available test categories:

  1. [CRITICAL] API1:2023 - Broken Object Level Authorization
  2. [CRITICAL] API2:2023 - Broken Authentication
  3. [HIGH] API3:2023 - Broken Object Property Level Authorization
  4. [HIGH] API4:2023 - Unrestricted Resource Consumption
  5. [CRITICAL] API5:2023 - Broken Function Level Authorization
  6. [HIGH] API7:2023 - Server Side Request Forgery
  7. [HIGH] API8:2023 - Security Misconfiguration
  8. [MEDIUM] API9:2023 - Improper Inventory Management
  9. [CRITICAL] API10:2023 - Injection Vulnerabilities
  10. Run ALL tests (recommended)

Enter your choice (number or 'all'): all

Review Configuration
Target: https://api.example.com
Headers: 1 custom header(s)
Tests: 9 test(s)

Proceed with scan? (y/n): y
```

## Project Structure

```
api-security-tester/
├── main.py                      # Main application entry point
├── requirements.txt             # Python dependencies
├── core/
│   └── scanner.py              # Scanner engine and orchestration
├── tests/
│   └── vulnerability_tests.py  # OWASP test implementations
├── reports/
│   ├── html_generator.py       # HTML report generation
│   └── pdf_generator.py        # PDF report generation
└── README.md                    # This file
```

## Understanding the Results

### Severity Levels

- **CRITICAL** 🔴 - Immediate action required
  - Complete authentication bypass
  - SQL/NoSQL injection
  - Unauthorized admin access
  
- **HIGH** 🟠 - High priority remediation
  - Missing rate limiting
  - SSRF vulnerabilities
  - Property-level authorization issues
  
- **MEDIUM** 🟡 - Should be addressed
  - Security header misconfigurations
  - API version management issues
  
- **LOW** 🔵 - Minor improvements
  - Server version disclosure
  - Verbose error messages
  
- **INFO** ℹ️ - Informational findings
  - API documentation exposure
  - Multiple API versions detected

### Report Components

Each vulnerability report includes:
- **Description** - What the vulnerability is
- **Evidence** - Proof of the finding
- **URL & Method** - Affected endpoint
- **Recommendation** - How to fix it
- **Severity** - Risk level

## Advanced Usage

### Custom Test Configuration

You can modify test parameters by editing `tests/vulnerability_tests.py`:

```python
# Example: Adjust rate limiting test
class UnrestrictedResourceConsumptionTest(SecurityTest):
    def run(self, target_url: str, headers: Dict = None, **kwargs):
        # Change from 15 to 50 requests
        for i in range(50):
            # ... test logic
```

### Integration with CI/CD

Use the JSON output for automated security testing:

```bash
# Run scan and capture JSON output
python3 main.py --target https://api.example.com --format json --output report.json

# Parse results in your pipeline
python3 -c "
import json
with open('report.json') as f:
    report = json.load(f)
    critical = report['summary']['critical']
    if critical > 0:
        exit(1)  # Fail build
"
```

### Custom Headers Examples

```
# API Key Authentication
API-Key: your-api-key-here

# Bearer Token
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

# Basic Auth
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=

# Custom Headers
X-API-Version: v2
X-Request-ID: 12345
```

## Security Testing Best Practices

### ⚠️ Important Warnings

1. **Only test APIs you own or have explicit permission to test**
2. **Rate limiting tests may trigger DDoS protection**
3. **Some tests may modify data - use test environments**
4. **Review your organization's security testing policies first**

### Testing Workflow

1. **Staging First** - Always test in non-production environments
2. **Incremental** - Start with safe tests, gradually increase
3. **Document** - Keep records of what was tested and when
4. **Fix & Retest** - Remediate issues and verify fixes
5. **Regular Scans** - Schedule periodic security assessments

### Interpreting Results

- **False Positives** - Automated tools may flag non-issues
- **Manual Review** - Critical findings should be manually verified
- **Context Matters** - Some "vulnerabilities" may be intentional design
- **Layered Security** - One scan doesn't find everything

## Common Use Cases

### 1. Pre-Production Security Check
```bash
# Before deploying to production
python3 main.py
# Target: https://staging-api.example.com
# Export: All formats for stakeholder review
```

### 2. API Development Security Gate
```bash
# During development sprint
# Test specific vulnerability categories
# Select: Authentication & Authorization tests
```

### 3. Compliance Audit
```bash
# Generate comprehensive PDF reports
# Run all tests for complete coverage
# Include in compliance documentation
```

### 4. Security Research
```bash
# Study API security patterns
# Use JSON export for analysis
# Build custom tooling on top
```

## Extending the Tool

### Adding New Tests

Create a new test class in `tests/vulnerability_tests.py`:

```python
class CustomSecurityTest(SecurityTest):
    def __init__(self):
        super().__init__(
            "My Custom Test",
            "CUSTOM:2024",
            "HIGH"
        )
    
    def run(self, target_url: str, headers: Dict = None, **kwargs):
        results = []
        
        # Your test logic here
        
        return results
```

Register it in the `ALL_TESTS` list:

```python
ALL_TESTS = [
    # ... existing tests
    CustomSecurityTest,
]
```

### Adding New Report Formats

Create a new generator in `reports/`:

```python
# reports/markdown_generator.py
def generate_markdown_report(session_data: Dict, output_file: str):
    # Generate markdown report
    pass
```

## Troubleshooting

### Common Issues

**Connection Errors**
- Verify target URL is accessible
- Check if API requires VPN or specific network
- Test with curl first: `curl -I https://api.example.com`

**Authentication Failures**
- Verify header format is correct
- Check if token/key is valid
- Try the endpoint manually with Postman/curl

**No Vulnerabilities Found**
- This is good! But verify tests are running
- Check if API has aggressive rate limiting
- Some APIs may block automated tools

**SSL/TLS Errors**
- Some tests disable SSL verification for testing
- In production, always use valid certificates
- Check certificate validity with: `openssl s_client -connect api.example.com:443`

## Dependencies

- **requests** - HTTP client for API testing
- **rich** - Beautiful terminal output
- **reportlab** - PDF generation
- **jinja2** - HTML templating
- **pyyaml** - Configuration handling

## Limitations

This tool provides automated testing for common vulnerabilities but:
- Cannot detect all security issues
- May produce false positives
- Does not replace manual security audits
- Cannot test business logic flaws
- Limited to black-box testing approach

## Contributing

To improve the tool:
1. Add more OWASP test cases
2. Enhance existing tests with better detection
3. Add support for GraphQL APIs
4. Implement authentication scheme detection
5. Add more report formats

## License

This is a security testing tool for educational and authorized testing purposes only.

## Credits

Built with ❤️ for the security community.

Based on:
- OWASP API Security Top 10 (2023)
- Industry best practices
- Real-world penetration testing experience

---

**Remember: Only test APIs you own or have explicit permission to test!**
