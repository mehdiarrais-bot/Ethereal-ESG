import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, Image, HRFlowable, PageBreak,
                                 KeepTogether)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from models import ESGRequest, ESGScores, AestheticTheme, ReportType

PALETTE = {
    AestheticTheme.CORPORATE_BLUE: {
        "primary": colors.HexColor("#1B3A6B"),
        "secondary": colors.HexColor("#2E86C1"),
        "accent": colors.HexColor("#F39C12"),
        "env": colors.HexColor("#27AE60"),
        "social": colors.HexColor("#2E86C1"),
        "gov": colors.HexColor("#8E44AD"),
        "light_bg": colors.HexColor("#EBF2FB"),
        "text": colors.HexColor("#2C3E50"),
    },
    AestheticTheme.GREEN_NATURE: {
        "primary": colors.HexColor("#1A5C38"),
        "secondary": colors.HexColor("#27AE60"),
        "accent": colors.HexColor("#F1C40F"),
        "env": colors.HexColor("#2ECC71"),
        "social": colors.HexColor("#3498DB"),
        "gov": colors.HexColor("#E67E22"),
        "light_bg": colors.HexColor("#D5F5E3"),
        "text": colors.HexColor("#1A3325"),
    },
    AestheticTheme.DARK_PREMIUM: {
        "primary": colors.HexColor("#1A1F28"),
        "secondary": colors.HexColor("#2D3748"),
        "accent": colors.HexColor("#F7C948"),
        "env": colors.HexColor("#3FB950"),
        "social": colors.HexColor("#58A6FF"),
        "gov": colors.HexColor("#BC8CFF"),
        "light_bg": colors.HexColor("#2D3748"),
        "text": colors.HexColor("#2C3E50"),
    },
    AestheticTheme.MINIMAL_WHITE: {
        "primary": colors.HexColor("#212121"),
        "secondary": colors.HexColor("#616161"),
        "accent": colors.HexColor("#FF6F00"),
        "env": colors.HexColor("#43A047"),
        "social": colors.HexColor("#1E88E5"),
        "gov": colors.HexColor("#8E24AA"),
        "light_bg": colors.HexColor("#F5F5F5"),
        "text": colors.HexColor("#212121"),
    },
}


# Design language per theme: fonts + header/cover/table styling
PDF_STYLES = {
    AestheticTheme.CORPORATE_BLUE: {
        "font": "Helvetica", "font_bold": "Helvetica-Bold", "font_italic": "Helvetica-Oblique",
        "header": "rule", "cover": "classic", "kpi": "filled", "uppercase": False,
        "title_size": 28, "h1_size": 20, "body_leading": 16,
    },
    AestheticTheme.GREEN_NATURE: {
        "font": "Helvetica", "font_bold": "Helvetica-Bold", "font_italic": "Helvetica-Oblique",
        "header": "banner", "cover": "banner", "kpi": "filled", "uppercase": False,
        "title_size": 30, "h1_size": 15, "body_leading": 17,
    },
    AestheticTheme.DARK_PREMIUM: {
        "font": "Times-Roman", "font_bold": "Times-Bold", "font_italic": "Times-Italic",
        "header": "goldrule", "cover": "luxe", "kpi": "dark", "uppercase": True,
        "title_size": 30, "h1_size": 19, "body_leading": 17,
    },
    AestheticTheme.MINIMAL_WHITE: {
        "font": "Helvetica", "font_bold": "Helvetica-Bold", "font_italic": "Helvetica-Oblique",
        "header": "minimal", "cover": "minimal", "kpi": "outline", "uppercase": True,
        "title_size": 34, "h1_size": 13, "body_leading": 18,
    },
}


def build_styles(pal: dict, ts: dict) -> dict:
    f, fb, fi = ts["font"], ts["font_bold"], ts["font_italic"]
    return {
        "title": ParagraphStyle("title", fontSize=ts["title_size"], textColor=pal["primary"],
                                 spaceAfter=8, fontName=fb, alignment=TA_LEFT),
        "h1": ParagraphStyle("h1", fontSize=ts["h1_size"], textColor=pal["primary"],
                              spaceAfter=6, spaceBefore=18, fontName=fb),
        "h1_light": ParagraphStyle("h1_light", fontSize=ts["h1_size"], textColor=colors.white,
                                    fontName=fb),
        "h2": ParagraphStyle("h2", fontSize=13, textColor=pal["secondary"],
                              spaceAfter=4, spaceBefore=12, fontName=fb),
        "body": ParagraphStyle("body", fontSize=10, textColor=pal["text"],
                                spaceAfter=6, fontName=f, leading=ts["body_leading"],
                                alignment=TA_JUSTIFY),
        "bullet": ParagraphStyle("bullet", fontSize=10, textColor=pal["text"],
                                  spaceAfter=4, fontName=f, leftIndent=16,
                                  leading=14),
        "kpi_label": ParagraphStyle("kpi_label", fontSize=9, textColor=pal["secondary"],
                                     fontName=fb, alignment=TA_CENTER),
        "kpi_value": ParagraphStyle("kpi_value", fontSize=22, textColor=pal["primary"],
                                     fontName=fb, alignment=TA_CENTER),
        "caption": ParagraphStyle("caption", fontSize=8, textColor=colors.grey,
                                   fontName=fi, alignment=TA_CENTER),
        "footer": ParagraphStyle("footer", fontSize=8, textColor=colors.grey,
                                  fontName=fi, alignment=TA_CENTER),
    }


def section_header(story, title, color, pal, styles, ts):
    """Themed section heading: rule / banner / goldrule / minimal."""
    if ts["uppercase"]:
        title = title.upper()
    mode = ts["header"]
    if mode == "banner":
        # Green Nature: full-width colored banner with white text
        t = Table([[Paragraph(title, styles["h1_light"])]], colWidths=[17 * cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), color),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('ROUNDEDCORNERS', [6, 6, 6, 6]),
        ]))
        story.append(Spacer(1, 0.4 * cm))
        story.append(t)
    elif mode == "goldrule":
        # Dark Premium: serif heading + thin gold rule
        story.append(Paragraph(title, styles["h1"]))
        story.append(HRFlowable(width="100%", thickness=0.8, color=pal["accent"]))
    elif mode == "minimal":
        # Minimal: small uppercase spaced heading + thin grey rule
        story.append(Paragraph(f'<font color="#{color.hexval()[2:]}">■</font>&nbsp;&nbsp;{title}',
                               styles["h1"]))
        story.append(HRFlowable(width="30%", thickness=0.7,
                                color=colors.HexColor("#BDBDBD"), hAlign='LEFT'))
    else:
        # Corporate: classic heading + thick colored rule
        story.append(Paragraph(title, styles["h1"]))
        story.append(HRFlowable(width="100%", thickness=2, color=color))
    story.append(Spacer(1, 0.3 * cm))


def score_to_color(score: float, pal: dict) -> colors.Color:
    if score >= 75:
        return pal["env"]
    elif score >= 50:
        return pal["accent"]
    return colors.HexColor("#E74C3C")


def kpi_table(kpi_list, pal, ts):
    kpi_style = ts["kpi"]
    value_color = colors.white if kpi_style == "dark" else pal["primary"]
    label_color = pal["accent"] if kpi_style == "dark" else pal["secondary"]

    data = []
    row = []
    for i, (label, value) in enumerate(kpi_list):
        cell_content = [Paragraph(str(value), ParagraphStyle(
            "kv", fontSize=18, fontName=ts["font_bold"],
            textColor=value_color, alignment=TA_CENTER)),
            Paragraph(label, ParagraphStyle(
                "kl", fontSize=9, fontName=ts["font"],
                textColor=label_color, alignment=TA_CENTER))]
        row.append(cell_content)
        if len(row) == 3:
            data.append(row)
            row = []
    if row:
        while len(row) < 3:
            row.append([Paragraph("", ParagraphStyle("empty", fontSize=10))])
        data.append(row)

    t = Table(data, colWidths=[5.5 * cm, 5.5 * cm, 5.5 * cm])
    if kpi_style == "dark":
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#1A1F28")),
            ('BOX', (0, 0), (-1, -1), 0.5, pal["accent"]),
            ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#3A4250")),
            ('ROWPADDING', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
    elif kpi_style == "outline":
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.7, colors.HexColor("#BDBDBD")),
            ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#E0E0E0")),
            ('ROWPADDING', (0, 0), (-1, -1), 14),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
    else:
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), pal["light_bg"]),
            ('BOX', (0, 0), (-1, -1), 0.5, pal["secondary"]),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
            ('ROWPADDING', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
    return t


def score_bar_table(env_s, soc_s, gov_s, total, pal):
    def bar_cell(label, score, color):
        bar_width = int(score * 1.2)
        bar_str = "█" * (bar_width // 10) + "░" * (12 - bar_width // 10)
        return [
            Paragraph(f"<b>{label}</b>", ParagraphStyle(
                "bl", fontSize=10, fontName="Helvetica-Bold",
                textColor=pal["text"])),
            Paragraph(f'<font color="#{color.hexval()[2:]}">{"█" * int(score // 8)}</font>',
                      ParagraphStyle("bv", fontSize=12, fontName="Helvetica")),
            Paragraph(f"<b>{score:.1f}/100</b>", ParagraphStyle(
                "bs", fontSize=12, fontName="Helvetica-Bold",
                textColor=color, alignment=TA_RIGHT)),
        ]

    data = [
        bar_cell("Environnement", env_s, pal["env"]),
        bar_cell("Social", soc_s, pal["social"]),
        bar_cell("Gouvernance", gov_s, pal["gov"]),
        bar_cell("Score ESG Global", total, pal["accent"]),
    ]
    t = Table(data, colWidths=[5 * cm, 8 * cm, 3.5 * cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), pal["light_bg"]),
        ('ROWPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.white),
        ('BACKGROUND', (0, 3), (-1, 3), pal["primary"]),
        ('TEXTCOLOR', (0, 3), (-1, 3), colors.white),
    ]))
    return t


def generate_pdf_report(request: ESGRequest, scores: ESGScores, content: dict,
                         chart_images: dict) -> bytes:
    buf = io.BytesIO()
    pal = PALETTE.get(request.aesthetic_theme, PALETTE[AestheticTheme.CORPORATE_BLUE])
    ts = PDF_STYLES.get(request.aesthetic_theme, PDF_STYLES[AestheticTheme.CORPORATE_BLUE])
    styles = build_styles(pal, ts)

    doc = SimpleDocTemplate(buf, pagesize=A4,
                             leftMargin=2 * cm, rightMargin=2 * cm,
                             topMargin=2 * cm, bottomMargin=2 * cm)
    story = []

    # ── Cover (varies per theme) ──────────────────────────────────────────
    type_labels = {
        "white_paper": "Livre Blanc ESG / RSE",
        "full_report": "Rapport ESG Complet",
        "executive_summary_pdf": "Synthèse Exécutive ESG",
    }
    type_label = type_labels.get(request.report_type.value, "Rapport ESG")
    meta_line = f"Exercice {request.company.reporting_year}  •  Secteur : {request.company.sector}  •  {request.company.country}"

    if ts["cover"] == "luxe":
        # Dark Premium: full dark block, centered serif, gold accents
        cover_cells = [
            [Paragraph(type_label.upper(), ParagraphStyle(
                "ck", fontSize=11, fontName=ts["font"], textColor=pal["accent"],
                alignment=TA_CENTER, spaceAfter=14))],
            [Paragraph(request.company.name.upper(), ParagraphStyle(
                "ct", fontSize=32, fontName=ts["font_bold"], textColor=colors.white,
                alignment=TA_CENTER, leading=38, spaceAfter=10))],
            [Paragraph(meta_line, ParagraphStyle(
                "cm", fontSize=10, fontName=ts["font_italic"],
                textColor=colors.HexColor("#8B949E"), alignment=TA_CENTER))],
            [Paragraph(f"—  {scores.rating}  —", ParagraphStyle(
                "cr", fontSize=26, fontName=ts["font_bold"], textColor=pal["accent"],
                alignment=TA_CENTER, spaceBefore=16))],
        ]
        cover_t = Table(cover_cells, colWidths=[17 * cm])
        cover_t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#0D1117")),
            ('BOX', (0, 0), (-1, -1), 1, pal["accent"]),
            ('TOPPADDING', (0, 0), (-1, 0), 36),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 36),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ]))
        story.append(Spacer(1, 2 * cm))
        story.append(cover_t)
        story.append(Spacer(1, 0.8 * cm))
    elif ts["cover"] == "banner":
        # Green Nature: big colored banner + light band
        banner = Table([[Paragraph(request.company.name, ParagraphStyle(
            "ct", fontSize=30, fontName=ts["font_bold"], textColor=colors.white,
            leading=36))]], colWidths=[17 * cm])
        banner.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), pal["primary"]),
            ('TOPPADDING', (0, 0), (-1, -1), 28),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 28),
            ('LEFTPADDING', (0, 0), (-1, -1), 18),
        ]))
        sub = Table([[Paragraph(f"{type_label} — {meta_line}", ParagraphStyle(
            "cs", fontSize=10, fontName=ts["font"], textColor=pal["primary"]))]],
            colWidths=[17 * cm])
        sub.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), pal["light_bg"]),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 18),
        ]))
        story.append(Spacer(1, 1.5 * cm))
        story.append(banner)
        story.append(sub)
        story.append(Spacer(1, 0.8 * cm))
    elif ts["cover"] == "minimal":
        # Minimal: whitespace, small kicker, huge title, thin rule
        story.append(Spacer(1, 3 * cm))
        story.append(Paragraph(type_label.upper(), ParagraphStyle(
            "ck", fontSize=10, fontName=ts["font_bold"],
            textColor=colors.HexColor("#9E9E9E"), spaceAfter=10)))
        story.append(Paragraph(request.company.name, styles["title"]))
        story.append(Spacer(1, 0.2 * cm))
        story.append(HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#BDBDBD")))
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph(meta_line, styles["body"]))
        story.append(Spacer(1, 1 * cm))
    else:
        # Corporate: classic left-aligned with thick accent rule
        story.append(Spacer(1, 2 * cm))
        story.append(Paragraph(request.company.name.upper(), styles["title"]))
        story.append(HRFlowable(width="100%", thickness=4, color=pal["accent"]))
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph(type_label, styles["h1"]))
        story.append(Paragraph(meta_line, styles["body"]))
        story.append(Spacer(1, 0.5 * cm))

    # Score summary table
    score_data = [
        [Paragraph("Score Environnemental", styles["kpi_label"]),
         Paragraph("Score Social", styles["kpi_label"]),
         Paragraph("Score Gouvernance", styles["kpi_label"]),
         Paragraph("Score ESG Global", styles["kpi_label"])],
        [Paragraph(f"<font color='#{pal['env'].hexval()[2:]}'><b>{scores.environmental_score:.1f}</b></font>",
                   ParagraphStyle("sv", fontSize=26, fontName="Helvetica-Bold",
                                  alignment=TA_CENTER)),
         Paragraph(f"<font color='#{pal['social'].hexval()[2:]}'><b>{scores.social_score:.1f}</b></font>",
                   ParagraphStyle("sv2", fontSize=26, fontName="Helvetica-Bold",
                                  alignment=TA_CENTER)),
         Paragraph(f"<font color='#{pal['gov'].hexval()[2:]}'><b>{scores.governance_score:.1f}</b></font>",
                   ParagraphStyle("sv3", fontSize=26, fontName="Helvetica-Bold",
                                  alignment=TA_CENTER)),
         Paragraph(f"<font color='#{pal['accent'].hexval()[2:]}'><b>{scores.total_esg_score:.1f}</b></font>",
                   ParagraphStyle("sv4", fontSize=26, fontName="Helvetica-Bold",
                                  alignment=TA_CENTER))],
        [Paragraph("/100", styles["caption"]), Paragraph("/100", styles["caption"]),
         Paragraph("/100", styles["caption"]),
         Paragraph(f"Note : {scores.rating}", ParagraphStyle(
             "rating", fontSize=12, fontName="Helvetica-Bold",
             textColor=pal["accent"], alignment=TA_CENTER))],
    ]
    score_table = Table(score_data, colWidths=[4 * cm] * 4)
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), pal["light_bg"]),
        ('BACKGROUND', (3, 0), (3, -1), pal["primary"]),
        ('TEXTCOLOR', (3, 0), (3, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, pal["secondary"]),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('ROWPADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.5 * cm))

    # Charts
    if "radar" in chart_images:
        img = Image(io.BytesIO(chart_images["radar"]), width=7 * cm, height=7 * cm)
        img.hAlign = 'CENTER'
        story.append(img)
        story.append(Paragraph("Profil ESG — Radar des piliers", styles["caption"]))
        story.append(Spacer(1, 0.3 * cm))

    story.append(PageBreak())

    # ── Executive Summary ──────────────────────────────────────────────────
    section_header(story, "1. Synthèse Exécutive", pal["secondary"], pal, styles, ts)

    exec_text = content.get("executive_summary",
        f"{request.company.name} présente son rapport ESG pour l'exercice {request.company.reporting_year}. "
        f"L'analyse des données extra-financières révèle un score ESG global de {scores.total_esg_score}/100, "
        f"correspondant à une notation {scores.rating}. Ce résultat reflète les engagements de l'entreprise "
        "en matière de responsabilité environnementale, sociale et de gouvernance d'entreprise."
    )
    story.append(Paragraph(exec_text, styles["body"]))
    story.append(Spacer(1, 0.5 * cm))

    # ── Environnement ─────────────────────────────────────────────────────
    section_header(story, "2. Pilier Environnemental", pal["env"], pal, styles, ts)
    story.append(Paragraph(
        f"Score environnemental : <b>{scores.environmental_score:.1f}/100</b>", styles["h2"]))

    env_text = content.get("environmental",
        "L'analyse environnementale couvre les émissions de gaz à effet de serre, "
        "la consommation d'énergie et d'eau, la gestion des déchets et les initiatives biodiversité."
    )
    story.append(Paragraph(env_text, styles["body"]))

    env = request.environmental
    env_kpis = []
    if env.co2_emissions_tonnes: env_kpis.append(("CO₂ total (t)", f"{env.co2_emissions_tonnes:,.0f}"))
    if env.renewable_energy_percent: env_kpis.append(("Renouvelable %", f"{env.renewable_energy_percent:.1f}%"))
    if env.energy_consumption_mwh: env_kpis.append(("Énergie (MWh)", f"{env.energy_consumption_mwh:,.0f}"))
    if env.water_consumption_m3: env_kpis.append(("Eau (m³)", f"{env.water_consumption_m3:,.0f}"))
    if env.waste_recycled_percent: env_kpis.append(("Recyclage %", f"{env.waste_recycled_percent:.1f}%"))
    if env.scope1_emissions: env_kpis.append(("Scope 1 (t)", f"{env.scope1_emissions:,.0f}"))
    if env.scope2_emissions: env_kpis.append(("Scope 2 (t)", f"{env.scope2_emissions:,.0f}"))
    if env.scope3_emissions: env_kpis.append(("Scope 3 (t)", f"{env.scope3_emissions:,.0f}"))

    if env_kpis:
        story.append(Spacer(1, 0.3 * cm))
        story.append(kpi_table(env_kpis, pal, ts))

    if "emissions_pie" in chart_images:
        story.append(Spacer(1, 0.3 * cm))
        img = Image(io.BytesIO(chart_images["emissions_pie"]), width=8 * cm, height=7 * cm)
        img.hAlign = 'CENTER'
        story.append(img)
        story.append(Paragraph("Répartition des émissions par scope", styles["caption"]))

    story.append(Spacer(1, 0.5 * cm))

    # ── Social ────────────────────────────────────────────────────────────
    section_header(story, "3. Pilier Social", pal["social"], pal, styles, ts)
    story.append(Paragraph(
        f"Score social : <b>{scores.social_score:.1f}/100</b>", styles["h2"]))

    soc_text = content.get("social",
        "La performance sociale englobe la gestion des ressources humaines, la diversité, "
        "la sécurité au travail, la formation et l'engagement avec les parties prenantes."
    )
    story.append(Paragraph(soc_text, styles["body"]))

    soc = request.social
    soc_kpis = []
    if soc.total_employees: soc_kpis.append(("Effectif", f"{soc.total_employees:,}"))
    if soc.female_employees_percent: soc_kpis.append(("Femmes %", f"{soc.female_employees_percent:.1f}%"))
    if soc.employee_turnover_percent: soc_kpis.append(("Turnover %", f"{soc.employee_turnover_percent:.1f}%"))
    if soc.training_hours_per_employee: soc_kpis.append(("Formation (h)", f"{soc.training_hours_per_employee:.0f}"))
    if soc.accident_frequency_rate: soc_kpis.append(("Taux freq. acc.", f"{soc.accident_frequency_rate:.2f}"))
    if soc.customer_satisfaction_score: soc_kpis.append(("Satisfaction /10", f"{soc.customer_satisfaction_score:.1f}"))

    if soc_kpis:
        story.append(Spacer(1, 0.3 * cm))
        story.append(kpi_table(soc_kpis, pal, ts))

    story.append(Spacer(1, 0.5 * cm))

    # ── Gouvernance ──────────────────────────────────────────────────────
    section_header(story, "4. Pilier Gouvernance", pal["gov"], pal, styles, ts)
    story.append(Paragraph(
        f"Score gouvernance : <b>{scores.governance_score:.1f}/100</b>", styles["h2"]))

    gov_text = content.get("governance",
        "La gouvernance évalue la qualité de la direction, l'indépendance du conseil, "
        "l'éthique des affaires, la cybersécurité et les mécanismes de contrôle interne."
    )
    story.append(Paragraph(gov_text, styles["body"]))

    gov = request.governance
    gov_kpis = []
    if gov.board_members: gov_kpis.append(("Membres CA", str(gov.board_members)))
    if gov.female_board_percent: gov_kpis.append(("Femmes CA %", f"{gov.female_board_percent:.1f}%"))
    if gov.independent_board_percent: gov_kpis.append(("Indépendants %", f"{gov.independent_board_percent:.1f}%"))
    if gov.csr_budget_eur: gov_kpis.append(("Budget RSE (€)", f"{gov.csr_budget_eur:,.0f}"))
    gov_kpis.append(("Audit ESG", "✓ Oui" if gov.esg_audit_conducted else "✗ Non"))
    gov_kpis.append(("Comité durable", "✓ Oui" if gov.sustainability_committee else "✗ Non"))

    if gov_kpis:
        story.append(Spacer(1, 0.3 * cm))
        story.append(kpi_table(gov_kpis, pal, ts))

    story.append(PageBreak())

    # ── Forces & Faiblesses ───────────────────────────────────────────────
    section_header(story, "5. Analyse Stratégique", pal["accent"], pal, styles, ts)

    story.append(Paragraph("Points forts identifiés", styles["h2"]))
    for s in scores.strengths:
        story.append(Paragraph(f"✅  {s}", styles["bullet"]))

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("Axes d'amélioration", styles["h2"]))
    for w in scores.weaknesses:
        story.append(Paragraph(f"⚠️  {w}", styles["bullet"]))

    if request.include_recommendations:
        story.append(Spacer(1, 0.4 * cm))
        section_header(story, "6. Recommandations Prioritaires", pal["accent"], pal, styles, ts)
        for i, rec in enumerate(scores.recommendations, 1):
            story.append(Paragraph(f"<b>{i}.</b>  {rec}", styles["bullet"]))

    # ── Alignement référentiels ───────────────────────────────────────────
    story.append(Spacer(1, 0.5 * cm))
    section_header(story, "7. Cadres de Référence & Alignement ODD", pal["secondary"], pal, styles, ts)

    ref_text = (
        "Ce rapport s'inscrit dans les cadres de référence suivants : <b>GRI Standards</b> (Global Reporting Initiative), "
        "<b>TCFD</b> (Task Force on Climate-related Financial Disclosures), <b>CSRD</b> (Corporate Sustainability Reporting Directive), "
        "<b>SFDR</b> (Sustainable Finance Disclosure Regulation) et les normes <b>ISO 14001 / 26000</b>. "
        "L'organisation contribue aux Objectifs de Développement Durable (ODD) de l'ONU, notamment les ODD 7, 8, 10, 12, 13 et 16."
    )
    story.append(Paragraph(ref_text, styles["body"]))

    # ── Conclusion ────────────────────────────────────────────────────────
    story.append(PageBreak())
    section_header(story, "8. Conclusion", pal["primary"], pal, styles, ts)

    conclusion = content.get("conclusion",
        f"{request.company.name} démontre une démarche ESG globale avec un score de "
        f"{scores.total_esg_score}/100 (note {scores.rating}). L'organisation s'engage "
        "à poursuivre ses efforts de transformation durable et à maintenir une transparence "
        "totale dans son reporting extra-financier, conformément aux meilleures pratiques internationales."
    )
    story.append(Paragraph(conclusion, styles["body"]))

    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=pal["secondary"]))
    story.append(Paragraph(
        f"© {request.company.reporting_year} {request.company.name} — Document généré automatiquement par la Plateforme ESG",
        styles["footer"]))

    # ── Section spécifique White Paper : Vision Stratégique ──────────────
    if request.report_type.value == "white_paper":
        story.append(Spacer(1, 0.5 * cm))
        section_header(story, "9. Vision Stratégique & Perspectives", pal["accent"], pal, styles, ts)
        story.append(Paragraph(
            "Ce livre blanc a vocation à documenter la trajectoire ESG de l'organisation sur le long terme. "
            "Il constitue un document de référence stratégique, destiné à éclairer les décisions "
            "d'investissement et à démontrer la maturité extra-financière de l'entreprise. "
            "Les engagements formulés dans ce document s'inscrivent dans une perspective de transformation "
            "durable, alignée sur l'Accord de Paris et les Objectifs de Développement Durable (ODD).",
            styles["body"]))
        story.append(Spacer(1, 0.3 * cm))
        # Objectifs 2027
        obj_data = [
            [Paragraph("<b>Horizon 2027 — Objectifs ESG cibles</b>",
                       ParagraphStyle("ot", fontSize=11, fontName="Helvetica-Bold",
                                      textColor=pal["primary"]))],
        ]
        pillars_obj = [
            ("Environnement", f"Score E cible : {min(100, scores.environmental_score + 15):.0f}/100 | +50% renouvelable | Scope 3 mesuré"),
            ("Social", f"Score S cible : {min(100, scores.social_score + 10):.0f}/100 | Parité 40% | 30h formation/an"),
            ("Gouvernance", f"Score G cible : {min(100, scores.governance_score + 5):.0f}/100 | Audit annuel | Comité durable"),
        ]
        for label, obj in pillars_obj:
            p = story[-1] if False else None
            story.append(Paragraph(f"<b>• {label} :</b> {obj}", styles["bullet"]))

    doc.build(story)
    buf.seek(0)
    return buf.read()
