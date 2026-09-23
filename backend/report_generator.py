"""Rapport ESG PDF, composé selon le gabarit éditorial choisi.

Structure (identique pour les six gabarits, seul l'habillage change) :
  couverture · sommaire · l'entreprise en bref · mot de la direction (si
  citation) · ESG en un coup d'œil · 1-4 synthèse et piliers · focus
  environnement · 5 analyses · chapitre 01 diagnostic · 6 analyse et
  diagnostic · chapitre 02 plan d'action · 7 recommandations et feuille de
  route · 8 conclusion, note méthodologique, glossaire · quatrième de
  couverture.

Le sommaire affiche les numéros de page : le document est donc composé en
deux passes, la première relevant la page de chaque section.
"""
import io
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, Image, PageBreak, KeepTogether,
                                NextPageTemplate, CondPageBreak)

from models import ESGRequest, ESGScores
from i18n import L
from pdf_kit import (Kit, Px, FullPage, Anchor, PX, PAGE_W, PAGE_H, clean, esc, hexc,
                     draw_header, draw_footer, paint_paper)
import pdf_pages as PG

pdf_txt = clean  # nom historique, conservé pour les appelants

# Zone de texte des pages courantes, en px de maquette (cf. pdf_kit.Px)
_M_LEFT, _M_TOP, _M_BOTTOM = 56, 96, 1066
CW = (794 - 2 * _M_LEFT) * PX          # largeur utile (pt)
_STATUS_HEX = {"good": "#2E7D32", "warn": "#D97706", "bad": "#C0392B"}
_PRIO_HEX = {"P1": "#C0392B", "P2": "#D97706", "P3": "#7F8C8D"}


# ═══════════════════════════════════════════════════════════════════════════
# Mise en forme des nombres (FR : espace des milliers, virgule décimale)
# ═══════════════════════════════════════════════════════════════════════════

def _num(v: float, lang: str, decimals: int = 0) -> str:
    s = f"{v:,.{decimals}f}"
    if lang == "en":
        return s
    return s.replace(",", " ").replace(".", ",")


def _pct(v: float, lang: str) -> str:
    return f"{_num(v, lang)}%" if lang == "en" else f"{_num(v, lang)} %"


# ═══════════════════════════════════════════════════════════════════════════
# Styles et composants de flux
# ═══════════════════════════════════════════════════════════════════════════

def build_styles(k: Kit) -> dict:
    return {
        "h1": k.ps("h1", 25, font=k.title_font, color="ink", leading=29, spaceBefore=6,
                   spaceAfter=4, keepWithNext=1),
        "h2": k.ps("h2", 13.5, font="display", color="ink", leading=17, spaceBefore=12,
                   spaceAfter=5, keepWithNext=1),
        "body": k.ps("body", 9.6, color="ink", leading=15, spaceAfter=6),
        "bullet": k.ps("bullet", 9.6, color="ink", leading=14, leftIndent=12, spaceAfter=3),
        "caption": k.ps("caption", 8, font="body_i", color="muted", alignment=TA_CENTER),
        "small": k.ps("small", 8.3, color="ink", leading=11.5),
        "small_b": k.ps("small_b", 8.3, font="body_b", color="ink", leading=11.5),
        "th": k.ps("th", 7.4, font="body_b", color="muted", leading=10, charSpace=0.5),
        "footer": k.ps("footer", 8, font="body_i", color="muted", alignment=TA_CENTER),
    }


def section_head(story, title, color_key, k: Kit, S, anchors, key=None, keep_cm=5):
    """Titre de section. « 2. Pilier… » est posé sur deux lignes (numéro en
    accent, titre dessous) ; l'extraction texte rend « 2. Pilier… », ce que
    vérifie le test de numérotation du sommaire."""
    if key:
        story.append(Anchor(key, anchors))
    story.append(CondPageBreak(keep_cm * 28.35))
    m = re.match(r"^(\d+)\.\s+(.*)$", title)
    if m:
        markup = (f'<font name="{k.f["display"]}" size="15" color="{hexc(k.c["accent"])}">'
                  f'{m.group(1)}.</font><br/>{esc(m.group(2))}')
    else:
        markup = esc(title)
    story.append(Paragraph(markup, S["h1"]))
    rule = Table([[""]], colWidths=[34], rowHeights=[1.6])
    rule.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), k.c[color_key])]))
    rule.hAlign = "LEFT"
    story.append(rule)
    story.append(Spacer(1, 10))


def _box(content, k: Kit, bg, left=None, left_w=2.2, pad=12):
    t = Table([[content]], colWidths=[CW])
    st = [("BACKGROUND", (0, 0), (-1, -1), bg),
          ("LEFTPADDING", (0, 0), (-1, -1), pad + 2), ("RIGHTPADDING", (0, 0), (-1, -1), pad),
          ("TOPPADDING", (0, 0), (-1, -1), pad - 2), ("BOTTOMPADDING", (0, 0), (-1, -1), pad)]
    if left is not None:
        st.append(("LINEBEFORE", (0, 0), (0, -1), left_w, left))
    if k.layout["radius"]:
        st.append(("ROUNDEDCORNERS", [k.layout["radius"]] * 4))
    t.setStyle(TableStyle(st))
    return t


def insight_callout(story, text, color_key, k: Kit):
    """Encadré « lecture métier » — le message clé de la section."""
    story.append(_box(Paragraph(esc(text), k.ps("ic", 10, color="ink", leading=15)), k,
                      k.c["panel"], left=k.c[color_key]))
    story.append(Spacer(1, 8))


def consultant_callout(story, text, k: Kit, TR):
    """Encart « L'analyse du consultant », distinct de la lecture automatique."""
    flow = [Paragraph(esc(TR["consultant_note"]), k.ps("cnh", 7.6, font="body_b",
                                                        color="accent_on_primary", charSpace=0.8,
                                                        spaceAfter=4)),
            Paragraph(esc(text), k.ps("cnb", 10, font="display_i", color="on_primary", leading=15))]
    story.append(_box(flow, k, k.c["primary"]))
    story.append(Spacer(1, 8))


def kpi_block(kpis, k: Kit, lang):
    """Indicateurs d'une section. Style selon le gabarit : filets (hairline),
    doubles filets (double_rule), cartes (cards) ou liste (list)."""
    mode = k.layout["kpi"]
    lab_st = k.ps("kl", 7.4, color="muted", leading=9.5, charSpace=0.4)
    val_st = k.ps("kv", 17, font="display", color="ink", leading=20)

    def val(item):
        status = item[2] if len(item) > 2 else None
        dot = (f'<font color="{_STATUS_HEX[status]}" size="13">•</font>&nbsp;'
               if status in _STATUS_HEX else "")
        return dot + esc(item[1])

    if mode == "list":
        rows = [[Paragraph(esc(i[0]), k.ps("ll", 9.4, color="ink")),
                 Paragraph(val(i), k.ps("lv", 9.4, font="body_b", color="ink", alignment=2))]
                for i in kpis]
        half = (len(rows) + 1) // 2
        n_right = len(rows) - half
        right = rows[half:] + [["", ""]] * (half - n_right)
        data = [l + [""] + r for l, r in zip(rows[:half], right)]
        w = (CW - 24) / 2
        t = Table(data, colWidths=[w * 0.62, w * 0.38, 24, w * 0.62, w * 0.38])
        st = [("LINEBELOW", (0, 0), (1, -1), 0.5, k.c["rule"]),
              ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
              ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
              ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]
        if n_right:
            st.append(("LINEBELOW", (3, 0), (4, n_right - 1), 0.5, k.c["rule"]))
        t.setStyle(TableStyle(st))
        return t

    cells = [[Paragraph(esc(i[0]).upper(), lab_st), Spacer(1, 4), Paragraph(val(i), val_st)]
             for i in kpis]
    ncol = 3
    data = [cells[i:i + ncol] + [""] * (ncol - len(cells[i:i + ncol]))
            for i in range(0, len(cells), ncol)]
    if mode == "cards":
        gap = 8
        w = (CW - gap * (ncol - 1)) / ncol
        grid = []
        for row in data:
            line = []
            for j, c in enumerate(row):
                card = _card(c, k, w) if c else ""
                line += [card] + ([""] if j < ncol - 1 else [])
            grid.append(line)
        t = Table(grid, colWidths=[w, gap] * (ncol - 1) + [w])
        t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                               ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), gap)]))
        return t
    t = Table(data, colWidths=[CW / ncol] * ncol)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
          ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
          ("LINEAFTER", (0, 0), (-2, -1), 0.5, k.c["rule"])]
    if mode == "double_rule":
        st += [("LINEABOVE", (0, 0), (-1, 0), 1.6, k.c["ink"]),
               ("LINEBELOW", (0, -1), (-1, -1), 1.6, k.c["ink"]),
               ("LINEBELOW", (0, 0), (-1, -2), 0.5, k.c["rule"])]
    else:
        st += [("LINEABOVE", (0, 0), (-1, 0), 0.8, k.c["ink"]),
               ("LINEBELOW", (0, 0), (-1, -1), 0.5, k.c["rule"])]
    t.setStyle(TableStyle(st))
    return t


def _card(content, k: Kit, w):
    t = Table([[content]], colWidths=[w])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), k.c["surface"]),
                           ("ROUNDEDCORNERS", [k.layout["radius"]] * 4),
                           ("LEFTPADDING", (0, 0), (-1, -1), 12), ("TOPPADDING", (0, 0), (-1, -1), 10),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 12)]))
    return t


def data_table(rows, widths, k: Kit, header=True, total=False, zebra=False):
    """Tableau éditorial : en-tête en petites capitales, filets fins, pas
    d'aplat (maquette Aurora). `total` : dernière ligne mise en valeur."""
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
          ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
          ("LINEBELOW", (0, 0), (-1, -1), 0.45, k.c["rule"])]
    if header:
        st += [("LINEBELOW", (0, 0), (-1, 0), 0.9, k.c["ink"]),
               ("BOTTOMPADDING", (0, 0), (-1, 0), 5)]
    if total:
        st += [("LINEABOVE", (0, -1), (-1, -1), 0.9, k.c["ink"]),
               ("BACKGROUND", (0, -1), (-1, -1), k.c["panel"])]
    if zebra:
        st.append(("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1), [k.c["surface"], None]))
    if k.layout["kpi"] == "cards":
        st += [("BACKGROUND", (0, 0), (-1, -1), k.c["surface"]),
               ("ROUNDEDCORNERS", [k.layout["radius"]] * 4)]
    t.setStyle(TableStyle(st))
    return t


def _chart(story, chart_images, key, w_cm, h_cm, caption, S):
    if key not in chart_images:
        return
    try:
        w = min(w_cm * 28.35, CW)
        im = Image(io.BytesIO(chart_images[key]), width=w, height=w * h_cm / w_cm)
        im.hAlign = "CENTER"
        story.append(im)
        if caption:
            story.append(Paragraph(caption, S["caption"]))
        story.append(Spacer(1, 8))
    except Exception as e:
        print(f"Chart '{key}' error: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# Contexte des pages composées (données réelles uniquement)
# ═══════════════════════════════════════════════════════════════════════════

def _env_metrics(request, TR, lang):
    env, lab = request.environmental, TR["ed_env_m"]
    out = []
    if env.co2_emissions_tonnes is not None:
        out.append((_num(env.co2_emissions_tonnes, lang), lab["co2"]))
    if env.renewable_energy_percent is not None:
        out.append((_pct(env.renewable_energy_percent, lang), lab["renewable"]))
    if env.waste_recycled_percent is not None:
        out.append((_pct(env.waste_recycled_percent, lang), lab["recycling"]))
    if env.energy_consumption_mwh is not None:
        out.append((_num(env.energy_consumption_mwh, lang), lab["energy"]))
    if env.water_consumption_m3 is not None:
        out.append((_num(env.water_consumption_m3, lang), lab["water"]))
    return out[:3]


def _soc_metrics(request, TR, lang):
    soc, lab = request.social, TR["ed_soc_m"]
    out = []
    if soc.female_employees_percent is not None:
        out.append((_pct(soc.female_employees_percent, lang), lab["women"]))
    if soc.training_hours_per_employee is not None:
        out.append((f"{_num(soc.training_hours_per_employee, lang)} h", lab["training"]))
    if soc.accident_frequency_rate is not None:
        out.append((_num(soc.accident_frequency_rate, lang, 1), lab["accident"]))
    if soc.employee_turnover_percent is not None:
        out.append((_pct(soc.employee_turnover_percent, lang), lab["turnover"]))
    if soc.total_employees is not None:
        out.append((_num(soc.total_employees, lang), lab["employees"]))
    return out[:3]


def _gov_line(request, TR, lang):
    gov, lab = request.governance, TR["ed_gov_m"]
    parts = []
    if gov.independent_board_percent is not None:
        parts.append(lab["independent"].format(v=_num(gov.independent_board_percent, lang)))
    if gov.female_board_percent is not None:
        parts.append(lab["women_board"].format(v=_num(gov.female_board_percent, lang)))
    if gov.sustainability_committee is not None:
        parts.append(lab["committee_yes" if gov.sustainability_committee else "committee_no"])
    if gov.esg_audit_conducted is not None:
        parts.append(lab["audit_yes" if gov.esg_audit_conducted else "audit_no"])
    return " · ".join(parts[:3])


def _facts(request, TR, lang):
    c, soc = request.company, request.social
    out = []
    if soc.total_employees:
        out.append((_num(soc.total_employees, lang), TR["ed_employees"]))
    if c.revenue_eur:
        out.append((_num(c.revenue_eur / 1e6, lang, 1 if c.revenue_eur < 1e7 else 0), TR["ed_revenue"]))
    out.append((str(c.reporting_year), TR["ed_year"]))
    out.append((str(max(c.target_year, c.reporting_year + 1)), TR["ed_target"]))
    return out[:4]


def _initiatives(request):
    raw = request.company.key_initiatives or ""
    return [s.strip() for s in re.split(r"[;\n]|,(?!\d)", raw) if s.strip()][:8]


def page_context(request, scores, TR, type_label):
    from content_generator import score_verdict, hero_stat, pillar_headline, _band
    lang = request.language
    band = _band(scores.total_esg_score) or "mid"
    prev = getattr(request, "previous_scores", None) or None
    delta = prev_vals = prev_year = None
    if prev and all(prev.get(x) is not None for x in ("env", "social", "gov", "total")):
        prev_year = prev.get("year")
        delta = {"env": scores.environmental_score - prev["env"],
                 "social": scores.social_score - prev["social"],
                 "gov": scores.governance_score - prev["gov"],
                 "total": scores.total_esg_score - prev["total"]}
        prev_vals = [prev["env"], prev["social"], prev["gov"]]
    return {
        "TR": TR, "lang": lang, "company": request.company, "name": request.company.name,
        "year": request.company.reporting_year, "type_label": type_label,
        "e": scores.environmental_score, "s": scores.social_score, "g": scores.governance_score,
        "t": scores.total_esg_score, "rating": scores.rating or "—",
        "delta": delta, "prev_vals": prev_vals, "prev_year": prev_year,
        "verdict": score_verdict(request, scores) or TR["cover_tag_" + band],
        "tagline": TR["cover_tag_" + band],
        "refs": TR["cover_refs_vsme"] if getattr(request, "reporting_framework", "csrd") == "vsme"
        else TR["cover_refs"],
        "env_m": _env_metrics(request, TR, lang), "soc_m": _soc_metrics(request, TR, lang),
        "gov_line": _gov_line(request, TR, lang), "facts": _facts(request, TR, lang),
        "initiatives": _initiatives(request), "hero": hero_stat(request, scores),
        "env_headline": pillar_headline(request, scores).get("env"),
        "footer_label": TR["rep_default"],
    }


# ═══════════════════════════════════════════════════════════════════════════
# Assemblage
# ═══════════════════════════════════════════════════════════════════════════

class _Story(list):
    """Histoire ReportLab qui gère la bascule pages composées / pages courantes."""

    def __init__(self, kit):
        super().__init__()
        self.kit, self.mode = kit, "full"

    def full(self, drawer, *args):
        if self.mode == "content":
            self += [NextPageTemplate("full"), PageBreak()]
        self.append(FullPage(self.kit, drawer, *args))
        self.mode = "full-used"

    def content(self):
        if self.mode != "content":
            self += [NextPageTemplate("content"), PageBreak()]
            self.mode = "content"


def _toc_parts(TR):
    """Entrées du sommaire, par acte : (numéro, acte, [(clé d'ancre, libellé)])."""
    return [
        ("01", TR["toc_part1"], [("s1", TR["pdf_s1"]), ("s2", TR["pdf_s2"]), ("s3", TR["pdf_s3"]),
                                 ("s4", TR["pdf_s4"]), ("s5", TR["pdf_s5"])]),
        ("02", TR["toc_part2"], [("s6", TR["pdf_s6"]), ("diag", TR["pdf_diag"])]),
        ("03", TR["toc_part3"], [("s7", TR["pdf_s7"]), ("roadmap", TR["roadmap_title"]),
                                 ("concl", TR["pdf_concl"])]),
    ]


def generate_pdf_report(request: ESGRequest, scores: ESGScores, content: dict,
                        chart_images: dict, logo_bytes: bytes = None) -> bytes:
    pages = {}
    _compose(request, scores, content, chart_images, logo_bytes, pages_in={}, anchors=pages)
    return _compose(request, scores, content, chart_images, logo_bytes, pages_in=pages, anchors={})


def _compose(request, scores, content, chart_images, logo_bytes, pages_in, anchors) -> bytes:
    k = Kit(request)
    if logo_bytes:
        k.logo = logo_bytes
    S = build_styles(k)
    TR = L(request.language)
    lang = request.language
    type_label = {"white_paper": TR["rep_white_paper"], "full_report": TR["rep_full_report"],
                  "executive_summary_pdf": TR["rep_executive_summary_pdf"]
                  }.get(request.report_type.value, TR["rep_default"])
    g = page_context(request, scores, TR, type_label)
    buf = io.BytesIO()

    def on_content(canvas, doc):
        p = Px(canvas, k)
        paint_paper(p, k)
        draw_header(p, k, TR["ed_report_year"].format(y=g["year"]))
        draw_footer(p, k, g["footer_label"], canvas.getPageNumber())

    doc = BaseDocTemplate(buf, pagesize=A4, title=clean(f"{type_label} — {request.company.name}"),
                          author=clean(request.company.name))
    full = Frame(0, 0, PAGE_W, PAGE_H, 0, 0, 0, 0, id="full")
    body = Frame(_M_LEFT * PX, (1123 - _M_BOTTOM) * PX, CW, (_M_BOTTOM - _M_TOP) * PX,
                 0, 0, 0, 0, id="body")
    doc.addPageTemplates([PageTemplate("full", [full]),
                          PageTemplate("content", [body], onPage=on_content)])

    story = _Story(k)
    story.full(PG.cover_page, g)
    story.full(PG.toc_page, g, _toc_parts(TR), pages_in)
    story.full(PG.company_page, g)
    if request.company.ceo_quote:
        story.full(PG.word_page, g)
    story.full(PG.glance_page, g)
    story.content()

    from content_generator import (pillar_insights, risks_opportunities, enriched_recommendations,
                                   benchmark_verdict, maturity_text, compliance_assessment,
                                   roadmap_12m, priority_reading)
    pi = pillar_insights(request, scores)
    notes = getattr(request, "consultant_notes", None) or {}

    _executive(story, request, scores, content, k, S, TR, anchors, notes,
               risks_opportunities(request, scores), enriched_recommendations(request, scores)[:3])
    _environment(story, request, scores, content, chart_images, k, S, TR, lang, anchors, notes, pi)
    story.full(PG.focus_page, g)
    story.content()
    _social(story, request, scores, content, k, S, TR, lang, anchors, notes, pi)
    _governance(story, request, scores, content, k, S, TR, lang, anchors, notes, pi)
    _analyses(story, content, chart_images, k, S, TR, anchors)

    story.full(PG.divider_page, g, "01", TR["div1_title"], TR["div1_sub"], "focus")
    story.content()
    _strategic(story, request, scores, chart_images, k, S, TR, anchors,
               benchmark_verdict(request, scores), maturity_text(request, scores),
               risks_opportunities(request, scores), compliance_assessment(request, scores))

    story.full(PG.divider_page, g, "02", TR["div2_title"], TR["div2_sub"], "action")
    story.content()
    if request.include_recommendations:
        _recommendations(story, request, scores, chart_images, k, S, TR, anchors,
                         enriched_recommendations(request, scores), priority_reading)
    _roadmap(story, request, scores, k, S, TR, anchors, roadmap_12m(request, scores))
    if request.report_type.value == "white_paper":
        _white_paper(story, request, scores, k, S, TR, anchors)
    _closing(story, request, scores, content, k, S, TR, anchors)
    story.full(PG.back_cover, g)

    doc.build(story)
    buf.seek(0)
    return buf.read()


# ═══════════════════════════════════════════════════════════════════════════
# Sections du flux courant
# ═══════════════════════════════════════════════════════════════════════════

def _executive(story, request, scores, content, k, S, TR, anchors, notes, ro, recs3):
    section_head(story, TR["pdf_s1"], "accent", k, S, anchors, "s1")
    exec_text = content.get("executive_summary",
                            f"{request.company.name} présente son rapport ESG pour l'exercice "
                            f"{request.company.reporting_year}.")
    story.append(Paragraph(esc(exec_text), S["body"]))
    story.append(Spacer(1, 8))

    def cell(head, items, col):
        flow = [Paragraph(esc(head).upper(), k.ps("dgh", 7.8, font="body_b", color=col,
                                                   charSpace=0.6, spaceAfter=5))]
        for it in items[:2]:
            flow.append(Paragraph(f'<font color="{hexc(col)}">—</font>&nbsp; {esc(it)}',
                                  k.ps("dgi", 8.6, color="ink", leading=12, spaceAfter=4)))
        return flow

    red = colors.HexColor(_STATUS_HEX["bad"])
    grid = Table([[cell(TR["digest_strengths"], scores.strengths, k.c["env"]),
                   cell(TR["digest_weak"], scores.weaknesses, red)],
                  [cell(TR["digest_risks"], [r["text"] for r in ro["risks"]], red),
                   cell(TR["digest_opps"], [o["text"] for o in ro["opportunities"]], k.c["env"])]],
                 colWidths=[CW / 2] * 2)
    grid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEABOVE", (0, 0), (-1, 0), 0.8, k.c["ink"]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, k.c["rule"]),
        ("LINEAFTER", (0, 0), (0, -1), 0.5, k.c["rule"]),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    story.append(grid)
    if recs3:
        acts = "   ".join(f"{i}. {r['title']}" for i, r in enumerate(recs3, 1))
        story.append(Spacer(1, 6))
        story.append(_box(Paragraph(f'<b>{esc(TR["digest_actions"]).upper()}</b> — {esc(acts)}',
                                    k.ps("dga", 8.4, color="ink", leading=12)), k, k.c["panel"], pad=9))
    if notes.get("global"):
        story.append(Spacer(1, 8))
        consultant_callout(story, notes["global"], k, TR)
    story.append(Spacer(1, 12))


def _status(v, good, warn, higher_better=True):
    if v is None:
        return None
    ok = (v >= good) if higher_better else (v <= good)
    mid = (v >= warn) if higher_better else (v <= warn)
    return "good" if ok else ("warn" if mid else "bad")


def _pillar_intro(story, title, key, score_label, score, insight, note, text, k, S, TR, anchors,
                  anchor):
    # 11 cm : titre, score, lecture et encart consultant restent ensemble
    section_head(story, title, key, k, S, anchors, anchor, keep_cm=11)
    story.append(Paragraph(f'{esc(score_label)} : <font name="{k.f["display"]}" size="15" '
                           f'color="{hexc(k.c[key])}">{score:.0f}</font>'
                           f'<font color="{hexc(k.c["muted"])}">/100</font>', S["h2"]))
    insight_callout(story, insight, key, k)
    if note:
        consultant_callout(story, note, k, TR)
    story.append(Paragraph(esc(text), S["body"]))


def _environment(story, request, scores, content, chart_images, k, S, TR, lang, anchors, notes, pi):
    _pillar_intro(story, TR["pdf_s2"], "env", TR["score_env_label"], scores.environmental_score,
                  pi["env"], notes.get("env"),
                  content.get("environmental", "L'analyse environnementale couvre les émissions, "
                              "l'énergie, l'eau, les déchets et la biodiversité."),
                  k, S, TR, anchors, "s2")
    env = request.environmental
    kpis = []
    if env.co2_emissions_tonnes is not None:
        ci = (env.co2_emissions_tonnes / request.company.revenue_eur * 1e6
              if request.company.revenue_eur else None)
        kpis.append((TR["kpit"]["co2"], _num(env.co2_emissions_tonnes, lang),
                     _status(ci, 30, 100, higher_better=False)))
    if env.renewable_energy_percent is not None:
        kpis.append((TR["kpit"]["renewable"], _pct(env.renewable_energy_percent, lang),
                     _status(env.renewable_energy_percent, 50, 30)))
    if env.energy_consumption_mwh is not None:
        kpis.append((TR["kpit"]["energy"], _num(env.energy_consumption_mwh, lang)))
    if env.water_consumption_m3 is not None:
        kpis.append((TR["kpit"]["water"], _num(env.water_consumption_m3, lang)))
    if env.waste_recycled_percent is not None:
        kpis.append((TR["kpit"]["recycling"], _pct(env.waste_recycled_percent, lang),
                     _status(env.waste_recycled_percent, 60, 40)))
    if kpis:
        story.append(Spacer(1, 6))
        story.append(kpi_block(kpis, k, lang))
    scopes = [("Scope 1", env.scope1_emissions), ("Scope 2", env.scope2_emissions),
              ("Scope 3", env.scope3_emissions)]
    known = [(n, v) for n, v in scopes if v is not None]
    if known:
        story.append(Spacer(1, 10))
        story.append(Paragraph(esc(TR["ed_ghg_table"]), S["h2"]))
        tot = sum(v for _, v in known)
        right = k.ps("r", 8.6, color="ink", alignment=2)
        rows = [[Paragraph("", S["th"]), Paragraph("t CO2e", k.ps("thr", 7.4, font="body_b",
                                                                  color="muted", alignment=2)),
                 Paragraph(esc(TR["ed_share"]).upper(), k.ps("ths", 7.4, font="body_b", color="muted",
                                                              alignment=2))]]
        for n, v in known:
            rows.append([Paragraph(n, S["small"]), Paragraph(_num(v, lang), right),
                         Paragraph(_pct(v / tot * 100, lang) if tot else "—", right)])
        if len(known) > 1:
            rows.append([Paragraph(f"<b>{esc(TR['ed_total'])}</b>", S["small"]),
                         Paragraph(f"<b>{_num(tot, lang)}</b>", right), Paragraph("100 %" if lang != "en" else "100%", right)])
        has_pie = "emissions_pie" in chart_images
        widths = [CW * 0.28, CW * 0.14, CW * 0.12] if has_pie else [CW * 0.5, CW * 0.25, CW * 0.25]
        tbl = data_table(rows, widths, k, total=len(known) > 1)
        if has_pie:
            try:
                pie = Image(io.BytesIO(chart_images["emissions_pie"]), width=CW * 0.40, height=CW * 0.35)
                wrap = Table([[tbl, pie]], colWidths=[CW * 0.56, CW * 0.44])
                wrap.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                          ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
                story.append(KeepTogether([wrap, Paragraph(TR["cap_pie"], S["caption"])]))
            except Exception as e:
                print(f"Pie error: {e}")
                story.append(tbl)
        else:
            story.append(tbl)
    story.append(Spacer(1, 12))


def _social(story, request, scores, content, k, S, TR, lang, anchors, notes, pi):
    _pillar_intro(story, TR["pdf_s3"], "social", TR["score_soc_label"], scores.social_score,
                  pi["social"], notes.get("social"),
                  content.get("social", "La performance sociale englobe les ressources humaines, "
                              "la diversité, la sécurité et la formation."),
                  k, S, TR, anchors, "s3")
    soc = request.social
    kpis = []
    if soc.total_employees is not None:
        kpis.append((TR["kpit"]["employees"], _num(soc.total_employees, lang)))
    if soc.female_employees_percent is not None:
        kpis.append((TR["kpit"]["women"], _pct(soc.female_employees_percent, lang),
                     _status(soc.female_employees_percent, 40, 35)))
    if soc.employee_turnover_percent is not None:
        kpis.append((TR["kpit"]["turnover"], _pct(soc.employee_turnover_percent, lang),
                     _status(soc.employee_turnover_percent, 10, 20, higher_better=False)))
    if soc.training_hours_per_employee is not None:
        kpis.append((TR["kpit"]["training"], _num(soc.training_hours_per_employee, lang),
                     _status(soc.training_hours_per_employee, 20, 10)))
    if soc.accident_frequency_rate is not None:
        kpis.append((TR["kpit"]["accident"], _num(soc.accident_frequency_rate, lang, 2),
                     _status(soc.accident_frequency_rate, 2, 5, higher_better=False)))
    if soc.customer_satisfaction_score is not None:
        kpis.append((TR["kpit"]["satisfaction"], _num(soc.customer_satisfaction_score, lang, 1),
                     _status(soc.customer_satisfaction_score, 8, 6)))
    if kpis:
        story.append(Spacer(1, 6))
        story.append(kpi_block(kpis, k, lang))
    story.append(Spacer(1, 12))


def _governance(story, request, scores, content, k, S, TR, lang, anchors, notes, pi):
    _pillar_intro(story, TR["pdf_s4"], "gov", TR["score_gov_label"], scores.governance_score,
                  pi["gov"], notes.get("gov"),
                  content.get("governance", "La gouvernance évalue la direction, l'indépendance du "
                              "conseil, l'éthique et le contrôle interne."),
                  k, S, TR, anchors, "s4")
    gov = request.governance
    yn = TR["kpit"]
    kpis = []
    if gov.board_members is not None:
        kpis.append((yn["board"], str(gov.board_members)))
    if gov.female_board_percent is not None:
        kpis.append((yn["women_board"], _pct(gov.female_board_percent, lang),
                     _status(gov.female_board_percent, 40, 30)))
    if gov.independent_board_percent is not None:
        kpis.append((yn["independent"], _pct(gov.independent_board_percent, lang),
                     _status(gov.independent_board_percent, 50, 33)))
    if gov.csr_budget_eur is not None:
        kpis.append((yn["csr"], _num(gov.csr_budget_eur, lang)))
    for flag, key in ((gov.esg_audit_conducted, "audit"), (gov.sustainability_committee, "committee")):
        kpis.append((yn[key], yn["yes"] if flag else (yn["no"] if flag is not None else yn["na"]),
                     "good" if flag else ("bad" if flag is not None else None)))
    story.append(Spacer(1, 6))
    story.append(kpi_block(kpis, k, lang))
    story.append(Spacer(1, 12))


def _analyses(story, content, chart_images, k, S, TR, anchors):
    story.append(PageBreak())
    section_head(story, TR["pdf_s5"], "accent", k, S, anchors, "s5")
    story.append(Paragraph(TR["sub_materiality"], S["h2"]))
    story.append(Paragraph(esc(content.get("materiality", "")), S["body"]))
    _chart(story, chart_images, "materiality", 16.5, 9.5, TR["cap_materiality"], S)
    story.append(Paragraph(TR["sub_targets"], S["h2"]))
    story.append(Paragraph(esc(content.get("targets", "")), S["body"]))
    if content.get("taxonomy"):
        story.append(Paragraph(TR["sub_taxonomy"], S["h2"]))
        story.append(Paragraph(esc(content["taxonomy"]), S["body"]))
        _chart(story, chart_images, "taxonomy", 14, 6.3, TR["cap_taxonomy"], S)
    story.append(Paragraph(TR["sub_climate"], S["h2"]))
    story.append(Paragraph(esc(content.get("climate_risk", "")), S["body"]))


def _strategic(story, request, scores, chart_images, k, S, TR, anchors, bv, mt, ro, gaps):
    import gap_status as GS
    section_head(story, TR["pdf_s6"], "accent", k, S, anchors, "s6")
    story.append(Paragraph(TR["strengths_ident"], S["h2"]))
    for s in scores.strengths:
        story.append(Paragraph(f'<font color="{hexc(k.c["env"])}">—</font>&nbsp; {esc(s)}',
                               S["bullet"]))
    story.append(Paragraph(TR["weaknesses_axes"], S["h2"]))
    for w in scores.weaknesses:
        story.append(Paragraph(f'<font color="{_STATUS_HEX["bad"]}">—</font>&nbsp; {esc(w)}',
                               S["bullet"]))

    story.append(PageBreak())
    section_head(story, TR["pdf_diag"], "accent", k, S, anchors, "diag")
    story.append(Paragraph(esc(bv["title"]), S["h2"]))
    story.append(Paragraph(TR["pdf_bench_sub"], k.ps("bs", 8.4, font="body_i", color="muted",
                                                      spaceAfter=6)))
    # Positionnement INTERNE : les trois piliers comparés entre eux. Aucune
    # donnée externe (la référence sectorielle d'origine était inventée).
    center = k.ps("c", 8.8, color="ink", alignment=TA_CENTER)
    lab = {"env": TR["pillar_env"], "social": TR["pillar_soc"], "gov": TR["pillar_gov"]}
    rows = [[Paragraph(esc(TR[x]).upper(), S["th"]) for x in
             ("bench_metric_col", "bench_you", "bench_delta_col", "bench_reading_col")]]
    for row in bv["rows"]:
        d = row["delta"]
        rcol = (_STATUS_HEX["good"] if row["role"] == "lead"
                else _STATUS_HEX["bad"] if row["role"] == "lag" else hexc(k.c["ink"]))
        rows.append([Paragraph(esc(lab[row["key"]]), S["small_b"]),
                     Paragraph(f"{row['score']:.0f}", center),
                     Paragraph("—" if d == 0 else f"{d:.0f} pts", center),
                     Paragraph(f'<font color="{rcol}"><b>{esc(row["reading"])}</b></font>', center)])
    rows.append([Paragraph(esc(TR.get("score_global_short", "Global")), S["small_b"]),
                 Paragraph(f"<b>{scores.total_esg_score:.0f}</b>", center), Paragraph("", center),
                 Paragraph(f"<b>{esc(scores.rating)}</b>", center)])
    story.append(data_table(rows, [CW * 0.36, CW * 0.17, CW * 0.19, CW * 0.28], k, total=True))
    story.append(Spacer(1, 8))
    insight_callout(story, bv["insight"], "accent", k)

    if "trend" in chart_images:
        story.append(Paragraph(TR["trend_title"], S["h2"]))
        _chart(story, chart_images, "trend", 16.5, 8.4, TR["cap_trend"], S)

    mat_lbl = TR.get("mat_" + mt.get("key", "structured"), "")
    story.append(Paragraph(f'{esc(TR["pdf_maturity_sub"])} : {esc(mat_lbl)} '
                           f'<font color="{hexc(k.c["muted"])}">({mt["stage"]}/5)</font>', S["h2"]))
    story.append(Paragraph(esc(mt["next_hint"]), S["body"]))

    # Couverture des exigences (libellés et couleurs : source unique gap_status)
    story.append(Paragraph(TR["gap_title"], S["h2"]))
    rows = [[Paragraph(esc(TR[x]).upper(), S["th"]) for x in ("gap_req", "gap_ref", "gap_status", "gap_note")]]
    for gp in gaps:
        rows.append([Paragraph(esc(gp["req"]), S["small_b"]), Paragraph(esc(gp["ref"]), S["small"]),
                     Paragraph(f'<font color="{GS.couleur(gp["status"], gp["nature"])}">'
                               f'<b>• {esc(GS.libelle(TR, gp["status"], gp["nature"]))}</b></font>',
                               S["small"]),
                     Paragraph(esc(gp["note"]), S["small"])])
    story.append(data_table(rows, [CW * 0.32, CW * 0.19, CW * 0.17, CW * 0.32], k))
    story.append(Spacer(1, 10))

    story.append(Paragraph(TR["risks_head"], S["h2"]))
    c2 = k.ps("rc", 8.4, color="ink", alignment=TA_CENTER)
    rows = [[Paragraph(esc(TR[x]).upper(), S["th"]) for x in ("risk_desc", "risk_impact", "risk_lik", "risk_prio")]]
    for it in ro["risks"]:
        pr = it.get("priority", "P2")
        rows.append([Paragraph(f'<b>{esc(it["tag"])}</b> — {esc(it["text"])}', S["small"]),
                     Paragraph(esc(it.get("impact", "—")), c2), Paragraph(esc(it.get("likelihood", "—")), c2),
                     Paragraph(f'<font color="{_PRIO_HEX[pr]}"><b>{pr}</b></font>', c2)])
    story.append(data_table(rows, [CW * 0.6, CW * 0.14, CW * 0.14, CW * 0.12], k))
    story.append(Spacer(1, 10))

    opp = [Paragraph(esc(TR["opps_head"]).upper(), k.ps("oh", 8, font="body_b", color="env",
                                                        charSpace=0.6, spaceAfter=6))]
    for it in ro["opportunities"]:
        opp.append(Paragraph(f'<font color="{hexc(k.c["env"])}"><b>{esc(it["tag"])}</b></font> — '
                             f'{esc(it["text"])}', k.ps("oi", 9, color="ink", leading=13, spaceAfter=5)))
    story.append(_box(opp, k, k.c["env_soft"], left=k.c["env"]))


def _recommendations(story, request, scores, chart_images, k, S, TR, anchors, recs, priority_reading):
    section_head(story, TR["pdf_s7"], "accent", k, S, anchors, "s7")
    done = getattr(request, "completed_actions", None) or []
    if done:
        flow = [Paragraph(esc(TR["done_head"]).upper(), k.ps("dh", 8, font="body_b",
                                                             color=colors.HexColor(_STATUS_HEX["good"]),
                                                             charSpace=0.6, spaceAfter=5))]
        for item in done:
            yr = f" ({item['year']})" if item.get("year") else ""
            flow.append(Paragraph(f'<font color="{_STATUS_HEX["good"]}">—</font>&nbsp; '
                                  f'{esc(item["title"])}{esc(yr)}', k.ps("di", 9, color="ink", leading=12)))
        story.append(_box(flow, k, k.c["env_soft"], left=colors.HexColor(_STATUS_HEX["good"])))
        story.append(Spacer(1, 8))
    if "priority" in chart_images:
        _chart(story, chart_images, "priority", 16.5, 9.5, TR["cap_prio"], S)
        insight_callout(story, priority_reading(request, scores), "accent", k)
    pcol = {"env": k.c["env"], "social": k.c["social"], "gov": k.c["gov"]}
    due = "Due" if request.language == "en" else "Échéance"
    rows = [["", Paragraph("ACTION", S["th"]),
             Paragraph(esc(f'{TR["objective_col"]} · {TR["owner_col"]} · {due}').upper(), S["th"])]]
    for i, rec in enumerate(recs, 1):
        c = pcol.get(rec["pillar"], k.c["accent"])
        rows.append([
            Paragraph(f"{i:02d}", k.ps("rn", 15, font="display", color=c, leading=18)),
            [Paragraph(esc(rec["title"]), k.ps("rt", 9.8, font="body_b", color="ink", leading=12.5,
                                               spaceAfter=2)),
             Paragraph(esc(rec["detail"]), k.ps("rd", 8.4, color="muted", leading=11))],
            [Paragraph(esc(rec.get("objective", "")), k.ps("ro", 8.4, font="body_b", color=c,
                                                          leading=11, spaceAfter=2)),
             Paragraph(f'{esc(rec.get("owner", ""))} · {esc(rec["horizon"])}',
                       k.ps("rw", 8, color="muted", leading=10.5))]])
    story.append(data_table(rows, [CW * 0.08, CW * 0.58, CW * 0.34], k))


def _roadmap(story, request, scores, k, S, TR, anchors, rm):
    if not any(ph["actions"] for ph in rm):
        return
    story.append(Spacer(1, 14))
    section_head(story, TR["roadmap_title"], "accent", k, S, anchors, "roadmap")
    pcol = {"env": k.c["env"], "social": k.c["social"], "gov": k.c["gov"]}
    heads, bodies = [], []
    for ph in rm:
        heads.append([Paragraph(esc(ph["label"]), k.ps("ph", 13, font="display", color="ink", leading=16)),
                      Paragraph(esc(ph["sub"]), k.ps("ps", 8, color="muted"))])
        acts = []
        for a in ph["actions"][:4]:
            qw = (f' <font color="{hexc(k.c["accent"])}" size="6.5"><b>{esc(TR["quick_win"])}</b></font>'
                  if a["quick_win"] else "")
            acts.append(Paragraph(f'<font color="{hexc(pcol.get(a["pillar"], k.c["accent"]))}">•</font>'
                                  f'&nbsp; {esc(a["title"])}{qw}',
                                  k.ps("ra", 8.6, color="ink", leading=11.5, spaceAfter=6)))
        bodies.append(acts)
    t = Table([heads, bodies], colWidths=[CW / 3] * 3)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEABOVE", (0, 0), (-1, 0), 1.6, k.c["accent"]),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, k.c["rule"]),
        ("LINEAFTER", (0, 0), (1, -1), 0.5, k.c["rule"]),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9)]))
    story.append(t)
    story.append(Spacer(1, 12))
    band = Table([[Paragraph(esc(TR["div2_sub"]), k.ps("bd", 13, font="display_i", color="on_primary",
                                                        leading=18))]], colWidths=[CW])
    band.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), k.c["primary"]),
                              ("LEFTPADDING", (0, 0), (-1, -1), 20), ("TOPPADDING", (0, 0), (-1, -1), 18),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 20)]))
    story.append(band)


def _white_paper(story, request, scores, k, S, TR, anchors):
    story.append(Spacer(1, 14))
    section_head(story, TR["pdf_s9_wp"], "accent", k, S, anchors)
    story.append(Paragraph(TR["wp_intro"], S["body"]))
    story.append(Paragraph(TR["wp_horizon"].format(
        y=max(request.company.target_year, request.company.reporting_year + 1)), S["h2"]))
    e, s, g = scores.environmental_score, scores.social_score, scores.governance_score
    if request.language == "en":
        objs = [("Environmental", f"Target E score: {min(100, e + 15):.0f}/100 | +50% renewable | Scope 3 measured"),
                ("Social", f"Target S score: {min(100, s + 10):.0f}/100 | 40% gender balance | 30h training/year"),
                ("Governance", f"Target G score: {min(100, g + 5):.0f}/100 | Annual audit | Sustainability committee")]
    else:
        objs = [("Environnement", f"Score E cible : {min(100, e + 15):.0f}/100 | +50% renouvelable | Scope 3 mesuré"),
                ("Social", f"Score S cible : {min(100, s + 10):.0f}/100 | Parité 40% | 30h formation/an"),
                ("Gouvernance", f"Score G cible : {min(100, g + 5):.0f}/100 | Audit annuel | Comité durable")]
    for label, obj in objs:
        story.append(Paragraph(f"<b>{esc(label)} :</b> {esc(obj)}", S["bullet"]))


def _closing(story, request, scores, content, k, S, TR, anchors):
    from glossary import glossary_entries
    story.append(PageBreak())
    title = TR["pdf_concl_wp"] if request.report_type.value == "white_paper" else TR["pdf_concl"]
    section_head(story, title, "accent", k, S, anchors, "concl")
    story.append(Paragraph(esc(content.get("conclusion",
                                           f"{request.company.name} — score ESG "
                                           f"{scores.total_esg_score}/100 (note {scores.rating}).")),
                           S["body"]))
    if content.get("methodology"):
        story.append(Spacer(1, 10))
        story.append(Paragraph(TR["pdf_methodo"], S["h2"]))
        story.append(_box(Paragraph(esc(content["methodology"]), k.ps("mn", 8.6, color="ink", leading=13)),
                          k, k.c["panel"], left=k.c["accent"]))
    # Les emplacements éditoriaux (focus, chapitres, 4e de couverture) viennent
    # toujours de la banque : la mention figure donc dans tout rapport.
    story.append(Spacer(1, 6))
    story.append(Paragraph(esc(TR["ed_photo_note"]), k.ps("pn", 7.6, font="body_i", color="muted",
                                                          leading=10.5)))
    gloss = glossary_entries(request, scores)
    if gloss:
        story.append(Spacer(1, 10))
        story.append(Paragraph(TR["pdf_glossary"], S["h2"]))
        rows = [[Paragraph(esc(e["term"]), S["small_b"]), Paragraph(esc(e["definition"]), S["small"])]
                for e in gloss]
        story.append(data_table(rows, [CW * 0.22, CW * 0.78], k, header=False))
    story.append(Spacer(1, 18))
    story.append(Paragraph(esc(f"© {request.company.reporting_year} {request.company.name} — " + TR["gen_auto"]),
                           S["footer"]))
