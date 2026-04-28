from io import BytesIO
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def generate_audit_pdf(audit):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"Audit Report - {audit.title}",
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    header_style = ParagraphStyle(
        'Header', parent=styles['Title'],
        fontSize=22, textColor=colors.HexColor('#0d1b2a'),
        spaceAfter=4, alignment=TA_CENTER
    )
    sub_style = ParagraphStyle(
        'Sub', parent=styles['Normal'],
        fontSize=10, textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER, spaceAfter=12
    )
    story.append(Paragraph('AuditShield', header_style))
    story.append(Paragraph('OFFICIAL AUDIT REPORT', sub_style))
    story.append(HRFlowable(width="100%", thickness=2,
                             color=colors.HexColor('#2563eb')))
    story.append(Spacer(1, 0.4 * cm))

    # ── Audit Info Table ──────────────────────────────────────────────────────
    label_style = ParagraphStyle('Label', parent=styles['Normal'],
                                 fontSize=9,
                                 textColor=colors.HexColor('#64748b'))
    value_style = ParagraphStyle('Value', parent=styles['Normal'],
                                 fontSize=10,
                                 textColor=colors.HexColor('#0d1b2a'),
                                 fontName='Helvetica-Bold')

    auditor_name = 'Unassigned'
    if audit.assigned_auditor:
        auditor_name = (audit.assigned_auditor.get_full_name()
                        or audit.assigned_auditor.username)

    created_by_name = 'Unknown'
    if audit.created_by:
        created_by_name = (audit.created_by.get_full_name()
                           or audit.created_by.username)

    info_data = [
        [Paragraph('Audit Title', label_style),
         Paragraph(str(audit.title), value_style),
         Paragraph('Department', label_style),
         Paragraph(str(audit.department.name), value_style)],
        [Paragraph('Start Date', label_style),
         Paragraph(str(audit.start_date), value_style),
         Paragraph('End Date', label_style),
         Paragraph(str(audit.end_date), value_style)],
        [Paragraph('Assigned Auditor', label_style),
         Paragraph(auditor_name, value_style),
         Paragraph('Status', label_style),
         Paragraph(audit.get_status_display(), value_style)],
        [Paragraph('Created By', label_style),
         Paragraph(created_by_name, value_style),
         Paragraph('Report Date', label_style),
         Paragraph(str(date.today()), value_style)],
    ]
    info_table = Table(info_data, colWidths=[3.5 * cm, 6 * cm, 3.5 * cm, 6 * cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Summary Section ───────────────────────────────────────────────────────
    section_style = ParagraphStyle(
        'Section', parent=styles['Heading2'],
        fontSize=12, textColor=colors.HexColor('#1b2a4a'),
        spaceBefore=10, spaceAfter=6,
        borderPad=4
    )
    findings = audit.findings.all()
    total_f = findings.count()
    open_f = findings.filter(status='open').count()
    inprog_f = findings.filter(status='in_progress').count()
    closed_f = findings.filter(status='closed').count()
    critical_f = findings.filter(severity='critical').count()
    today = date.today()
    overdue_f = sum(
        1 for f in findings
        if f.target_closure_date < today and f.status != 'closed'
    )

    story.append(Paragraph('Executive Summary', section_style))
    summary_data = [
        ['Total Findings', str(total_f),
         'Critical Findings', str(critical_f)],
        ['Open', str(open_f),
         'Overdue', str(overdue_f)],
        ['In Progress', str(inprog_f),
         'Closed', str(closed_f)],
    ]
    summary_table = Table(summary_data,
                          colWidths=[4 * cm, 4.5 * cm, 4 * cm, 4.5 * cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#bfdbfe')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#bfdbfe')),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Findings Table ────────────────────────────────────────────────────────
    story.append(Paragraph('Findings Detail', section_style))
    findings_header = ['#', 'Finding Title', 'Severity',
                       'Status', 'Target Date', 'Overdue']
    findings_rows = [findings_header]

    sev_colors = {
        'critical': colors.HexColor('#fee2e2'),
        'high':     colors.HexColor('#ffedd5'),
        'medium':   colors.HexColor('#fef9c3'),
        'low':      colors.HexColor('#dcfce7'),
    }
    row_bg_styles = []

    for i, f in enumerate(findings, start=1):
        is_overdue = f.target_closure_date < today and f.status != 'closed'
        findings_rows.append([
            str(i),
            str(f.title)[:60],
            f.severity.upper(),
            f.get_status_display(),
            str(f.target_closure_date),
            'YES' if is_overdue else 'No',
        ])
        bg = sev_colors.get(f.severity, colors.white)
        row_bg_styles.append(
            ('BACKGROUND', (0, i), (-1, i), bg)
        )

    col_widths = [1 * cm, 6.5 * cm, 2.5 * cm, 2.5 * cm, 3 * cm, 2 * cm]
    f_table = Table(findings_rows, colWidths=col_widths, repeatRows=1)
    base_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1b2a4a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (5, 0), (5, -1), 'CENTER'),
    ]
    f_table.setStyle(TableStyle(base_style + row_bg_styles))
    story.append(f_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Recommendations ───────────────────────────────────────────────────────
    story.append(Paragraph('Recommendations', section_style))
    rec_style = ParagraphStyle('Rec', parent=styles['Normal'],
                               fontSize=9, spaceAfter=8,
                               leftIndent=10)
    title_rec_style = ParagraphStyle('RecTitle', parent=styles['Normal'],
                                     fontSize=9, fontName='Helvetica-Bold',
                                     textColor=colors.HexColor('#1b2a4a'))
    for f in findings:
        story.append(Paragraph(f'• {f.title}', title_rec_style))
        story.append(Paragraph(
            str(f.recommendation) if f.recommendation else 'No recommendation provided.',
            rec_style
        ))

    # ── Footer ────────────────────────────────────────────────────────────────
    def add_footer(canvas_obj, doc_obj):
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 7)
        canvas_obj.setFillColor(colors.HexColor('#94a3b8'))
        w, h = A4
        footer_text = (
            f'Generated by AuditShield  |  Confidential  |  '
            f'{date.today()}  |  Page {doc_obj.page}'
        )
        canvas_obj.drawCentredString(w / 2, 1 * cm, footer_text)
        canvas_obj.restoreState()

    # ── Build PDF ──────────────────────────────────────────────────────────────
    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)

    # CRITICAL: rewind buffer before returning
    buffer.seek(0)
    return buffer
