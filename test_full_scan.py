#!/usr/bin/env python3
"""
End-to-End Scanner Test
Runs all 9 OWASP tests against the local vulnerable test server.

Requirements:
  - test_api_server.py must be running: python test_api_server.py
  - No Azure credentials needed

Usage:
  python test_full_scan.py
"""
import sys
import json
import time
from pathlib import Path

# Project root on path
sys.path.insert(0, str(Path(__file__).parent))

import requests
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


# ─── Pre-flight check ────────────────────────────────────────────────────────

TARGET_URL = "http://localhost:5000"


def check_server_running() -> bool:
    """Verify the test server is reachable before scanning."""
    try:
        requests.get(TARGET_URL, timeout=3)
        return True
    except requests.RequestException:
        return False


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    console.print("\n[bold cyan]╔══════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║   End-to-End Full Scan Test          ║[/bold cyan]")
    console.print("[bold cyan]╚══════════════════════════════════════╝[/bold cyan]\n")

    # 1. Check server
    console.print("[cyan]Checking test server...[/cyan]")
    if not check_server_running():
        console.print("[bold red]✗ Test server not running![/bold red]")
        console.print("\nStart it first:")
        console.print("  [yellow]python test_api_server.py[/yellow]\n")
        sys.exit(1)
    console.print(f"[green]✓ Server reachable at {TARGET_URL}[/green]\n")

    # 2. Import scanner components
    try:
        from core.scanner import SecurityScanner, ScanSession
        from tests.vulnerability_tests import ALL_TESTS
    except ImportError as e:
        console.print(f"[red]Import error: {e}[/red]")
        console.print("Ensure you are running from the project root with venv active.")
        sys.exit(1)

    console.print(f"[green]✓ Loaded {len(ALL_TESTS)} OWASP test modules[/green]\n")

    # 3. Run scan (non-interactive)
    scanner = SecurityScanner()
    config = {
        "target_url": TARGET_URL,
        "headers": {},
        "selected_tests": ALL_TESTS,
    }

    console.print(f"[bold yellow]Starting scan against {TARGET_URL}...[/bold yellow]")
    console.print(f"Running {len(ALL_TESTS)} tests\n")

    start = time.time()
    session = scanner.run_scan(config)
    elapsed = time.time() - start

    # 4. Display results
    scanner.display_results(session)

    # 5. Summary table
    summary = session.summary
    table = Table(title="Final Summary", box=box.ROUNDED)
    table.add_column("Metric", style="cyan", min_width=28)
    table.add_column("Count", justify="right", style="white")

    table.add_row("Total tests run", str(summary["total_tests"]))
    table.add_row("Vulnerabilities found", f"[red]{summary['vulnerabilities_found']}[/red]")
    table.add_row("  CRITICAL", f"[red]{summary['critical']}[/red]")
    table.add_row("  HIGH", f"[orange1]{summary['high']}[/orange1]")
    table.add_row("  MEDIUM", f"[yellow]{summary['medium']}[/yellow]")
    table.add_row("  LOW", f"[blue]{summary['low']}[/blue]")
    table.add_row("Passed (no issues)", f"[green]{summary['passed']}[/green]")
    table.add_row("Informational", str(summary["info"]))
    table.add_row("Scan duration", f"{elapsed:.1f}s")

    console.print(table)

    # 6. Save JSON
    output_file = f"scan_{session.scan_id}.json"
    scanner.save_results(session, format="json")
    console.print(f"\n[green]✓ Results saved to: {output_file}[/green]")

    # 7. Outcome verdict
    if summary["vulnerabilities_found"] > 0:
        console.print(
            f"\n[bold red]✓ SCAN COMPLETE — {summary['vulnerabilities_found']} "
            f"vulnerabilit{'y' if summary['vulnerabilities_found'] == 1 else 'ies'} detected "
            f"(expected for the intentionally vulnerable test server)[/bold red]\n"
        )
    else:
        console.print("\n[bold green]✓ SCAN COMPLETE — No vulnerabilities detected[/bold green]\n")

    return session


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Scan cancelled.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
