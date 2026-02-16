"""
API Security Scanner Engine
Orchestrates security tests and manages scan sessions
"""

import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from rich import box

sys.path.append('/home/claude/api-security-tester')
from tests.vulnerability_tests import ALL_TESTS


class ScanSession:
    """Represents a single security scan session"""
    
    def __init__(self, target_url: str, scan_id: str = None):
        self.target_url = target_url
        self.scan_id = scan_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = datetime.now()
        self.end_time = None
        self.results = []
        self.summary = {
            "total_tests": 0,
            "vulnerabilities_found": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
            "passed": 0
        }
    
    def add_results(self, test_results: List[Dict]):
        """Add test results to the session"""
        self.results.extend(test_results)
        self.summary["total_tests"] += len(test_results)
        
        for result in test_results:
            status = result.get("status", "").upper()
            severity = result.get("severity", "").upper()
            
            if status == "VULNERABLE":
                self.summary["vulnerabilities_found"] += 1
                
                if severity == "CRITICAL":
                    self.summary["critical"] += 1
                elif severity == "HIGH":
                    self.summary["high"] += 1
                elif severity == "MEDIUM":
                    self.summary["medium"] += 1
                elif severity == "LOW":
                    self.summary["low"] += 1
            elif status == "INFO":
                self.summary["info"] += 1
            elif status == "PASSED":
                self.summary["passed"] += 1
    
    def finalize(self):
        """Mark scan as complete"""
        self.end_time = datetime.now()
    
    def get_duration(self) -> str:
        """Get scan duration"""
        if self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
            return f"{duration:.2f}s"
        return "In progress"
    
    def to_dict(self) -> Dict:
        """Convert session to dictionary"""
        return {
            "scan_id": self.scan_id,
            "target_url": self.target_url,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.get_duration(),
            "summary": self.summary,
            "results": self.results
        }


class SecurityScanner:
    """Main security scanner engine"""
    
    def __init__(self):
        self.console = Console()
        self.test_classes = ALL_TESTS
        self.session: Optional[ScanSession] = None
    
    def print_banner(self):
        """Print scanner banner"""
        banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║       API Security Tester                             ║
    ║       OWASP API Security Top 10 Scanner               ║
    ╚═══════════════════════════════════════════════════════╝
        """
        self.console.print(banner, style="bold cyan")
    
    def get_scan_configuration(self) -> Dict[str, Any]:
        """Interactive configuration gathering"""
        self.console.print("\n[bold yellow]Configure Your Security Scan[/bold yellow]\n")
        
        # Get target URL
        target_url = self.console.input("[cyan]Enter target API URL:[/cyan] ").strip()
        
        if not target_url:
            self.console.print("[red]Error: Target URL is required[/red]")
            sys.exit(1)
        
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'https://' + target_url
        
        # Get headers
        self.console.print("\n[cyan]Add custom headers? (e.g., Authorization, API-Key)[/cyan]")
        self.console.print("[dim]Press Enter to skip, or enter in format 'Key: Value'[/dim]")
        
        headers = {}
        while True:
            header = self.console.input("[cyan]Header (or press Enter to continue):[/cyan] ").strip()
            if not header:
                break
            
            if ':' in header:
                key, value = header.split(':', 1)
                headers[key.strip()] = value.strip()
            else:
                self.console.print("[yellow]Invalid format. Use 'Key: Value'[/yellow]")
        
        # Test selection
        self.console.print("\n[bold yellow]Select Tests to Run[/bold yellow]")
        self.console.print("[dim]Available test categories:[/dim]\n")
        
        for idx, test_class in enumerate(self.test_classes, 1):
            test = test_class()
            self.console.print(f"  {idx}. [{test.severity}] {test.category} - {test.name}")
        
        self.console.print(f"  {len(self.test_classes) + 1}. Run ALL tests (recommended)")
        
        choice = self.console.input("\n[cyan]Enter your choice (number or 'all'):[/cyan] ").strip().lower()
        
        selected_tests = []
        if choice == 'all' or choice == str(len(self.test_classes) + 1):
            selected_tests = self.test_classes
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(self.test_classes):
                    selected_tests = [self.test_classes[idx]]
                else:
                    self.console.print("[red]Invalid choice. Running all tests.[/red]")
                    selected_tests = self.test_classes
            except ValueError:
                self.console.print("[red]Invalid input. Running all tests.[/red]")
                selected_tests = self.test_classes
        
        return {
            "target_url": target_url,
            "headers": headers,
            "selected_tests": selected_tests
        }
    
    def run_scan(self, config: Dict[str, Any]) -> ScanSession:
        """Execute the security scan"""
        target_url = config["target_url"]
        headers = config.get("headers", {})
        selected_tests = config.get("selected_tests", self.test_classes)
        
        # Create scan session
        self.session = ScanSession(target_url)
        
        self.console.print(f"\n[bold green]Starting Security Scan[/bold green]")
        self.console.print(f"Target: {target_url}")
        self.console.print(f"Scan ID: {self.session.scan_id}")
        self.console.print(f"Tests: {len(selected_tests)}\n")
        
        # Run tests with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            for test_class in selected_tests:
                test = test_class()
                task = progress.add_task(f"Running: {test.name}", total=None)
                
                try:
                    results = test.run(target_url, headers=headers)
                    self.session.add_results(results)
                    
                    # Show immediate feedback for vulnerabilities
                    vulnerable_count = sum(1 for r in results if r.get("status") == "VULNERABLE")
                    if vulnerable_count > 0:
                        progress.console.print(
                            f"  [red]⚠ Found {vulnerable_count} potential issue(s)[/red]"
                        )
                    else:
                        progress.console.print(f"  [green]✓ Passed[/green]")
                    
                except Exception as e:
                    self.console.print(f"  [red]✗ Error: {str(e)}[/red]")
                
                progress.remove_task(task)
        
        self.session.finalize()
        return self.session
    
    def display_results(self, session: ScanSession):
        """Display scan results in terminal"""
        self.console.print("\n" + "="*70)
        self.console.print("[bold cyan]SCAN RESULTS[/bold cyan]")
        self.console.print("="*70 + "\n")
        
        # Summary table
        summary_table = Table(title="Scan Summary", box=box.ROUNDED)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="white")
        
        summary_table.add_row("Scan ID", session.scan_id)
        summary_table.add_row("Target", session.target_url)
        summary_table.add_row("Duration", session.get_duration())
        summary_table.add_row("Total Tests", str(session.summary["total_tests"]))
        summary_table.add_row("Vulnerabilities Found", 
                            f"[red]{session.summary['vulnerabilities_found']}[/red]")
        
        self.console.print(summary_table)
        self.console.print()
        
        # Severity breakdown
        if session.summary["vulnerabilities_found"] > 0:
            severity_table = Table(title="Vulnerabilities by Severity", box=box.ROUNDED)
            severity_table.add_column("Severity", style="bold")
            severity_table.add_column("Count", justify="right")
            
            if session.summary["critical"] > 0:
                severity_table.add_row("[red]CRITICAL[/red]", 
                                     f"[red]{session.summary['critical']}[/red]")
            if session.summary["high"] > 0:
                severity_table.add_row("[orange1]HIGH[/orange1]", 
                                     f"[orange1]{session.summary['high']}[/orange1]")
            if session.summary["medium"] > 0:
                severity_table.add_row("[yellow]MEDIUM[/yellow]", 
                                     f"[yellow]{session.summary['medium']}[/yellow]")
            if session.summary["low"] > 0:
                severity_table.add_row("[blue]LOW[/blue]", 
                                     f"[blue]{session.summary['low']}[/blue]")
            
            self.console.print(severity_table)
            self.console.print()
        
        # Detailed findings
        vulnerabilities = [r for r in session.results if r.get("status") == "VULNERABLE"]
        
        if vulnerabilities:
            self.console.print("[bold red]DETAILED FINDINGS[/bold red]\n")
            
            for idx, vuln in enumerate(vulnerabilities, 1):
                severity_color = {
                    "CRITICAL": "red",
                    "HIGH": "orange1",
                    "MEDIUM": "yellow",
                    "LOW": "blue"
                }.get(vuln.get("severity", "MEDIUM"), "yellow")
                
                panel_content = f"""[bold]Test:[/bold] {vuln.get('test', 'Unknown')}
[bold]URL:[/bold] {vuln.get('url', 'N/A')}
[bold]Method:[/bold] {vuln.get('method', 'N/A')}
[bold]Description:[/bold] {vuln.get('description', 'N/A')}
[bold]Evidence:[/bold] {vuln.get('evidence', 'N/A')}
[bold]Recommendation:[/bold] {vuln.get('recommendation', 'N/A')}"""
                
                panel = Panel(
                    panel_content,
                    title=f"[{severity_color}]Finding #{idx} - {vuln.get('severity', 'MEDIUM')}[/{severity_color}]",
                    border_style=severity_color
                )
                self.console.print(panel)
                self.console.print()
        
        # Info findings
        info_items = [r for r in session.results if r.get("status") == "INFO"]
        if info_items:
            self.console.print("[bold blue]INFORMATIONAL FINDINGS[/bold blue]\n")
            for item in info_items:
                self.console.print(f"  • {item.get('description', 'N/A')}")
            self.console.print()
        
        # Passed tests
        passed = session.summary["passed"]
        if passed > 0:
            self.console.print(f"[green]✓ {passed} test(s) passed with no issues detected[/green]\n")
    
    def save_results(self, session: ScanSession, format: str = "json") -> str:
        """Save results to file"""
        filename = f"scan_{session.scan_id}.{format}"
        
        if format == "json":
            with open(filename, 'w') as f:
                json.dump(session.to_dict(), f, indent=2)
        
        return filename
    
    def interactive_scan(self):
        """Run interactive scan workflow"""
        self.print_banner()
        
        # Get configuration
        config = self.get_scan_configuration()
        
        # Confirm scan
        self.console.print("\n[bold yellow]Review Configuration[/bold yellow]")
        self.console.print(f"Target: {config['target_url']}")
        self.console.print(f"Headers: {len(config.get('headers', {}))} custom header(s)")
        self.console.print(f"Tests: {len(config['selected_tests'])} test(s)")
        
        confirm = self.console.input("\n[cyan]Proceed with scan? (y/n):[/cyan] ").strip().lower()
        
        if confirm != 'y':
            self.console.print("[yellow]Scan cancelled.[/yellow]")
            return
        
        # Run scan
        session = self.run_scan(config)
        
        # Display results
        self.display_results(session)
        
        # Export options
        self.console.print("\n[bold yellow]Export Results[/bold yellow]")
        self.console.print("1. JSON")
        self.console.print("2. HTML Report")
        self.console.print("3. PDF Report")
        self.console.print("4. All formats")
        self.console.print("5. Skip export")
        
        export_choice = self.console.input("\n[cyan]Select export option:[/cyan] ").strip()
        
        return session, export_choice


if __name__ == "__main__":
    scanner = SecurityScanner()
    scanner.interactive_scan()