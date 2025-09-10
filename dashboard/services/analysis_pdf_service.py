from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.http import HttpResponse
from datetime import datetime

class AnalysisPDFService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for the PDF"""
        self.header_style = ParagraphStyle(
            'HeaderStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        )
        
        self.title_style = ParagraphStyle(
            'TitleStyle',
            parent=self.styles['Normal'],
            fontSize=14,
            alignment=TA_CENTER,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        )
    
    def generate_technical_analysis_report_pdf(self, report):
        """Generate PDF for Technical Analysis Report (TAR)"""
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="TAR_{report.id}_{datetime.now().strftime("%Y%m%d")}.pdf"'
        
        doc = SimpleDocTemplate(
            response, 
            pagesize=A4, 
            rightMargin=30, 
            leftMargin=30, 
            topMargin=30, 
            bottomMargin=30
        )
        
        elements = []
        
        # Header
        elements.extend(self._add_header(report))
        
        # Basic Info
        elements.extend(self._add_basic_info(report))
        
        # Machine Info
        elements.extend(self._add_machine_info(report))
        
        # Problem Info
        elements.extend(self._add_problem_info(report))
        
        # Analysis (if extended fields exist)
        elements.extend(self._add_analysis_info(report))
        
        # Signature
        elements.extend(self._add_signature(report))
        
        # Build PDF
        doc.build(elements)
        return response
    
    def _add_header(self, report):
        """Add header section"""
        elements = []
        
        # Company header
        header_data = [
            ['PT. RIUNG MITRA LESTARI\nMechanic Development', 'TECHNICAL ANALYSIS REPORT (TAR)']
        ]
        
        header_table = Table(header_data, colWidths=[3.5*inch, 3.5*inch])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 10),
            ('FONTSIZE', (1, 0), (1, 0), 14),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 10))
        
        return elements
    
    def _add_basic_info(self, report):
        """Add basic information"""
        elements = []
        
        # Basic info
        basic_data = [
            [
                'REPORT NO :', 
                getattr(report, 'no_report', '') or f'RMGM/{datetime.now().year}', 
                'WO NUMBER', 
                ':', 
                getattr(report, 'WO_Number', '') or ''
            ],
            [
                'REPORT DATE :', 
                report.report_date.strftime('%d/%m/%Y') if hasattr(report, 'report_date') and report.report_date else '', 
                'WO DATE', 
                ':', 
                report.WO_date.strftime('%d/%m/%Y') if hasattr(report, 'WO_date') and report.WO_date else ''
            ]
        ]
        
        basic_table = Table(basic_data, colWidths=[1.2*inch, 1.8*inch, 1*inch, 0.2*inch, 1.8*inch])
        basic_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        elements.append(basic_table)
        elements.append(Spacer(1, 8))
        
        return elements
    
    def _add_machine_info(self, report):
        """Add machine information"""
        elements = []
        
        # Machine headers
        machine_data = [
            ['CODE NUMBER', 'MACHINE MAKER', 'MACHINE MODEL', 'MACHINE S/N', 'ENGINE MODEL', 'ENGINE NUMBER'],
            [
                getattr(report, 'unit_code', '') or '',
                'KOMATSU',
                'HD785-7', 
                report.foreman.nrp if hasattr(report, 'foreman') and report.foreman and hasattr(report.foreman, 'nrp') else '',
                'SAA12V140E-3',
                '514276'
            ]
        ]
        
        machine_table = Table(machine_data, colWidths=[1.17*inch] * 6)
        machine_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        elements.append(machine_table)
        elements.append(Spacer(1, 8))
        
        return elements
    
    def _add_problem_info(self, report):
        """Add problem information"""
        elements = []
        
        # Problem info
        problem_display = ''
        if hasattr(report, 'get_problem_display'):
            try:
                problem_display = report.get_problem_display() or ''
            except:
                problem_display = getattr(report, 'problem', '') or ''
        else:
            problem_display = getattr(report, 'problem', '') or ''
        
        trouble_date = ''
        if hasattr(report, 'Trouble_date') and report.Trouble_date:
            trouble_date = report.Trouble_date.strftime('%d/%m/%Y')
        
        problem_data = [
            [
                'PROBLEM', 
                problem_display, 
                'TROUBLE DATE', 
                trouble_date, 
                'HM', 
                getattr(report, 'Hm', '') or ''
            ],
            [
                '', 
                '', 
                '', 
                '', 
                'KM', 
                ''
            ]
        ]
        
        problem_table = Table(problem_data, colWidths=[1*inch, 2*inch, 1.2*inch, 1*inch, 0.5*inch, 1.3*inch])
        problem_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('SPAN', (0, 0), (0, 1)),  # PROBLEM
            ('SPAN', (1, 0), (1, 1)),  # Problem value
            ('SPAN', (2, 0), (2, 1)),  # TROUBLE DATE
            ('SPAN', (3, 0), (3, 1)),  # Date value
        ]))
        
        elements.append(problem_table)
        elements.append(Spacer(1, 8))
        
        # Part info
        part_data = [
            ['PART NUMBER', 'PART NAME', 'COMP/PART GROUP', 'LIFE TIME (HM)'],
            [
                getattr(report, 'part_no', '') or '', 
                getattr(report, 'part_name', '') or '', 
                '', 
                ''
            ]
        ]
        
        part_table = Table(part_data, colWidths=[2*inch, 2*inch, 1.5*inch, 1.5*inch])
        part_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        elements.append(part_table)
        elements.append(Spacer(1, 10))
        
        return elements
    
    def _add_analysis_info(self, report):
        """Add analysis information (extended fields)"""
        elements = []
        
        # Analysis header
        elements.append(Paragraph('DESCRIBE AND ANALYZE THE PROBLEM', 
                                ParagraphStyle('AnalysisHeader', 
                                             parent=self.styles['Normal'], 
                                             fontSize=10, 
                                             alignment=TA_LEFT, 
                                             fontName='Helvetica-Bold')))
        elements.append(Spacer(1, 6))
        
        # Check for extended fields and add them
        extended_fields = [
            ('nama_fungsi_komponen', 'NAMA DAN FUNGSI KOMPONEN'),
            ('gejala_masalah', 'GEJALA MASALAH YANG DIHADAPI'),
            ('akar_penyebab_masalah', 'AKAR PENYEBAB MASALAH'),
            ('tindakan_dilakukan', 'TINDAKAN YANG DILAKUKAN'),
            ('tindakan_pencegahan', 'TINDAKAN PENCEGAHAN')
        ]
        
        for field_name, field_title in extended_fields:
            if hasattr(report, field_name):
                field_value = getattr(report, field_name, '')
                if field_value:
                    # Add field title
                    elements.append(Paragraph(field_title, 
                                            ParagraphStyle('FieldTitle', 
                                                         parent=self.styles['Normal'], 
                                                         fontSize=9, 
                                                         alignment=TA_LEFT, 
                                                         fontName='Helvetica-Bold')))
                    
                    # Add field content in a box
                    content_table = Table([[str(field_value)]], colWidths=[7*inch], rowHeights=[0.8*inch])
                    content_table.setStyle(TableStyle([
                        ('BOX', (0, 0), (-1, -1), 1, colors.black),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ]))
                    
                    elements.append(content_table)
                    elements.append(Spacer(1, 6))
        
        return elements
    
    def _add_signature(self, report):
        """Add signature section"""
        elements = []
        
        # Get names safely
        foreman_name = ''
        leader_name = ''
        
        if hasattr(report, 'foreman') and report.foreman:
            if hasattr(report.foreman, 'name') and report.foreman.name:
                foreman_name = report.foreman.name
            elif hasattr(report.foreman, 'get_full_name'):
                try:
                    foreman_name = report.foreman.get_full_name()
                except:
                    foreman_name = str(report.foreman)
            
            if hasattr(report.foreman, 'leader') and report.foreman.leader:
                if hasattr(report.foreman.leader, 'name') and report.foreman.leader.name:
                    leader_name = report.foreman.leader.name
                elif hasattr(report.foreman.leader, 'get_full_name'):
                    try:
                        leader_name = report.foreman.leader.get_full_name()
                    except:
                        leader_name = str(report.foreman.leader)
        
        # Signature table
        sig_data = [
            ['MECHANIC NAME', foreman_name, 'SUPERVISOR NAME', leader_name],
            ['', '', '', ''],
            ['SIGN', '', 'SIGN', '']
        ]
        
        sig_table = Table(sig_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(sig_table)
        
        return elements