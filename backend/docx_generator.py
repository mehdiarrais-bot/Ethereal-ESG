import io
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy
from models import ESGRequest, ESGScores, AestheticTheme

THEME_HEX = {
    AestheticTheme.CORPORATE_BLUE: {
        "primary": "1B3A6B", "secondary": "2E86C1", "accent": "F39C12",
        "env": "27AE60", "social": "2E86C1", "gov": "8E44AD",
    },
    AestheticTheme.GREEN_NATURE: {
        "primary": "1A5C38", "secondary": "27AE60", "accent": "F1C40F",
        "env": "2ECC71", "social": "3498DB", "gov": "E67E22",
    },
    AestheticTheme.DARK_PREMIUM: {
        "primary": "1A1F28", "secondary": "58A6FF", "accent": "F7C948",
        "env": "3FB950", "social": "58A6FF", "gov": "BC8CFF",
    },
    AestheticTheme.MINIMAL_WHITE: {
        "primary": "212121", "secondary": "1E88E5", "accent": "FF6F00",
        "env": "43A047", "social": "1E88E5", "gov": "8E24AA",
    },
}


def hex_to_rgb(h):
    h = h.lstrip('#')
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def add_heading(doc, text, level, color_hex, size=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.bold = True
    run.font.color.rgb = hex_to_rgb(color_hex)
    sizes = {1: 22, 2: 16, 3: 13}
    run.font.size = Pt(size or sizes.get(level, 13))
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    return p


def add_hr(doc, color_hex):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(8)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '4')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), color_hex)
    pBdr.append(bottom)
    pPr.append(pBdr)


def add_kpi_table(doc, kpi_list, colors):
    if not kpi_list:
        return
    rows = [kpi_list[i:i+3] for i in range(0, len(kpi_list), 3)]
    for row_data in rows:
        while len(row_data) < 3:
            row_data.append(('', ''))
        table = doc.add_table(rows=2, cols=3)
        table.style = 'Table Grid'
        for col_idx, (label, value) in enumerate(row_data):
            # Label row
            cell = table.rows[0].cells[col_idx]
            cell.paragraphs[0].clear()
            run = cell.paragraphs[0].add_run(label)
            run.font.size = Pt(9)
            run.font.bold = True
            run.font.color.rgb = hex_to_rgb(colors["secondary"])
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            # Value row
            cell2 = table.rows[1].cells[col_idx]
            cell2.paragraphs[0].clear()
            run2 = cell2.paragraphs[0].add_run(str(value))
            run2.font.size = Pt(16)
            run2.font.bold = True
            run2.font.color.rgb = hex_to_rgb(colors["primary"])
            cell2.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph()


def add_score_block(doc, label, score, color_hex):
    p = doc.add_paragraph()
    run = p.add_run(f"{label} : ")
    run.font.size = Pt(11)
    run.bold = True
    score_run = p.add_run(f"{score:.1f}/100")
    score_run.font.size = Pt(14)
    score_run.bold = True
    score_run.font.color.rgb = hex_to_rgb(color_hex)


def add_bullet_list(doc, items, icon, color_hex):
    for item in items:
        p = doc.add_paragraph()
        icon_run = p.add_run(f"{icon}  ")
        icon_run.font.color.rgb = hex_to_rgb(color_hex)
        icon_run.font.size = Pt(10)
        text_run = p.add_run(item)
        text_run.font.size = Pt(10)
        p.paragraph_format.left_indent = Cm(0.5)
        p.paragraph_format.space_after = Pt(3)


def generate_word_report(request: ESGRequest, scores: ESGScores, content: dict) -> bytes:
    colors = THEME_HEX.get(request.aesthetic_theme, THEME_HEX[AestheticTheme.CORPORATE_BLUE])

    doc = Document()

    # Page margins
    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)

    # ── Cover ─────────────────────────────────────────────────────────────
    title_p = doc.add_paragraph()
    title_run = title_p.add_run(request.company.name.upper())
    title_run.font.size = Pt(32)
    title_run.bold = True
    title_run.font.color.rgb = hex_to_rgb(colors["primary"])
    title_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    title_p.paragraph_format.space_after = Pt(4)

    add_hr(doc, colors["accent"])

    type_map = {
        "white_paper": "Livre Blanc ESG / RSE",
        "full_report": "Rapport ESG Complet",
        "executive_summary_pdf": "Synthèse Exécutive ESG",
    }
    sub_p = doc.add_paragraph()
    sub_run = sub_p.add_run(type_map.get(request.report_type.value, "Rapport ESG"))
    sub_run.font.size = Pt(18)
    sub_run.bold = True
    sub_run.font.color.rgb = hex_to_rgb(colors["secondary"])

    meta_p = doc.add_paragraph()
    meta_run = meta_p.add_run(
        f"Exercice {request.company.reporting_year}  •  {request.company.sector}  •  {request.company.country}"
    )
    meta_run.font.size = Pt(11)
    meta_run.font.color.rgb = hex_to_rgb("7F8C8D")
    meta_p.paragraph_format.space_after = Pt(20)

    # Score summary table
    summary_table = doc.add_table(rows=2, cols=4)
    summary_table.style = 'Table Grid'
    headers = ["Environnement", "Social", "Gouvernance", "Score Global"]
    values = [scores.environmental_score, scores.social_score,
              scores.governance_score, scores.total_esg_score]
    value_colors = [colors["env"], colors["social"], colors["gov"], colors["accent"]]

    for i, (hdr, val, col) in enumerate(zip(headers, values, value_colors)):
        hdr_cell = summary_table.rows[0].cells[i]
        hdr_cell.paragraphs[0].clear()
        r = hdr_cell.paragraphs[0].add_run(hdr)
        r.font.size = Pt(9)
        r.bold = True
        r.font.color.rgb = hex_to_rgb(colors["secondary"])
        hdr_cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        val_cell = summary_table.rows[1].cells[i]
        val_cell.paragraphs[0].clear()
        rv = val_cell.paragraphs[0].add_run(f"{val:.1f}")
        rv.font.size = Pt(24)
        rv.bold = True
        rv.font.color.rgb = hex_to_rgb(col)
        val_cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()

    rating_p = doc.add_paragraph()
    rating_run = rating_p.add_run(f"Note ESG : {scores.rating}")
    rating_run.font.size = Pt(16)
    rating_run.bold = True
    rating_run.font.color.rgb = hex_to_rgb(colors["accent"])
    rating_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rating_p.paragraph_format.space_after = Pt(24)

    doc.add_page_break()

    # ── 1. Synthèse Exécutive ─────────────────────────────────────────────
    add_heading(doc, "1. Synthèse Exécutive", 1, colors["primary"])
    add_hr(doc, colors["secondary"])
    exec_text = content.get("executive_summary",
        f"{request.company.name} présente son rapport ESG {request.company.reporting_year} "
        f"avec un score global de {scores.total_esg_score}/100 (note {scores.rating}).")
    doc.add_paragraph(exec_text).paragraph_format.space_after = Pt(12)

    # ── 2. Environnement ──────────────────────────────────────────────────
    add_heading(doc, "2. Pilier Environnemental", 1, colors["env"])
    add_hr(doc, colors["env"])
    add_score_block(doc, "Score Environnemental", scores.environmental_score, colors["env"])

    env_text = content.get("environmental", "Analyse des données environnementales.")
    doc.add_paragraph(env_text).paragraph_format.space_after = Pt(8)

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
    add_kpi_table(doc, env_kpis, colors)

    # ── 3. Social ──────────────────────────────────────────────────────────
    add_heading(doc, "3. Pilier Social", 1, colors["social"])
    add_hr(doc, colors["social"])
    add_score_block(doc, "Score Social", scores.social_score, colors["social"])

    soc_text = content.get("social", "Analyse des données sociales.")
    doc.add_paragraph(soc_text).paragraph_format.space_after = Pt(8)

    soc = request.social
    soc_kpis = []
    if soc.total_employees: soc_kpis.append(("Effectif", f"{soc.total_employees:,}"))
    if soc.female_employees_percent: soc_kpis.append(("Femmes %", f"{soc.female_employees_percent:.1f}%"))
    if soc.employee_turnover_percent: soc_kpis.append(("Turnover %", f"{soc.employee_turnover_percent:.1f}%"))
    if soc.training_hours_per_employee: soc_kpis.append(("Formation (h)", f"{soc.training_hours_per_employee:.0f}"))
    if soc.accident_frequency_rate: soc_kpis.append(("TF accidents", f"{soc.accident_frequency_rate:.2f}"))
    if soc.customer_satisfaction_score: soc_kpis.append(("Satisfaction /10", f"{soc.customer_satisfaction_score:.1f}"))
    add_kpi_table(doc, soc_kpis, colors)

    # ── 4. Gouvernance ────────────────────────────────────────────────────
    add_heading(doc, "4. Pilier Gouvernance", 1, colors["gov"])
    add_hr(doc, colors["gov"])
    add_score_block(doc, "Score Gouvernance", scores.governance_score, colors["gov"])

    gov_text = content.get("governance", "Analyse des données de gouvernance.")
    doc.add_paragraph(gov_text).paragraph_format.space_after = Pt(8)

    gov = request.governance
    gov_kpis = []
    if gov.board_members: gov_kpis.append(("Membres CA", str(gov.board_members)))
    if gov.female_board_percent: gov_kpis.append(("Femmes CA %", f"{gov.female_board_percent:.1f}%"))
    if gov.independent_board_percent: gov_kpis.append(("Indépendants %", f"{gov.independent_board_percent:.1f}%"))
    if gov.csr_budget_eur: gov_kpis.append(("Budget RSE (€)", f"{gov.csr_budget_eur:,.0f}"))
    gov_kpis.append(("Audit ESG", "✓ Oui" if gov.esg_audit_conducted else "✗ Non"))
    gov_kpis.append(("Comité durable", "✓ Oui" if gov.sustainability_committee else "✗ Non"))
    add_kpi_table(doc, gov_kpis, colors)

    doc.add_page_break()

    # ── 5. Analyse Stratégique ────────────────────────────────────────────
    add_heading(doc, "5. Analyse Stratégique ESG", 1, colors["primary"])
    add_hr(doc, colors["accent"])

    add_heading(doc, "Points Forts", 2, colors["env"])
    add_bullet_list(doc, scores.strengths, "✅", colors["env"])

    add_heading(doc, "Axes d'Amélioration", 2, "E74C3C")
    add_bullet_list(doc, scores.weaknesses, "⚠️", "E74C3C")

    if request.include_recommendations and scores.recommendations:
        add_heading(doc, "6. Recommandations Prioritaires", 1, colors["primary"])
        add_hr(doc, colors["accent"])
        for i, rec in enumerate(scores.recommendations, 1):
            p = doc.add_paragraph()
            num = p.add_run(f"{i}.  ")
            num.bold = True
            num.font.color.rgb = hex_to_rgb(colors["accent"])
            p.add_run(rec).font.size = Pt(10)
            p.paragraph_format.space_after = Pt(4)

    # ── 7. Référentiels ───────────────────────────────────────────────────
    add_heading(doc, "7. Cadres de Référence & Alignement ODD", 1, colors["primary"])
    add_hr(doc, colors["secondary"])
    ref_text = (
        "Ce rapport s'inscrit dans les cadres de référence suivants : GRI Standards, TCFD, CSRD, SFDR et ISO 14001/26000. "
        "L'organisation contribue aux ODD de l'ONU : ODD 7 (Énergie propre), ODD 8 (Travail décent), "
        "ODD 10 (Inégalités), ODD 12 (Consommation responsable), ODD 13 (Action climatique), ODD 16 (Institutions)."
    )
    doc.add_paragraph(ref_text)

    # ── Conclusion ────────────────────────────────────────────────────────
    doc.add_page_break()
    add_heading(doc, "8. Conclusion", 1, colors["primary"])
    add_hr(doc, colors["primary"])
    conclusion = content.get("conclusion",
        f"{request.company.name} réaffirme son engagement vers un modèle d'affaires durable. "
        "Les axes d'amélioration identifiés feront l'objet de plans d'action concrets."
    )
    doc.add_paragraph(conclusion)

    doc.add_paragraph()
    footer_p = doc.add_paragraph(
        f"© {request.company.reporting_year} {request.company.name} — Document généré par la Plateforme ESG"
    )
    footer_p.runs[0].font.size = Pt(8)
    footer_p.runs[0].font.color.rgb = hex_to_rgb("7F8C8D")
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()
