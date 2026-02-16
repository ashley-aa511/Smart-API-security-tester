"""
PDF Report Generator
Creates professional PDF security reports
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.pdfgen import canvas
from datetime import datetime
from typing import Dict, List
import os


class NumberedCanvas(canvas.Canvas):
    """Custom canvas for page numbers"""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
    
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
    
    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
    
    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.grey)
        self.drawRightString(
            7.5 * inch,
            0.5 * inch,
            f"Page {self._pageNumber} of {page_count}"
        )


def get_severity_color(severity: str):
    """Get color for severity level"""
    colors_map = {
        "CRITICAL": colors.red,
        "HIGH": colors.orange,
        "MEDIUM": colors.yellow,
        "LOW": colors.lightblue,
        "INFO": colors.lightgreen
    }
    return colors_map.get(severity, colors.grey)


def generate_pdf_report(session_data: Dict, output_file: str):
    """Generate a professional PDF report"""
    
    # Create document
    doc = SimpleDocTemplate(
        output_file,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=1*inch
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#764ba2'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        spaceAfter=10
    )
    
    # Title Page
    elements.append(Spacer(1, 2*inch))
    elements.append(Paragraph("🛡️ API Security Test Report", title_style))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("OWASP API Security Top 10 Assessment", 
                             ParagraphStyle('subtitle', parent=normal_style, 
                                          fontSize=14, alignment=TA_CENTER)))
    elements.append(Spacer(1, 1*inch))
    
    # Scan Information Table
    scan_info_data = [
        ['Scan ID:', session_data['scan_id']],
        ['Target URL:', session_data['target_url']],
        ['Scan Date:', session_data['start_time'].split('T')[0]],
        ['Duration:', session_data['duration']],
        ['Total Tests:', str(session_data['summary']['total_tests'])]
    ]
    
    scan_info_table = Table(scan_info_data, colWidths=[2*inch, 4*inch])
    scan_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    
    elements.append(scan_info_table)
    elements.append(PageBreak())
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    summary = session_data['summary']
    
    if summary['vulnerabilities_found'] > 0:
        summary_text = f"""
        This security assessment identified <b>{summary['vulnerabilities_found']}</b> potential 
        vulnerabilities in the target API. The findings include {summary['critical']} critical, 
        {summary['high']} high, {summary['medium']} medium, and {summary['low']} low severity issues.
        Immediate attention is recommended for critical and high severity vulnerabilities.
        """
    else:
        summary_text = """
        This security assessment did not identify any obvious vulnerabilities in the target API.
        All tests passed successfully. However, this does not guarantee the API is completely secure.
        Regular security assessments and code reviews are recommended.
        """
    
    elements.append(Paragraph(summary_text, normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Severity Summary Table
    severity_data = [
        ['Severity', 'Count', 'Status'],
        ['Critical', str(summary['critical']), '❌' if summary['critical'] > 0 else '✅'],
        ['High', str(summary['high']), '⚠️' if summary['high'] > 0 else '✅'],
        ['Medium', str(summary['medium']), '⚠️' if summary['medium'] > 0 else '✅'],
        ['Low', str(summary['low']), 'ℹ️' if summary['low'] > 0 else '✅'],
        ['Info', str(summary['info']), 'ℹ️'],
        ['Passed', str(summary['passed']), '✅']
    ]
    
    severity_table = Table(severity_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    severity_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ]))
    
    elements.append(severity_table)
    elements.append(PageBreak())
    
    # Detailed Findings
    vulnerabilities = [r for r in session_data['results'] if r.get('status') == 'VULNERABLE']
    
    if vulnerabilities:
        elements.append(Paragraph("Detailed Findings", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        for idx, vuln in enumerate(vulnerabilities, 1):
            # Create finding header
            severity = vuln.get('severity', 'MEDIUM')
            finding_title = f"Finding #{idx}: {vuln.get('test', 'Unknown Test')}"
            
            elements.append(Paragraph(finding_title, subheading_style))
            
            # Severity badge
            severity_para = Paragraph(
                f'<font color="{get_severity_color(severity).hexval()}"><b>[{severity}]</b></font>',
                normal_style
            )
            elements.append(severity_para)
            elements.append(Spacer(1, 0.1*inch))
            
            # Finding details
            details_data = [
                ['Description:', vuln.get('description', 'N/A')],
                ['URL:', vuln.get('url', 'N/A')],
                ['Method:', vuln.get('method', 'N/A')],
                ['Evidence:', vuln.get('evidence', 'N/A')],
            ]
            
            details_table = Table(details_data, colWidths=[1.5*inch, 5*inch])
            details_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            
            finding_elements = [details_table]
            
            # Recommendation box
            finding_elements.append(Spacer(1, 0.1*inch))
            recommendation_text = f"""
            <b>💡 Recommendation:</b><br/>
            {vuln.get('recommendation', 'No recommendation provided')}
            """
            recommendation_para = Paragraph(recommendation_text, normal_style)
            
            # Create recommendation box
            rec_data = [[recommendation_para]]
            rec_table = Table(rec_data, colWidths=[6.5*inch])
            rec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#d1ecf1')),
                ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#0dcaf0')),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ]))
            
            finding_elements.append(rec_table)
            finding_elements.append(Spacer(1, 0.3*inch))
            
            # Keep finding together on same page
            elements.append(KeepTogether(finding_elements))
    else:
        elements.append(Paragraph("No Vulnerabilities Detected", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(
            "All security tests passed successfully. No vulnerabilities were detected during this scan.",
            normal_style
        ))
    
    # Informational Findings
    info_items = [r for r in session_data['results'] if r.get('status') == 'INFO']
    if info_items:
        elements.append(PageBreak())
        elements.append(Paragraph("Informational Findings", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        for item in info_items:
            bullet = f"• {item.get('description', 'N/A')}"
            elements.append(Paragraph(bullet, normal_style))
            elements.append(Spacer(1, 0.05*inch))
    
    # Conclusion
    elements.append(PageBreak())
    elements.append(Paragraph("Conclusion", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    conclusion_text = f"""
    This report documents the findings of an automated API security assessment conducted on 
    {session_data['target_url']}. The assessment covered the OWASP API Security Top 10 
    vulnerabilities and identified {summary['vulnerabilities_found']} potential security issues.
    <br/><br/>
    It is recommended to:
    <br/>
    • Address all critical and high severity vulnerabilities immediately
    <br/>
    • Review and remediate medium and low severity issues
    <br/>
    • Implement secure coding practices
    <br/>
    • Conduct regular security assessments
    <br/>
    • Keep all dependencies and frameworks up to date
    <br/><br/>
    <i>Note: This is an automated scan and may not detect all security vulnerabilities. 
    Manual security testing and code review are recommended for comprehensive coverage.</i>
    """
    
    elements.append(Paragraph(conclusion_text, normal_style))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_text = f"""
    <i>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
    API Security Tester - OWASP API Security Top 10 Scanner</i>
    """
    footer_style = ParagraphStyle('footer', parent=normal_style, 
                                 fontSize=9, alignment=TA_CENTER, 
                                 textColor=colors.grey)
    elements.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(elements, canvasmaker=NumberedCanvas)
    
    return output_file