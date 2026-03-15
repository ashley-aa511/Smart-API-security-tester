#!/usr/bin/env python3
"""
Setup Verification Script
Checks if your environment is ready to run tests
"""
import os
import sys
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print("🔍 Checking Python version...")
    if version.major >= 3 and version.minor >= 11:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"   ⚠️  Python {version.major}.{version.minor}.{version.micro} (Recommended: 3.11+)")
        return True  # Still allow older versions

def check_dependencies():
    """Check if required packages are installed"""
    print("\n🔍 Checking dependencies...")

    required = {
        'requests': ('requests', 'HTTP client'),
        'rich': ('rich', 'Terminal formatting'),
        'flask': ('flask', 'Test server'),
        'openai': ('openai', 'Azure OpenAI client'),
        'python-dotenv': ('dotenv', 'Environment variables'),
        'jinja2': ('jinja2', 'HTML templates'),
        'reportlab': ('reportlab', 'PDF generation'),
    }

    missing = []
    for package, (import_name, description) in required.items():
        try:
            __import__(import_name)
            print(f"   ✅ {package:20} - {description}")
        except ImportError:
            print(f"   ❌ {package:20} - {description} (NOT INSTALLED)")
            missing.append(package)

    if missing:
        print(f"\n   ⚠️  Missing {len(missing)} package(s). Run: pip install -r requirements.txt")
        return False
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("\n🔍 Checking .env configuration...")

    env_path = Path('.env')
    if not env_path.exists():
        print("   ❌ .env file not found")
        return False

    print("   ✅ .env file exists")

    # Load .env
    from dotenv import load_dotenv
    load_dotenv()

    # Check required variables for AI agent
    azure_vars = {
        'AZURE_OPENAI_ENDPOINT': os.getenv('AZURE_OPENAI_ENDPOINT'),
        'AZURE_OPENAI_API_KEY': os.getenv('AZURE_OPENAI_API_KEY'),
        'AZURE_OPENAI_DEPLOYMENT_NAME': os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
        'AZURE_OPENAI_API_VERSION': os.getenv('AZURE_OPENAI_API_VERSION'),
    }

    has_azure = True
    for var, value in azure_vars.items():
        if not value or 'your-' in value.lower() or 'your_' in value.lower():
            print(f"   ⚠️  {var}: Not configured (placeholder detected)")
            has_azure = False
        else:
            # Mask sensitive values
            if 'KEY' in var:
                masked = value[:10] + '...' + value[-4:] if len(value) > 14 else '***'
                print(f"   ✅ {var}: {masked}")
            else:
                print(f"   ✅ {var}: {value}")

    if not has_azure:
        print("\n   ℹ️  Azure OpenAI not configured - AI features won't work")
        print("      You can still test: test_api_server.py and test_helpers.py")

    return has_azure

def check_file_structure():
    """Check if key files exist"""
    print("\n🔍 Checking file structure...")

    files = {
        'test_api_server.py': 'Test vulnerable API',
        'test_helpers.py': 'Helper function tests',
        'test_integration.py': 'Integration test',
        'src/agents/coordinator_agent.py': 'AI Coordinator Agent',
        'helpers.py': 'Utility functions',
        'html_generator.py': 'HTML report generator',
        'pdf_generator.py': 'PDF report generator',
    }

    all_exist = True
    for file, description in files.items():
        path = Path(file)
        if path.exists():
            print(f"   ✅ {file:40} - {description}")
        else:
            print(f"   ❌ {file:40} - {description} (MISSING)")
            all_exist = False

    return all_exist

def check_broken_components():
    """Check for known broken components"""
    print("\n🔍 Checking for broken components...")

    # Check if vulnerability_tests.py exists
    vuln_test_path = Path('tests/vulnerability_tests.py')
    if not vuln_test_path.exists():
        print("   ⚠️  tests/vulnerability_tests.py - MISSING (main.py won't work)")

    print("   ℹ️  main.py - Will fail (missing vulnerability tests)")
    print("   ℹ️  core/scanner.py - Will fail (imports missing file)")

def print_summary(deps_ok, env_ok, files_ok):
    """Print summary and recommendations"""
    print("\n" + "=" * 70)
    print("SETUP VERIFICATION SUMMARY")
    print("=" * 70)

    if deps_ok and files_ok:
        print("\n✅ BASIC SETUP: Complete")
        print("\nYou can run:")
        print("  • python test_helpers.py")
        print("  • python test_api_server.py")
    else:
        print("\n❌ BASIC SETUP: Incomplete")
        if not deps_ok:
            print("\n📌 ACTION REQUIRED:")
            print("   pip install -r requirements.txt")

    if env_ok:
        print("\n✅ AZURE AI SETUP: Complete")
        print("\nYou can run:")
        print("  • python src/agents/coordinator_agent.py")
        print("  • python test_integration.py (with test server running)")
    else:
        print("\n⚠️  AZURE AI SETUP: Not configured")
        print("\n📌 TO ENABLE AI FEATURES:")
        print("   1. Get Azure OpenAI credentials")
        print("   2. Update .env file with your credentials")
        print("   3. Run this script again to verify")

    print("\n" + "=" * 70)
    print("WHAT'S BROKEN:")
    print("=" * 70)
    print("\n❌ Cannot run: python main.py")
    print("   Reason: Missing tests/vulnerability_tests.py")
    print("\n❌ Cannot run: Full security scans")
    print("   Reason: No OWASP test implementations")

    print("\n" + "=" * 70)
    print("\n📚 For detailed testing instructions, see: TESTING_GUIDE.md")
    print()

def main():
    """Run all checks"""
    print("=" * 70)
    print("SMART API SECURITY TESTER - Setup Verification")
    print("=" * 70)

    python_ok = check_python_version()
    deps_ok = check_dependencies()
    env_ok = check_env_file()
    files_ok = check_file_structure()
    check_broken_components()

    print_summary(deps_ok, env_ok, files_ok)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nVerification cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Verification failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
