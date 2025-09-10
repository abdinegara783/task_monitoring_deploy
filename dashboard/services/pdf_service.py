from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.http import HttpResponse
from django.conf import settings
from datetime import datetime, timedelta
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
            fontSize=14,
            spaceAfter=5,
            alignment=TA_CENTER,
            textColor=colors.black
        )
        
        # Title Style
        self.title_style = ParagraphStyle(
            'ReportTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            alignment=TA_CENTER,
            textColor=colors.white,
            backColor=colors.darkblue
        )
        
        # Subtitle Style
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=10,
            alignment=TA_CENTER,
            textColor=colors.blue
        )
    
    def generate_activity_reports_pdf(self, reports, date_range=None):
        """Generate PDF for Activity Reports - Format PT. RIUNG MITRA LESTARI"""
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Mechanic_Activity_Report_{datetime.now().strftime("%Y%m%d")}.pdf"'
        
        doc = SimpleDocTemplate(response, pagesize=A4, 
                              rightMargin=50, leftMargin=50, 
                              topMargin=40, bottomMargin=40)
        
        elements = []
        
        # Get first report for foreman data
        foreman_data = None
        if reports and len(reports) > 0:
            foreman_data = reports[0].foreman
        
        # Add company header dengan logo
        elements.extend(self._add_company_header_with_logo())
        
        # Add main title
        title = "Mechanic Activity Report"
        elements.append(Paragraph(title, self.title_style))
        elements.append(Spacer(1, 15))
        
        # Add website
        website = "www.riungmitra.co.id"
        elements.append(Paragraph(website, self.subtitle_style))
        elements.append(Spacer(1, 20))
        
        # Add form header section dengan data foreman
        elements.extend(self._add_form_header_section(foreman_data, reports))
        
        # Add activity table
        elements.extend(self._add_activity_table(reports))
        
        # Add footer section dengan nama foreman dan leader
        elements.extend(self._add_footer_section(foreman_data))
        
        # Build PDF
        doc.build(elements)
        return response
    
    def _add_company_header_with_logo(self):
        """Add company header with logo placeholder"""
        elements = []
        
        # Create header table dengan logo space dan company info
        header_data = []
        
        # Logo placeholder dan company info dalam satu row
        logo_cell = "[LOGO]\n\nTempat untuk\nlogo perusahaan\n(100x60 px)"
        company_info = "PT. RIUNG MITRA LESTARI SITE RMGM\n\nMining Contractor"
        
        header_data.append([logo_cell, company_info])
        
        header_table = Table(header_data, colWidths=[2*inch, 4*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica'),
            ('FONTSIZE', (0, 0), (0, 0), 8),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (1, 0), 12),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.grey),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.black),
            ('BOX', (0, 0), (0, 0), 1, colors.grey),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _add_form_header_section(self, foreman_data, reports):
        """Add form header section dengan data yang diisi"""
        elements = []
        
        # Form title
        form_title = "FORMULIR MECHANIC ACTIVITY REPORT"
        title_para = Paragraph(form_title, ParagraphStyle(
            'FormTitle',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceAfter=15
        ))
        elements.append(title_para)
        
        # Prepare data
        nama = foreman_data.name or foreman_data.get_full_name() if foreman_data else ''
        nrp = foreman_data.nrp or '' if foreman_data else ''
        section = foreman_data.get_department_display() or '' if foreman_data else ''
        date = reports[0].date.strftime('%d/%m/%Y') if reports and len(reports) > 0 else ''
        cc_atasan = ''
        if foreman_data and foreman_data.leader:
            leader_name = foreman_data.leader.name or foreman_data.leader.get_full_name()
            cc_atasan = f"{leader_name}@gmail.com"
        
        # Form fields table dengan data yang diisi
        form_data = [
            ['Nama', ':', nama, 'Date', ':', date],
            ['NRP', ':', nrp, 'CC Atasan', ':', cc_atasan],
            ['', '', '', 'Section', ':', section]
        ]
        
        form_table = Table(form_data, colWidths=[1*inch, 0.2*inch, 2*inch, 1*inch, 0.2*inch, 2*inch])
        form_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (1, -1), 'LEFT'),  # Labels dan colon
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),  # Data kiri
            ('ALIGN', (3, 0), (4, -1), 'LEFT'),  # Labels kanan
            ('ALIGN', (5, 0), (5, -1), 'LEFT'),  # Data kanan
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Underlines untuk data fields
            ('LINEBELOW', (2, 0), (2, 0), 1, colors.black),  # Nama
            ('LINEBELOW', (2, 1), (2, 1), 1, colors.black),  # NRP
            ('LINEBELOW', (5, 0), (5, 0), 1, colors.black),  # Date
            ('LINEBELOW', (5, 1), (5, 1), 1, colors.black),  # CC Atasan
            ('LINEBELOW', (5, 2), (5, 2), 1, colors.black),  # Section
        ]))
        
        elements.append(form_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_activity_table(self, reports):
        """Add main activity table dengan data yang rapi"""
        elements = []
        
        # Table headers
        headers = [
            'NO', 'START', 'STOP', 'DURASI\n(JAM)', 'ACTIVITIES', 
            'UNIT\nCODE', 'HM/KM', 'SC/US', 'COMPONENT'
        ]
        
        # Create table data
        table_data = [headers]
        
        # Add 5 rows (sesuai dokumen asli)
        for i in range(1, 6):
            row = [str(i), '', '', '', '', '', '', '', '']
            table_data.append(row)
        
        # Populate dengan data reports jika ada
        if reports:
            for i, report in enumerate(reports[:5], 1):
                if i <= len(table_data) - 1:
                    start_time = report.start_time.strftime('%H:%M') if report.start_time else ''
                    end_time = report.end_time.strftime('%H:%M') if report.end_time else ''
                    duration = self._calculate_duration(report.start_time, report.end_time)
                    activities = (report.activities[:30] + '...') if len(report.activities or '') > 30 else (report.activities or '')
                    unit_code = report.Unit_Code or ''
                    hmkm = report.Hmkm or ''
                    component = report.get_component_display() or ''
                    
                    table_data[i] = [
                        str(i), start_time, end_time, duration, activities,
                        unit_code, hmkm, '', component
                    ]
        
        # Create table dengan column widths yang proporsional
        table = Table(table_data, colWidths=[
            0.4*inch,   # NO
            0.7*inch,   # START
            0.7*inch,   # STOP
            0.7*inch,   # DURASI
            2.2*inch,   # ACTIVITIES
            0.7*inch,   # UNIT CODE
            0.7*inch,   # HM/KM
            0.6*inch,   # SC/US
            1*inch      # COMPONENT
        ])
        
        # Style the table
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Body styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_footer_section(self, foreman_data):
        """Add footer section dengan nama yang diisi"""
        elements = []
        
        # Total Durasi section
        total_text = "Total Durasi (Jam) :"
        total_para = Paragraph(total_text, ParagraphStyle(
            'TotalStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
            textColor=colors.black,
            spaceAfter=10
        ))
        elements.append(total_para)
        
        # Date and location
        date_location = f"Laung Tuhup, ({datetime.now().strftime('%d/%m/%Y')})"
        date_para = Paragraph(date_location, ParagraphStyle(
            'DateStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_RIGHT,
            textColor=colors.black,
            spaceAfter=30
        ))
        elements.append(date_para)
        
        # Prepare names
        foreman_name = ''
        leader_name = ''
        if foreman_data:
            foreman_name = foreman_data.name or foreman_data.get_full_name()
            if foreman_data.leader:
                leader_name = foreman_data.leader.name or foreman_data.leader.get_full_name()
        
        # Signature section dengan nama yang diisi
        sig_data = [
            ['Group Leader', 'Mekanik'],
            ['', ''],
            ['', ''],
            ['', ''],
            [f'({leader_name})', f'({foreman_name})']
        ]
        
        sig_table = Table(sig_data, colWidths=[3*inch, 3*inch])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Underlines untuk signatures
            ('LINEBELOW', (0, 0), (0, 0), 1, colors.black),
            ('LINEBELOW', (1, 0), (1, 0), 1, colors.black),
            ('LINEBELOW', (0, 4), (0, 4), 1, colors.black),
            ('LINEBELOW', (1, 4), (1, 4), 1, colors.black),
        ]))
        
        elements.append(sig_table)
        
        return elements
    
    def _calculate_duration(self, start_time, end_time):
        """Calculate duration between start and end time"""
        if start_time and end_time:
            try:
                # Convert to datetime for calculation
                start_dt = datetime.combine(datetime.today(), start_time)
                end_dt = datetime.combine(datetime.today(), end_time)
                
                # Handle overnight shifts
                if end_dt < start_dt:
                    end_dt += timedelta(days=1)
                
                duration = end_dt - start_dt
                hours = duration.total_seconds() / 3600
                return f"{hours:.1f}"
            except:
                return ''
        return ''
    
    # Keep existing methods for analysis reports
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
        """Add company header with logo (untuk analysis reports)"""
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
        """Add signature section (untuk analysis reports)"""
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