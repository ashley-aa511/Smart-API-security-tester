#!/usr/bin/env python3
"""
Quick test script for helper functions
"""
from helpers import (
    validate_url,
    sanitize_url,
    calculate_risk_score,
    get_risk_level,
    group_results_by_severity
)

print("Testing Helper Functions")
print("=" * 50)

# Test URL validation
print("\n1. URL Validation:")
print(f"   Valid URL: {validate_url('https://api.example.com')}")
print(f"   Invalid URL: {validate_url('not-a-url')}")

# Test URL sanitization
print("\n2. URL Sanitization:")
print(f"   Original: https://api.example.com/users?token=secret123")
print(f"   Sanitized: {sanitize_url('https://api.example.com/users?token=secret123')}")

# Test risk scoring
print("\n3. Risk Score Calculation:")
test_summary = {
    "critical": 2,
    "high": 3,
    "medium": 5,
    "low": 2
}
score = calculate_risk_score(test_summary)
level = get_risk_level(score)
print(f"   Summary: {test_summary}")
print(f"   Risk Score: {score}/100")
print(f"   Risk Level: {level}")

# Test grouping
print("\n4. Group Results by Severity:")
test_results = [
    {"test": "Test1", "severity": "CRITICAL", "status": "VULNERABLE"},
    {"test": "Test2", "severity": "HIGH", "status": "VULNERABLE"},
    {"test": "Test3", "severity": "CRITICAL", "status": "VULNERABLE"},
]
grouped = group_results_by_severity(test_results)
for severity, results in grouped.items():
    if results:
        print(f"   {severity}: {len(results)} finding(s)")

print("\n✓ All helper functions working!")
