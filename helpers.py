"""
Utility functions for API security tester
"""

from typing import Dict, List, Any
from urllib.parse import urlparse
import re


def validate_url(url: str) -> bool:
    """Validate if a string is a valid URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def sanitize_url(url: str) -> str:
    """Sanitize URL for safe display"""
    parsed = urlparse(url)
    # Remove query parameters that might contain sensitive data
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


def extract_base_url(url: str) -> str:
    """Extract base URL from full URL"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def is_internal_ip(ip: str) -> bool:
    """Check if IP is internal/private"""
    internal_patterns = [
        r'^127\.',
        r'^10\.',
        r'^172\.(1[6-9]|2[0-9]|3[01])\.',
        r'^192\.168\.',
        r'^localhost$',
        r'^::1$'
    ]
    
    return any(re.match(pattern, ip) for pattern in internal_patterns)


def format_severity(severity: str) -> str:
    """Format severity with color codes"""
    colors = {
        "CRITICAL": "\033[91m",  # Red
        "HIGH": "\033[93m",      # Yellow
        "MEDIUM": "\033[94m",    # Blue
        "LOW": "\033[92m",       # Green
        "INFO": "\033[96m"       # Cyan
    }
    reset = "\033[0m"
    
    color = colors.get(severity, "")
    return f"{color}{severity}{reset}"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def group_results_by_severity(results: List[Dict]) -> Dict[str, List[Dict]]:
    """Group vulnerability results by severity"""
    grouped = {
        "CRITICAL": [],
        "HIGH": [],
        "MEDIUM": [],
        "LOW": [],
        "INFO": []
    }
    
    for result in results:
        severity = result.get("severity", "INFO")
        if severity in grouped:
            grouped[severity].append(result)
    
    return grouped


def calculate_risk_score(summary: Dict) -> int:
    """Calculate overall risk score (0-100)"""
    weights = {
        "critical": 25,
        "high": 15,
        "medium": 8,
        "low": 3
    }
    
    score = 0
    score += summary.get("critical", 0) * weights["critical"]
    score += summary.get("high", 0) * weights["high"]
    score += summary.get("medium", 0) * weights["medium"]
    score += summary.get("low", 0) * weights["low"]
    
    return min(score, 100)  # Cap at 100


def get_risk_level(score: int) -> str:
    """Get risk level from score"""
    if score >= 75:
        return "CRITICAL"
    elif score >= 50:
        return "HIGH"
    elif score >= 25:
        return "MEDIUM"
    else:
        return "LOW"