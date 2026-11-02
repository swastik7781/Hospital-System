import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.models.prescription import Prescription


def generate_prescription_pdf(prescription: Prescription) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=colors.HexColor("#0D9488"),
        leading=24,
    )
    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.HexColor("#64748B"),
        leading=14,
    )
    section_title = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=10,
        spaceAfter=6,
    )
    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
    )
    rx_symbol_style = ParagraphStyle(
        "RxStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        textColor=colors.HexColor("#0D9488"),
    )

    story = []

    # Header
    story.append(Paragraph("UTKAL HOSPITAL & MEDICAL RESEARCH CENTRE", title_style))
    story.append(Paragraph("Niladri Vihar, Chandrasekharpur, Bhubaneswar, Odisha 751021 | Helpline: +91 674 274 0100 | contact@utkalhospital.com", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0D9488"), spaceBefore=5, spaceAfter=15))

    # Doctor & Patient Info Table
    doc_name = prescription.doctor.full_name if prescription.doctor else "Medical Staff"
    doc_spec = prescription.doctor.specialization if prescription.doctor else "General Practice"
    doc_qual = prescription.doctor.qualification if prescription.doctor else "MBBS"
    
    patient_name = prescription.patient.full_name if prescription.patient else "Patient"
    patient_age = f"{prescription.patient.gender}, DOB: {prescription.patient.date_of_birth}" if prescription.patient else "N/A"
    patient_phone = prescription.patient.phone if prescription.patient else "N/A"

    info_data = [
        [
            Paragraph(f"<b>Prescribing Doctor:</b><br/>{doc_name}<br/>{doc_spec} ({doc_qual})", normal_style),
            Paragraph(f"<b>Patient Details:</b><br/>{patient_name}<br/>{patient_age}<br/>Phone: {patient_phone}", normal_style),
            Paragraph(f"<b>Prescription ID:</b> #{prescription.id}<br/><b>Date:</b> {prescription.prescription_date}<br/><b>Visit Ref:</b> #{prescription.visit_id or 'N/A'}", normal_style)
        ]
    ]
    info_table = Table(info_data, colWidths=[180, 200, 150])
    info_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("PADDING", (0, 0), (-1, -1), 10),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 15))

    # Rx Symbol & Medications
    story.append(Paragraph("℞ Medications", rx_symbol_style))
    story.append(Spacer(1, 8))

    med_headers = [
        Paragraph("<b>Medicine</b>", normal_style),
        Paragraph("<b>Dosage</b>", normal_style),
        Paragraph("<b>Frequency</b>", normal_style),
        Paragraph("<b>Duration</b>", normal_style),
        Paragraph("<b>Qty</b>", normal_style),
        Paragraph("<b>Notes</b>", normal_style),
    ]
    med_rows = [med_headers]

    for item in prescription.items:
        med_rows.append([
            Paragraph(f"<b>{item.medicine_name}</b>", normal_style),
            Paragraph(item.dosage, normal_style),
            Paragraph(item.frequency, normal_style),
            Paragraph(item.duration, normal_style),
            Paragraph(str(item.quantity), normal_style),
            Paragraph(item.notes or "-", normal_style),
        ])

    if len(med_rows) == 1:
        med_rows.append([Paragraph("No items prescribed", normal_style), "", "", "", "", ""])

    med_table = Table(med_rows, colWidths=[130, 70, 110, 70, 40, 110])
    med_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E6FFFA")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0D9488")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(med_table)
    story.append(Spacer(1, 15))

    # Instructions
    if prescription.instructions:
        story.append(Paragraph("Special Instructions & Advice", section_title))
        story.append(Paragraph(prescription.instructions, normal_style))
        story.append(Spacer(1, 20))

    # Doctor Signature Footer
    story.append(Spacer(1, 30))
    sig_data = [
        ["", Paragraph("____________________________<br/><b>Doctor's Signature & Stamp</b>", normal_style)]
    ]
    sig_table = Table(sig_data, colWidths=[330, 200])
    sig_table.setStyle(TableStyle([
        ("ALIGN", (1, 0), (1, 0), "CENTER"),
    ]))
    story.append(sig_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
