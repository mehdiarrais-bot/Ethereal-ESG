import io
from dataclasses import dataclass
from typing import Any, cast

from docx import Document
from docx.styles.style import ParagraphStyle
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.document import Document as DocumentObject
from docx.text.paragraph import Paragraph
from esg_calculator import NON_NOTE, score_label
from models import ESGRequest, ESGScores, AestheticTheme
from i18n import L

def docx_hex(theme: AestheticTheme) -> dict:
    """Couleurs Word (hex sans « # ») converties depuis le gabarit."""
    from report_designs import colors_of
    c = colors_of(theme)
    return {"light": c["panel"][1:], "primary": c["primary"][1:], "secondary": c["muted"][1:],
            "accent": c["accent"][1:], "env": c["env"][1:], "social": c["social"][1:],
            "gov": c["gov"][1:], "paper": c["paper"][1:], "ink": c["ink"][1:]}


# Traitement des titres par gabarit ; polices système sûres (report_designs)
_DOCX_HEADING = {
    AestheticTheme.AURORA: ("plain", 22), AestheticTheme.ANNUEL: ("plain", 22),
    AestheticTheme.INSTITUTIONNEL: ("plain", 22), AestheticTheme.PORTRAIT: ("plain", 22),
    AestheticTheme.TERRE: ("shaded", 18), AestheticTheme.GALERIE: ("plain", 20),
}


def docx_style(theme: AestheticTheme) -> dict:
    from report_designs import design, DEFAULT_DESIGN
    heading, size = _DOCX_HEADING.get(theme, _DOCX_HEADING[DEFAULT_DESIGN])
    return {"font": design(theme)["office"]["body"], "font_title": design(theme)["office"]["display"],
            "heading": heading, "uppercase": False, "h1_size": size}


def hex_to_rgb(h: str) -> RGBColor:
    h = h.lstrip('#')
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def shade_cell(cell, color_hex: str) -> None:  # cell: pas de type public dans python-docx
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)


def shade_paragraph(p: Paragraph, color_hex: str) -> None:
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:fill'), color_hex)
    pPr.append(shd)


def add_heading(doc, text, level, color_hex, size=None, style=None):
    style = style or docx_style(AestheticTheme.AURORA)
    if style["uppercase"]:
        text = text.upper()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.bold = True
    run.font.name = style["font"]
    sizes = {1: style["h1_size"], 2: max(12, style["h1_size"] - 5), 3: 12}
    run.font.size = Pt(size or sizes.get(level, 12))
    if style["heading"] == "shaded" and level == 1:
        # Green Nature: white text on colored band
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shade_paragraph(p, color_hex)
    else:
        run.font.color.rgb = hex_to_rgb(color_hex)
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    return p


def add_hr(doc: DocumentObject, color_hex: str) -> None:
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
            shade_cell(cell, colors.get("light", "F5F5F5"))
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
    score_run = p.add_run(f"{score:.1f}/100" if score is not None else NON_NOTE)
    score_run.font.size = Pt(14)
    score_run.bold = True
    score_run.font.color.rgb = hex_to_rgb(color_hex)


def add_bullet_list(doc: DocumentObject, items: list[str], icon: str,
                    color_hex: str) -> None:
    for item in items:
        p = doc.add_paragraph()
        icon_run = p.add_run(f"{icon}  ")
        icon_run.font.color.rgb = hex_to_rgb(color_hex)
        icon_run.font.size = Pt(10)
        text_run = p.add_run(item)
        text_run.font.size = Pt(10)
        p.paragraph_format.left_indent = Cm(0.5)
        p.paragraph_format.space_after = Pt(3)



def add_consultant_note(doc, text, colors, TR):
    """Encart « L'analyse du consultant » (fond primaire clair, italique)."""
    kp = doc.add_paragraph()
    kr = kp.add_run(TR["consultant_note"])
    kr.bold = True; kr.font.size = Pt(8.5)
    kr.font.color.rgb = hex_to_rgb(colors["accent"])
    kp.paragraph_format.space_before = Pt(6)
    kp.paragraph_format.space_after = Pt(1)
    np_ = doc.add_paragraph()
    nr = np_.add_run(text)
    nr.italic = True; nr.font.size = Pt(10)
    nr.font.color.rgb = hex_to_rgb(colors["primary"])
    shade_paragraph(np_, colors.get("light", "F0F2F5"))
    np_.paragraph_format.space_after = Pt(8)

@dataclass
class _Report:
    """Ce que lisent les sections du rapport Word, calculé une fois (avant :
    risques, écarts et feuille de route étaient recalculés dans la fonction).
    Le texte analytique vient de narrative.py, partagé avec le PDF."""
    doc: Any
    request: ESGRequest
    scores: ESGScores
    content: dict
    colors: dict
    style: dict
    TR: dict
    ref: str                  # référentiel affiché (CSRD ou VSME)
    ro: dict                  # risks_opportunities
    gaps: list                # compliance_assessment
    recs: list                # enriched_recommendations, vides sans recommandations
    roadmap: list             # roadmap_12m
    headlines: dict           # pillar_headline
    section_heads: dict       # section_headlines
    notes: dict               # analyses du consultant
    charts: dict

    @property
    def lang(self) -> str:
        return self.request.language

    @property
    def light(self) -> str:
        return self.colors.get("light", "F0F2F5")

    def heading(self, text: str, level: int, color_hex: str) -> None:
        add_heading(self.doc, text, level, color_hex, style=self.style)

    def text(self, text, size=10.5, italic=False, shade=None, after=8):
        par = self.doc.add_paragraph()
        run = par.add_run(text)
        run.font.size = Pt(size)
        run.italic = italic
        if shade:
            shade_paragraph(par, shade)
        par.paragraph_format.space_after = Pt(after)
        return par

    def conclusion(self, text: str, color_hex: str) -> None:
        """Sous-titre en gras = la conclusion de la section (information scent)."""
        p = self.doc.add_paragraph()
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(12.5)
        run.font.color.rgb = hex_to_rgb(color_hex)
        p.paragraph_format.space_after = Pt(6)

    def reading(self, pillar: str, color_hex: str) -> None:
        """« Lecture des indicateurs » + leviers du plan d'action (comme le PDF)."""
        import narrative as NR
        self.heading(NR.T[self.lang]["reading_title"], 2, color_hex)
        for para in NR.pillar_paragraphs(self.request, self.scores, pillar):
            self.text(para)
        if self.request.include_recommendations:
            self.text(NR.levers_sentence(self.request, self.recs, pillar))
        self.analysis(pillar, color_hex)

    def analysis(self, pillar: str, color_hex: str) -> None:
        """Analyse approfondie (analysis.py), partagée avec le PDF."""
        import analysis as AN
        sections = AN.pillar_analysis(self.request, self.scores, pillar)
        if not sections:
            return
        import illustrations as IL
        where = IL.placements(pillar, [sec.key for sec in sections])
        self.heading(AN.analysis_title(self.request, pillar), 2, color_hex)
        for key in where.get("_start", []):
            self.illustration(key)
        for sec in sections:
            head = add_heading(self.doc, sec.title, 3, color_hex, size=11, style=self.style)
            head.paragraph_format.keep_with_next = True
            for para in sec.paragraphs:
                self.text(para)
            for key in where.get(sec.key, []):
                self.illustration(key)

    def illustration(self, key: str) -> None:
        """Illustration de l'analyse et sa légende (illustrations.py)."""
        import illustrations as IL
        if key in self.charts:
            self.image(key, 15.5)
            self.text(IL.caption(self.request, key), size=8.5, italic=True, after=10)

    def image(self, key: str, width_cm: float) -> None:
        if key in self.charts:
            try:
                pic_p = self.doc.add_paragraph()
                pic_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                pic_p.add_run().add_picture(io.BytesIO(self.charts[key]), width=Cm(width_cm))
                pic_p.paragraph_format.space_after = Pt(8)
            except Exception:
                pass


def _report(request: ESGRequest, scores: ESGScores, content: dict, charts: dict | None) -> _Report:
    from content_generator import (pillar_headline, section_headlines, risks_opportunities,
                                   compliance_assessment, enriched_recommendations, roadmap_12m)
    colors = docx_hex(request.aesthetic_theme)
    if getattr(request, "custom_colors", None):
        from branding import brand_docx_hex
        colors = brand_docx_hex(colors, request.custom_colors)
    style = docx_style(request.aesthetic_theme)
    TR = L(request.language)
    ref = TR["cover_refs_vsme"] if getattr(request, "reporting_framework", "csrd") == "vsme" \
        else TR["cover_refs"]

    doc = Document()
    normal = cast(ParagraphStyle, doc.styles['Normal'])
    normal.font.name = style["font"]
    normal.font.size = Pt(10.5)
    # Page margins
    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)

    return _Report(
        doc=doc, request=request, scores=scores, content=content, colors=colors, style=style,
        TR=TR, ref=ref, ro=risks_opportunities(request, scores),
        gaps=compliance_assessment(request, scores),
        recs=enriched_recommendations(request, scores) if request.include_recommendations else [],
        roadmap=roadmap_12m(request, scores), headlines=pillar_headline(request, scores),
        section_heads=section_headlines(request, scores),
        notes=getattr(request, "consultant_notes", None) or {}, charts=charts or {})


def _cover(r: _Report, logo_bytes: bytes | None, cover_art: bytes | None) -> None:
    """Couverture : identité, illustration, scores, note ; puis saut de page."""
    _cover_identity(r, logo_bytes)
    _cover_meta(r)
    # Illustration de couverture (générée localement)
    if cover_art:
        try:
            art_p = r.doc.add_paragraph()
            art_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            art_p.add_run().add_picture(io.BytesIO(cover_art), width=Cm(16))
            art_p.paragraph_format.space_after = Pt(12)
        except Exception:
            pass
    _cover_scores(r)
    r.doc.add_page_break()


def _cover_identity(r: _Report, logo_bytes: bytes | None) -> None:
    """Logo et nom de l'entreprise, filet d'accent."""
    doc, request, colors, style = r.doc, r.request, r.colors, r.style
    # Logo entreprise
    if logo_bytes:
        try:
            logo_p = doc.add_paragraph()
            logo_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            logo_p.add_run().add_picture(io.BytesIO(logo_bytes), height=Cm(2))
        except Exception:
            pass

    title_p = doc.add_paragraph()
    title_run = title_p.add_run(request.company.name.upper())
    title_run.font.size = Pt(32)
    title_run.bold = True
    title_run.font.name = style["font"]
    title_run.font.name = style["font_title"]
    if request.aesthetic_theme == AestheticTheme.TERRE:
        title_run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shade_paragraph(title_p, colors["primary"])
        title_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    else:
        title_run.font.color.rgb = hex_to_rgb(colors["primary"])
        title_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    title_p.paragraph_format.space_after = Pt(4)

    add_hr(doc, colors["accent"])


def _cover_meta(r: _Report) -> None:
    """Type de rapport, exercice / secteur / pays, présentateur."""
    doc, request, colors, TR = r.doc, r.request, r.colors, r.TR
    type_map = {
        "white_paper": TR["rep_white_paper"],
        "full_report": TR["rep_full_report"],
        "executive_summary_pdf": TR["rep_executive_summary_pdf"],
    }
    sub_p = doc.add_paragraph()
    sub_run = sub_p.add_run(type_map.get(request.report_type.value, "Rapport ESG"))
    sub_run.font.size = Pt(18)
    sub_run.bold = True
    sub_run.font.color.rgb = hex_to_rgb(colors["secondary"])

    meta_p = doc.add_paragraph()
    meta_run = meta_p.add_run(
        f"{TR['exercise']} {request.company.reporting_year}  •  {request.company.sector}  •  {request.company.country}"
    )
    meta_run.font.size = Pt(11)
    meta_run.font.color.rgb = hex_to_rgb("7F8C8D")
    meta_p.paragraph_format.space_after = Pt(8)

    # Présentateur
    if request.company.presenter_name:
        pres_line = f"{TR['presented_by']} {request.company.presenter_name}"
        if request.company.presenter_title:
            pres_line += f" — {request.company.presenter_title}"
        pres_p = doc.add_paragraph()
        pres_run = pres_p.add_run(pres_line)
        pres_run.font.size = Pt(11)
        pres_run.italic = True
        pres_run.font.color.rgb = hex_to_rgb(colors["secondary"])
        pres_p.paragraph_format.space_after = Pt(12)


def _cover_scores(r: _Report) -> None:
    """Tableau des trois piliers + score global, puis la note lettrée."""
    doc, scores, colors, TR = r.doc, r.scores, r.colors, r.TR
    summary_table = doc.add_table(rows=2, cols=4)
    summary_table.style = 'Table Grid'
    headers = [TR["chart_env"], TR["chart_soc"], TR["chart_gov"], TR["score_global_short"]]
    values = [scores.environmental_score, scores.social_score,
              scores.governance_score, scores.total_esg_score]
    value_colors = [colors["env"], colors["social"], colors["gov"], colors["accent"]]

    for i, (hdr, val, col) in enumerate(zip(headers, values, value_colors)):
        hdr_cell = summary_table.rows[0].cells[i]
        shade_cell(hdr_cell, colors.get("light", "F5F5F5"))
        hdr_cell.paragraphs[0].clear()
        run = hdr_cell.paragraphs[0].add_run(hdr)
        run.font.size = Pt(9)
        run.bold = True
        run.font.color.rgb = hex_to_rgb(colors["secondary"])
        hdr_cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        val_cell = summary_table.rows[1].cells[i]
        val_cell.paragraphs[0].clear()
        rv = val_cell.paragraphs[0].add_run(score_label(val, 1))
        rv.font.size = Pt(24)
        rv.bold = True
        rv.font.color.rgb = hex_to_rgb(col)
        val_cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()

    rating_p = doc.add_paragraph()
    rating_run = rating_p.add_run(f"{TR['note']} : {scores.rating or NON_NOTE}")
    rating_run.font.size = Pt(16)
    rating_run.bold = True
    rating_run.font.color.rgb = hex_to_rgb(colors["accent"])
    rating_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rating_p.paragraph_format.space_after = Pt(24)


def _ceo_quote(r: _Report) -> None:
    """Mot de la direction (citation), s'il a été saisi."""
    request, colors, doc = r.request, r.colors, r.doc
    if not request.company.ceo_quote:
        return
    kp = doc.add_paragraph()
    kr = kp.add_run(r.TR["quote_kicker"])
    kr.bold = True; kr.font.size = Pt(9)
    kr.font.color.rgb = hex_to_rgb(colors["accent"])
    quote = request.company.ceo_quote.strip().strip('"“”')
    qp = doc.add_paragraph()
    qr = qp.add_run(f"« {quote} »" if request.language != "en" else f"“{quote}”")
    qr.italic = True; qr.font.size = Pt(13)
    qr.font.color.rgb = hex_to_rgb(colors["primary"])
    shade_paragraph(qp, r.light)
    qp.paragraph_format.space_after = Pt(4)
    if request.company.presenter_name:
        ap = doc.add_paragraph()
        attrib = request.company.presenter_name
        if request.company.presenter_title:
            attrib += f" — {request.company.presenter_title}"
        ar = ap.add_run(attrib)
        ar.bold = True; ar.font.size = Pt(9.5)
        ar.font.color.rgb = hex_to_rgb("7F8C8D")
        ap.paragraph_format.space_after = Pt(18)


def _company(r: _Report) -> None:
    """L'entreprise en bref + initiatives déclarées."""
    import narrative as NR
    r.heading(r.TR["ed_company"], 1, r.colors["primary"])
    add_hr(r.doc, r.colors["secondary"])
    for para in NR.company_paragraphs(r.request, r.ref):
        r.text(para)
    inits = NR.initiatives(r.request)
    if inits:
        r.heading(r.TR["ed_initiatives"], 2, r.colors["secondary"])
        add_bullet_list(r.doc, inits, "•", r.colors["accent"])


def _bullets(r: _Report, items, numbered=False) -> None:
    for it in items:
        p = r.doc.add_paragraph(style="List Number" if numbered else "List Bullet")
        p.add_run(it).font.size = Pt(10.5)


def _overview(r: _Report) -> None:
    """Diagnostic d'ensemble (synthesis.py), comme le PDF."""
    import synthesis as SY
    import illustrations as IL
    o = SY.overview(r.request, r.scores)
    primary = r.colors["primary"]
    r.heading(o["title"], 2, primary)
    r.heading(o["profile_title"], 3, primary)
    for p in o["profile"]:
        r.text(p)
    if o["issues"]:
        r.heading(o["issues_title"], 3, primary)
        r.text(o["issues_intro"])
        for key in IL.placements_overview():
            r.illustration(key)
        pillar_hex = {"env": r.colors.get("env", primary), "social": r.colors.get("social", primary),
                      "gov": r.colors.get("gov", primary)}
        for n, issue in enumerate(o["issues"], 1):
            head = add_heading(r.doc, f"{n}. {issue.title}", 3, pillar_hex[issue.pillar], size=11,
                               style=r.style)
            head.paragraph_format.keep_with_next = True
            r.text(issue.cause)
            r.text(issue.csq)
    if o["links"]:
        r.heading(o["links_title"], 3, primary)
        _bullets(r, o["links"])


def _closing_synthesis(r: _Report) -> None:
    import synthesis as SY
    c = SY.closing(r.request, r.scores)
    color = r.colors["secondary"]
    if c["retain"]:
        r.heading(c["retain_title"], 2, color)
        _bullets(r, c["retain"])
    if c["horizon"]:
        r.heading(c["horizon_title"], 2, color)
        for p in c["horizon"]:
            r.text(p)
    r.heading(c["first_title"], 2, color)
    r.text(c["first_intro"])
    _bullets(r, c["first"], numbered=True)


def _executive(r: _Report) -> None:
    """1. Synthèse exécutive + analyse globale du consultant."""
    request, scores = r.request, r.scores
    r.heading(r.TR["pdf_s1"], 1, r.colors["primary"])
    add_hr(r.doc, r.colors["secondary"])
    exec_text = r.content.get("executive_summary",
        f"{request.company.name} présente son rapport ESG {request.company.reporting_year} "
        f"avec un score global de {score_label(scores.total_esg_score, 1)}/100 (note {scores.rating or NON_NOTE}).")
    r.doc.add_paragraph(exec_text).paragraph_format.space_after = Pt(12)
    if r.notes.get("global"):
        add_consultant_note(r.doc, r.notes["global"], r.colors, r.TR)


def _env_kpis(env, k: dict) -> list:
    kpis = []
    if env.co2_emissions_tonnes is not None: kpis.append((k["co2"], f"{env.co2_emissions_tonnes:,.0f}"))
    if env.renewable_energy_percent is not None: kpis.append((k["renewable"], f"{env.renewable_energy_percent:.1f}%"))
    if env.energy_consumption_mwh is not None: kpis.append((k["energy"], f"{env.energy_consumption_mwh:,.0f}"))
    if env.water_consumption_m3 is not None: kpis.append((k["water"], f"{env.water_consumption_m3:,.0f}"))
    if env.waste_recycled_percent is not None: kpis.append((k["recycling"], f"{env.waste_recycled_percent:.1f}%"))
    if env.scope1_emissions is not None: kpis.append((k["s1"], f"{env.scope1_emissions:,.0f}"))
    if env.scope2_emissions is not None: kpis.append((k["s2"], f"{env.scope2_emissions:,.0f}"))
    if env.scope3_emissions is not None: kpis.append((k["s3"], f"{env.scope3_emissions:,.0f}"))
    return kpis


def _social_kpis(soc, k: dict) -> list:
    kpis = []
    if soc.total_employees is not None: kpis.append((k["employees"], f"{soc.total_employees:,}"))
    if soc.female_employees_percent is not None: kpis.append((k["women"], f"{soc.female_employees_percent:.1f}%"))
    if soc.employee_turnover_percent is not None: kpis.append((k["turnover"], f"{soc.employee_turnover_percent:.1f}%"))
    if soc.training_hours_per_employee is not None: kpis.append((k["training"], f"{soc.training_hours_per_employee:.0f}"))
    if soc.accident_frequency_rate is not None: kpis.append((k["accident"], f"{soc.accident_frequency_rate:.2f}"))
    if soc.customer_satisfaction_score is not None: kpis.append((k["satisfaction"], f"{soc.customer_satisfaction_score:.1f}"))
    return kpis


def _gov_kpis(gov, k: dict) -> list:
    kpis = []
    if gov.board_members is not None: kpis.append((k["board"], str(gov.board_members)))
    if gov.female_board_percent is not None: kpis.append((k["women_board"], f"{gov.female_board_percent:.1f}%"))
    if gov.independent_board_percent is not None: kpis.append((k["independent"], f"{gov.independent_board_percent:.1f}%"))
    if gov.csr_budget_eur is not None: kpis.append((k["csr"], f"{gov.csr_budget_eur:,.0f}"))
    if gov.esg_audit_conducted is not None:
        kpis.append((k["audit"], k["yes"] if gov.esg_audit_conducted else k["no"]))
    if gov.sustainability_committee is not None:
        kpis.append((k["committee"], k["yes"] if gov.sustainability_committee else k["no"]))
    return kpis


# Pilier -> (titre de section, libellé du score, attribut du score, texte par
# défaut si le contenu manque, extracteur des indicateurs)
_PILLAR_SECTIONS = {
    "env": ("pdf_s2", "score_env_label", "environmental_score",
            "Analyse des données environnementales.", _env_kpis),
    "social": ("pdf_s3", "score_soc_label", "social_score",
               "Analyse des données sociales.", _social_kpis),
    "gov": ("pdf_s4", "score_gov_label", "governance_score",
            "Analyse des données de gouvernance.", _gov_kpis),
}
_CONTENT_KEY = {"env": "environmental", "social": "social", "gov": "governance"}


def _pillar(r: _Report, pillar: str) -> None:
    """Section d'un pilier : conclusion, note du consultant, score, texte,
    tableau d'indicateurs, lecture ; bilan GES pour l'environnement."""
    import narrative as NR
    title_key, score_label, score_attr, fallback, kpis_of = _PILLAR_SECTIONS[pillar]
    color = r.colors[pillar]
    r.heading(r.TR[title_key], 1, color)
    add_hr(r.doc, color)
    r.conclusion(r.headlines[pillar], color)
    if r.notes.get(pillar):
        add_consultant_note(r.doc, r.notes[pillar], r.colors, r.TR)
    add_score_block(r.doc, r.TR[score_label], getattr(r.scores, score_attr), color)

    r.doc.add_paragraph(r.content.get(_CONTENT_KEY[pillar], fallback)).paragraph_format.space_after = Pt(8)

    data = {"env": r.request.environmental, "social": r.request.social,
            "gov": r.request.governance}[pillar]
    add_kpi_table(r.doc, kpis_of(data, r.TR["kpit"]), r.colors)
    r.reading(pillar, color)
    if pillar == "env":
        ghg = NR.ghg_paragraph(r.request)
        if ghg:
            r.heading(r.TR["ed_ghg_table"], 2, color)
            r.text(ghg)


def _analyses(r: _Report) -> None:
    """5. Analyses de durabilité : priorisation, objectifs, taxonomie, climat."""
    content, colors, TR = r.content, r.colors, r.TR
    r.heading(TR["pdf_s5"], 1, colors["primary"])
    add_hr(r.doc, colors["secondary"])

    r.heading(TR["sub_materiality"], 2, colors["secondary"])
    if content.get("materiality"):
        r.doc.add_paragraph(content["materiality"]).paragraph_format.space_after = Pt(6)
    r.image("materiality", 12)

    r.heading(TR["sub_targets"], 2, colors["secondary"])
    if content.get("targets"):
        r.doc.add_paragraph(content["targets"]).paragraph_format.space_after = Pt(6)
    # (supprimes) graphiques "targets" et "carbon_trajectory" — voir esg_advanced.py

    if content.get("taxonomy"):
        r.heading(TR["sub_taxonomy"], 2, colors["secondary"])
        r.doc.add_paragraph(content["taxonomy"]).paragraph_format.space_after = Pt(6)
        r.image("taxonomy", 14)

    r.heading(TR["sub_climate"], 2, colors["secondary"])
    if content.get("climate_risk"):
        r.doc.add_paragraph(content["climate_risk"]).paragraph_format.space_after = Pt(8)

    r.doc.add_page_break()


def _act1(r: _Report) -> None:
    """Ouverture du chapitre 01 — Diagnostic."""
    import narrative as NR
    TR = r.TR
    r.heading(f'01 — {TR["div1_title"]}', 1, r.colors["accent"])
    r.text(TR["div1_sub"], size=12, italic=True, after=4)
    r.text(NR.act1_intro(r.request, r.scores, r.gaps, r.ro["risks"]), shade=r.light, after=14)


def _strategic(r: _Report) -> None:
    """6. Analyse stratégique : points forts / axes d'amélioration."""
    TR, colors = r.TR, r.colors
    r.heading(TR["pdf_s6"], 1, colors["primary"])
    add_hr(r.doc, colors["accent"])
    r.conclusion(r.section_heads["strategic"], colors["accent"])

    r.heading(TR["strengths"], 2, colors["env"])
    add_bullet_list(r.doc, r.scores.strengths, "✅", colors["env"])

    r.heading(TR["weaknesses"], 2, "E74C3C")
    add_bullet_list(r.doc, r.scores.weaknesses, "⚠️", "E74C3C")


def _recommendations(r: _Report) -> None:
    """Chapitre 02 — Plan d'action : recommandations détaillées."""
    if not (r.request.include_recommendations and r.scores.recommendations):
        return
    import narrative as NR
    TR, colors, doc = r.TR, r.colors, r.doc
    r.heading(f'02 — {TR["div2_title"]}', 1, colors["accent"])
    r.text(TR["div2_sub"], size=12, italic=True, after=4)
    r.text(NR.act2_intro(r.request, r.recs, r.roadmap), shade=r.light, after=14)
    r.heading(TR["pdf_s7"], 1, colors["primary"])
    add_hr(doc, colors["accent"])
    r.text(NR.recs_intro(r.request, r.recs))
    for i, rec in enumerate(r.recs, 1):
        p = doc.add_paragraph()
        num = p.add_run(f"{i}.  ")
        num.bold = True
        num.font.color.rgb = hex_to_rgb(colors["accent"])
        tr_ = p.add_run(rec["title"]); tr_.bold = True; tr_.font.size = Pt(10.5)
        p.paragraph_format.space_after = Pt(1)
        dp = doc.add_paragraph()
        dp.paragraph_format.left_indent = Cm(0.7)
        dp.paragraph_format.space_after = Pt(6)
        dr = dp.add_run(rec["detail"]); dr.font.size = Pt(9.5)
        meta = dp.add_run(f'\n{TR["objective_col"]} : {rec["objective"]}  ·  '
                          f'{TR["owner_col"]} : {rec["owner"]}  ·  {rec["horizon"]}')
        meta.font.size = Pt(8.5)
        meta.font.color.rgb = hex_to_rgb("7F8C8D")


def _positioning(r: _Report) -> None:
    """Diagnostic stratégique : positionnement interne des piliers + maturité.
    Aucune référence externe (cf. report_generator.py)."""
    import narrative as NR
    from content_generator import benchmark_verdict, maturity_text
    bv = benchmark_verdict(r.request, r.scores)
    mt = maturity_text(r.request, r.scores)
    TR, colors, doc, scores = r.TR, r.colors, r.doc, r.scores

    r.heading(TR["pdf_diag"], 1, colors["primary"])
    add_hr(doc, colors["accent"])
    if bv is None:  # moins de deux piliers notés : rien à positionner
        from content_generator import POSITIONNEMENT_IMPOSSIBLE
        r.text(POSITIONNEMENT_IMPOSSIBLE[r.lang])
    else:
        p = doc.add_paragraph()
        r_ = p.add_run(bv["title"]); r_.bold = True; r_.font.size = Pt(12)
        r_.font.color.rgb = hex_to_rgb(colors["secondary"])
        r.text(NR.bench_intro(r.request), after=4)
        cap = doc.add_paragraph(TR["pdf_bench_sub"]); cap.runs[0].font.size = Pt(8)
        cap.runs[0].font.color.rgb = hex_to_rgb("7F8C8D")
        _positioning_table(r, bv["rows"])
        ins = doc.add_paragraph(); ins.paragraph_format.space_before = Pt(6)
        ins.add_run(bv["insight"]).font.size = Pt(10)
        shade_paragraph(ins, r.light)

    from content_generator import maturite_libelle
    mp = doc.add_paragraph(); mp.paragraph_format.space_before = Pt(8)
    mr = mp.add_run(f'{TR["pdf_maturity_sub"]} : {maturite_libelle(mt, TR)}')
    mr.bold = True; mr.font.color.rgb = hex_to_rgb(colors["secondary"]); mr.font.size = Pt(11)
    doc.add_paragraph(mt["next_hint"])


def _positioning_table(r: _Report, bench_rows: list) -> None:
    """Piliers classés : score, écart au meilleur pilier, lecture ; puis le global."""
    TR, colors, doc, scores = r.TR, r.colors, r.doc, r.scores
    pil_lbl = {"env": TR["pillar_env"], "social": TR["pillar_soc"], "gov": TR["pillar_gov"]}
    rows = [(TR["bench_metric_col"], TR["bench_you"], TR["bench_delta_col"], TR["bench_reading_col"])]
    for row in bench_rows:
        delta = row["delta"]
        rows.append((pil_lbl[row["key"]], score_label(row["score"]),
                     "—" if not delta else f"{delta:.0f} pts", row["reading"] or TR["bench_not_rated"]))
    rows.append((TR.get("score_global_short", "Global"), score_label(scores.total_esg_score),
                 "", scores.rating or NON_NOTE))
    tbl = doc.add_table(rows=len(rows), cols=4)
    tbl.style = "Table Grid"
    for ci, val in enumerate(rows[0]):
        c = tbl.rows[0].cells[ci]; c.paragraphs[0].add_run(val).bold = True
        shade_cell(c, colors["primary"])
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        c.paragraphs[0].runs[0].font.size = Pt(9)
    for ri in range(1, len(rows)):
        for ci, val in enumerate(rows[ri]):
            c = tbl.rows[ri].cells[ci]; run = c.paragraphs[0].add_run(val)
            run.font.size = Pt(9.5)
            if ci == 0:
                run.bold = True
            if ci == 3:
                run.bold = True
                run.font.color.rgb = hex_to_rgb("2E7D32" if not val.startswith("-") else "E74C3C")


def _coverage(r: _Report) -> None:
    """Couverture des exigences de reporting (statuts : gap_status, source unique)."""
    import narrative as NR
    import gap_status as GS
    TR, colors, doc = r.TR, r.colors, r.doc
    r.heading(TR["gap_title"], 2, colors["secondary"])
    r.text(NR.gaps_intro(r.request, r.gaps, r.ref))
    gtbl = doc.add_table(rows=len(r.gaps) + 1, cols=4)
    gtbl.style = "Table Grid"
    for ci, h in enumerate((TR["gap_req"], TR["gap_ref"], TR["gap_status"], TR["gap_note"])):
        c = gtbl.rows[0].cells[ci]
        run = c.paragraphs[0].add_run(h); run.bold = True; run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shade_cell(c, colors["primary"])
    for ri, g in enumerate(r.gaps, 1):
        vals = (g["req"], g["ref"], GS.libelle(TR, g["status"], g["nature"]), g["note"])
        for ci, v in enumerate(vals):
            run = gtbl.rows[ri].cells[ci].paragraphs[0].add_run(v)
            run.font.size = Pt(9)
            if ci == 0:
                run.bold = True
            if ci == 2:
                run.bold = True
                run.font.color.rgb = hex_to_rgb(GS.hex_sans_diese(g["status"], g["nature"]))
    doc.add_paragraph()


def _risks(r: _Report) -> None:
    """Risques cotés (impact × probabilité, P1-P3) et opportunités."""
    import narrative as NR
    TR = r.TR
    r.heading(TR["risks_head"], 2, "E74C3C")
    r.text(NR.risks_intro(r.request, r.ro["risks"]))
    add_bullet_list(r.doc, [
        f'[{i.get("priority", "P2")}] {i["tag"]} — {i["text"]} '
        f'({TR["risk_impact"].lower()} : {i.get("impact", "—").lower()} · '
        f'{TR["risk_lik"].lower()} : {i.get("likelihood", "—").lower()})'
        for i in r.ro["risks"]], "▪", "E74C3C")
    r.heading(TR["opps_head"], 2, r.colors["env"])
    add_bullet_list(r.doc, [f'{i["tag"]} — {i["text"]}' for i in r.ro["opportunities"]], "▪", r.colors["env"])


def _roadmap(r: _Report) -> None:
    """Feuille de route 12 mois, si au moins une action est planifiée."""
    if not any(ph["actions"] for ph in r.roadmap):
        return
    import narrative as NR
    TR, colors, doc = r.TR, r.colors, r.doc
    r.heading(TR["roadmap_title"], 2, colors["accent"])
    r.text(NR.roadmap_intro(r.request, r.roadmap))
    for ph in r.roadmap:
        pp = doc.add_paragraph()
        hr = pp.add_run(f'{ph["label"]} — {ph["sub"]}')
        hr.bold = True; hr.font.color.rgb = hex_to_rgb(colors["primary"]); hr.font.size = Pt(10.5)
        for act in ph["actions"][:4]:
            ap = doc.add_paragraph(style="List Bullet")
            ar = ap.add_run(act["title"]); ar.font.size = Pt(10)
            if act["quick_win"]:
                qw = ap.add_run(f'  [{TR["quick_win"]}]')
                qw.bold = True; qw.font.size = Pt(8)
                qw.font.color.rgb = hex_to_rgb(colors["accent"])


# (supprimee) Section « 7. Cadres de Référence & Alignement ODD » — voir la
# note dans report_generator.py.


def _closing(r: _Report, cover_art: bytes | None) -> None:
    """Conclusion, note méthodologique (et mention des photos d'illustration)."""
    TR, colors, doc, request = r.TR, r.colors, r.doc, r.request
    doc.add_page_break()
    r.heading(TR["pdf_concl"], 1, colors["primary"])
    add_hr(doc, colors["primary"])
    conclusion = r.content.get("conclusion",
        f"{request.company.name} réaffirme son engagement vers un modèle d'affaires durable. "
        "Les axes d'amélioration identifiés feront l'objet de plans d'action concrets."
    )
    doc.add_paragraph(conclusion)
    _closing_synthesis(r)

    if r.content.get("methodology"):
        r.heading(TR["pdf_methodo"], 2, colors["secondary"])
        mp = doc.add_paragraph()
        mr = mp.add_run(r.content["methodology"])
        mr.font.size = Pt(8.5)
        mr.font.color.rgb = hex_to_rgb("5A6572")
        shade_paragraph(mp, r.light)
    # Photo de couverture issue de la banque d'illustration : mention
    if cover_art:
        from pdf_kit import Kit
        if Kit(request).uses_bank(("cover",)):
            r.text(TR["ed_photo_note"], size=8, italic=True)


def _glossary(r: _Report) -> None:
    """Glossaire filtré sur les termes que le rapport emploie."""
    from glossary import glossary_entries
    entries = glossary_entries(r.request, r.scores)
    if not entries:
        return
    r.heading(r.TR["pdf_glossary"], 2, r.colors["secondary"])
    gt = r.doc.add_table(rows=len(entries), cols=2)
    gt.style = "Table Grid"
    for ri, e in enumerate(entries):
        tr_ = gt.rows[ri].cells[0].paragraphs[0].add_run(e["term"])
        tr_.bold = True
        tr_.font.size = Pt(8.5)
        tr_.font.color.rgb = hex_to_rgb(r.colors["primary"])
        dr = gt.rows[ri].cells[1].paragraphs[0].add_run(e["definition"])
        dr.font.size = Pt(8.5)


def _footer(r: _Report) -> None:
    r.doc.add_paragraph()
    footer_p = r.doc.add_paragraph(
        f"© {r.request.company.reporting_year} {r.request.company.name} — " + r.TR["gen_auto"]
    )
    footer_p.runs[0].font.size = Pt(8)
    footer_p.runs[0].font.color.rgb = hex_to_rgb("7F8C8D")
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def generate_word_report(request: ESGRequest, scores: ESGScores, content: dict,
                         logo_bytes: bytes | None = None, cover_art: bytes | None = None,
                         charts: dict | None = None) -> bytes:
    """Rapport Word éditable, même plan et même texte analytique que le PDF :
    ouverture, trois piliers, analyses, chapitre 01 (diagnostic), chapitre 02
    (plan d'action), clôture. Une fonction par section."""
    r = _report(request, scores, content, charts)
    _cover(r, logo_bytes, cover_art)
    _ceo_quote(r)
    _company(r)
    _executive(r)
    _overview(r)
    for pillar in ("env", "social", "gov"):
        _pillar(r, pillar)
    r.doc.add_page_break()
    _analyses(r)
    _act1(r)
    _strategic(r)
    _recommendations(r)
    _positioning(r)
    _coverage(r)
    _risks(r)
    _roadmap(r)
    _closing(r, cover_art)
    _glossary(r)
    _footer(r)

    buf = io.BytesIO()
    from typo import fix_docx
    fix_docx(r.doc, request.language)  # nombres à la française (typo.py)
    r.doc.save(buf)
    buf.seek(0)
    return buf.read()
