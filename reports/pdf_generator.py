"""
PDF Report Generator - re-exported from root module
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from pdf_generator import generate_pdf_report

__all__ = ['generate_pdf_report']
