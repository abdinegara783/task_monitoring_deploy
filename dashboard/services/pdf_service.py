from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, A3
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
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
        elements.extend(self._add_footer_section(foreman_data, reports))
        
        # Build PDF
        doc.build(elements)
        return response
    
    def _add_company_header_with_logo(self):
        """Add company header with actual logo"""
        elements = []
        
        # Create header table dengan logo dan company info
        header_data = []
        
        # Logo path
        logo_path = os.path.join(settings.BASE_DIR, 'media', 'logo', 'LOGO.png')
        
        # Check if logo exists, if not use placeholder
        if os.path.exists(logo_path):
            try:
                # Create logo image
                logo = Image(logo_path, width=1.5*inch, height=1*inch)
                logo.hAlign = 'CENTER'
                logo_cell = logo
            except:
                # Fallback to text if image fails to load
                logo_cell = "[LOGO]\n\nTempat untuk\nlogo perusahaan\n(100x60 px)"
        else:
            logo_cell = "[LOGO]\n\nTempat untuk\nlogo perusahaan\n(100x60 px)"
        
        company_info = "PT. RIUNG MITRA LESTARI SITE RMGM\n\nMining Contractor"
        
        header_data.append([logo_cell, company_info])
        
        header_table = Table(header_data, colWidths=[2*inch, 4*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (1, 0), 12),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.black),
        ]))
        
        # Only add box if using text placeholder
        if isinstance(logo_cell, str):
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
        """Add main activity table dengan data yang rapi - Updated for new ActivityReport model"""
        elements = []
        
        # Table headers - Updated to match new structure
        headers = [
            'NO', 'TANGGAL', 'NRP', 'SECTION', 'START', 'STOP', 
            'UNIT\nCODE', 'COMPONENT', 'ACTIVITIES', 'STATUS'
        ]
        
        # Create table data
        table_data = [headers]
        
        # Populate dengan data reports jika ada
        if reports:
            row_num = 1
            for report in reports:
                # Get all activities for this report
                activities = report.activities.all().order_by('activity_number')
                
                if activities.exists():
                    # Add each activity as a separate row
                    for activity in activities:
                        start_time = activity.start_time.strftime('%H:%M') if activity.start_time else ''
                        stop_time = activity.stop_time.strftime('%H:%M') if activity.stop_time else ''
                        unit_code = activity.unit_code or ''
                        component = activity.get_component_display() or ''
                        activities_desc = (activity.activities[:25] + '...') if len(activity.activities or '') > 25 else (activity.activities or '')
                        
                        table_data.append([
                            str(row_num),
                            report.date.strftime('%d/%m/%Y'),
                            report.nrp or '',
                            report.get_section_display() or '',
                            start_time,
                            stop_time,
                            unit_code,
                            component,
                            activities_desc,
                            report.get_status_display()
                        ])
                        row_num += 1
                else:
                    # If no activities, show report with empty activity data
                    table_data.append([
                        str(row_num),
                        report.date.strftime('%d/%m/%Y'),
                        report.nrp or '',
                        report.get_section_display() or '',
                        '',
                        '',
                        '',
                        '',
                        'No activities',
                        report.get_status_display()
                    ])
                    row_num += 1
        else:
            # Add empty rows if no reports
            for i in range(1, 6):
                table_data.append([str(i), '', '', '', '', '', '', '', '', ''])
        
        # Create table dengan column widths yang proporsional - Updated for new columns
        table = Table(table_data, colWidths=[
            0.3*inch,   # NO
            0.8*inch,   # TANGGAL
            0.6*inch,   # NRP
            0.8*inch,   # SECTION
            0.5*inch,   # START
            0.5*inch,   # STOP
            0.7*inch,   # UNIT CODE
            0.9*inch,   # COMPONENT
            2.0*inch,   # ACTIVITIES
            0.7*inch    # STATUS
        ])
        
        # Style the table
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Body styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            
            # Left align for text columns
            ('ALIGN', (8, 1), (8, -1), 'LEFT'),  # ACTIVITIES column
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_footer_section(self, foreman_data, reports=None):
        """Add footer section dengan nama yang diisi dan total durasi jam kerja"""
        elements = []
        
        # Calculate total duration from all activities
        total_duration = 0.0
        if reports:
            for report in reports:
                activities = report.activities.all()
                for activity in activities:
                    if activity.start_time and activity.stop_time:
                        duration_hours = self._calculate_duration_hours(activity.start_time, activity.stop_time)
                        total_duration += duration_hours
        
        # Total Durasi section dengan nilai yang dihitung
        total_text = f"Total Durasi (Jam) : {total_duration:.1f} jam"
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
    
    def _calculate_duration_hours(self, start_time, end_time):
        """Calculate duration in hours between start and end time"""
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
                return hours
            except:
                return 0.0
        return 0.0
    
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
        
        # Company logo - use the actual logo path
        logo_path = os.path.join(settings.BASE_DIR, 'media', 'logo', 'LOGO.png')
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=2*inch, height=1.3*inch)
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 12))
            except:
                # If logo fails to load, skip it
                pass
        
        # Company name
        company_name = "PT. RIUNG MITRA LESTARI"
        elements.append(Paragraph(company_name, self.company_style))
        
        # Company address
        address = "Mining Contractor<br/>Site RMGM"
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
    def _get_machine_data(self, section):
        """Fetch machine data based on the section code"""
        # Mapping data mesin berdasarkan section dari SECTION_CHOICES di models.py
        machine_data_map = {
            "WATER PUMP (WP)": {
                "unit_model": "KSB-DND-150-4H",
                "unit_code": "WP-001",
                "serial_number": "049-P2210179-001",
                "hm": "5000",
                "engine_model": "TAD1343VE",
                "engine_sn": "20132255277",
                "application": "Dewatering",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Sangatta"
            },
            "TL": {
                "unit_model": "TL-450",
                "unit_code": "TL-001",
                "serial_number": "TL45012345",
                "hm": "3000",
                "engine_model": "Cummins QSB6.7",
                "engine_sn": "CM67890123",
                "application": "Material Handling",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Tanjung Enim"
            },
            "CAT395": {
                "unit_model": "CAT 395",
                "unit_code": "CAT395-001",
                "serial_number": "CAT39512345",
                "hm": "8000",
                "engine_model": "CAT C18",
                "engine_sn": "C1812345678",
                "application": "Mining",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Sangatta"
            },
            "BOMAG COMPACTOR": {
                "unit_model": "BOMAG BW211D-40",
                "unit_code": "BOMAG-001",
                "serial_number": "BW21112345",
                "hm": "4500",
                "engine_model": "Deutz TCD 2012",
                "engine_sn": "DTZ12345678",
                "application": "Road Construction",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Tanjung"
            },
            "DYNAPAC COMPACTOR": {
                "unit_model": "DYNAPAC CA2500D",
                "unit_code": "DYNAPAC-001",
                "serial_number": "DYN25012345",
                "hm": "3800",
                "engine_model": "Cummins QSB4.5",
                "engine_sn": "CM45678901",
                "application": "Road Construction",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Tanjung Enim"
            },
            "D85": {
                "unit_model": "Komatsu D85ESS-2",
                "unit_code": "D85-001",
                "serial_number": "D8512345",
                "hm": "12000",
                "engine_model": "Komatsu SAA6D125E-5",
                "engine_sn": "KM12345678",
                "application": "Mining",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Sangatta"
            },
            "D155": {
                "unit_model": "Komatsu D155AX-6",
                "unit_code": "D155-001",
                "serial_number": "D15512345",
                "hm": "10000",
                "engine_model": "Komatsu SAA6D140E-5",
                "engine_sn": "KM23456789",
                "application": "Mining",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Tanjung"
            },
            "D375": {
                "unit_model": "Komatsu D375A-6",
                "unit_code": "D375-001",
                "serial_number": "D37512345",
                "hm": "9000",
                "engine_model": "Komatsu SAA6D170E-5",
                "engine_sn": "KM34567890",
                "application": "Mining",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Sangatta"
            },
            "DX800": {
                "unit_model": "Doosan DX800LC",
                "unit_code": "DX800-001",
                "serial_number": "DX80012345",
                "hm": "7500",
                "engine_model": "Perkins 2506C-E15TA",
                "engine_sn": "PK12345678",
                "application": "Mining",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Tanjung"
            },
            "EPIROC DM30": {
                "unit_model": "EPIROC DM30 II",
                "unit_code": "DM30-001",
                "serial_number": "DM3012345",
                "hm": "6000",
                "engine_model": "CAT C15",
                "engine_sn": "C1523456789",
                "application": "Drilling",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Sangatta"
            },
            "GD955": {
                "unit_model": "Komatsu GD955-5",
                "unit_code": "GD955-001",
                "serial_number": "GD95512345",
                "hm": "5500",
                "engine_model": "Komatsu SAA6D140E-5",
                "engine_sn": "KM45678901",
                "application": "Road Construction",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Tanjung"
            },
            "GD160K/M": {
                "unit_model": "Komatsu GD160-2",
                "unit_code": "GD160-001",
                "serial_number": "GD16012345",
                "hm": "4800",
                "engine_model": "Komatsu SAA6D107E-1",
                "engine_sn": "KM56789012",
                "application": "Road Construction",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Tanjung Enim"
            },
            "GD535": {
                "unit_model": "Komatsu GD535-5",
                "unit_code": "GD535-001",
                "serial_number": "GD53512345",
                "hm": "4200",
                "engine_model": "Komatsu SAA4D107E-1",
                "engine_sn": "KM67890123",
                "application": "Road Construction",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Sangatta"
            },
            "GENSET": {
                "unit_model": "Cummins C500D5",
                "unit_code": "GENSET-001",
                "serial_number": "GEN12345",
                "hm": "10000",
                "engine_model": "Cummins QSX15-G8",
                "engine_sn": "CM78901234",
                "application": "Power Generation",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Tanjung"
            },
            "HD785": {
                "unit_model": "Komatsu HD785-7",
                "unit_code": "HD785-001",
                "serial_number": "HD78512345",
                "hm": "15000",
                "engine_model": "Komatsu SAA12V140E-3",
                "engine_sn": "KM89012345",
                "application": "Mining",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Sangatta"
            },
            "HINO DT": {
                "unit_model": "HINO 500 FM260JD",
                "unit_code": "HINODT-001",
                "serial_number": "HIN12345",
                "hm": "8000",
                "engine_model": "HINO J08E-VB",
                "engine_sn": "HIN23456789",
                "application": "Dump Truck",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Tanjung Enim"
            },
            "HINO WT/LT/CT": {
                "unit_model": "HINO 500 FM260JW",
                "unit_code": "HINOWT-001",
                "serial_number": "HIN23456",
                "hm": "7000",
                "engine_model": "HINO J08E-VB",
                "engine_sn": "HIN34567890",
                "application": "Water Truck",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Sangatta"
            },
            "KATO CRANE": {
                "unit_model": "KATO NK550VR",
                "unit_code": "KATO-001",
                "serial_number": "KAT12345",
                "hm": "3500",
                "engine_model": "Mitsubishi 6D24-TLE2A",
                "engine_sn": "MIT12345678",
                "application": "Lifting",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Tanjung"
            },
            "MANITAOU": {
                "unit_model": "MANITOU MT1840",
                "unit_code": "MANITOU-001",
                "serial_number": "MAN12345",
                "hm": "4000",
                "engine_model": "Mercedes OM904LA",
                "engine_sn": "MER12345678",
                "application": "Material Handling",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Tanjung Enim"
            },
            "MERCY DT": {
                "unit_model": "Mercedes-Benz Actros 4043",
                "unit_code": "MERCYDT-001",
                "serial_number": "MER23456",
                "hm": "9000",
                "engine_model": "Mercedes OM501LA",
                "engine_sn": "MER23456789",
                "application": "Dump Truck",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Sangatta"
            },
            "PC200/210": {
                "unit_model": "Komatsu PC210-10M0",
                "unit_code": "PC210-001",
                "serial_number": "PC21012345",
                "hm": "6500",
                "engine_model": "Komatsu SAA6D107E-1",
                "engine_sn": "KM90123456",
                "application": "Mining",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Tanjung"
            },
            "PC300": {
                "unit_model": "Komatsu PC300-8M0",
                "unit_code": "PC300-001",
                "serial_number": "PC30012345",
                "hm": "7200",
                "engine_model": "Komatsu SAA6D114E-3",
                "engine_sn": "KM01234567",
                "application": "Mining",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Sangatta"
            },
            "PC500": {
                "unit_model": "Komatsu PC500LC-10",
                "unit_code": "PC500-001",
                "serial_number": "PC50012345",
                "hm": "8500",
                "engine_model": "Komatsu SAA6D125E-6",
                "engine_sn": "KM12345098",
                "application": "Mining",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Tanjung Enim"
            },
            "PC1250": {
                "unit_model": "Komatsu PC1250-8",
                "unit_code": "PC1250-001",
                "serial_number": "PC125012345",
                "hm": "12000",
                "engine_model": "Komatsu SAA6D170E-5",
                "engine_sn": "KM23456098",
                "application": "Mining",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Sangatta"
            },
            "RENAULT FT/LB": {
                "unit_model": "Renault Kerax 440.34",
                "unit_code": "RENAULT-001",
                "serial_number": "REN12345",
                "hm": "7800",
                "engine_model": "Renault DXi11",
                "engine_sn": "REN12345678",
                "application": "Fuel Truck",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Tanjung"
            },
            "VOLVO FMX400": {
                "unit_model": "Volvo FMX 400",
                "unit_code": "VOLVO-001",
                "serial_number": "VOL12345",
                "hm": "8200",
                "engine_model": "Volvo D13A",
                "engine_sn": "VOL12345678",
                "application": "Dump Truck",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Sangatta"
            },
            "HD465/WT": {
                "unit_model": "Komatsu HD465-7",
                "unit_code": "HD465-001",
                "serial_number": "HD46512345",
                "hm": "11000",
                "engine_model": "Komatsu SAA6D170E-3",
                "engine_sn": "KM34567098",
                "application": "Mining",
                "customer": "PT. Riung Mitra Lestari",
                "location": "Tanjung Enim"
            }
        }
        
        # Jika section tidak ditemukan, kembalikan data kosong
        return machine_data_map.get(section, {})

    def generate_technical_analysis_report_pdf(self, report):
        """Generate PDF for Technical Analysis Report (TAR) based on the new template"""
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="TAR_{report.id}_{datetime.now().strftime("%Y%m%d")}.pdf"'
        
        # Create PDF document with A3 size for more space
        doc = SimpleDocTemplate(response, pagesize=A3,
                              rightMargin=8*mm, leftMargin=8*mm,
                              topMargin=8*mm, bottomMargin=8*mm)
        
        # Story list to hold all elements
        elements = []
        
        # Calculate consistent page width
        page_width = 281*mm  # A3 width minus margins (297-16)
        
        # Define consistent column structure (9 columns base)
        col_width = page_width / 9  # ~31.2mm per column
        
        # Custom styles with smaller fonts
        styles = getSampleStyleSheet()
        
        header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=TA_LEFT)
        title_style = ParagraphStyle('TitleStyle', parent=styles['Normal'], fontSize=12, fontName='Helvetica-Bold', alignment=TA_CENTER)
        cell_style = ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=6, fontName='Helvetica')
        
        # 1. HEADER SECTION - 3 columns aligned
        # Create logo for TAR header
        logo_path = os.path.join(settings.BASE_DIR, 'media', 'logo', 'LOGO.png')
        logo_cell = 'RIUNG\n[LOGO AREA]'  # Default text
        
        if os.path.exists(logo_path):
            try:
                # Create smaller logo for TAR header
                logo = Image(logo_path, width=25*mm, height=17*mm)
                logo.hAlign = 'CENTER'
                logo_cell = logo
            except:
                # Fallback to text if image fails to load
                logo_cell = 'RIUNG\n[LOGO AREA]'
        
        header_data = [
            [
                logo_cell,  # 1.5 cols
                Paragraph('<b>PT. RIUNG MITRA LESTARI<br/>Mechanic Development</b>', header_style),  # 3 cols
                Paragraph('<b>TECHNICAL ANALYSIS REPORT (TAR)</b>', title_style)  # 4.5 cols
            ]
        ]
        
        header_table = Table(header_data, colWidths=[col_width*1.5, col_width*3, col_width*4.5])
        header_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('ALIGN', (2, 0), (2, 0), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        elements.append(header_table)
        
        # 2. REPORT INFO SECTION - Aligned to same grid
        report_no = report.no_report if hasattr(report, 'no_report') and report.no_report else '<<REPORT NO>>'
        report_date = report.report_date.strftime('%d/%m/%Y') if hasattr(report, 'report_date') and report.report_date else '<<REPORT DATE>>'
        wo_number = report.WO_Number if hasattr(report, 'WO_Number') and report.WO_Number else '<<WO NUMBER>>'
        wo_date = report.WO_date.strftime('%d/%m/%Y') if hasattr(report, 'WO_date') and report.WO_date else '<<WO DATE>>'
        
        report_info_data = [
            ['REPORT NO :', report_date, '/RML/2025', 'WO NUMBER', ':', wo_number],
            ['REPORT DATE :', 'report_date', '', 'WO DATE', ':', wo_date]
        ]
            # Precise column widths yang total = page_width
        report_col_widths = [
            col_width * 1.0,    # REPORT NO/DATE label
            col_width * 1.5,    # Report number value
            col_width * 1.2,    # /RML/2025 
            col_width * 1.3,    # WO NUMBER/DATE label
            col_width * 0.2,    # Colon (:)
            col_width * 3.8     # WO values - sisa untuk precise fit
        ]
        
        report_table = Table(report_info_data,
                            colWidths=report_col_widths,
                            rowHeights=[8*mm, 8*mm])
        report_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        elements.append(report_table)
        
        # 3. MACHINE DETAILS SECTION - 6 equal columns
        
        # Ambil data mesin berdasarkan section
        section = report.section_track if hasattr(report, 'section_track') and report.section_track else ''
        print(section)
        machine_data = self._get_machine_data(section)

        
        # Gunakan data mesin yang diperoleh atau tampilkan placeholder
        code_unit = machine_data.get('unit_code', report.unit_code if hasattr(report, 'unit_code') and report.unit_code else '<<CODE UNIT>>')
        machine_maker = machine_data.get('machine_maker', '<<MACHINE MAKER>>')
        machine_model = machine_data.get('unit_model', '<<MACHINE MODEL>>')
        machine_sn = machine_data.get('serial_number', '<<MACHINE S/N>>')
        engine_model = machine_data.get('engine_model', '<<ENGINE MODEL>>')
        engine_sn = machine_data.get('engine_sn', '<<ENGINE NUMBER>>')
        machine_data_table = [
            ['CODE NUMBER', 'MACHINE MAKER', 'MACHINE MODEL', 'MACHINE S/N', 'ENGINE MODEL', 'ENGINE NUMBER'],
            [code_unit, machine_maker, machine_model, machine_sn, engine_model, engine_sn]
        ]
        
        machine_col_width = page_width / 6
        machine_table = Table(machine_data_table,
                             colWidths=[machine_col_width]*6,
                             rowHeights=[8*mm, 8*mm])
        machine_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(machine_table)
        
        # 4. APPLICATION SECTION - Structured like original
        # Application details header - aligned to 9-column grid
        app_header_data = [
            ['APPLICATION', '', 'ENVIRONMENT', '', 'OPERATION', '', '', '', '']
        ]
        
            # Precise column widths untuk APPLICATION section
        app_col_widths = [
            col_width * 0.8,    # LOC/WORK
            col_width * 1.0,    # OTHER values
            col_width * 1.3,    # GROUND labels
            col_width * 1.0,    # OTHER values
            col_width * 1.0,    # CODE UNIT/OPR TABLE
            col_width * 0.6,    # Numbers (38, 3)
            col_width * 0.9,    # Oil labels
            col_width * 1.2,    # GULF/CI values
            col_width * 1.2     # Last column untuk balance
        ]
        app_header_table = Table(app_header_data,
                               colWidths=app_col_widths)
        app_header_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
            ('BACKGROUND', (2, 0), (3, 0), colors.lightgrey),
            ('BACKGROUND', (4, 0), (8, 0), colors.lightgrey),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Merge headers properly
            ('SPAN', (0, 0), (1, 0)),  # APPLICATION
            ('SPAN', (2, 0), (3, 0)),  # ENVIRONMENT
            ('SPAN', (4, 0), (8, 0)),  # OPERATION
        ]))
        elements.append(app_header_table)
        
        # Application details - aligned to 9-column grid
        app_details_data = [
            ['LOC.', 'OTHER', 'GROUND CONDITION', 'OTHER', 'CODE UNIT', '38', 'Oil Wide', 'GULF', ''],
            ['WORK', 'OTHER', 'GROUND CARACTER', 'OTHER', 'OPR TABLE', '3', 'Oil Class', 'CI', ''],
            ['', '', '', '', '', '', 'Oil Visco', 'SAE 15W-40', '']
        ]
        
        app_details_table = Table(app_details_data,
                                colWidths=app_col_widths,
                                rowHeights=[7*mm, 7*mm, 7*mm])
        app_details_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            # Merge last column for SAE 15W-40
            ('SPAN', (7, 2), (8, 2)),
        ]))
        elements.append(app_details_table)
        
        # 5. PROBLEM SECTION - Matching original layout
        problem_code = report.get_problem_display() if hasattr(report, 'problem') and report.problem else '<<PROBLEM CODE>>'
        trouble_date = report.Trouble_date.strftime('%d/%m/%Y') if hasattr(report, 'Trouble_date') and report.Trouble_date else '<<TROUBLE DATE>>'
        hm = report.Hm if hasattr(report, 'HM') and report.HM else '<<HM>>'
        print(hm, "------------")
        judul_problem = report.title_problem if hasattr(report, 'title_problem') and report.title_problem else '<<JUDUL PROBLEM>>'
        
        problem_data = [
            ['PROBLEM', problem_code, 'TROUBLE DATE', trouble_date, 'HM', hm],
            ['', judul_problem, '', '', 'KM', '']
        ]
        # Precise column widths untuk PROBLEM section
        problem_col_widths = [
            col_width * 1.0,    # PROBLEM label
            col_width * 3.0,    # Problem code/title (wide area)
            col_width * 1.5,    # TROUBLE DATE
            col_width * 1.5,    # Trouble date value
            col_width * 0.8,    # HM/KM
            col_width * 1.2     # HM value - balance untuk precise fit
        ]
        problem_table = Table(problem_data,
                             colWidths=problem_col_widths,
                             rowHeights=[8*mm, 8*mm])
        problem_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('SPAN', (1, 0), (1, 1)),  # Problem code spans 2 rows
            ('SPAN', (2, 1), (3, 1)),  # Empty cell under trouble date
        ]))
        elements.append(problem_table)
        
        # 6. PART INFORMATION - Full width aligned
        part_no = report.part_no if hasattr(report, 'part_no') and report.part_no else '<<PART NO>>'
        part_name = report.part_name if hasattr(report, 'part_name') and report.part_name else '<<PART NAME>>'
        part_group = report.component if hasattr(report, 'component') and report.component else '<<PART GROUP>>'
        
        part_data = [
            ['PART NUMBER OF MAIN PART CAUSING THE PROBLEM', 'PART NAME', 'COMP/PART GROUP', 'LIFE TIME (HM)'],
            [part_no, part_name, part_group, '']
        ]
        
        part_table = Table(part_data,
                          colWidths=[col_width*3, col_width*2, col_width*2, col_width*2],
                          rowHeights=[8*mm, 8*mm])
        part_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (-1, 1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(part_table)
        
        # 7. ANALYSIS SECTIONS - Full width, each section as single row
        nama_fungsi = report.nama_fungsi_komponen if hasattr(report, 'nama_fungsi_komponen') and report.nama_fungsi_komponen else '<<NAMA & FUNGSI KOMPONEN>>'
        gejala = report.gejala_masalah if hasattr(report, 'gejala_masalah') and report.gejala_masalah else '<<GEJALA>>'
        akar_penyebab = report.akar_penyebab_masalah if hasattr(report, 'akar_penyebab_masalah') and report.akar_penyebab_masalah else '<<AKAR PENYEBAB MASALAH>>'
        tindakan = report.tindakan_dilakukan if hasattr(report, 'tindakan_dilakukan') and report.tindakan_dilakukan else '<<TINDAKAN YANG DILAKUKAN>>'
        pencegahan = report.tindakan_pencegahan if hasattr(report, 'tindakan_pencegahan') and report.tindakan_pencegahan else '<<TINDAKAN PENCEGAHAN>>'
        
        analysis_sections = [
            ("DESCRIBE AND ANALYZE THE PROBLEM (WITH PICTURE)", ""),
            ("NAMA DAN FUNGSI KOMPONEN", nama_fungsi),
            ("GEJALA MASALAH YANG DIHADAPI", gejala),
            ("AKAR PENYEBAB MASALAH", akar_penyebab),
            ("TINDAKAN YANG DILAKUKAN", tindakan),
            ("TINDAKAN PENCEGAHAN", pencegahan)
        ]
        
        for i, (section_title, content) in enumerate(analysis_sections):
            # Section header
            header_data = [[section_title]]
            header_table = Table(header_data, colWidths=[page_width])
            header_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(header_table)
            
            # Section content
            content_height = 20*mm if i == 0 else 12*mm  # First section bigger for picture
            content_data = [[content]]
            content_table = Table(content_data, colWidths=[page_width], rowHeights=[content_height])
            content_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 6),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(content_table)
        
        # 8. DOCUMENTATION SECTION - Two equal columns
        doc_header_data = [['DOKUMENTASI SEBELUM', 'DOKUMENTASI SESUDAH']]
        doc_header_table = Table(doc_header_data, colWidths=[page_width/2, page_width/2])
        doc_header_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(doc_header_table)
        
        dokumentasi_sebelum = report.dokumentasi_sebelum if hasattr(report, 'dokumentasi_sebelum') and report.dokumentasi_sebelum else '<<DOKUMENTASI SEBELUM>>'
        dokumentasi_sesudah = report.dokumentasi_sesudah if hasattr(report, 'dokumentasi_sesudah') and report.dokumentasi_sesudah else '<<DOKUMENTASI SESUDAH>>'
        
        doc_content_data = [[dokumentasi_sebelum, dokumentasi_sesudah]]
        doc_content_table = Table(doc_content_data,
                                colWidths=[page_width/2, page_width/2],
                                rowHeights=[25*mm])
        doc_content_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(doc_content_table)
        
        # 9. BOTTOM SECTION - Aligned to 9-column grid
        cause_table = report.cause_table if hasattr(report, 'cause_table') and report.cause_table else '<<CAUSE TABLE>>'
        email_aktif = report.email if hasattr(report, 'email_aktif') and report.email_aktif else '<<EMAIL AKTIF>>'
        correction_made = report.correction_made if hasattr(report, 'correction_made') and report.correction_made else '<<CORRECTION MADE>>'
        correction_date = report.correction_date.strftime('%d/%m/%Y') if hasattr(report, 'correction_date') and report.correction_date else '<<CORRECTION DATE>>'
        man_hour = report.man_hour if hasattr(report, 'man_hour') and report.man_hour else '<<MAN HOUR>>'
        nrp = report.foreman.nrp if hasattr(report, 'foreman') and hasattr(report.foreman, 'nrp') and report.foreman.nrp else '<<NRP>>'
        grade = report.grade if hasattr(report, 'grade') and report.grade else '<<GRADE>>'
        mechanic_name = report.foreman.name if hasattr(report, 'foreman') and hasattr(report.foreman, 'name') and report.foreman.name else '<<MECHANIC NAME>>'
        working_partner1 = report.working_partner1 if hasattr(report, 'working_partner1') and report.working_partner1 else '<<WORKING PARTNER 1>>'
        grade1 = report.grade1 if hasattr(report, 'grade1') and report.grade1 else '<<GRADE 1>>'
        working_partner2 = report.working_partner2 if hasattr(report, 'working_partner2') and report.working_partner2 else '<<WORKING PARTNER 2>>'
        grade2 = report.grade2 if hasattr(report, 'grade2') and report.grade2 else '<<GRADE 2>>'
        instruktur = report.foreman.leader.name if hasattr(report, 'foreman') and hasattr(report.foreman, 'leader') and hasattr(report.foreman.leader, 'name') and report.foreman.leader.name else '<<INSTRUKTUR>>'
        sign = '<<SIGN>>'
        print(report)
        
        bottom_data = [
        # Row 1: CAUSE TABLE dan EMAIL AKTIF
        ['CAUSE TABLE', '<<CAUSE TABLE>>', 'EMAIL AKTIF :', email_aktif, '', ''],
        # Row 2: CORRECTION MADE, CORRECTION DATE, MAN HOUR dengan area kosong
        ['CORRECTION MADE', '<<CORRECTION MADE>>', 'CORRECTION DATE', 'MAN HOUR', '', ''],
        # Row 3: Empty, Empty, values for DATE and HOUR dengan area kosong
        ['', '', '<<CORRECTION DATE>>', '<<MAN HOUR>>', '', ''],
        # Row 4: NIK, NRP, GRADE, GRADE_VAL, WORKING PARTNER 1, GRADE 1, SUPERVISOR NAME
        ['NIK', '<<NRP>>', 'GRADE', '<<GRADE>>', 'WORKING PARTNER 1', 'GRADE 1'],
        # Row 5: MECHANIC NAME, NAME_VAL, PARTNER1_VAL, GRADE1_VAL, SUPERVISOR NAME area
        ['MECHANIC NAME :', '<<MECHANIC NAME>>', '<<WORKING PARTNER 1>>', '<<GRADE 1>>', 'SUPERVISOR NAME :', '<<INSTRUKTUR>>'],
        # Row 6: Empty area, WORKING PARTNER 2, GRADE 2, QR CODE AREA, SIGN, SUPERVISOR SIGN  
        ['', '', 'WORKING PARTNER 2', 'GRADE 2', '[QR CODE AREA]', 'SIGN'],
        # Row 7: SIGN, SIGN content, PARTNER2_VAL, GRADE2_VAL, dan merge area bawah
        ['SIGN', '<<SIGN>>', '<<WORKING PARTNER 2>>', '<<GRADE 2>>', '', '<<SUPERVISOR SIGN>>']
        ]
        
        # Bottom section - 6 column layout untuk match gambar
        bottom_col_widths = [
            col_width*1.2,      # Column 0: Labels (NIK, MECHANIC, SIGN)
            col_width*1.8,      # Column 1: Values (NRP, MECHANIC NAME, SIGN content)
            col_width*1.5,      # Column 2: GRADE/WORKING PARTNER 2  
            col_width*1.2,      # Column 3: Grade values/GRADE 2
            col_width*1.8,      # Column 4: QR CODE area
            col_width*1.5       # Column 5: SIGN/SUPERVISOR area
        ]
        
        bottom_table = Table(bottom_data,
                            colWidths=bottom_col_widths,
                            rowHeights=[8*mm, 8*mm, 8*mm, 8*mm, 8*mm, 8*mm, 30*mm])
        bottom_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 6),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                
                # MERGE CELLS sesuai koreksi gambar
                # Row 1: EMAIL AKTIF area merge
                ('SPAN', (2, 0), (5, 0)),  # EMAIL AKTIF : <<EMAIL AKTIF>> spans 4 cols
                
                # Row 2: Area kosong di kanan merge
                ('SPAN', (4, 1), (5, 1)),  # Empty area setelah MAN HOUR
                
                # Row 3: Area kosong merge
                ('SPAN', (0, 2), (1, 2)),  # Empty area di kiri
                ('SPAN', (4, 2), (5, 2)),  # Empty area di kanan
                
                # Row 4: SUPERVISOR NAME area
                ('SPAN', (4, 3), (5, 3)),  # WORKING PARTNER 1 + GRADE 1
                
                # Row 5: SUPERVISOR area merge
                ('SPAN', (4, 4), (5, 4)),  # SUPERVISOR NAME + INSTRUKTUR
                
                # Row 6: QR CODE dan SIGN area (naik ke atas)
                ('SPAN', (0, 5), (1, 5)),  # Empty area merge di kiri
                ('SPAN', (4, 5), (5, 5)),  # QR CODE AREA + SIGN
                
                # Row 7: SIGN area merge bawah (sesuai koreksi poin 3)
                ('SPAN', (4, 6), (5, 6)),  # Area bawah QR merge
                
                # Center alignment untuk QR dan SIGN areas
                ('ALIGN', (4, 5), (5, 6), 'CENTER'),
                
                # Bold formatting untuk labels
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),  # CAUSE TABLE
                ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),  # EMAIL AKTIF
                ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),  # CORRECTION MADE
                ('FONTNAME', (2, 1), (2, 1), 'Helvetica-Bold'),  # CORRECTION DATE
                ('FONTNAME', (3, 1), (3, 1), 'Helvetica-Bold'),  # MAN HOUR
                ('FONTNAME', (0, 3), (0, 3), 'Helvetica-Bold'),  # NIK
                ('FONTNAME', (2, 3), (2, 3), 'Helvetica-Bold'),  # GRADE
                ('FONTNAME', (4, 3), (4, 3), 'Helvetica-Bold'),  # WORKING PARTNER 1
                ('FONTNAME', (0, 4), (0, 4), 'Helvetica-Bold'),  # MECHANIC NAME
                ('FONTNAME', (4, 4), (4, 4), 'Helvetica-Bold'),  # SUPERVISOR NAME
                ('FONTNAME', (2, 5), (2, 5), 'Helvetica-Bold'),  # WORKING PARTNER 2
                ('FONTNAME', (3, 5), (3, 5), 'Helvetica-Bold'),  # GRADE 2
                ('FONTNAME', (5, 5), (5, 5), 'Helvetica-Bold'),  # SIGN
                ('FONTNAME', (0, 6), (0, 6), 'Helvetica-Bold'),  # SIGN
            ]))
        elements.append(bottom_table)
        
        # Build PDF
        doc.build(elements)
        return response