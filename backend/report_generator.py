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


def build_styles(pal: dict) -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", fontSize=28, textColor=pal["primary"],
                                 spaceAfter=8, fontName="Helvetica-Bold", alignment=TA_LEFT),
        "h1": ParagraphStyle("h1", fontSize=20, textColor=pal["primary"],
                              spaceAfter=6, spaceBefore=18, fontName="Helvetica-Bold"),
        "h2": ParagraphStyle("h2", fontSize=15, textColor=pal["secondary"],
                              spaceAfter=4, spaceBefore=12, fontName="Helvetica-Bold"),
        "body": ParagraphStyle("body", fontSize=10, textColor=pal["text"],
                                spaceAfter=6, fontName="Helvetica", leading=16,
                                alignment=TA_JUSTIFY),
        "bullet": ParagraphStyle("bullet", fontSize=10, textColor=pal["text"],
                                  spaceAfter=4, fontName="Helvetica", leftIndent=16,
                                  leading=14),
        "kpi_label": ParagraphStyle("kpi_label", fontSize=9, textColor=pal["secondary"],
                                     fontName="Helvetica-Bold", alignment=TA_CENTER),
        "kpi_value": ParagraphStyle("kpi_value", fontSize=22, textColor=pal["primary"],
                                     fontName="Helvetica-Bold", alignment=TA_CENTER),
        "caption": ParagraphStyle("caption", fontSize=8, textColor=colors.grey,
                                   fontName="Helvetica-Oblique", alignment=TA_CENTER),
        "cover_title": ParagraphStyle("cover_title", fontSize=36, textColor=colors.white,
                                       fontName="Helvetica-Bold", alignment=TA_LEFT, leading=44),
        "cover_sub": ParagraphStyle("cover_sub", fontSize=16, textColor=colors.HexColor("#AECAE8"),
                                     fontName="Helvetica", alignment=TA_LEFT),
        "score_label": ParagraphStyle("score_label", fontSize=11, textColor=pal["text"],
                                       fontName="Helvetica-Bold", alignment=TA_CENTER),
        "footer": ParagraphStyle("footer", fontSize=8, textColor=colors.grey,
                                  fontName="Helvetica-Oblique", alignment=TA_CENTER),
    }


def score_to_color(score: float, pal: dict) -> colors.Color:
    if score >= 75:
        return pal["env"]
    elif score >= 50:
        return pal["accent"]
    return colors.HexColor("#E74C3C")


def kpi_table(kpi_list, pal):
    data = []
    row = []
    for i, (label, value) in enumerate(kpi_list):
        cell_content = [Paragraph(str(value), ParagraphStyle(
            "kv", fontSize=18, fontName="Helvetica-Bold",
            textColor=pal["primary"], alignment=TA_CENTER)),
            Paragraph(label, ParagraphStyle(
                "kl", fontSize=9, fontName="Helvetica",
                textColor=pal["secondary"], alignment=TA_CENTER))]
        row.append(cell_content)
        if len(row) == 3:
            data.append(row)
            row = []
    if row:
        while len(row) < 3:
            row.append([Paragraph("", ParagraphStyle("empty", fontSize=10))])
        data.append(row)

    t = Table(data, colWidths=[5.5 * cm, 5.5 * cm, 5.5 * cm])
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
    styles = build_styles(pal)

    doc = SimpleDocTemplate(buf, pagesize=A4,
                             leftMargin=2 * cm, rightMargin=2 * cm,
                             topMargin=2 * cm, bottomMargin=2 * cm)
    story = []

    # ── Cover ─────────────────────────────────────────────────────────────
    type_labels = {
        "white_paper": "Livre Blanc ESG / RSE",
        "full_report": "Rapport ESG Complet",
        "executive_summary_pdf": "Synthèse Exécutive ESG",
    }
    type_label = type_labels.get(request.report_type.value, "Rapport ESG")

    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph(request.company.name.upper(), styles["title"]))
    story.append(HRFlowable(width="100%", thickness=4, color=pal["accent"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(type_label, styles["h1"]))
    story.append(Paragraph(
        f"Exercice {request.company.reporting_year}  •  Secteur : {request.company.sector}  •  {request.company.country}",
        styles["body"]))
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
    story.append(Paragraph("1. Synthèse Exécutive", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=2, color=pal["secondary"]))
    story.append(Spacer(1, 0.3 * cm))

    exec_text = content.get("executive_summary",
        f"{request.company.name} présente son rapport ESG pour l'exercice {request.company.reporting_year}. "
        f"L'analyse des données extra-financières révèle un score ESG global de {scores.total_esg_score}/100, "
        f"correspondant à une notation {scores.rating}. Ce résultat reflète les engagements de l'entreprise "
        "en matière de responsabilité environnementale, sociale et de gouvernance d'entreprise."
    )
    story.append(Paragraph(exec_text, styles["body"]))
    story.append(Spacer(1, 0.5 * cm))

    # ── Environnement ─────────────────────────────────────────────────────
    story.append(Paragraph("2. Pilier Environnemental", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=2, color=pal["env"]))
    story.append(Spacer(1, 0.3 * cm))
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
        story.append(kpi_table(env_kpis, pal))

    if "emissions_pie" in chart_images:
        story.append(Spacer(1, 0.3 * cm))
        img = Image(io.BytesIO(chart_images["emissions_pie"]), width=8 * cm, height=7 * cm)
        img.hAlign = 'CENTER'
        story.append(img)
        story.append(Paragraph("Répartition des émissions par scope", styles["caption"]))

    story.append(Spacer(1, 0.5 * cm))

    # ── Social ────────────────────────────────────────────────────────────
    story.append(Paragraph("3. Pilier Social", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=2, color=pal["social"]))
    story.append(Spacer(1, 0.3 * cm))
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
        story.append(kpi_table(soc_kpis, pal))

    story.append(Spacer(1, 0.5 * cm))

    # ── Gouvernance ──────────────────────────────────────────────────────
    story.append(Paragraph("4. Pilier Gouvernance", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=2, color=pal["gov"]))
    story.append(Spacer(1, 0.3 * cm))
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
        story.append(kpi_table(gov_kpis, pal))

    story.append(PageBreak())

    # ── Forces & Faiblesses ───────────────────────────────────────────────
    story.append(Paragraph("5. Analyse Stratégique", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=2, color=pal["accent"]))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("Points forts identifiés", styles["h2"]))
    for s in scores.strengths:
        story.append(Paragraph(f"✅  {s}", styles["bullet"]))

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("Axes d'amélioration", styles["h2"]))
    for w in scores.weaknesses:
        story.append(Paragraph(f"⚠️  {w}", styles["bullet"]))

    if request.include_recommendations:
        story.append(Spacer(1, 0.4 * cm))
        story.append(Paragraph("6. Recommandations Prioritaires", styles["h1"]))
        story.append(HRFlowable(width="100%", thickness=2, color=pal["accent"]))
        story.append(Spacer(1, 0.3 * cm))
        for i, rec in enumerate(scores.recommendations, 1):
            story.append(Paragraph(f"<b>{i}.</b>  {rec}", styles["bullet"]))

    # ── Alignement référentiels ───────────────────────────────────────────
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("7. Cadres de Référence & Alignement ODD", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=2, color=pal["secondary"]))
    story.append(Spacer(1, 0.3 * cm))

    ref_text = (
        "Ce rapport s'inscrit dans les cadres de référence suivants : <b>GRI Standards</b> (Global Reporting Initiative), "
        "<b>TCFD</b> (Task Force on Climate-related Financial Disclosures), <b>CSRD</b> (Corporate Sustainability Reporting Directive), "
        "<b>SFDR</b> (Sustainable Finance Disclosure Regulation) et les normes <b>ISO 14001 / 26000</b>. "
        "L'organisation contribue aux Objectifs de Développement Durable (ODD) de l'ONU, notamment les ODD 7, 8, 10, 12, 13 et 16."
    )
    story.append(Paragraph(ref_text, styles["body"]))

    # ── Conclusion ────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("8. Conclusion", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=2, color=pal["primary"]))
    story.append(Spacer(1, 0.3 * cm))

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

    doc.build(story)
    buf.seek(0)
    return buf.read()
