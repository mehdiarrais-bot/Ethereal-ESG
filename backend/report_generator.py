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
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (Flowable, BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, Image, PageBreak, KeepTogether,
                                NextPageTemplate, CondPageBreak)

from esg_calculator import NON_NOTE, score_label
from models import ESGRequest, ESGScores
from i18n import L
from pdf_kit import (Kit, Px, FullPage, Anchor, PX, PAGE_W, PAGE_H, clean, esc, hexc,
                     draw_header, draw_footer, paint_paper)
import pdf_pages as PG
import analysis as AN
import narrative as NR
from bands import classer

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
        # allowWidows/allowOrphans=0 : jamais une ligne seule en haut ou en
        # bas de page (règle typographique d'un rapport publié)
        "body": k.ps("body", 9.6, color="ink", leading=15, spaceAfter=7,
                     allowWidows=0, allowOrphans=0),
        "lead": k.ps("lead", 11.2, color="ink", leading=17.5, spaceAfter=9,
                     allowWidows=0, allowOrphans=0),
        "bullet": k.ps("bullet", 9.6, color="ink", leading=14, leftIndent=12, spaceAfter=3,
                       allowWidows=0, allowOrphans=0),
        "caption": k.ps("caption", 8, font="body_i", color="muted", alignment=TA_CENTER),
        # Intertitre de l'analyse approfondie (analysis.py), lié au paragraphe suivant
        "h3": k.ps("h3", 10.2, font="body_b", color="ink", leading=14, spaceBefore=7,
                   spaceAfter=3, keepWithNext=1),
        "small": k.ps("small", 8.3, color="ink", leading=11.5),
        "small_b": k.ps("small_b", 8.3, font="body_b", color="ink", leading=11.5),
        "th": k.ps("th", 7.4, font="body_b", color="muted", leading=10, charSpace=0.5),
        "footer": k.ps("footer", 8, font="body_i", color="muted", alignment=TA_CENTER),
    }


def section_head(story, title, color_key, k: Kit, S, anchors, key=None, keep_cm=5):
    """Titre de section. « 2. Pilier… » est posé sur deux lignes (numéro en
    accent, titre dessous) ; l'extraction texte rend « 2. Pilier… », ce que
    vérifie le test de numérotation du sommaire."""
    story.append(CondPageBreak(keep_cm * 28.35))
    # Repère APRÈS le saut conditionnel : posé avant, il notait la page
    # précédente quand le titre partait en haut de la page suivante.
    if key:
        story.append(Anchor(key, anchors))
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
    story.append(_sp(k, 10))


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
    story.append(_sp(k, 8))


def consultant_callout(story, text, k: Kit, TR):
    """Encart « L'analyse du consultant », distinct de la lecture automatique."""
    flow = [Paragraph(esc(TR["consultant_note"]), k.ps("cnh", 7.6, font="body_b",
                                                        color="accent_on_primary", charSpace=0.8,
                                                        spaceAfter=4)),
            Paragraph(esc(text), k.ps("cnb", 10, font="display_i", color="on_primary", leading=15))]
    story.append(_box(flow, k, k.c["primary"]))
    story.append(_sp(k, 8))


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

    cells = [[Paragraph(esc(i[0]).upper(), lab_st), _sp(k, 4), Paragraph(val(i), val_st)]
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


class GuardedTable(Table):
    """Table qui refuse une coupure laissant moins de MIN_ROWS lignes de
    données d'un côté ou de l'autre du saut de page : le tableau passe alors
    entier à la page suivante (ou se coupe plus loin). ReportLab recrée les
    fragments via self.__class__, qui restent donc protégés."""
    MIN_ROWS = 3

    def split(self, aw, ah):
        parts = super().split(aw, ah)
        if len(parts) < 2:
            return parts
        head = self.repeatRows if isinstance(self.repeatRows, int) else len(self.repeatRows)
        # split() d'une Table ne rend que des Table : _cellvalues existe.
        first = len(getattr(parts[0], "_cellvalues")) - head
        rest = len(getattr(parts[1], "_cellvalues")) - head
        if first < self.MIN_ROWS or rest < self.MIN_ROWS:
            return []
        return parts


def data_table(rows, widths, k: Kit, header=True, total=False, zebra=False):
    """Tableau éditorial : en-tête en petites capitales, filets fins, pas
    d'aplat (maquette Aurora). `total` : dernière ligne mise en valeur."""
    t = GuardedTable(rows, colWidths=widths, repeatRows=1 if header else 0)
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


def _sp(k: Kit, pt: float) -> Spacer:
    """Espace vertical proportionnel à la densité de la séquence."""
    return Spacer(1, k.space(pt))


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


def page_context(request, scores, TR, type_label):
    from content_generator import score_verdict, hero_stat, pillar_headline, _band
    lang = request.language
    band = _band(scores.total_esg_score) or "none"  # sans score global : aucun jugement
    prev = getattr(request, "previous_scores", None) or None
    delta = prev_vals = prev_year = None
    if prev and all(prev.get(x) is not None for x in ("env", "social", "gov", "total")):
        prev_year = prev.get("year")
        from content_generator import _ecart
        delta = {"env": _ecart(scores.environmental_score, prev["env"]),
                 "social": _ecart(scores.social_score, prev["social"]),
                 "gov": _ecart(scores.governance_score, prev["gov"]),
                 "total": _ecart(scores.total_esg_score, prev["total"])}
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
        "initiatives": NR.initiatives(request), "hero": hero_stat(request, scores),
        "env_headline": pillar_headline(request, scores).get("env"),
        "ghg_text": NR.ghg_paragraph(request),
        "footer_label": TR["rep_default"],
    }


# ═══════════════════════════════════════════════════════════════════════════
# Assemblage
# ═══════════════════════════════════════════════════════════════════════════

class _RunMarker(Flowable):
    """Repère invisible : les pages suivantes appartiennent à la séquence n."""

    def __init__(self, run: int, state: dict):
        super().__init__()
        self.run, self.state = run, state

    def wrap(self, aW, aH):
        return 0, 0

    def draw(self):
        self.state["run"] = self.run


class _Story(list):
    """Histoire ReportLab qui gère la bascule pages composées / pages courantes.

    Une « séquence » (run) est une suite de pages courantes entre deux pages
    composées. Chaque séquence a sa densité (Kit.density), réglée par
    compose_report pour que sa dernière page ne soit pas presque vide."""

    def __init__(self, kit, densities: dict, state: dict):
        super().__init__()
        self.kit, self.mode, self.run = kit, "full", -1
        self.densities, self.state = densities, state

    def full(self, drawer, *args):
        if self.mode == "content":
            self += [NextPageTemplate("full"), PageBreak()]
        self.append(FullPage(self.kit, drawer, *args))
        self.mode = "full-used"

    def content(self):
        if self.mode != "content":
            self.run += 1
            self.kit.density = self.densities.get(self.run, 1.0)
            self += [NextPageTemplate("content"), PageBreak(), _RunMarker(self.run, self.state)]
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
                        chart_images: dict, logo_bytes: bytes | None = None) -> bytes:
    return compose_report(request, scores, content, chart_images, logo_bytes)[0]


# Une séquence qui finit sur moins de SPARSE_FILL de page est jugée « en
# débord » ; on essaie ces densités, dans l'ordre, jusqu'à la résorber
# (resserrer d'abord, puis desserrer pour remplir la dernière page).
SPARSE_FILL = 0.35
_DENSITY_STEPS = (0.85, 0.72, 0.6, 1.1, 1.2, 1.32, 1.45)


def _sparse_runs(layout) -> set:
    """Séquences dont la dernière page courante est presque vide."""
    last = {}
    for page, run, fill in layout["pages"]:
        last.setdefault(run, []).append((page, fill))
    return {run for run, pages in last.items() if len(pages) > 1 and pages[-1][1] < SPARSE_FILL}


def compose_report(request, scores, content, chart_images, logo_bytes=None):
    """(pdf, mise en page).

    1. Composition d'essai : relève la page de chaque section (sommaire) et
       le remplissage de chaque page courante.
    2. Pour toute séquence finissant sur une page presque vide (le « débord
       de trois lignes »), nouvelles compositions à densité ajustée.
    3. Composition finale avec les numéros de page définitifs.
    `mise en page` = {"pages": [(page, séquence, remplissage)], "content_pages": [...],
    "densities": {...}} — lue par les tests de pagination."""
    import typo
    with typo.language(request.language):
        return _compose_report(request, scores, content, chart_images, logo_bytes)


def _compose_report(request, scores, content, chart_images, logo_bytes):
    args = (request, scores, content, chart_images, logo_bytes)
    opts = {"densities": {}, "inline_focus": False}
    anchors, layout = _trial(*args, opts, {})
    anchors, layout = _fit_densities(args, opts, anchors, layout)
    if _FOCUS_RUN in _sparse_runs(layout):
        # Dernier recours pour la séquence Environnement : le focus quitte sa
        # page propre et vient remplir la page du débord (même contenu).
        opts = {"densities": {}, "inline_focus": True}
        anchors, layout = _trial(*args, opts, anchors)
        anchors, layout = _fit_densities(args, opts, anchors, layout)
    final_anchors = {}
    layout = _new_layout(opts)
    pdf = _compose(*args, pages_in=anchors, anchors=final_anchors, layout=layout, opts=opts)
    if final_anchors != anchors:  # la pagination a bougé : dernière passe
        layout = _new_layout(opts)
        pdf = _compose(*args, pages_in=final_anchors, anchors={}, layout=layout, opts=opts)
    return pdf, layout


# Séquence suivie de la page Focus (synthèse + pilier environnemental)
_FOCUS_RUN = 1


def _new_layout(opts):
    return {"pages": [], "content_pages": [], "densities": opts["densities"],
            "inline_focus": opts["inline_focus"]}


def _fit_densities(args: tuple[Any, Any, Any, Any, Any], opts, anchors, layout):
    """Essaie les densités de _DENSITY_STEPS sur les séquences en débord ;
    garde, pour chaque séquence, la première qui résorbe son débord."""
    for step in _DENSITY_STEPS:
        sparse = _sparse_runs(layout)
        if not sparse:
            break
        trial = dict(opts, densities={**opts["densities"], **{r: step for r in sparse}})
        _, t_layout = _trial(*args, trial, anchors)
        fixed = sparse - _sparse_runs(t_layout)
        if fixed:
            opts["densities"].update({r: step for r in fixed})
            anchors, layout = _trial(*args, opts, anchors)
    return anchors, layout


def _trial(request, scores, content, chart_images, logo_bytes, opts, pages_in):
    anchors, layout = {}, _new_layout(opts)
    _compose(request, scores, content, chart_images, logo_bytes, pages_in=pages_in,
             anchors=anchors, layout=layout, opts=opts)
    return anchors, layout


def _compose(request, scores, content, chart_images, logo_bytes, pages_in, anchors, layout,
             opts) -> bytes:
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
        layout["content_pages"].append(canvas.getPageNumber())
        p = Px(canvas, k)
        paint_paper(p, k)
        draw_header(p, k, TR["ed_report_year"].format(y=g["year"]))
        draw_footer(p, k, g["footer_label"], canvas.getPageNumber())

    state = {"run": 0}

    def on_content_end(canvas, doc):
        f = doc.frame
        fill = (f._y2 - f._y) / (f._y2 - f._y1)
        layout["pages"].append((canvas.getPageNumber(), state["run"], round(fill, 3)))

    doc = BaseDocTemplate(buf, pagesize=A4, title=clean(f"{type_label} — {request.company.name}"),
                          author=clean(request.company.name))
    full = Frame(0, 0, PAGE_W, PAGE_H, 0, 0, 0, 0, id="full")
    body = Frame(_M_LEFT * PX, (1123 - _M_BOTTOM) * PX, CW, (_M_BOTTOM - _M_TOP) * PX,
                 0, 0, 0, 0, id="body")
    doc.addPageTemplates([PageTemplate("full", [full]),
                          PageTemplate("content", [body], onPage=on_content,
                                       onPageEnd=on_content_end)])

    story = _Story(k, opts["densities"], state)
    story.full(PG.cover_page, g)
    story.full(PG.toc_page, g, _toc_parts(TR), pages_in)
    story.content()
    S = build_styles(k)
    _company(story, request, k, S, TR, g)
    story.full(PG.glance_page, g)
    story.content()
    S = build_styles(k)

    from content_generator import (pillar_insights, risks_opportunities, enriched_recommendations,
                                   benchmark_verdict, maturity_text, compliance_assessment,
                                   roadmap_12m, priority_reading)
    pi = pillar_insights(request, scores)
    notes = getattr(request, "consultant_notes", None) or {}
    ro = risks_opportunities(request, scores)
    gaps = compliance_assessment(request, scores)
    recs = enriched_recommendations(request, scores) if request.include_recommendations else []
    rm = roadmap_12m(request, scores)

    _executive(story, request, scores, content, k, S, TR, anchors, notes, ro, recs[:3])
    _overview(story, request, scores, chart_images, k, S)
    _environment(story, request, scores, content, chart_images, k, S, TR, lang, anchors, notes, pi,
                 recs)
    if opts["inline_focus"]:
        _focus_inline(story, k, S, g)
    else:
        story.full(PG.focus_page, g)
        story.content()
        S = build_styles(k)
    _social(story, request, scores, content, chart_images, k, S, TR, lang, anchors, notes, pi,
            recs)
    _governance(story, request, scores, content, chart_images, k, S, TR, lang, anchors, notes, pi,
                recs)
    _analyses(story, content, chart_images, k, S, TR, anchors)

    story.full(PG.divider_page, g, "01", TR["div1_title"], TR["div1_sub"],
               NR.act1_intro(request, scores, gaps, ro["risks"]),
               NR.act1_figures(request, scores, gaps, ro["risks"]))
    story.content()
    S = build_styles(k)
    _strategic(story, request, scores, chart_images, k, S, TR, anchors,
               benchmark_verdict(request, scores), maturity_text(request, scores),
               ro, gaps, g["refs"])

    story.full(PG.divider_page, g, "02", TR["div2_title"], TR["div2_sub"],
               NR.act2_intro(request, recs, rm), NR.act2_figures(request, recs, rm))
    story.content()
    S = build_styles(k)
    if request.include_recommendations:
        _recommendations(story, request, scores, chart_images, k, S, TR, anchors,
                         recs, priority_reading)
    _roadmap(story, request, scores, k, S, TR, anchors, rm)
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

def _focus_inline(story, k, S, g):
    """Le focus environnement dans le flux : photo nature et chiffre-clé côte
    à côte (même contenu que la page Focus, sans la page dédiée)."""
    from pdf_kit import crop_jpeg
    hs, TR = g["hero"], g["TR"]
    w_img, h = CW * 0.42, CW * 0.52
    photo = k.photo("environment")
    img = Image(io.BytesIO(crop_jpeg(photo, round(w_img / h, 3))), width=w_img, height=h) if photo else ""
    text = [Paragraph(esc(TR["ed_focus"]).upper(), k.ps("fk", 7.8, color="muted", charSpace=0.9,
                                                         spaceAfter=8)),
            Paragraph(esc(hs["statement"]), k.ps("fs", 17, font="display", color="ink", leading=22,
                                                 spaceAfter=14)),
            Paragraph(esc(f"{hs['value']}{hs['unit']}".replace(" ", "")),
                      k.ps("fv", 44, font="display", color="accent", leading=48)),
            Paragraph(esc(hs["label"]), k.ps("fl", 10, color="muted", leading=14, spaceAfter=12))]
    if g.get("env_headline"):
        text.append(Paragraph(esc(g["env_headline"]), S["body"]))
    t = Table([[img, text]], colWidths=[w_img, CW - w_img])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("LEFTPADDING", (0, 0), (0, 0), 0), ("LEFTPADDING", (1, 0), (1, 0), 24),
                           ("LINEABOVE", (0, 0), (-1, 0), 0.8, k.c["ink"]),
                           ("TOPPADDING", (0, 0), (-1, -1), 14)]))
    story.append(_sp(k, 10))
    story.append(KeepTogether(t))


def _company(story, request, k, S, TR, g):
    """L'entreprise en bref : présentation, périmètre et complétude, chiffres
    saisis, photo fournie par l'entreprise, initiatives, mot de la direction."""
    c = request.company
    story.append(Paragraph(esc(TR["ed_company"]), k.ps("ct", 30, font=k.title_font, color="ink",
                                                        leading=35, spaceAfter=14)))
    paras = NR.company_paragraphs(request, g["refs"])
    story.append(Paragraph(esc(paras[0]), S["lead"]))
    facts = g["facts"]
    if facts:
        val = k.ps("fv", 24, font="display", color="ink", leading=28)
        lab = k.ps("fl", 7.8, color="muted", leading=10, charSpace=0.3)
        cells = [[Paragraph(esc(v), val), _sp(k, 3), Paragraph(esc(l).upper(), lab)] for v, l in facts]
        t = Table([cells], colWidths=[CW / len(cells)] * len(cells))
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("LINEABOVE", (0, 0), (-1, 0), 0.8, k.c["ink"]),
                               ("LINEBELOW", (0, 0), (-1, 0), 0.5, k.c["rule"]),
                               ("LINEAFTER", (0, 0), (-2, -1), 0.5, k.c["rule"]),
                               ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                               ("LEFTPADDING", (0, 0), (-1, -1), 12)]))
        story.append(_sp(k, 6))
        story.append(t)
        story.append(_sp(k, 14))
    for para in paras[1:]:
        story.append(Paragraph(esc(para), S["body"]))
    photo = k.photo("company") if k.has_client_photo("company") else None
    if photo:
        from pdf_kit import crop_jpeg
        story.append(_sp(k, 8))
        story.append(Image(io.BytesIO(crop_jpeg(photo, round(16 / 7, 3))), width=CW, height=CW * 7 / 16))
    if g["initiatives"]:
        block: list[Flowable] = [Paragraph(esc(TR["ed_initiatives"]), S["h2"])]
        block += [Paragraph(f'<font color="{hexc(k.c["accent"])}">•</font>&nbsp; {esc(it)}', S["bullet"])
                  for it in g["initiatives"]]
        story.append(KeepTogether(block))
    if c.ceo_quote:
        q = c.ceo_quote.strip().strip('"\u201c\u201d\u00ab\u00bb ')
        q = f"\u00ab {q} \u00bb" if request.language != "en" else f"\u201c{q}\u201d"
        flow = [Paragraph(esc(TR["ed_word"]).upper(), k.ps("wk", 7.8, font="body_b",
                                                          color="accent_on_primary", charSpace=0.8,
                                                          spaceAfter=8)),
                Paragraph(esc(q), k.ps("wq", 15, font="display_i", color="on_primary", leading=22))]
        if c.presenter_name:
            attrib = c.presenter_name + (f" — {c.presenter_title}" if c.presenter_title else "")
            flow.append(Paragraph(esc(attrib), k.ps("wa", 9, color="accent_on_primary", spaceBefore=10)))
        story.append(_sp(k, 12))
        story.append(KeepTogether(_box(flow, k, k.c["primary"], pad=20)))


def _bullets(story, items, k, S, numbered=False):
    for n, it in enumerate(items, 1):
        mark = f"{n}." if numbered else "•"
        story.append(Paragraph(f'<font color="{hexc(k.c["accent"])}">{mark}</font>&nbsp; {esc(it)}',
                               S["bullet"]))


def _overview(story, request, scores, chart_images, k, S):
    """Diagnostic d'ensemble (synthesis.py) : profil, enjeux structurants,
    liens entre piliers — propre au dossier."""
    import synthesis as SY
    import illustrations as IL
    o = SY.overview(request, scores)
    story.append(Paragraph(esc(o["title"]), S["h2"]))
    story.append(Paragraph(esc(o["profile_title"]), S["h3"]))
    story.extend(Paragraph(esc(p), S["body"]) for p in o["profile"])
    if o["issues"]:
        story.append(Paragraph(esc(o["issues_title"]), S["h3"]))
        story.append(Paragraph(esc(o["issues_intro"]), S["body"]))
        for key in IL.placements_overview():
            _illustration(story, request, chart_images, key, S)
        for n, issue in enumerate(o["issues"], 1):
            story.append(Paragraph(f'<font color="{hexc(k.c[issue.pillar])}">{n}. '
                                   f'{esc(issue.title)}</font>', S["h3"]))
            story.append(Paragraph(esc(issue.cause), S["body"]))
            story.append(Paragraph(esc(issue.csq), S["body"]))
    if o["links"]:
        story.append(Paragraph(esc(o["links_title"]), S["h3"]))
        _bullets(story, o["links"], k, S)
    story.append(_sp(k, 12))


def _closing_synthesis(story, request, scores, k, S):
    """Ce que nous retenons, si rien ne change, les 90 premiers jours."""
    import synthesis as SY
    c = SY.closing(request, scores)
    if c["retain"]:
        story.append(Paragraph(esc(c["retain_title"]), S["h2"]))
        _bullets(story, c["retain"], k, S)
    if c["horizon"]:
        story.append(Paragraph(esc(c["horizon_title"]), S["h2"]))
        story.extend(Paragraph(esc(p), S["body"]) for p in c["horizon"])
    story.append(Paragraph(esc(c["first_title"]), S["h2"]))
    story.append(Paragraph(esc(c["first_intro"]), S["body"]))
    _bullets(story, c["first"], k, S, numbered=True)


def _executive(story, request, scores, content, k, S, TR, anchors, notes, ro, recs3):
    section_head(story, TR["pdf_s1"], "accent", k, S, anchors, "s1")
    exec_text = content.get("executive_summary",
                            f"{request.company.name} présente son rapport ESG pour l'exercice "
                            f"{request.company.reporting_year}.")
    story.append(Paragraph(esc(exec_text), S["body"]))
    story.append(_sp(k, 8))

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
        story.append(_sp(k, 6))
        story.append(_box(Paragraph(f'<b>{esc(TR["digest_actions"]).upper()}</b> — {esc(acts)}',
                                    k.ps("dga", 8.4, color="ink", leading=12)), k, k.c["panel"], pad=9))
    if notes.get("global"):
        story.append(_sp(k, 8))
        consultant_callout(story, notes["global"], k, TR)
    story.append(_sp(k, 12))


_BAND_STATUS = {"exemplaire": "good", "solide": "good", "satisfaisant": "warn",
                "fragile": "bad", "critique": "bad"}


def _status(request, indicator, value):
    """Pastille d'un indicateur, lue dans la grille du score (bands.py) —
    la même que le texte : une pastille ne peut plus contredire la phrase.
    (Avant le 2026-09-24, le PDF portait ses propres seuils, divergents.)"""
    if value is None:
        return None
    tranche = classer(indicator, value, request.company.sector)
    return _BAND_STATUS.get(tranche) if tranche is not None else None


def _pillar_intro(story, title, key, score_label, score, insight, note, text, k, S, TR, anchors,
                  anchor):
    # 11 cm : titre, score, lecture et encart consultant restent ensemble
    section_head(story, title, key, k, S, anchors, anchor, keep_cm=11)
    from esg_calculator import score_label as _lbl
    sur_100 = f'<font color="{hexc(k.c["muted"])}">/100</font>' if score is not None else ""
    story.append(Paragraph(f'{esc(score_label)} : <font name="{k.f["display"]}" size="15" '
                           f'color="{hexc(k.c[key])}">{_lbl(score)}</font>' + sur_100, S["h2"]))
    insight_callout(story, insight, key, k)
    if note:
        consultant_callout(story, note, k, TR)
    story.append(Paragraph(esc(text), S["body"]))


def _pillar_reading(story, request, scores, pillar, kpis, k, S, TR, lang, recs=()):
    """« Lecture des indicateurs » : texte chiffré puis tableau, insécables."""
    first, second = NR.pillar_paragraphs(request, scores, pillar)
    story.append(KeepTogether([Paragraph(esc(NR.T[lang]["reading_title"]), S["h2"]),
                               Paragraph(esc(first), S["body"])]))
    if kpis:
        story.append(KeepTogether([_sp(k, 4), kpi_block(kpis, k, lang), _sp(k, 10)]))
    story.append(Paragraph(esc(second), S["body"]))
    if request.include_recommendations:
        story.append(Paragraph(esc(NR.levers_sentence(request, recs, pillar)), S["body"]))


def _illustration(story, request, chart_images, key, S):
    """Illustration pleine largeur (proportions du PNG) et sa légende, insécables."""
    from reportlab.lib.utils import ImageReader
    import illustrations as IL
    data = chart_images.get(key)
    if not data:
        return
    try:
        iw, ih = ImageReader(io.BytesIO(data)).getSize()
        w = min(CW, iw / IL.DPI * 72)
        im = Image(io.BytesIO(data), width=w, height=w * ih / iw)
        im.hAlign = "CENTER"
        story.append(KeepTogether([Spacer(1, 4), im,
                                   Paragraph(esc(IL.caption(request, key)), S["caption"]),
                                   Spacer(1, 6)]))
    except Exception as e:
        print(f"Illustration '{key}' error: {e}")


def _pillar_analysis(story, request, scores, pillar, chart_images, k, S):
    """Analyse approfondie (constat, cause, conséquence, levier) en fin de
    pilier, illustrée aux endroits fixés par illustrations.ANCHORS."""
    import illustrations as IL
    sections = AN.pillar_analysis(request, scores, pillar)
    if not sections:
        return
    where = IL.placements(pillar, [sec.key for sec in sections])
    story.append(Paragraph(esc(AN.analysis_title(request, pillar)), S["h2"]))
    for key in where.get("_start", []):
        _illustration(story, request, chart_images, key, S)
    for sec in sections:
        story.append(Paragraph(f'<font color="{hexc(k.c[pillar])}">{esc(sec.title)}</font>',
                               S["h3"]))
        story.extend(Paragraph(esc(p), S["body"]) for p in sec.paragraphs)
        for key in where.get(sec.key, []):
            _illustration(story, request, chart_images, key, S)


def _environment(story, request, scores, content, chart_images, k, S, TR, lang, anchors, notes, pi,
                 recs):
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
                     _status(request, "co2_emissions_tonnes", round(ci) if ci else None)))
    if env.renewable_energy_percent is not None:
        kpis.append((TR["kpit"]["renewable"], _pct(env.renewable_energy_percent, lang),
                     _status(request, "renewable_energy_percent", env.renewable_energy_percent)))
    if env.energy_consumption_mwh is not None:
        kpis.append((TR["kpit"]["energy"], _num(env.energy_consumption_mwh, lang)))
    if env.water_consumption_m3 is not None:
        kpis.append((TR["kpit"]["water"], _num(env.water_consumption_m3, lang)))
    if env.waste_recycled_percent is not None:
        kpis.append((TR["kpit"]["recycling"], _pct(env.waste_recycled_percent, lang),
                     _status(request, "waste_recycled_percent", env.waste_recycled_percent)))
    _pillar_reading(story, request, scores, "env", kpis, k, S, TR, lang, recs)
    scopes = [("Scope 1", env.scope1_emissions), ("Scope 2", env.scope2_emissions),
              ("Scope 3", env.scope3_emissions)]
    known = [(n, v) for n, v in scopes if v is not None]
    if known:
        story.append(_sp(k, 6))
        ghg_head: list[Flowable] = [Paragraph(esc(TR["ed_ghg_table"]), S["h2"]),
                    Paragraph(esc(NR.ghg_paragraph(request)), S["body"])]
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
                story.append(KeepTogether(ghg_head + [wrap, Paragraph(TR["cap_pie"], S["caption"])]))
            except Exception as e:
                print(f"Pie error: {e}")
                story.append(KeepTogether(ghg_head + [tbl]))
        else:
            story.append(KeepTogether(ghg_head + [tbl]))
    _pillar_analysis(story, request, scores, "env", chart_images, k, S)
    story.append(_sp(k, 12))


def _social(story, request, scores, content, chart_images, k, S, TR, lang, anchors, notes, pi,
            recs):
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
                     _status(request, "female_employees_percent", soc.female_employees_percent)))
    if soc.employee_turnover_percent is not None:
        kpis.append((TR["kpit"]["turnover"], _pct(soc.employee_turnover_percent, lang),
                     _status(request, "employee_turnover_percent", soc.employee_turnover_percent)))
    if soc.training_hours_per_employee is not None:
        kpis.append((TR["kpit"]["training"], _num(soc.training_hours_per_employee, lang),
                     _status(request, "training_hours_per_employee", soc.training_hours_per_employee)))
    if soc.accident_frequency_rate is not None:
        kpis.append((TR["kpit"]["accident"], _num(soc.accident_frequency_rate, lang, 2),
                     _status(request, "accident_frequency_rate", soc.accident_frequency_rate)))
    if soc.customer_satisfaction_score is not None:
        kpis.append((TR["kpit"]["satisfaction"], _num(soc.customer_satisfaction_score, lang, 1),
                     _status(request, "customer_satisfaction_score", soc.customer_satisfaction_score)))
    _pillar_reading(story, request, scores, "social", kpis, k, S, TR, lang, recs)
    _pillar_analysis(story, request, scores, "social", chart_images, k, S)
    story.append(_sp(k, 12))


def _governance(story, request, scores, content, chart_images, k, S, TR, lang, anchors, notes,
                pi, recs):
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
                     _status(request, "female_board_percent", gov.female_board_percent)))
    if gov.independent_board_percent is not None:
        kpis.append((yn["independent"], _pct(gov.independent_board_percent, lang),
                     _status(request, "independent_board_percent", gov.independent_board_percent)))
    if gov.csr_budget_eur is not None:
        kpis.append((yn["csr"], _num(gov.csr_budget_eur, lang)))
    for flag, key in ((gov.esg_audit_conducted, "audit"), (gov.sustainability_committee, "committee")):
        kpis.append((yn[key], yn["yes"] if flag else (yn["no"] if flag is not None else yn["na"]),
                     "good" if flag else ("bad" if flag is not None else None)))
    _pillar_reading(story, request, scores, "gov", kpis, k, S, TR, lang, recs)
    _pillar_analysis(story, request, scores, "gov", chart_images, k, S)
    story.append(_sp(k, 12))


def _analyses(story, content, chart_images, k, S, TR, anchors):
    section_head(story, TR["pdf_s5"], "accent", k, S, anchors, "s5", keep_cm=10)
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


def _strategic(story, request, scores, chart_images, k, S, TR, anchors, bv, mt, ro, gaps, ref):
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

    story.append(_sp(k, 12))
    section_head(story, TR["pdf_diag"], "accent", k, S, anchors, "diag", keep_cm=10)
    _positioning(story, request, scores, bv, k, S, TR)

    if "trend" in chart_images:
        story.append(Paragraph(TR["trend_title"], S["h2"]))
        _chart(story, chart_images, "trend", 16.5, 8.4, TR["cap_trend"], S)

    if mt["stage"] is None:  # sans score global : maturité non évaluée
        story.append(Paragraph(f'{esc(TR["pdf_maturity_sub"])} : {esc(TR["mat_none"])}', S["h2"]))
    else:
        mat_lbl = TR.get("mat_" + mt["key"], "")
        story.append(Paragraph(f'{esc(TR["pdf_maturity_sub"])} : {esc(mat_lbl)} '
                               f'<font color="{hexc(k.c["muted"])}">({mt["stage"]}/5)</font>', S["h2"]))
    story.append(Paragraph(esc(mt["next_hint"]), S["body"]))

    # Couverture des exigences (libellés et couleurs : source unique gap_status)
    gap_head: list[Flowable] = [Paragraph(TR["gap_title"], S["h2"]),
                Paragraph(esc(NR.gaps_intro(request, gaps, ref)), S["body"])]
    rows = [[Paragraph(esc(TR[x]).upper(), S["th"]) for x in ("gap_req", "gap_ref", "gap_status", "gap_note")]]
    for gp in gaps:
        rows.append([Paragraph(esc(gp["req"]), S["small_b"]), Paragraph(esc(gp["ref"]), S["small"]),
                     Paragraph(f'<font color="{GS.couleur(gp["status"], gp["nature"])}">'
                               f'<b>• {esc(GS.libelle(TR, gp["status"], gp["nature"]))}</b></font>',
                               S["small"]),
                     Paragraph(esc(gp["note"]), S["small"])])
    story.append(KeepTogether(gap_head + [data_table(rows, [CW * 0.32, CW * 0.19, CW * 0.17, CW * 0.32], k)]))
    story.append(_sp(k, 10))

    risk_head: list[Flowable] = [Paragraph(TR["risks_head"], S["h2"]),
                 Paragraph(esc(NR.risks_intro(request, ro["risks"])), S["body"])]
    c2 = k.ps("rc", 8.4, color="ink", alignment=TA_CENTER)
    rows = [[Paragraph(esc(TR[x]).upper(), S["th"]) for x in ("risk_desc", "risk_impact", "risk_lik", "risk_prio")]]
    for it in ro["risks"]:
        pr = it.get("priority", "P2")
        rows.append([Paragraph(f'<b>{esc(it["tag"])}</b> — {esc(it["text"])}', S["small"]),
                     Paragraph(esc(it.get("impact", "—")), c2), Paragraph(esc(it.get("likelihood", "—")), c2),
                     Paragraph(f'<font color="{_PRIO_HEX[pr]}"><b>{pr}</b></font>', c2)])
    story.append(KeepTogether(risk_head + [data_table(rows, [CW * 0.6, CW * 0.14, CW * 0.14, CW * 0.12], k)]))
    story.append(_sp(k, 10))

    opp = [Paragraph(esc(TR["opps_head"]).upper(), k.ps("oh", 8, font="body_b", color="env",
                                                        charSpace=0.6, spaceAfter=6))]
    for it in ro["opportunities"]:
        opp.append(Paragraph(f'<font color="{hexc(k.c["env"])}"><b>{esc(it["tag"])}</b></font> — '
                             f'{esc(it["text"])}', k.ps("oi", 9, color="ink", leading=13, spaceAfter=5)))
    story.append(KeepTogether(_box(opp, k, k.c["env_soft"], left=k.c["env"])))


def _positioning(story, request, scores, bv, k, S, TR):
    """Positionnement INTERNE : les piliers notés comparés entre eux. Aucune
    donnée externe (la référence sectorielle d'origine était inventée). Sous
    deux piliers notés (bv None), la section le dit au lieu de classer."""
    if bv is None:
        from content_generator import POSITIONNEMENT_IMPOSSIBLE
        story.append(Paragraph(esc(POSITIONNEMENT_IMPOSSIBLE[request.language]), S["body"]))
        return
    bench_head: list[Flowable] = [Paragraph(esc(bv["title"]), S["h2"]),
                  Paragraph(esc(NR.bench_intro(request)), S["body"]),
                  Paragraph(TR["pdf_bench_sub"], k.ps("bs", 8.4, font="body_i", color="muted",
                                                      spaceAfter=6))]
    center = k.ps("c", 8.8, color="ink", alignment=TA_CENTER)
    lab = {"env": TR["pillar_env"], "social": TR["pillar_soc"], "gov": TR["pillar_gov"]}
    rows = [[Paragraph(esc(TR[x]).upper(), S["th"]) for x in
             ("bench_metric_col", "bench_you", "bench_delta_col", "bench_reading_col")]]
    for row in bv["rows"]:
        d = row["delta"]
        rcol = (_STATUS_HEX["good"] if row["role"] == "lead"
                else _STATUS_HEX["bad"] if row["role"] == "lag" else hexc(k.c["ink"]))
        rows.append([Paragraph(esc(lab[row["key"]]), S["small_b"]),
                     Paragraph(score_label(row["score"]), center),
                     Paragraph("—" if not d else f"{d:.0f} pts", center),
                     Paragraph(f'<font color="{rcol}"><b>{esc(row["reading"] or TR["bench_not_rated"])}</b></font>',
                               center)])
    rows.append([Paragraph(esc(TR.get("score_global_short", "Global")), S["small_b"]),
                 Paragraph(f"<b>{score_label(scores.total_esg_score)}</b>", center), Paragraph("", center),
                 Paragraph(f"<b>{esc(scores.rating or NON_NOTE)}</b>", center)])
    story.append(KeepTogether(bench_head + [data_table(rows, [CW * 0.36, CW * 0.17, CW * 0.19, CW * 0.28],
                                                       k, total=True)]))
    story.append(_sp(k, 8))
    insight_callout(story, bv["insight"], "accent", k)


def _recommendations(story, request, scores, chart_images, k, S, TR, anchors, recs, priority_reading):
    section_head(story, TR["pdf_s7"], "accent", k, S, anchors, "s7", keep_cm=10)
    story.append(Paragraph(esc(NR.recs_intro(request, recs)), S["lead"]))
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
        story.append(_sp(k, 8))
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
    story.append(_sp(k, 6))


def _roadmap(story, request, scores, k, S, TR, anchors, rm):
    if not any(ph["actions"] for ph in rm):
        return
    story.append(_sp(k, 14))
    section_head(story, TR["roadmap_title"], "accent", k, S, anchors, "roadmap", keep_cm=10)
    story.append(Paragraph(esc(NR.roadmap_intro(request, rm)), S["body"]))
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
    band = Table([[Paragraph(esc(TR["div2_sub"]), k.ps("bd", 13, font="display_i", color="on_primary",
                                                        leading=18))]], colWidths=[CW])
    band.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), k.c["primary"]),
                              ("LEFTPADDING", (0, 0), (-1, -1), 20), ("TOPPADDING", (0, 0), (-1, -1), 18),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 20)]))
    story.append(KeepTogether([t, _sp(k, 12), band]))


def _white_paper(story, request, scores, k, S, TR, anchors):
    story.append(_sp(k, 14))
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
    story.append(_sp(k, 14))
    title = TR["pdf_concl_wp"] if request.report_type.value == "white_paper" else TR["pdf_concl"]
    section_head(story, title, "accent", k, S, anchors, "concl", keep_cm=10)
    story.append(Paragraph(esc(content.get("conclusion",
                                           f"{request.company.name} — score ESG "
                                           f"{score_label(scores.total_esg_score, 1)}/100 (note {scores.rating or NON_NOTE}).")),
                           S["body"]))
    _closing_synthesis(story, request, scores, k, S)
    if content.get("methodology"):
        story.append(_sp(k, 10))
        story.append(Paragraph(TR["pdf_methodo"], S["h2"]))
        story.append(_box(Paragraph(esc(content["methodology"]),
                                    k.ps("mn", 8.6, color="ink", leading=13, allowWidows=0,
                                         allowOrphans=0)),
                          k, k.c["panel"], left=k.c["accent"]))
    if k.uses_bank():
        story.append(Paragraph(esc(TR["ed_photo_note"]), k.ps("pn", 7.6, font="body_i", color="muted",
                                                              leading=10.5, spaceBefore=6)))
    gloss = glossary_entries(request, scores)
    if gloss:
        story.append(_sp(k, 10))
        story.append(Paragraph(TR["pdf_glossary"], S["h2"]))
        rows = [[Paragraph(esc(e["term"]), S["small_b"]), Paragraph(esc(e["definition"]), S["small"])]
                for e in gloss]
        story.append(data_table(rows, [CW * 0.22, CW * 0.78], k, header=False))
    story.append(_sp(k, 18))
    story.append(Paragraph(esc(f"© {request.company.reporting_year} {request.company.name} — " + TR["gen_auto"]),
                           S["footer"]))
