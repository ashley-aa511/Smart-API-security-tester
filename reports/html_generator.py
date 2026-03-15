"""
HTML Report Generator - re-exported from root module
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from html_generator import generate_html_report

__all__ = ['generate_html_report']
