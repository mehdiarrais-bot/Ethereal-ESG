import io
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
from pptx.chart.data import ChartData
from pptx.enum.chart import XL_CHART_TYPE
import copy
from models import ESGRequest, ESGScores, AestheticTheme, PresentationType

# Color palettes per theme
THEMES = {
    AestheticTheme.CORPORATE_BLUE: {
        "bg_primary": RGBColor(0x1B, 0x3A, 0x6B),
        "bg_secondary": RGBColor(0xF4, 0xF7, 0xFD),
        "accent": RGBColor(0xF3, 0x9C, 0x12),
        "env": RGBColor(0x27, 0xAE, 0x60),
        "social": RGBColor(0x2E, 0x86, 0xC1),
        "gov": RGBColor(0x8E, 0x44, 0xAD),
        "text_light": RGBColor(0xFF, 0xFF, 0xFF),
        "text_dark": RGBColor(0x2C, 0x3E, 0x50),
        "subtitle": RGBColor(0xAE, 0xC6, 0xE8),
        "card_bg": RGBColor(0xEB, 0xF2, 0xFB),
    },
    AestheticTheme.GREEN_NATURE: {
        "bg_primary": RGBColor(0x1A, 0x5C, 0x38),
        "bg_secondary": RGBColor(0xF0, 0xFB, 0xF4),
        "accent": RGBColor(0xF1, 0xC4, 0x0F),
        "env": RGBColor(0x2E, 0xCC, 0x71),
        "social": RGBColor(0x34, 0x98, 0xDB),
        "gov": RGBColor(0xE6, 0x7E, 0x22),
        "text_light": RGBColor(0xFF, 0xFF, 0xFF),
        "text_dark": RGBColor(0x1A, 0x33, 0x25),
        "subtitle": RGBColor(0xA9, 0xDB, 0xBC),
        "card_bg": RGBColor(0xD5, 0xF5, 0xE3),
    },
    AestheticTheme.DARK_PREMIUM: {
        "bg_primary": RGBColor(0x0D, 0x11, 0x17),
        "bg_secondary": RGBColor(0x16, 0x1B, 0x22),
        "accent": RGBColor(0xF7, 0xC9, 0x48),
        "env": RGBColor(0x3F, 0xB9, 0x50),
        "social": RGBColor(0x58, 0xA6, 0xFF),
        "gov": RGBColor(0xBC, 0x8C, 0xFF),
        "text_light": RGBColor(0xE6, 0xED, 0xF3),
        "text_dark": RGBColor(0xE6, 0xED, 0xF3),
        "subtitle": RGBColor(0x7D, 0x8B, 0x9A),
        "card_bg": RGBColor(0x21, 0x26, 0x2D),
    },
    AestheticTheme.MINIMAL_WHITE: {
        "bg_primary": RGBColor(0x21, 0x21, 0x21),
        "bg_secondary": RGBColor(0xFA, 0xFA, 0xFA),
        "accent": RGBColor(0xFF, 0x6F, 0x00),
        "env": RGBColor(0x43, 0xA0, 0x47),
        "social": RGBColor(0x1E, 0x88, 0xE5),
        "gov": RGBColor(0x8E, 0x24, 0xAA),
        "text_light": RGBColor(0xFF, 0xFF, 0xFF),
        "text_dark": RGBColor(0x21, 0x21, 0x21),
        "subtitle": RGBColor(0x75, 0x75, 0x75),
        "card_bg": RGBColor(0xF0, 0xF0, 0xF0),
    },
}

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)


def rgb_to_hex(r, g, b):
    return f"#{r:02X}{g:02X}{b:02X}"


def add_bg_rect(slide, left, top, width, height, color: RGBColor, alpha=None):
    shape = slide.shapes.add_shape(1, left, top, width, height)
    shape.line.fill.background()
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    if alpha is not None:
        shape.fill.fore_color.theme_color = None
    return shape


def add_text(slide, text, left, top, width, height, font_size=18,
             bold=False, color: RGBColor = RGBColor(0, 0, 0),
             align=PP_ALIGN.LEFT, italic=False, word_wrap=True):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = word_wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return txBox


def add_image_from_bytes(slide, img_bytes, left, top, width, height):
    img_io = io.BytesIO(img_bytes)
    slide.shapes.add_picture(img_io, left, top, width, height)


def score_color(score: float, theme_colors: dict) -> RGBColor:
    if score >= 75:
        return theme_colors["env"]
    elif score >= 50:
        return theme_colors["accent"]
    return RGBColor(0xE7, 0x4C, 0x3C)


def generate_pptx(request: ESGRequest, scores: ESGScores, content: dict,
                  chart_images: dict) -> bytes:
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    theme = THEMES.get(request.aesthetic_theme, THEMES[AestheticTheme.CORPORATE_BLUE])
    ptype = request.presentation_type

    # Slide layout (blank)
    blank_layout = prs.slide_layouts[6]

    # ── SLIDE 1: Cover ──────────────────────────────────────────────────
    slide = prs.slides.add_slide(blank_layout)
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_primary"])

    # Accent bar left
    add_bg_rect(slide, 0, 0, Inches(0.15), SLIDE_H, theme["accent"])

    # Decorative circle top-right
    circ = slide.shapes.add_shape(9, Inches(10.5), Inches(-1.5), Inches(4), Inches(4))
    circ.fill.solid()
    circ.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    circ.line.fill.background()

    # Title
    add_text(slide, request.company.name.upper(),
             Inches(0.6), Inches(1.2), Inches(9), Inches(1.2),
             font_size=40, bold=True, color=theme["text_light"])

    # Subtitle
    subtitle_map = {
        PresentationType.EXECUTIVE_SUMMARY: "Rapport ESG — Synthèse Exécutive",
        PresentationType.INVESTOR_DECK: "ESG Investor Deck",
        PresentationType.DETAILED_REPORT: "Rapport ESG Détaillé",
        PresentationType.STAKEHOLDER_BRIEF: "Communication Parties Prenantes",
        PresentationType.ANNUAL_REPORT: "Rapport Annuel ESG / RSE",
    }
    add_text(slide, subtitle_map.get(ptype, "Rapport ESG"),
             Inches(0.6), Inches(2.5), Inches(9), Inches(0.7),
             font_size=22, color=theme["subtitle"])

    add_text(slide, f"Exercice {request.company.reporting_year}  •  {request.company.sector}  •  {request.company.country}",
             Inches(0.6), Inches(3.3), Inches(10), Inches(0.5),
             font_size=14, color=theme["subtitle"])

    # Rating badge
    badge = add_bg_rect(slide, Inches(10.5), Inches(5.5), Inches(2.2), Inches(1.5), theme["accent"])
    add_text(slide, f"ESG {scores.rating}",
             Inches(10.5), Inches(5.5), Inches(2.2), Inches(1.5),
             font_size=28, bold=True, color=theme["bg_primary"], align=PP_ALIGN.CENTER)

    add_text(slide, f"Score Global: {scores.total_esg_score}/100",
             Inches(0.6), Inches(5.8), Inches(6), Inches(0.5),
             font_size=14, color=theme["subtitle"])

    add_text(slide, f"Généré automatiquement — ESG Platform",
             Inches(0.6), Inches(6.8), Inches(8), Inches(0.4),
             font_size=9, italic=True, color=theme["subtitle"])

    # ── SLIDE 2: Tableau de Bord ESG ────────────────────────────────────
    slide = prs.slides.add_slide(blank_layout)
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_secondary"])
    add_bg_rect(slide, 0, 0, SLIDE_W, Inches(1.1), theme["bg_primary"])
    add_bg_rect(slide, 0, Inches(1.1), Inches(0.07), SLIDE_H - Inches(1.1), theme["accent"])

    add_text(slide, "Tableau de Bord ESG", Inches(0.3), Inches(0.15),
             Inches(10), Inches(0.8), font_size=26, bold=True, color=theme["text_light"])

    # Score cards (3 piliers)
    pillars = [
        ("E — Environnement", scores.environmental_score, theme["env"], Inches(0.3)),
        ("S — Social", scores.social_score, theme["social"], Inches(4.55)),
        ("G — Gouvernance", scores.governance_score, theme["gov"], Inches(8.8)),
    ]
    for label, score, color, left in pillars:
        card = add_bg_rect(slide, left, Inches(1.3), Inches(4.0), Inches(2.4), theme["card_bg"])
        add_bg_rect(slide, left, Inches(1.3), Inches(4.0), Inches(0.12), color)
        add_text(slide, label, left + Inches(0.2), Inches(1.5),
                 Inches(3.6), Inches(0.5), font_size=13, bold=True, color=theme["text_dark"])
        add_text(slide, f"{score:.1f}", left + Inches(0.2), Inches(2.0),
                 Inches(2.0), Inches(0.9), font_size=44, bold=True, color=color)
        add_text(slide, "/100", left + Inches(1.5), Inches(2.4),
                 Inches(1.5), Inches(0.4), font_size=14, color=theme["subtitle"])

    # Global score
    add_bg_rect(slide, Inches(0.3), Inches(3.9), Inches(12.7), Inches(0.08), theme["accent"])
    add_text(slide, f"Score ESG Global : {scores.total_esg_score}/100  —  Note : {scores.rating}",
             Inches(0.3), Inches(4.1), Inches(10), Inches(0.6),
             font_size=20, bold=True, color=theme["text_dark"], align=PP_ALIGN.CENTER)

    # Radar chart
    if "radar" in chart_images:
        add_image_from_bytes(slide, chart_images["radar"],
                             Inches(0.3), Inches(4.8), Inches(5.5), Inches(2.5))

    # Bar chart
    if "bars" in chart_images:
        add_image_from_bytes(slide, chart_images["bars"],
                             Inches(6.0), Inches(4.8), Inches(7.0), Inches(2.5))

    # ── SLIDE 3: Environnement ───────────────────────────────────────────
    slide = prs.slides.add_slide(blank_layout)
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_secondary"])
    add_bg_rect(slide, 0, 0, SLIDE_W, Inches(1.1), theme["env"])
    add_bg_rect(slide, 0, Inches(1.1), Inches(0.07), SLIDE_H - Inches(1.1), theme["env"])

    add_text(slide, "🌍  Pilier Environnemental", Inches(0.3), Inches(0.12),
             Inches(12), Inches(0.85), font_size=26, bold=True, color=theme["text_light"])

    env = request.environmental
    env_kpis = []
    if env.co2_emissions_tonnes is not None:
        env_kpis.append(("Émissions CO₂ totales", f"{env.co2_emissions_tonnes:,.0f} t CO₂e"))
    if env.scope1_emissions is not None:
        env_kpis.append(("Scope 1", f"{env.scope1_emissions:,.0f} t CO₂e"))
    if env.scope2_emissions is not None:
        env_kpis.append(("Scope 2", f"{env.scope2_emissions:,.0f} t CO₂e"))
    if env.scope3_emissions is not None:
        env_kpis.append(("Scope 3", f"{env.scope3_emissions:,.0f} t CO₂e"))
    if env.renewable_energy_percent is not None:
        env_kpis.append(("Énergie renouvelable", f"{env.renewable_energy_percent:.1f}%"))
    if env.energy_consumption_mwh is not None:
        env_kpis.append(("Consommation énergie", f"{env.energy_consumption_mwh:,.0f} MWh"))
    if env.water_consumption_m3 is not None:
        env_kpis.append(("Consommation eau", f"{env.water_consumption_m3:,.0f} m³"))
    if env.waste_generated_tonnes is not None:
        env_kpis.append(("Déchets générés", f"{env.waste_generated_tonnes:,.1f} t"))
    if env.waste_recycled_percent is not None:
        env_kpis.append(("Taux de recyclage", f"{env.waste_recycled_percent:.1f}%"))

    cols = [Inches(0.3), Inches(4.55), Inches(8.8)]
    for idx, (kpi_label, kpi_val) in enumerate(env_kpis[:9]):
        col = cols[idx % 3]
        row = Inches(1.3) + (idx // 3) * Inches(1.9)
        card = add_bg_rect(slide, col, row, Inches(4.0), Inches(1.7), theme["card_bg"])
        add_bg_rect(slide, col, row, Inches(4.0), Inches(0.1), theme["env"])
        add_text(slide, kpi_label, col + Inches(0.15), row + Inches(0.15),
                 Inches(3.7), Inches(0.45), font_size=11, color=theme["subtitle"])
        add_text(slide, kpi_val, col + Inches(0.15), row + Inches(0.6),
                 Inches(3.7), Inches(0.85), font_size=22, bold=True, color=theme["env"])

    score_pos_left = Inches(10.0)
    add_text(slide, f"Score E\n{scores.environmental_score:.0f}/100",
             score_pos_left, Inches(6.5), Inches(3), Inches(0.9),
             font_size=18, bold=True, color=theme["env"], align=PP_ALIGN.RIGHT)

    if "emissions_pie" in chart_images:
        add_image_from_bytes(slide, chart_images["emissions_pie"],
                             Inches(9.5), Inches(1.2), Inches(3.7), Inches(3.0))

    # ── SLIDE 4: Social ──────────────────────────────────────────────────
    slide = prs.slides.add_slide(blank_layout)
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_secondary"])
    add_bg_rect(slide, 0, 0, SLIDE_W, Inches(1.1), theme["social"])
    add_bg_rect(slide, 0, Inches(1.1), Inches(0.07), SLIDE_H - Inches(1.1), theme["social"])

    add_text(slide, "👥  Pilier Social", Inches(0.3), Inches(0.12),
             Inches(12), Inches(0.85), font_size=26, bold=True, color=theme["text_light"])

    soc = request.social
    soc_kpis = []
    if soc.total_employees is not None:
        soc_kpis.append(("Effectif total", f"{soc.total_employees:,}"))
    if soc.female_employees_percent is not None:
        soc_kpis.append(("Femmes dans l'effectif", f"{soc.female_employees_percent:.1f}%"))
    if soc.employee_turnover_percent is not None:
        soc_kpis.append(("Turnover", f"{soc.employee_turnover_percent:.1f}%"))
    if soc.training_hours_per_employee is not None:
        soc_kpis.append(("Formation/employé/an", f"{soc.training_hours_per_employee:.0f} h"))
    if soc.work_accidents is not None:
        soc_kpis.append(("Accidents de travail", f"{soc.work_accidents}"))
    if soc.accident_frequency_rate is not None:
        soc_kpis.append(("Taux de fréquence", f"{soc.accident_frequency_rate:.2f}"))
    if soc.community_investment_eur is not None:
        soc_kpis.append(("Investissement communauté", f"{soc.community_investment_eur:,.0f} €"))
    if soc.customer_satisfaction_score is not None:
        soc_kpis.append(("Satisfaction client", f"{soc.customer_satisfaction_score:.1f}/10"))
    if soc.disabled_employees_percent is not None:
        soc_kpis.append(("Salariés handicapés", f"{soc.disabled_employees_percent:.1f}%"))

    for idx, (kpi_label, kpi_val) in enumerate(soc_kpis[:9]):
        col = cols[idx % 3]
        row = Inches(1.3) + (idx // 3) * Inches(1.9)
        add_bg_rect(slide, col, row, Inches(4.0), Inches(1.7), theme["card_bg"])
        add_bg_rect(slide, col, row, Inches(4.0), Inches(0.1), theme["social"])
        add_text(slide, kpi_label, col + Inches(0.15), row + Inches(0.15),
                 Inches(3.7), Inches(0.45), font_size=11, color=theme["subtitle"])
        add_text(slide, kpi_val, col + Inches(0.15), row + Inches(0.6),
                 Inches(3.7), Inches(0.85), font_size=22, bold=True, color=theme["social"])

    add_text(slide, f"Score S\n{scores.social_score:.0f}/100",
             Inches(10.0), Inches(6.5), Inches(3), Inches(0.9),
             font_size=18, bold=True, color=theme["social"], align=PP_ALIGN.RIGHT)

    # ── SLIDE 5: Gouvernance ─────────────────────────────────────────────
    slide = prs.slides.add_slide(blank_layout)
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_secondary"])
    add_bg_rect(slide, 0, 0, SLIDE_W, Inches(1.1), theme["gov"])
    add_bg_rect(slide, 0, Inches(1.1), Inches(0.07), SLIDE_H - Inches(1.1), theme["gov"])

    add_text(slide, "⚖️  Pilier Gouvernance", Inches(0.3), Inches(0.12),
             Inches(12), Inches(0.85), font_size=26, bold=True, color=theme["text_light"])

    gov = request.governance
    gov_kpis = []
    if gov.board_members is not None:
        gov_kpis.append(("Membres du CA", f"{gov.board_members}"))
    if gov.female_board_percent is not None:
        gov_kpis.append(("Femmes au CA", f"{gov.female_board_percent:.1f}%"))
    if gov.independent_board_percent is not None:
        gov_kpis.append(("Administrateurs indépendants", f"{gov.independent_board_percent:.1f}%"))
    if gov.ethics_violations is not None:
        gov_kpis.append(("Violations éthiques", f"{gov.ethics_violations}"))
    if gov.corruption_cases is not None:
        gov_kpis.append(("Cas de corruption", f"{gov.corruption_cases}"))
    if gov.data_breaches is not None:
        gov_kpis.append(("Violations de données", f"{gov.data_breaches}"))
    if gov.csr_budget_eur is not None:
        gov_kpis.append(("Budget RSE", f"{gov.csr_budget_eur:,.0f} €"))
    gov_kpis.append(("Audit ESG conduit", "Oui ✓" if gov.esg_audit_conducted else "Non ✗"))
    gov_kpis.append(("Comité durabilité", "Oui ✓" if gov.sustainability_committee else "Non ✗"))

    for idx, (kpi_label, kpi_val) in enumerate(gov_kpis[:9]):
        col = cols[idx % 3]
        row = Inches(1.3) + (idx // 3) * Inches(1.9)
        add_bg_rect(slide, col, row, Inches(4.0), Inches(1.7), theme["card_bg"])
        add_bg_rect(slide, col, row, Inches(4.0), Inches(0.1), theme["gov"])
        add_text(slide, kpi_label, col + Inches(0.15), row + Inches(0.15),
                 Inches(3.7), Inches(0.45), font_size=11, color=theme["subtitle"])
        add_text(slide, kpi_val, col + Inches(0.15), row + Inches(0.6),
                 Inches(3.7), Inches(0.85), font_size=20, bold=True, color=theme["gov"])

    add_text(slide, f"Score G\n{scores.governance_score:.0f}/100",
             Inches(10.0), Inches(6.5), Inches(3), Inches(0.9),
             font_size=18, bold=True, color=theme["gov"], align=PP_ALIGN.RIGHT)

    # ── SLIDE 6: Forces & Faiblesses ────────────────────────────────────
    slide = prs.slides.add_slide(blank_layout)
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_secondary"])
    add_bg_rect(slide, 0, 0, SLIDE_W, Inches(1.1), theme["bg_primary"])
    add_bg_rect(slide, 0, Inches(1.1), Inches(0.07), SLIDE_H - Inches(1.1), theme["accent"])

    add_text(slide, "Analyse Stratégique ESG", Inches(0.3), Inches(0.12),
             Inches(12), Inches(0.85), font_size=26, bold=True, color=theme["text_light"])

    # Forces (left)
    add_bg_rect(slide, Inches(0.3), Inches(1.2), Inches(6.0), Inches(5.8), theme["card_bg"])
    add_bg_rect(slide, Inches(0.3), Inches(1.2), Inches(6.0), Inches(0.55), theme["env"])
    add_text(slide, "  ✅  Points Forts", Inches(0.3), Inches(1.2),
             Inches(6.0), Inches(0.55), font_size=14, bold=True, color=theme["text_light"])

    for i, strength in enumerate(scores.strengths):
        add_text(slide, f"• {strength}",
                 Inches(0.5), Inches(1.85) + i * Inches(0.85),
                 Inches(5.6), Inches(0.8), font_size=12, color=theme["text_dark"])

    # Faiblesses (right)
    add_bg_rect(slide, Inches(6.9), Inches(1.2), Inches(6.1), Inches(5.8), theme["card_bg"])
    add_bg_rect(slide, Inches(6.9), Inches(1.2), Inches(6.1), Inches(0.55), RGBColor(0xE7, 0x4C, 0x3C))
    add_text(slide, "  ⚠️  Axes d'Amélioration", Inches(6.9), Inches(1.2),
             Inches(6.1), Inches(0.55), font_size=14, bold=True, color=theme["text_light"])

    for i, weakness in enumerate(scores.weaknesses):
        add_text(slide, f"• {weakness}",
                 Inches(7.1), Inches(1.85) + i * Inches(0.85),
                 Inches(5.7), Inches(0.8), font_size=12, color=theme["text_dark"])

    # ── SLIDE 7: Recommandations ─────────────────────────────────────────
    if request.include_recommendations:
        slide = prs.slides.add_slide(blank_layout)
        add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_secondary"])
        add_bg_rect(slide, 0, 0, SLIDE_W, Inches(1.1), theme["bg_primary"])
        add_bg_rect(slide, 0, Inches(1.1), Inches(0.07), SLIDE_H - Inches(1.1), theme["accent"])

        add_text(slide, "Recommandations Prioritaires", Inches(0.3), Inches(0.12),
                 Inches(12), Inches(0.85), font_size=26, bold=True, color=theme["text_light"])

        rec_colors = [theme["env"], theme["social"], theme["gov"], theme["accent"],
                      theme["env"], theme["social"]]
        for i, rec in enumerate(scores.recommendations[:6]):
            row = Inches(1.2) + (i % 3) * Inches(2.0)
            col = Inches(0.3) + (i // 3) * Inches(6.5)
            num_color = rec_colors[i]
            add_bg_rect(slide, col, row, Inches(6.1), Inches(1.8), theme["card_bg"])
            add_bg_rect(slide, col, row, Inches(0.5), Inches(1.8), num_color)
            add_text(slide, str(i + 1), col, row + Inches(0.5),
                     Inches(0.5), Inches(0.8), font_size=20, bold=True,
                     color=theme["text_light"], align=PP_ALIGN.CENTER)
            add_text(slide, rec, col + Inches(0.6), row + Inches(0.25),
                     Inches(5.4), Inches(1.3), font_size=11, color=theme["text_dark"])

    # ── SLIDE 8: Alignement ODD ──────────────────────────────────────────
    slide = prs.slides.add_slide(blank_layout)
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_secondary"])
    add_bg_rect(slide, 0, 0, SLIDE_W, Inches(1.1), theme["bg_primary"])
    add_bg_rect(slide, 0, Inches(1.1), Inches(0.07), SLIDE_H - Inches(1.1), theme["accent"])

    add_text(slide, "Alignement — ODD & Cadres de Référence", Inches(0.3), Inches(0.12),
             Inches(12), Inches(0.85), font_size=24, bold=True, color=theme["text_light"])

    odds = [
        ("ODD 7", "Énergie propre", theme["accent"]),
        ("ODD 8", "Travail décent", theme["social"]),
        ("ODD 10", "Inégalités réduites", theme["gov"]),
        ("ODD 12", "Conso. responsable", theme["env"]),
        ("ODD 13", "Action climatique", theme["env"]),
        ("ODD 16", "Paix & Institutions", theme["gov"]),
    ]

    for idx, (odd_num, odd_label, odd_color) in enumerate(odds):
        col = Inches(0.3) + (idx % 3) * Inches(4.3)
        row = Inches(1.3) + (idx // 3) * Inches(1.8)
        add_bg_rect(slide, col, row, Inches(4.0), Inches(1.6), odd_color)
        add_text(slide, odd_num, col + Inches(0.15), row + Inches(0.1),
                 Inches(3.7), Inches(0.6), font_size=18, bold=True,
                 color=RGBColor(0xFF, 0xFF, 0xFF))
        add_text(slide, odd_label, col + Inches(0.15), row + Inches(0.75),
                 Inches(3.7), Inches(0.7), font_size=13,
                 color=RGBColor(0xFF, 0xFF, 0xFF))

    frameworks = ["GRI Standards", "TCFD", "CSRD / DPEF", "SFDR", "ISO 14001 / 26000"]
    add_bg_rect(slide, Inches(0.3), Inches(5.1), Inches(12.7), Inches(0.08), theme["accent"])
    add_text(slide, "Cadres reportés : " + "  |  ".join(frameworks),
             Inches(0.3), Inches(5.3), Inches(12.7), Inches(0.6),
             font_size=13, bold=True, color=theme["text_dark"], align=PP_ALIGN.CENTER)

    # ── SLIDE 9: Conclusion ──────────────────────────────────────────────
    slide = prs.slides.add_slide(blank_layout)
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_primary"])
    add_bg_rect(slide, 0, 0, Inches(0.15), SLIDE_H, theme["accent"])

    add_text(slide, "Conclusion & Engagements", Inches(0.6), Inches(0.8),
             Inches(11), Inches(1.0), font_size=30, bold=True, color=theme["text_light"])

    conclusion_text = content.get("conclusion",
        f"{request.company.name} affiche un score ESG global de {scores.total_esg_score}/100 "
        f"(note {scores.rating}), témoignant d'une démarche structurée de développement durable. "
        "La société s'engage à renforcer ses performances sur les axes identifiés "
        "et à maintenir la transparence de son reporting extra-financier."
    )
    add_text(slide, conclusion_text, Inches(0.6), Inches(2.0),
             Inches(11.5), Inches(2.8), font_size=14, color=theme["subtitle"])

    add_text(slide, f"Score ESG : {scores.total_esg_score}/100  —  Note : {scores.rating}",
             Inches(0.6), Inches(5.0), Inches(10), Inches(0.7),
             font_size=22, bold=True, color=theme["accent"])

    add_text(slide, f"© {request.company.reporting_year} {request.company.name} — Document confidentiel",
             Inches(0.6), Inches(6.7), Inches(11), Inches(0.4),
             font_size=9, italic=True, color=theme["subtitle"])

    buf = io.BytesIO()
    prs.save(buf)
    buf.seek(0)
    return buf.read()
