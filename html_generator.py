"""
HTML Report Generator
Creates interactive HTML security reports
"""

from datetime import datetime
from typing import Dict
import json


def generate_html_report(session_data: Dict, output_file: str):
    """Generate an interactive HTML report"""
    
    summary = session_data["summary"]
    results = session_data["results"]
    
    vulnerabilities = [r for r in results if r.get("status") == "VULNERABLE"]
    info_items = [r for r in results if r.get("status") == "INFO"]
    
    # Calculate severity color
    def get_severity_color(severity):
        colors = {
            "CRITICAL": "#dc3545",
            "HIGH": "#fd7e14",
            "MEDIUM": "#ffc107",
            "LOW": "#0dcaf0",
            "INFO": "#0d6efd"
        }
        return colors.get(severity, "#6c757d")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Security Test Report - {session_data['scan_id']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .summary-card {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .summary-card h3 {{
            color: #6c757d;
            font-size: 0.9em;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}
        
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #212529;
        }}
        
        .severity-badges {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 40px;
        }}
        
        .badge {{
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
            color: white;
        }}
        
        .badge.critical {{ background: #dc3545; }}
        .badge.high {{ background: #fd7e14; }}
        .badge.medium {{ background: #ffc107; color: #000; }}
        .badge.low {{ background: #0dcaf0; }}
        .badge.info {{ background: #0d6efd; }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #212529;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .vulnerability-card {{
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 20px;
            border-left: 4px solid;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .vulnerability-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .vuln-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .vuln-title {{
            font-size: 1.3em;
            font-weight: 600;
            color: #212529;
        }}
        
        .vuln-detail {{
            margin: 10px 0;
        }}
        
        .vuln-detail strong {{
            color: #495057;
            display: inline-block;
            width: 150px;
        }}
        
        .code {{
            background: #f8f9fa;
            padding: 12px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #212529;
            overflow-x: auto;
            margin: 10px 0;
        }}
        
        .recommendation {{
            background: #d1ecf1;
            border-left: 4px solid #0dcaf0;
            padding: 15px;
            border-radius: 4px;
            margin-top: 15px;
        }}
        
        .recommendation strong {{
            color: #055160;
        }}
        
        .info-list {{
            list-style: none;
        }}
        
        .info-list li {{
            padding: 12px;
            background: #f8f9fa;
            margin-bottom: 10px;
            border-radius: 4px;
            border-left: 3px solid #0d6efd;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
        }}
        
        .chart-container {{
            margin: 30px 0;
            text-align: center;
        }}
        
        .severity-bar {{
            display: flex;
            height: 40px;
            border-radius: 8px;
            overflow: hidden;
            margin: 20px 0;
        }}
        
        .severity-segment {{
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            transition: all 0.3s;
        }}
        
        .severity-segment:hover {{
            opacity: 0.8;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
            }}
            .vulnerability-card {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ API Security Test Report</h1>
            <p>Comprehensive OWASP API Security Assessment</p>
        </div>
        
        <div class="content">
            <!-- Summary Section -->
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>Scan ID</h3>
                    <div class="value" style="font-size: 1.2em;">{session_data['scan_id']}</div>
                </div>
                <div class="summary-card">
                    <h3>Target URL</h3>
                    <div class="value" style="font-size: 1em; word-break: break-all;">{session_data['target_url']}</div>
                </div>
                <div class="summary-card">
                    <h3>Total Tests</h3>
                    <div class="value">{summary['total_tests']}</div>
                </div>
                <div class="summary-card">
                    <h3>Vulnerabilities</h3>
                    <div class="value" style="color: #dc3545;">{summary['vulnerabilities_found']}</div>
                </div>
                <div class="summary-card">
                    <h3>Duration</h3>
                    <div class="value" style="font-size: 1.5em;">{session_data['duration']}</div>
                </div>
                <div class="summary-card">
                    <h3>Tests Passed</h3>
                    <div class="value" style="color: #198754;">{summary['passed']}</div>
                </div>
            </div>
            
            <!-- Severity Distribution -->
            <div class="section">
                <h2>Severity Distribution</h2>
                <div class="severity-badges">
                    <div class="badge critical">CRITICAL: {summary['critical']}</div>
                    <div class="badge high">HIGH: {summary['high']}</div>
                    <div class="badge medium">MEDIUM: {summary['medium']}</div>
                    <div class="badge low">LOW: {summary['low']}</div>
                    <div class="badge info">INFO: {summary['info']}</div>
                </div>
"""
    
    # Add severity bar if there are vulnerabilities
    if summary['vulnerabilities_found'] > 0:
        total = summary['vulnerabilities_found']
        critical_pct = (summary['critical'] / total) * 100
        high_pct = (summary['high'] / total) * 100
        medium_pct = (summary['medium'] / total) * 100
        low_pct = (summary['low'] / total) * 100
        
        html_content += f"""
                <div class="severity-bar">
"""
        if summary['critical'] > 0:
            html_content += f"""
                    <div class="severity-segment" style="width: {critical_pct}%; background: #dc3545;">
                        {summary['critical']}
                    </div>
"""
        if summary['high'] > 0:
            html_content += f"""
                    <div class="severity-segment" style="width: {high_pct}%; background: #fd7e14;">
                        {summary['high']}
                    </div>
"""
        if summary['medium'] > 0:
            html_content += f"""
                    <div class="severity-segment" style="width: {medium_pct}%; background: #ffc107; color: #000;">
                        {summary['medium']}
                    </div>
"""
        if summary['low'] > 0:
            html_content += f"""
                    <div class="severity-segment" style="width: {low_pct}%; background: #0dcaf0;">
                        {summary['low']}
                    </div>
"""
        html_content += """
                </div>
"""
    
    html_content += """
            </div>
"""
    
    # Vulnerabilities section
    if vulnerabilities:
        html_content += """
            <div class="section">
                <h2>🚨 Vulnerabilities Detected</h2>
"""
        
        for idx, vuln in enumerate(vulnerabilities, 1):
            severity = vuln.get('severity', 'MEDIUM')
            color = get_severity_color(severity)
            
            html_content += f"""
                <div class="vulnerability-card" style="border-left-color: {color};">
                    <div class="vuln-header">
                        <div class="vuln-title">Finding #{idx}: {vuln.get('test', 'Unknown Test')}</div>
                        <div class="badge {severity.lower()}">{severity}</div>
                    </div>
                    
                    <div class="vuln-detail">
                        <strong>Category:</strong> OWASP API Security
                    </div>
                    
                    <div class="vuln-detail">
                        <strong>Description:</strong> {vuln.get('description', 'N/A')}
                    </div>
                    
                    <div class="vuln-detail">
                        <strong>URL:</strong>
                        <div class="code">{vuln.get('url', 'N/A')}</div>
                    </div>
                    
                    <div class="vuln-detail">
                        <strong>Method:</strong> {vuln.get('method', 'N/A')}
                    </div>
                    
                    <div class="vuln-detail">
                        <strong>Evidence:</strong>
                        <div class="code">{vuln.get('evidence', 'N/A')}</div>
                    </div>
                    
                    <div class="recommendation">
                        <strong>💡 Recommendation:</strong><br>
                        {vuln.get('recommendation', 'No recommendation provided')}
                    </div>
                </div>
"""
        
        html_content += """
            </div>
"""
    
    # Informational findings
    if info_items:
        html_content += """
            <div class="section">
                <h2>ℹ️ Informational Findings</h2>
                <ul class="info-list">
"""
        for item in info_items:
            html_content += f"""
                    <li>{item.get('description', 'N/A')}</li>
"""
        
        html_content += """
                </ul>
            </div>
"""
    
    # No vulnerabilities message
    if not vulnerabilities:
        html_content += """
            <div class="section">
                <div style="text-align: center; padding: 40px; background: #d1e7dd; border-radius: 8px;">
                    <h2 style="color: #0f5132; border: none;">✅ No Vulnerabilities Detected</h2>
                    <p style="color: #0f5132; margin-top: 10px;">All security tests passed successfully!</p>
                </div>
            </div>
"""
    
    html_content += f"""
        </div>
        
        <div class="footer">
            <p>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>API Security Tester - OWASP API Security Top 10 Scanner</p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_file