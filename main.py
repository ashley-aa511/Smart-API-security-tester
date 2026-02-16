#!/usr/bin/env python3
"""
API Security Tester - Main Application
Interactive API security scanner with comprehensive reporting
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.scanner import SecurityScanner
from reports.html_generator import generate_html_report
from reports.pdf_generator import generate_pdf_report
from rich.console import Console
import json


def main():
    """Main application entry point"""
    console = Console()
    scanner = SecurityScanner()
    
    try:
        # Run interactive scan
        result = scanner.interactive_scan()
        
        if result is None:
            return
        
        session, export_choice = result
        
        # Handle export
        if export_choice == '5':
            console.print("\n[green]Scan completed. Results not exported.[/green]")
            return
        
        output_dir = Path.cwd()
        base_filename = f"security_report_{session.scan_id}"
        
        console.print("\n[bold cyan]Generating reports...[/bold cyan]")
        
        exported_files = []
        
        # Export based on choice
        if export_choice in ['1', '4']:
            # JSON export
            json_file = output_dir / f"{base_filename}.json"
            with open(json_file, 'w') as f:
                json.dump(session.to_dict(), f, indent=2)
            exported_files.append(str(json_file))
            console.print(f"[green]✓ JSON report saved: {json_file.name}[/green]")
        
        if export_choice in ['2', '4']:
            # HTML export
            html_file = output_dir / f"{base_filename}.html"
            generate_html_report(session.to_dict(), str(html_file))
            exported_files.append(str(html_file))
            console.print(f"[green]✓ HTML report saved: {html_file.name}[/green]")
        
        if export_choice in ['3', '4']:
            # PDF export
            pdf_file = output_dir / f"{base_filename}.pdf"
            generate_pdf_report(session.to_dict(), str(pdf_file))
            exported_files.append(str(pdf_file))
            console.print(f"[green]✓ PDF report saved: {pdf_file.name}[/green]")
        
        console.print("\n[bold green]✓ Scan completed successfully![/bold green]")
        
        if exported_files:
            console.print("\n[bold]Exported files:[/bold]")
            for file in exported_files:
                console.print(f"  • {file}")
        
        # Summary
        if session.summary['vulnerabilities_found'] > 0:
            console.print(f"\n[bold red]⚠ Action Required: {session.summary['vulnerabilities_found']} vulnerabilities found[/bold red]")
            console.print("[yellow]Review the reports and address critical/high severity issues immediately.[/yellow]")
        else:
            console.print("\n[bold green]✓ No vulnerabilities detected in this scan[/bold green]")
            console.print("[dim]Note: Automated scans may not detect all security issues.[/dim]")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Scan interrupted by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()