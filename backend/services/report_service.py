import os
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)
from backend.utils.config import REPORTS_DIR
from backend.models.schemas import (
    ContractAnalysisResponse,
    RiskLevel,
    ImportanceLevel
)

def generate_pdf_report(analysis_data: ContractAnalysisResponse) -> str:
    """
    Generates a clean, professional, executive PDF report for the analyzed contract using ReportLab.
    Returns the file path of the generated PDF.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    clean_sess = "".join([c if c.isalnum() else "_" for c in analysis_data.session_id])
    pdf_filename = f"ClauseClear_Report_{clean_sess[:20]}.pdf"
    pdf_path = REPORTS_DIR / pdf_filename

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1E293B"),
        fontName="Helvetica-Bold",
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#64748B"),
        fontName="Helvetica",
        spaceAfter=12
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#0F172A"),
        fontName="Helvetica-Bold",
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155"),
        fontName="Helvetica"
    )
    bold_body = ParagraphStyle(
        'BoldBody',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#0F172A"),
        fontName="Helvetica-Bold"
    )
    alert_style = ParagraphStyle(
        'AlertText',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#991B1B"),
        fontName="Helvetica"
    )
    alt_wording_style = ParagraphStyle(
        'AltWording',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#166534"),
        fontName="Helvetica-Oblique"
    )
    disclaimer_style = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Normal'],
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#64748B"),
        fontName="Helvetica-Oblique"
    )

    elements = []

    # 1. Header Banner
    elements.append(Paragraph("CLAUSECLEAR — Contract Analysis & Negotiation Brief", title_style))
    elements.append(Paragraph(f"AI-Powered Contract Review • Srijan Hackathon • Generated on {datetime.now().strftime('%d %B %Y, %H:%M')}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3B82F6"), spaceAfter=10))

    # 2. Document & Fairness Summary Table
    score = analysis_data.fairness.fairness_score
    score_color = "#16A34A" if score >= 85 else ("#CA8A04" if score >= 70 else ("#EA580C" if score >= 50 else "#DC2626"))

    meta_table_data = [
        [
            Paragraph(f"<b>Document:</b> {analysis_data.filename}", body_style),
            Paragraph(f"<b>Contract Type:</b> {analysis_data.contract_type.upper()}", body_style),
            Paragraph(f"<b>Fairness Score:</b> <font color='{score_color}' size='+2'><b>{score}/100</b></font> ({analysis_data.fairness.fairness_label})", body_style)
        ],
        [
            Paragraph(f"<b>Total Clauses:</b> {len(analysis_data.clauses)}", body_style),
            Paragraph(f"<b>Risk Breakdown:</b> <font color='#16A34A'><b>{analysis_data.fairness.green_count} Green</b></font> | <font color='#CA8A04'><b>{analysis_data.fairness.yellow_count} Yellow</b></font> | <font color='#DC2626'><b>{analysis_data.fairness.red_count} Red</b></font>", body_style),
            Paragraph(f"<b>Missing Protections:</b> <b>{len(analysis_data.missing_protections)}</b> detected", body_style)
        ]
    ]

    meta_table = Table(meta_table_data, colWidths=[2.2*inch, 2.5*inch, 2.8*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 10))

    # 3. Executive AI Summary
    elements.append(Paragraph("Executive Summary", section_heading))
    elements.append(Paragraph(f"<b>Overview:</b> {analysis_data.executive_summary}", body_style))
    elements.append(Spacer(1, 8))

    # 4. High-Risk (RED) Clauses Section
    red_clauses = [
        (c, a) for c in analysis_data.clauses for a in analysis_data.analysis
        if c.id == a.clause_id and a.risk_level == RiskLevel.RED
    ]

    if red_clauses:
        elements.append(Paragraph(f"High-Risk Clauses Requiring Negotiation ({len(red_clauses)} Flagged)", section_heading))
        for cl, an in red_clauses:
            clause_content = [
                [
                    Paragraph(f"<font color='#DC2626'><b>[RED ALERT] {cl.title}</b> ({cl.id})</font>", bold_body)
                ],
                [
                    Paragraph(f"<b>Plain English:</b> {an.plain_english}", body_style)
                ],
                [
                    Paragraph(f"<b>Key Concern:</b> {an.key_concern}", alert_style)
                ]
            ]
            if an.suggested_alternative:
                clause_content.append([
                    Paragraph(f"<b>Negotiation Alternative:</b> \"{an.suggested_alternative}\"", alt_wording_style)
                ])

            clause_table = Table(clause_content, colWidths=[7.5*inch])
            clause_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF2F2")),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#FECACA")),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ]))
            elements.append(clause_table)
            elements.append(Spacer(1, 6))

    # 5. Caution (YELLOW) Clauses Section
    yellow_clauses = [
        (c, a) for c in analysis_data.clauses for a in analysis_data.analysis
        if c.id == a.clause_id and a.risk_level == RiskLevel.YELLOW
    ]

    if yellow_clauses:
        elements.append(Paragraph(f"Caution & Ambiguous Clauses ({len(yellow_clauses)} Flagged)", section_heading))
        for cl, an in yellow_clauses[:4]: # Show top 4
            clause_content = [
                [
                    Paragraph(f"<font color='#B45309'><b>[CAUTION] {cl.title}</b> ({cl.id})</font>", bold_body)
                ],
                [
                    Paragraph(f"<b>Plain English:</b> {an.plain_english}", body_style)
                ],
                [
                    Paragraph(f"<b>Recommended Action:</b> {an.recommended_user_action}", body_style)
                ]
            ]
            if an.suggested_alternative:
                clause_content.append([
                    Paragraph(f"<b>Suggested Wording:</b> \"{an.suggested_alternative}\"", alt_wording_style)
                ])

            clause_table = Table(clause_content, colWidths=[7.5*inch])
            clause_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFBEB")),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#FDE68A")),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ]))
            elements.append(clause_table)
            elements.append(Spacer(1, 6))

    # 6. Missing Protections Section
    if analysis_data.missing_protections:
        elements.append(Paragraph(f"Missing Standard Protections ({len(analysis_data.missing_protections)} Items)", section_heading))
        mp_rows = [
            [
                Paragraph("<b>Missing Protection</b>", bold_body),
                Paragraph("<b>Importance</b>", bold_body),
                Paragraph("<b>Why It Matters & Suggested Addition</b>", bold_body)
            ]
        ]
        for mp in analysis_data.missing_protections[:5]:
            imp_color = "#DC2626" if mp.importance == ImportanceLevel.HIGH else ("#D97706" if mp.importance == ImportanceLevel.MEDIUM else "#2563EB")
            mp_rows.append([
                Paragraph(f"<b>{mp.name}</b>", body_style),
                Paragraph(f"<font color='{imp_color}'><b>{mp.importance.value}</b></font>", body_style),
                Paragraph(f"{mp.reason}<br/><b>Recommendation:</b> {mp.recommendation or 'Add explicit terms.'}", body_style)
            ])

        mp_table = Table(mp_rows, colWidths=[2.2*inch, 1.0*inch, 4.3*inch])
        mp_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#FFFFFF")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(mp_table)
        elements.append(Spacer(1, 10))

    # 7. Legal Disclaimer Footer
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#CBD5E1"), spaceAfter=6))
    elements.append(Paragraph(
        "<b>LEGAL DISCLAIMER:</b> ClauseClear provides AI-generated educational information only and does NOT constitute formal legal advice or representation. For critical contractual, financial, or dispute decisions, consult a qualified advocate or attorney licensed in your jurisdiction.",
        disclaimer_style
    ))

    # Build Document
    doc.build(elements)
    return str(pdf_path)
