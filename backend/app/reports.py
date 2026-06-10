import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_child_health_card_pdf(child, record, recommendations, schemes):
    """
    Generates a beautifully structured PDF Health Card for a child.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    story = []
    
    # Base Styles
    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#4f46e5'), # Brand Purple/Indigo
        spaceAfter=6,
        alignment=1 # Centered
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.HexColor('#475569'),
        spaceAfter=20,
        alignment=1
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    
    bold_body_style = ParagraphStyle(
        'BoldBodyText',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    # 1. Header Title
    story.append(Paragraph("PoshanAI Child Health Card", title_style))
    story.append(Paragraph("Integrated Child Development Services (ICDS) Support Hub • Government of India", subtitle_style))
    
    # 2. Child Profile Info Table
    profile_data = [
        [Paragraph("<b>Child Name:</b>", body_style), Paragraph(child.name, bold_body_style),
         Paragraph("<b>Age:</b>", body_style), Paragraph(f"{child.age_months:.0f} Months", body_style)],
        [Paragraph("<b>Gender:</b>", body_style), Paragraph(child.gender, body_style),
         Paragraph("<b>Parent/Guardian:</b>", body_style), Paragraph(child.parent_name if hasattr(child, 'parent_name') else "Guardian", body_style)],
        [Paragraph("<b>Village:</b>", body_style), Paragraph(child.village, body_style),
         Paragraph("<b>District/State:</b>", body_style), Paragraph(f"{child.district}, {child.state}", body_style)],
        [Paragraph("<b>Family Income:</b>", body_style), Paragraph(child.family_income, body_style),
         Paragraph("<b>Date Generated:</b>", body_style), Paragraph(record.recorded_at.strftime("%Y-%m-%d"), body_style)]
    ]
    
    profile_table = Table(profile_data, colWidths=[1.3*inch, 2.2*inch, 1.3*inch, 2.2*inch])
    profile_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1e293b')), # Sleek Dark Mode vibe matching main UI
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#334155')),
    ]))
    
    # Adjust styles for light text inside the dark table
    table_body_style = ParagraphStyle('TableBody', parent=body_style, textColor=colors.HexColor('#cbd5e1'))
    table_bold_style = ParagraphStyle('TableBold', parent=bold_body_style, textColor=colors.HexColor('#ffffff'))
    for r_idx in range(len(profile_data)):
        for c_idx in range(len(profile_data[r_idx])):
            profile_data[r_idx][c_idx].style = table_bold_style if "Bold" in profile_data[r_idx][c_idx].style.name or "<b>" in profile_data[r_idx][c_idx].text else table_body_style

    story.append(profile_table)
    story.append(Spacer(1, 10))
    
    # 3. Diagnostic Alert Box
    # Define colors based on severity
    if record.status == "Severe Malnutrition":
        status_bg = '#fee2e2'
        status_border = '#ef4444'
        status_txt = '#b91c1c'
    elif record.status == "Moderate Malnutrition":
        status_bg = '#ffedd5'
        status_border = '#f97316'
        status_txt = '#c2410c'
    elif record.status == "Mild Malnutrition":
        status_bg = '#fef9c3'
        status_border = '#eab308'
        status_txt = '#854d0e'
    else:
        status_bg = '#dcfce7'
        status_border = '#22c55e'
        status_txt = '#15803d'

    status_style = ParagraphStyle(
        'StatusAlert',
        parent=bold_body_style,
        fontSize=11,
        textColor=colors.HexColor(status_txt),
        alignment=1
    )
    
    status_data = [
        [
            Paragraph(f"Nutritional Status: <b>{record.status}</b>", status_style),
            Paragraph(f"System Risk Index: <b>{record.risk_score:.1f}%</b>", status_style)
        ]
    ]
    status_table = Table(status_data, colWidths=[3.5*inch, 3.5*inch])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(status_bg)),
        ('PADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor(status_border)),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(status_table)
    story.append(Spacer(1, 12))
    
    # 4. Clinical Measurement Logs
    story.append(Paragraph("Clinical Measurement Analytics", section_style))
    
    clinical_data = [
        [Paragraph("<b>Measurement Parameter</b>", bold_body_style), Paragraph("<b>Recorded Value</b>", bold_body_style), Paragraph("<b>WHO Z-Score / Reference Thresholds</b>", bold_body_style)],
        [Paragraph("Weight (Kg)", body_style), Paragraph(f"{record.weight_kg:.2f} Kg", body_style), Paragraph(f"Weight-for-Age Z-Score: {record.underweight_z:.2f}" if record.underweight_z is not None else "N/A", body_style)],
        [Paragraph("Height (Cm)", body_style), Paragraph(f"{record.height_cm:.1f} Cm", body_style), Paragraph(f"Height-for-Age Z-Score: {record.stunting_z:.2f}" if record.stunting_z is not None else "N/A", body_style)],
        [Paragraph("Weight-for-Height (Wasting)", body_style), Paragraph("-", body_style), Paragraph(f"Weight-for-Height Z-Score: {record.wasting_z:.2f}" if record.wasting_z is not None else "N/A", body_style)],
        [Paragraph("MUAC (Mid Upper Arm)", body_style), Paragraph(f"{record.muac_cm:.1f} Cm", body_style), Paragraph("Normal (>=13.5)" if record.muac_cm >= 13.5 else ("SAM Risk (<11.5)" if record.muac_cm < 11.5 else "MAM Risk (11.5 - 12.5)"), body_style)],
        [Paragraph("Hemoglobin (Anemia check)", body_style), Paragraph(f"{record.hemoglobin_gdl:.1f} g/dL" if record.hemoglobin_gdl else "Not Logged", body_style), Paragraph("Normal (>=11.0)" if record.hemoglobin_gdl and record.hemoglobin_gdl >= 11.0 else ("Anemic (<11.0)" if record.hemoglobin_gdl else "N/A"), body_style)]
    ]
    
    clinical_table = Table(clinical_data, colWidths=[2.2*inch, 1.3*inch, 3.5*inch])
    clinical_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#94a3b8')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(clinical_table)
    story.append(Spacer(1, 10))
    
    # 5. Diet Recommendations
    story.append(Paragraph("Adaptive Nutritional Guidelines", section_style))
    story.append(Paragraph(f"Daily Targets: Energy: <b>{recommendations['required_calories']:.0f} Kcal</b> | Protein: <b>{recommendations['required_protein_g']:.1f} g</b> ({recommendations['region']})", body_style))
    story.append(Spacer(1, 4))
    
    food_recs = recommendations.get("food_recommendations", [])
    food_list = []
    for food in food_recs[:4]: # Show top 4
        food_list.append([
            Paragraph(f"• <b>{food['food']}</b>: {food['benefits']}", body_style)
        ])
    
    food_table = Table(food_list, colWidths=[7.0*inch])
    food_table.setStyle(TableStyle([
        ('PADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(food_table)
    story.append(Spacer(1, 10))
    
    # 6. Eligible Government Schemes
    story.append(Paragraph("Eligible Government Support Schemes & Actions", section_style))
    scheme_rows = []
    for s in schemes[:3]: # Show top 3
        scheme_rows.append([
            Paragraph(f"<b>{s['name']}</b> ({s['ministry']})<br/>"
                      f"• <i>Benefits:</i> {s['benefits']}<br/>"
                      f"• <i>Steps:</i> {s['how_to_apply']}", body_style)
        ])
    
    scheme_table = Table(scheme_rows, colWidths=[7.0*inch])
    scheme_table.setStyle(TableStyle([
        ('PADDING', (0,0), (-1,-1), 5),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(scheme_table)
    
    # Build Document
    doc.build(story)
    buffer.seek(0)
    return buffer
