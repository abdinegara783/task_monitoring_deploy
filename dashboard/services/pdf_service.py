from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.http import HttpResponse
from django.conf import settings
from datetime import datetime
import os

class PDFReportService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for the PDF"""
        # Company Header Style
        self.company_style = ParagraphStyle(
            'CompanyHeader',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Title Style
        self.title_style = ParagraphStyle(
            'ReportTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.black
        )
        
        # Subtitle Style
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
    
    def generate_activity_reports_pdf(self, reports, date_range=None):
        """Generate PDF for Activity Reports"""
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Activity_Reports_{datetime.now().strftime("%Y%m%d")}.pdf"'
        
        doc = SimpleDocTemplate(response, pagesize=A4, 
                              rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Add company header
        elements.extend(self._add_company_header())
        
        # Add report title
        title = "LAPORAN AKTIVITAS HARIAN"
        if date_range:
            title += f"<br/>Periode: {date_range}"
        elements.append(Paragraph(title, self.title_style))
        elements.append(Spacer(1, 12))
        
        # Add report info
        report_info = f"Tanggal Cetak: {datetime.now().strftime('%d %B %Y %H:%M')}<br/>Total Laporan: {len(reports)}"
        elements.append(Paragraph(report_info, self.subtitle_style))
        elements.append(Spacer(1, 20))
        
        # Create table data
        table_data = [
            ['No', 'Tanggal', 'Foreman', 'Shift', 'Unit Code', 'Komponen', 'Aktivitas', 'Status']
        ]
        
        for i, report in enumerate(reports, 1):
            table_data.append([
                str(i),
                report.date.strftime('%d/%m/%Y'),
                report.foreman.name or report.foreman.username,
                f"Shift {report.shift}",
                report.Unit_Code or '-',
                report.get_component_display() or '-',
                (report.activities[:30] + '...') if len(report.activities) > 30 else report.activities,
                report.get_status_display()
            ])
        
        # Create table
        table = Table(table_data, colWidths=[0.5*inch, 0.8*inch, 1.2*inch, 0.7*inch, 0.8*inch, 1*inch, 1.5*inch, 0.8*inch])
        
        # Style the table
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            
            # Body styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 30))
        
        # Add signature section
        elements.extend(self._add_signature_section())
        
        # Build PDF
        doc.build(elements)
        return response
    
    def generate_analysis_reports_pdf(self, reports, date_range=None):
        """Generate PDF for Analysis Reports"""
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Analysis_Reports_{datetime.now().strftime("%Y%m%d")}.pdf"'
        
        doc = SimpleDocTemplate(response, pagesize=A4, 
                              rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        elements = []
        
        # Add company header
        elements.extend(self._add_company_header())
        
        # Add report title
        title = "LAPORAN ANALISIS TEKNIS"
        if date_range:
            title += f"<br/>Periode: {date_range}"
        elements.append(Paragraph(title, self.title_style))
        elements.append(Spacer(1, 12))
        
        # Add report info
        report_info = f"Tanggal Cetak: {datetime.now().strftime('%d %B %Y %H:%M')}<br/>Total Laporan: {len(reports)}"
        elements.append(Paragraph(report_info, self.subtitle_style))
        elements.append(Spacer(1, 20))
        
        # Create table data
        table_data = [
            ['No', 'Tanggal', 'Foreman', 'Section', 'Unit Code', 'Problem', 'Part No', 'Status']
        ]
        
        for i, report in enumerate(reports, 1):
            table_data.append([
                str(i),
                report.report_date.strftime('%d/%m/%Y'),
                report.foreman.name or report.foreman.username,
                report.get_section_track_display() or '-',
                report.unit_code or '-',
                report.get_problem_display() or '-',
                report.part_no or '-',
                report.get_status_display()
            ])
        
        # Create table
        table = Table(table_data, colWidths=[0.5*inch, 0.8*inch, 1.2*inch, 0.8*inch, 0.8*inch, 1.2*inch, 0.8*inch, 0.8*inch])
        
        # Style the table
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            
            # Body styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 30))
        
        # Add signature section
        elements.extend(self._add_signature_section())
        
        # Build PDF
        doc.build(elements)
        return response
    
    def _add_company_header(self):
        """Add company header with logo"""
        elements = []
        
        # Company logo (if exists)
        logo_path = os.path.join(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0], 'img', 'logo.png')
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=2*inch, height=1*inch)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 12))
        
        # Company name
        company_name = "PT. MONITORING MANAGEMENT SYSTEM"
        elements.append(Paragraph(company_name, self.company_style))
        
        # Company address
        address = "Jl. Industri No. 123, Jakarta 12345<br/>Tel: (021) 1234-5678 | Email: info@monman.com"
        elements.append(Paragraph(address, self.subtitle_style))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_signature_section(self):
        """Add signature section"""
        elements = []
        
        # Signature table
        sig_data = [
            ['', 'Jakarta, ' + datetime.now().strftime('%d %B %Y')],
            ['Dibuat oleh:', 'Disetujui oleh:'],
            ['', ''],
            ['', ''],
            ['', ''],
            ['(_________________)', '(_________________)'],
            ['Admin System', 'Manager']
        ]
        
        sig_table = Table(sig_data, colWidths=[3*inch, 3*inch])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(sig_table)
        return elements