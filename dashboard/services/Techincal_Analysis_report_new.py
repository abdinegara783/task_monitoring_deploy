from reportlab.lib.pagesizes import A3, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def create_tar_template():
    # Create PDF document with A3 size for more space
    filename = "technical_analysis_report_template.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A3,
                          rightMargin=8*mm, leftMargin=8*mm,
                          topMargin=8*mm, bottomMargin=8*mm)

    # Story list to hold all elements
    story = []

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
    header_data = [
        [
            'RIUNG\n[LOGO AREA]',  # 1.5 cols
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
    story.append(header_table)

    # 2. REPORT INFO SECTION - Precise alignment with page_width
    report_info_data = [
        ['REPORT NO :', '<<REPORT NO>>', '/RML/2025', 'WO NUMBER', ':', '<<WO NUMBER>>'],
        ['REPORT DATE :', '', '<<REPORT DATE>>', 'WO DATE', ':', '<<WO DATE>>']
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
    story.append(report_table)

    # 3. MACHINE DETAILS SECTION - 6 equal columns
    machine_data = [
        ['CODE NUMBER', 'MACHINE MAKER', 'MACHINE MODEL', 'MACHINE S/N', 'ENGINE MODEL', 'ENGINE NUMBER'],
        ['<<CODE UNIT>>', 'KSB', 'KSB-DND-150-4H', '049-P2210179-001', 'TAD1343VE', '20132255277']
    ]

    machine_col_width = page_width / 6
    machine_table = Table(machine_data,
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
    story.append(machine_table)

    # 4. APPLICATION SECTION - Precise alignment dengan page_width
    # Application details header - precise column alignment
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

    app_header_table = Table(app_header_data, colWidths=app_col_widths)
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
    story.append(app_header_table)

    # Application details - same column widths
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
        # Merge empty cells in row 3
        ('SPAN', (0, 2), (5, 2)),  # Merge empty cells in row 3
        ('SPAN', (7, 2), (8, 2)),  # SAE 15W-40 spans last 2 columns
    ]))
    story.append(app_details_table)

    # 5. PROBLEM SECTION - Precise width alignment
    problem_data = [
        ['PROBLEM', '<<PROBLEM CODE>>', 'TROUBLE DATE', '<<TROUBLE DATE>>', 'HM', '<<HM>>'],
        ['', '<<JUDUL PROBLEM>>', '', '', 'KM', '']
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
    story.append(problem_table)

    # 6. PART INFORMATION - Full width aligned
    part_data = [
        ['PART NUMBER OF MAIN PART CAUSING THE PROBLEM', 'PART NAME', 'COMP/PART GROUP', 'LIFE TIME (HM)'],
        ['<<PART NO>>', '<<PART NAME>>', '<<PART GROUP>>', '']
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
    story.append(part_table)

    # 7. ANALYSIS SECTIONS - Full width, each section as single row
    analysis_sections = [
        ("DESCRIBE AND ANALYZE THE PROBLEM (WITH PICTURE)", ""),
        ("NAMA DAN FUNGSI KOMPONEN", "<<NAMA & FUNGSI KOMPONEN>>"),
        ("GEJALA MASALAH YANG DIHADAPI", "<<GEJALA>>"),
        ("AKAR PENYEBAB MASALAH", "<<AKAR PENYEBAB MASALAH>>"),
        ("TINDAKAN YANG DILAKUKAN", "<<TINDAKAN YANG DILAKUKAN>>"),
        ("TINDAKAN PENCEGAHAN", "<<TINDAKAN PENCEGAHAN>>")
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
        story.append(header_table)

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
        story.append(content_table)

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
    story.append(doc_header_table)

    doc_content_data = [['<<DOKUMENTASI SEBELUM>>', '<<DOKUMENTASI SESUDAH>>']]
    doc_content_table = Table(doc_content_data,
                            colWidths=[page_width/2, page_width/2],
                            rowHeights=[25*mm])
    doc_content_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(doc_content_table)

    # 9. BOTTOM SECTION - Sesuai koreksi dengan struktur yang benar
    bottom_data = [
        # Row 1: CAUSE TABLE dan EMAIL AKTIF
        ['CAUSE TABLE', '<<CAUSE TABLE>>', 'EMAIL AKTIF :', '<<EMAIL AKTIF>>', '', ''],
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
    story.append(bottom_table)

    # Build PDF
    doc.build(story)
    print(f"Template TAR berhasil dibuat: {filename}")
    return filename

# Preview function
def preview_template():
    """Create and preview the template"""
    filename = create_tar_template()

    print("\n=== TECHNICAL ANALYSIS REPORT TEMPLATE (MERGED CELLS) ===")
    print(f"File: {filename}")
    print("\n✅ Perbaikan Bottom Section:")
    print("   📐 Merged empty cells untuk tampilan rapi")
    print("   🔗 CAUSE TABLE: Content spans 2 columns")
    print("   📧 EMAIL AKTIF: Spans to end of row")
    print("   🔧 CORRECTION MADE: Content spans 2 columns")
    print("   👤 MECHANIC NAME: Content spans 2 columns")
    print("   👥 SUPERVISOR: Spans to end")
    print("   📱 QR CODE: Centered, spans 2 columns")
    print("   ✍️  SIGN areas: Proper alignment")

    print(f"\n📊 Bottom Section Layout:")
    print("   • Row 1: CAUSE TABLE (merged) + EMAIL AKTIF (merged)")
    print("   • Row 2: CORRECTION MADE (merged) + DATE/HOUR + empty (merged)")
    print("   • Row 3: Empty start (merged) + DATE/HOUR + empty end (merged)")
    print("   • Row 4: NIK + NRP + GRADE + GRADE + PARTNER 1 + GRADE 1 + SUPERVISOR (merged)")
    print("   • Row 5: MECHANIC (merged) + PARTNER 1 + GRADE 1 + INSTRUKTUR (merged)")
    print("   • Row 6: Empty (merged) + PARTNER 2 + GRADE 2 + empty end (merged)")
    print("   • Row 7: SIGN + SIGN + PARTNER 2 + GRADE 2 + QR (merged) + SIGN (merged)")

    print(f"\n🎨 Visual Improvements:")
    print("   ✓ Tidak ada sel kosong yang terpisah")
    print("   ✓ Content area yang lebih luas")
    print("   ✓ Layout yang clean dan profesional")
    print("   ✓ Grid tetap konsisten 9-column")

    return filename

# Run preview
if __name__ == "__main__":
    preview_template()