import io
from dataclasses import dataclass
from typing import Any

from pptx import Presentation
from pptx.util import Emu, Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.slide import Slide
from pptx.shapes.autoshape import Shape
from pptx.enum.text import PP_ALIGN
from esg_calculator import NON_NOTE, score_label
from models import ESGRequest, ESGScores, AestheticTheme, PresentationType
from visual_kit import pillar_hero, icon_png, ring_png
from i18n import L


def _hexstr(rgb: RGBColor) -> str:
    """RGBColor -> '#RRGGBB' pour visual_kit."""
    return "#" + str(rgb)

# Mise en page PPTX par gabarit (couleurs et polices : report_designs).
# Les six gabarits sont clairs : aucune diapositive sombre.
_PPTX_LAYOUT = {
    AestheticTheme.AURORA: {"header": "minimal", "card": "flat", "cover": "classic"},
    AestheticTheme.ANNUEL: {"header": "minimal", "card": "outline", "cover": "minimal"},
    AestheticTheme.INSTITUTIONNEL: {"header": "band", "card": "rounded", "cover": "classic"},
    AestheticTheme.PORTRAIT: {"header": "minimal", "card": "flat", "cover": "luxe"},
    AestheticTheme.TERRE: {"header": "pill", "card": "rounded", "cover": "organic"},
    AestheticTheme.GALERIE: {"header": "minimal", "card": "outline", "cover": "minimal"},
}


def _rgb(hexstr: str) -> RGBColor:
    h = hexstr.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def pptx_theme(theme: AestheticTheme) -> dict:
    """Palette PPTX convertie depuis le gabarit."""
    from report_designs import colors_of
    c = colors_of(theme)
    return {"bg_primary": _rgb(c["primary"]), "bg_secondary": _rgb(c["paper"]),
            "accent": _rgb(c["accent"]), "env": _rgb(c["env"]), "social": _rgb(c["social"]),
            "gov": _rgb(c["gov"]), "text_light": _rgb(c["on_primary"]), "text_dark": _rgb(c["ink"]),
            "subtitle": _rgb(c["accent_on_primary"]), "muted": _rgb(c["muted"]),
            "card_bg": _rgb(c["panel"])}


def pptx_style(theme: AestheticTheme) -> dict:
    """Langage de mise en page PPTX : polices système sûres du gabarit."""
    from report_designs import design, DEFAULT_DESIGN
    d = design(theme)
    return dict(_PPTX_LAYOUT.get(theme, _PPTX_LAYOUT[DEFAULT_DESIGN]),
                font_title=d["office"]["display"], font_body=d["office"]["body"],
                dark_slides=False, uppercase_titles=False)


SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)

RECT = MSO_SHAPE.RECTANGLE
ROUNDED_RECT = MSO_SHAPE.ROUNDED_RECTANGLE
OVAL = MSO_SHAPE.OVAL


def _emu(v: float) -> Emu:
    """Position en EMU entière ; python-pptx tronquait déjà les décimales."""
    return Emu(int(v))


def add_shape(slide: Slide, shape_type: MSO_SHAPE, left: float, top: float,
              width: float, height: float, fill: RGBColor | None = None,
              line_color: RGBColor | None = None,
              line_width_pt: float | None = None) -> Shape:
    shape = slide.shapes.add_shape(shape_type, _emu(left), _emu(top), _emu(width), _emu(height))
    if fill is not None:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    else:
        shape.fill.background()
    if line_color is not None:
        shape.line.color.rgb = line_color
        if line_width_pt:
            shape.line.width = Pt(line_width_pt)
    else:
        shape.line.fill.background()
    return shape


def add_bg_rect(slide: Slide, left: float, top: float, width: float,
                height: float, color: RGBColor) -> Shape:
    return add_shape(slide, RECT, left, top, width, height, fill=color)


def add_text(slide: Slide, text: str, left: float, top: float, width: float,
             height: float, font_size: float = 18, bold: bool = False,
             color: RGBColor = RGBColor(0, 0, 0),
             align: PP_ALIGN = PP_ALIGN.LEFT, italic: bool = False,
             word_wrap: bool = True, font: str | None = None) -> Shape:
    txBox = slide.shapes.add_textbox(_emu(left), _emu(top), _emu(width), _emu(height))
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
    if font:
        run.font.name = font
    return txBox


def add_image_from_bytes(slide: Slide, img_bytes: bytes, left: float, top: float,
                         width: float | None = None,
                         height: float | None = None) -> None:
    img_io = io.BytesIO(img_bytes)
    slide.shapes.add_picture(img_io, _emu(left), _emu(top),
                             None if width is None else _emu(width),
                             None if height is None else _emu(height))


def maybe_upper(text: str, style: dict) -> str:
    return text.upper() if style["uppercase_titles"] else text


def _fit_title(base, title):
    """Réduit la taille du titre s'il est long (titres-conclusion)."""
    n = len(title)
    if n > 52:
        return base * 0.66
    if n > 38:
        return base * 0.78
    if n > 28:
        return base * 0.9
    return base


def content_slide(prs, blank_layout, theme, style, title, color: RGBColor, kicker=None):
    """Slide à en-tête thématisé. `kicker` = petit sur-titre optionnel."""
    slide = prs.slides.add_slide(blank_layout)
    title = maybe_upper(title, style)
    ft, fb = style["font_title"], style["font_body"]

    if style["header"] == "band":
        add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_secondary"])
        add_bg_rect(slide, 0, 0, SLIDE_W, Inches(1.25), color)
        add_bg_rect(slide, 0, Inches(1.25), Inches(0.07), SLIDE_H - Inches(1.25), theme["accent"])
        if kicker:
            add_text(slide, kicker.upper(), Inches(0.32), Inches(0.14), Inches(12), Inches(0.32),
                     font_size=11, bold=True, color=theme["accent"], font=fb)
        add_text(slide, title, Inches(0.3), Inches(0.42 if kicker else 0.2), Inches(12.7), Inches(0.78),
                 font_size=_fit_title(26, title), bold=True, color=theme["text_light"], font=ft)

    elif style["header"] == "pill":
        add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_secondary"])
        add_shape(slide, OVAL, Inches(11.8), Inches(-1.2), Inches(3), Inches(3), fill=theme["card_bg"])
        add_shape(slide, OVAL, Inches(12.6), Inches(6.4), Inches(2), Inches(2), fill=theme["card_bg"])
        add_shape(slide, ROUNDED_RECT, Inches(0.3), Inches(0.22), Inches(11.2), Inches(0.95), fill=color)
        add_text(slide, title, Inches(0.6), Inches(0.3), Inches(10.8), Inches(0.8),
                 font_size=_fit_title(22, title), bold=True, color=theme["text_light"], font=ft)

    elif style["header"] == "hairline":
        add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_primary"])
        if kicker:
            add_text(slide, kicker.upper(), Inches(0.5), Inches(0.24), Inches(12), Inches(0.3),
                     font_size=11, bold=True, color=theme["accent"], font=fb)
        add_text(slide, title, Inches(0.5), Inches(0.5 if kicker else 0.32), Inches(12.3), Inches(0.7),
                 font_size=_fit_title(24, title), bold=False, color=color, font=ft)
        add_bg_rect(slide, Inches(0.5), Inches(1.28), Inches(12.3), Inches(0.02), theme["accent"])

    else:  # minimal
        add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_secondary"])
        add_bg_rect(slide, Inches(0.5), Inches(0.42), Inches(0.22), Inches(0.22), color)
        add_text(slide, title, Inches(0.9), Inches(0.26), Inches(11.8), Inches(0.75),
                 font_size=_fit_title(20, title), bold=True, color=theme["text_dark"], font=ft)
        add_bg_rect(slide, Inches(0.5), Inches(1.12), Inches(2.2), Inches(0.02), theme["text_dark"])

    return slide


def section_divider(prs, blank_layout, theme, style, part_no: str, title: str, subtitle: str | None = None):
    """Carton de transition pleine page (rythme éditorial « rapport annuel »)."""
    ft, fb = style["font_title"], style["font_body"]
    slide = prs.slides.add_slide(blank_layout)
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_primary"])
    add_bg_rect(slide, 0, 0, Inches(0.18), SLIDE_H, theme["accent"])
    # Numéro de partie géant en filigrane
    add_text(slide, part_no, Inches(0.55), Inches(1.15), Inches(6), Inches(3.2),
             font_size=200, bold=True, color=theme["card_bg"], font=ft)
    # Kicker + titre
    add_text(slide, maybe_upper(title.upper(), style), Inches(0.7), Inches(4.55), Inches(11.9), Inches(1.6),
             font_size=_fit_title(40, title), bold=True, color=theme["text_light"], font=ft)
    add_bg_rect(slide, Inches(0.75), Inches(4.35), Inches(2.2), Inches(0.08), theme["accent"])
    if subtitle:
        add_text(slide, subtitle, Inches(0.75), Inches(6.05), Inches(11.5), Inches(0.9),
                 font_size=16, italic=True, color=theme["subtitle"], font=fb)
    return slide


def kpi_card(slide, left, top, w, h, theme, style, color: RGBColor):
    """Draw a KPI card background in the theme's card style."""
    if style["card"] == "flat":
        add_bg_rect(slide, left, top, w, h, theme["card_bg"])
        add_bg_rect(slide, left, top, w, Inches(0.1), color)
    elif style["card"] == "rounded":
        add_shape(slide, ROUNDED_RECT, left, top, w, h, fill=theme["card_bg"])
        add_shape(slide, OVAL, left + Inches(0.15), top + Inches(0.15),
                  Inches(0.18), Inches(0.18), fill=color)
    elif style["card"] == "dark":
        add_bg_rect(slide, left, top, w, h, theme["card_bg"])
        add_bg_rect(slide, left, top, w, Inches(0.03), theme["accent"])
    else:  # outline
        add_shape(slide, RECT, left, top, w, h, fill=theme["card_bg"],
                  line_color=RGBColor(0xE0, 0xE0, 0xE0), line_width_pt=1.0)
        add_bg_rect(slide, left, top, Inches(0.06), h, color)


def kpi_grid(slide, kpis, theme, style, color: RGBColor, top_start=Inches(1.3), ncols=3):
    fb = style["font_body"]
    cols = [Inches(0.3), Inches(4.55), Inches(8.8)][:ncols]
    max_cards = ncols * 3
    label_indent = Inches(0.42) if style["card"] == "rounded" else Inches(0.2)
    for idx, (kpi_label, kpi_val) in enumerate(kpis[:max_cards]):
        col = cols[idx % ncols]
        row = top_start + (idx // ncols) * Inches(1.9)
        kpi_card(slide, col, row, Inches(4.0), Inches(1.7), theme, style, color)
        add_text(slide, kpi_label, col + label_indent, row + Inches(0.15),
                 Inches(3.5), Inches(0.45), font_size=11, color=theme["muted"], font=fb)
        add_text(slide, kpi_val, col + Inches(0.2), row + Inches(0.65),
                 Inches(3.7), Inches(0.85), font_size=22, bold=True, color=color, font=fb)


# ── Covers ────────────────────────────────────────────────────────────────

def _cover_tag(TR, scores):
    total = scores.total_esg_score
    if total is None:  # sans score global : aucun jugement
        return TR["cover_tag_none"]
    b = "high" if total >= 75 else "good" if total >= 60 else "mid" if total >= 45 else "low"
    return TR["cover_tag_" + b]


def cover_classic(slide, theme, style, request, scores, subtitle, TR):
    # Couverture sur la primaire sombre : accents en « subtitle »
    # (accent_on_primary du gabarit), lisibles sur fond foncé.
    ft, fb = style["font_title"], style["font_body"]
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_primary"])
    add_bg_rect(slide, 0, 0, Inches(0.18), SLIDE_H, theme["subtitle"])
    # Aplat sombre en bas pour ancrer la composition (magazine)
    add_bg_rect(slide, 0, Inches(5.4), SLIDE_W, Inches(2.1), theme["bg_primary"])

    # Kicker + nom géant + accroche (bloc éditorial gauche)
    add_text(slide, subtitle.upper(), Inches(0.65), Inches(1.15), Inches(9), Inches(0.5),
             font_size=15, bold=True, color=theme["subtitle"], font=fb)
    add_text(slide, request.company.name.upper(), Inches(0.6), Inches(1.75), Inches(9.2), Inches(1.9),
             font_size=52, bold=True, color=theme["text_light"], font=ft)
    add_bg_rect(slide, Inches(0.65), Inches(3.75), Inches(2.0), Inches(0.06), theme["subtitle"])
    add_text(slide, _cover_tag(TR, scores), Inches(0.65), Inches(4.0), Inches(8.5), Inches(0.7),
             font_size=21, italic=True, color=theme["subtitle"], font=fb)

    # Bandeau bas : méta à gauche, score mis en scène à droite
    add_text(slide, f"{TR['exercise']} {request.company.reporting_year}   |   {request.company.sector}   |   {request.company.country}",
             Inches(0.65), Inches(6.55), Inches(8), Inches(0.5),
             font_size=13, color=theme["subtitle"], font=fb)
    add_text(slide, score_label(scores.total_esg_score), Inches(8.55), Inches(5.35), Inches(2.4), Inches(1.6),
             font_size=82, bold=True, color=theme["subtitle"], align=PP_ALIGN.RIGHT, font=ft)
    add_text(slide, "/100", Inches(8.55), Inches(6.75), Inches(2.4), Inches(0.4),
             font_size=14, color=theme["subtitle"], align=PP_ALIGN.RIGHT, font=fb)
    add_shape(slide, ROUNDED_RECT, Inches(11.2), Inches(5.55), Inches(1.55), Inches(0.95), fill=theme["subtitle"])
    add_text(slide, scores.rating or NON_NOTE, Inches(11.2), Inches(5.68), Inches(1.55), Inches(0.7),
             font_size=32, bold=True, color=theme["bg_primary"], align=PP_ALIGN.CENTER, font=ft)


def cover_organic(slide, theme, style, request, scores, subtitle, TR):
    ft, fb = style["font_title"], style["font_body"]
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_secondary"])
    # Cercles organiques (identité) en haut à droite
    add_shape(slide, OVAL, Inches(9.6), Inches(-2.4), Inches(6.0), Inches(6.0), fill=theme["card_bg"])
    add_shape(slide, OVAL, Inches(11.3), Inches(-0.9), Inches(3.6), Inches(3.6), fill=theme["env"])
    add_shape(slide, OVAL, Inches(10.5), Inches(1.7), Inches(1.3), Inches(1.3), fill=theme["accent"])
    # Bloc éditorial
    add_text(slide, subtitle.upper(), Inches(0.75), Inches(1.35), Inches(8.5), Inches(0.5),
             font_size=15, bold=True, color=theme["env"], font=fb)
    add_text(slide, request.company.name, Inches(0.7), Inches(1.95), Inches(9), Inches(1.7),
             font_size=48, bold=True, color=theme["bg_primary"], font=ft)
    add_shape(slide, ROUNDED_RECT, Inches(0.75), Inches(3.75), Inches(2.0), Inches(0.08), fill=theme["accent"])
    add_text(slide, _cover_tag(TR, scores), Inches(0.75), Inches(4.0), Inches(8.5), Inches(0.7),
             font_size=21, italic=True, color=theme["muted"], font=fb)
    # Bandeau bas : score mis en scène
    add_shape(slide, ROUNDED_RECT, Inches(0.7), Inches(5.35), Inches(11.93), Inches(1.5), fill=theme["bg_primary"])
    add_text(slide, f"{TR['exercise']} {request.company.reporting_year}   |   {request.company.sector}   |   {request.company.country}",
             Inches(1.15), Inches(5.65), Inches(7), Inches(0.5), font_size=13, color=theme["subtitle"], font=fb)
    add_text(slide, f"{TR['chart_global']}", Inches(1.15), Inches(6.15), Inches(7), Inches(0.5),
             font_size=13, bold=True, color=theme["text_light"], font=fb)
    add_text(slide, score_label(scores.total_esg_score), Inches(8.7), Inches(5.42), Inches(2.2), Inches(1.4),
             font_size=54, bold=True, color=theme["accent"], align=PP_ALIGN.RIGHT, font=ft)
    add_shape(slide, OVAL, Inches(11.15), Inches(5.62), Inches(1.0), Inches(1.0), fill=theme["accent"])
    add_text(slide, scores.rating or NON_NOTE, Inches(11.15), Inches(5.78), Inches(1.0), Inches(0.6),
             font_size=24, bold=True, color=theme["bg_primary"], align=PP_ALIGN.CENTER, font=ft)


def cover_luxe(slide, theme, style, request, scores, subtitle, TR):
    ft, fb = style["font_title"], style["font_body"]
    gold = theme["subtitle"]
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_primary"])
    # Fin cadre or (élégance)
    m, tk = Inches(0.4), Inches(0.015)
    add_bg_rect(slide, m, m, SLIDE_W - m - m, tk, gold)
    add_bg_rect(slide, m, SLIDE_H - m, SLIDE_W - m - m, tk, gold)
    add_bg_rect(slide, m, m, tk, SLIDE_H - m - m, gold)
    add_bg_rect(slide, SLIDE_W - m, m, tk, SLIDE_H - m - m + tk, gold)
    # Composition serif centrée
    add_text(slide, subtitle.upper(), Inches(1), Inches(1.15), Inches(11.33), Inches(0.5),
             font_size=14, bold=True, color=gold, align=PP_ALIGN.CENTER, font=fb)
    add_text(slide, request.company.name.upper(), Inches(1), Inches(1.95), Inches(11.33), Inches(1.4),
             font_size=46, bold=False, color=theme["text_light"], align=PP_ALIGN.CENTER, font=ft)
    add_bg_rect(slide, Inches(6.06), Inches(3.5), Inches(1.2), Inches(0.02), gold)
    add_text(slide, _cover_tag(TR, scores), Inches(1), Inches(3.75), Inches(11.33), Inches(0.6),
             font_size=17, italic=True, color=theme["subtitle"], align=PP_ALIGN.CENTER, font=ft)
    # Note mise en scène (le grand signe de qualité)
    add_text(slide, scores.rating or NON_NOTE, Inches(1), Inches(4.6), Inches(11.33), Inches(1.3),
             font_size=64, bold=True, color=gold, align=PP_ALIGN.CENTER, font=ft)
    add_text(slide, f"{TR['chart_global']}  {score_label(scores.total_esg_score)} / 100", Inches(1), Inches(6.0),
             Inches(11.33), Inches(0.5), font_size=15, color=theme["subtitle"], align=PP_ALIGN.CENTER, font=fb)
    add_text(slide, f"{TR['exercise']} {request.company.reporting_year}  •  {request.company.sector}  •  {request.company.country}",
             Inches(1), Inches(6.55), Inches(11.33), Inches(0.4),
             font_size=12, italic=True, color=theme["subtitle"], align=PP_ALIGN.CENTER, font=ft)


def cover_minimal(slide, theme, style, request, scores, subtitle, TR):
    ft, fb = style["font_title"], style["font_body"]
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_secondary"])
    add_bg_rect(slide, Inches(0.7), Inches(1.05), Inches(0.4), Inches(0.4), theme["accent"])
    add_text(slide, subtitle.upper(), Inches(0.72), Inches(1.65), Inches(11), Inches(0.5),
             font_size=13, bold=True, color=theme["muted"], font=fb)
    add_text(slide, request.company.name, Inches(0.65), Inches(2.25), Inches(11.7), Inches(1.7),
             font_size=54, bold=True, color=theme["text_dark"], font=ft)
    add_text(slide, _cover_tag(TR, scores), Inches(0.7), Inches(4.0), Inches(9), Inches(0.6),
             font_size=19, italic=True, color=theme["muted"], font=fb)
    add_bg_rect(slide, Inches(0.7), Inches(4.85), Inches(11.9), Inches(0.02), RGBColor(0xBD, 0xBD, 0xBD))
    # Méta gauche + score mis en scène droite
    add_text(slide, f"{TR['exercise']} {request.company.reporting_year}", Inches(0.7), Inches(5.15),
             Inches(4), Inches(0.4), font_size=13, color=theme["muted"], font=fb)
    add_text(slide, request.company.sector, Inches(0.7), Inches(5.55), Inches(5), Inches(0.4),
             font_size=13, color=theme["muted"], font=fb)
    add_text(slide, request.company.country, Inches(0.7), Inches(5.95), Inches(5), Inches(0.4),
             font_size=13, color=theme["muted"], font=fb)
    add_text(slide, score_label(scores.total_esg_score), Inches(8.3), Inches(5.0), Inches(2.6), Inches(1.6),
             font_size=88, bold=True, color=theme["accent"], align=PP_ALIGN.RIGHT, font=ft)
    add_text(slide, f"/100  —  {TR['note']} {scores.rating or NON_NOTE}", Inches(6.9), Inches(6.5), Inches(4.0), Inches(0.4),
             font_size=15, bold=True, color=theme["text_dark"], align=PP_ALIGN.RIGHT, font=fb)


COVERS = {"classic": cover_classic, "organic": cover_organic,
          "luxe": cover_luxe, "minimal": cover_minimal}


def add_notes(slide, paragraphs) -> None:
    """Texte analytique du rapport (narrative.py) en notes de l'orateur : la
    présentation porte le même contenu que le PDF et le Word, sans
    surcharger la diapositive."""
    text = "\n\n".join(p for p in paragraphs if p)
    if text:
        slide.notes_slide.notes_text_frame.text = text


def pillar_infographic(prs, blank_layout, theme, style, pillar_key,
                       title, subtitle, score, kpis, t, insight=""):
    """Slide de pilier en infographie : héros illustré à gauche + chips KPI.

    kpis : liste de (icon_name, value_str, label). 6 max affichés.
    """
    ft, fb = style["font_title"], style["font_body"]
    color = theme[pillar_key]
    dark = style["dark_slides"]
    white = RGBColor(0xFF, 0xFF, 0xFF)

    slide = prs.slides.add_slide(blank_layout)
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_primary"] if dark else theme["bg_secondary"])

    # ── Héros illustré (flanc gauche) ──────────────────────────────
    HERO_W = Inches(4.5)
    pal = {"top": _hexstr(theme["bg_primary"]), "bottom": _hexstr(color),
           "accent": _hexstr(theme["accent"]), "light": _hexstr(theme["card_bg"])}
    try:
        hero = pillar_hero(pillar_key, pal, 470, 780)
        add_image_from_bytes(slide, hero, 0, 0, HERO_W, SLIDE_H)
    except Exception:
        add_bg_rect(slide, 0, 0, HERO_W, SLIDE_H, color)

    # Kicker = identité du pilier ; grand titre = la conclusion (information scent)
    add_text(slide, title.upper(), Inches(0.37), Inches(0.42), Inches(3.85), Inches(0.35),
             font_size=13, bold=True, color=theme["accent"], font=fb)
    add_text(slide, subtitle, Inches(0.35), Inches(0.85), Inches(3.95), Inches(2.5),
             font_size=_fit_title(24, subtitle), bold=True, color=white, font=ft)

    # Anneau de score en bas du héros
    if score is not None:  # pilier non noté : ni anneau ni chiffre, « — »
        try:
            ring = ring_png(score, 320, _hexstr(theme["accent"]))
            add_image_from_bytes(slide, ring, Inches(1.4), Inches(4.75), Inches(1.75), Inches(1.75))
        except Exception:
            pass
    add_text(slide, score_label(score), Inches(1.4), Inches(5.28), Inches(1.75), Inches(0.7),
             font_size=38, bold=True, color=white, align=PP_ALIGN.CENTER, font=ft)
    add_text(slide, t["score_100_caps"], Inches(1.0), Inches(6.65), Inches(2.55), Inches(0.4),
             font_size=11, bold=True, color=white, align=PP_ALIGN.CENTER, font=fb)

    # ── En-tête droite ─────────────────────────────────────────────
    RX = Inches(4.95)
    RW = Inches(8.05)
    add_text(slide, t["key_indicators"].upper(), RX, Inches(0.5), Inches(8), Inches(0.5),
             font_size=15, bold=True, color=theme["muted"], font=fb)
    add_bg_rect(slide, RX, Inches(1.02), Inches(1.4), Inches(0.045), color)

    # ── Chips KPI (2 × 2, plus grandes et lisibles) ────────────────
    chip_w, chip_h = Inches(3.9), Inches(1.42)
    gap_x, gap_y = Inches(0.25), Inches(0.24)
    top0 = Inches(1.35)
    border = RGBColor(0x3A, 0x40, 0x4A) if dark else RGBColor(0xE2, 0xE8, 0xF0)
    circ = Inches(0.9)
    for i, (icon_name, value, label) in enumerate(kpis[:4]):
        col, row = i % 2, i // 2
        x = RX + col * (chip_w + gap_x)
        y = top0 + row * (chip_h + gap_y)
        add_shape(slide, ROUNDED_RECT, x, y, chip_w, chip_h, fill=theme["card_bg"],
                  line_color=border, line_width_pt=0.75)
        add_shape(slide, RECT, x, y + Inches(0.18), Inches(0.06), chip_h - Inches(0.36), fill=color)
        add_shape(slide, OVAL, x + Inches(0.24), y + Inches(0.27), circ, circ, fill=color)
        try:
            add_image_from_bytes(slide, icon_png(icon_name, 130, "#FFFFFF"),
                                 x + Inches(0.43), y + Inches(0.46), Inches(0.52), Inches(0.52))
        except Exception:
            pass
        add_text(slide, value, x + Inches(1.35), y + Inches(0.24), chip_w - Inches(1.45), Inches(0.65),
                 font_size=23, bold=True, color=color, font=ft)
        add_text(slide, label, x + Inches(1.36), y + Inches(0.9), chip_w - Inches(1.45), Inches(0.45),
                 font_size=10.5, color=theme["muted"], font=fb)

    # ── Carte « Lecture métier » (insight rédigé) ──────────────────
    iy = top0 + 2 * (chip_h + gap_y) + Inches(0.18)
    ih = Inches(2.02)
    add_shape(slide, ROUNDED_RECT, RX, iy, RW, ih,
              fill=color if dark else theme["card_bg"],
              line_color=color, line_width_pt=1.5)
    add_shape(slide, RECT, RX, iy, Inches(0.11), ih, fill=color)
    lbl_color = white if dark else color
    add_text(slide, t["key_takeaway"], RX + Inches(0.42), iy + Inches(0.24), RW - Inches(0.7), Inches(0.4),
             font_size=12.5, bold=True, color=lbl_color, font=fb)
    txt_color = white if dark else theme["text_dark"]
    add_text(slide, insight or "", RX + Inches(0.42), iy + Inches(0.72), RW - Inches(0.8), ih - Inches(0.85),
             font_size=16, color=txt_color, font=fb)
    return slide


@dataclass
class _Deck:
    """Ce que lisent les diapositives : un seul objet passé à chaque fonction
    de section, calculé une fois (avant : recommandations, risques, écarts et
    feuille de route étaient recalculés deux ou trois fois dans la fonction)."""
    prs: Any
    layout: Any
    request: ESGRequest
    scores: ESGScores
    charts: dict
    theme: dict
    style: dict
    t: dict
    ref: str                  # référentiel affiché (CSRD ou VSME)
    all_recs: list            # enriched_recommendations, toujours calculées
    recs: list                # idem, vides si le client n'en veut pas
    ro: dict                  # risks_opportunities
    gaps: list                # compliance_assessment
    roadmap: list             # roadmap_12m
    verdict: str              # score_verdict, ou la phrase « pas de score global »
    insights: dict            # pillar_insights
    headlines: dict           # pillar_headline
    section_heads: dict       # section_headlines
    header_color: RGBColor

    @property
    def ft(self) -> str:
        return self.style["font_title"]

    @property
    def fb(self) -> str:
        return self.style["font_body"]

    @property
    def dark(self) -> bool:
        return self.style["dark_slides"]

    def new_slide(self) -> Slide:
        return self.prs.slides.add_slide(self.layout)

    def content_slide(self, title: str, kicker: str | None = None) -> Slide:
        return content_slide(self.prs, self.layout, self.theme, self.style, title,
                             self.header_color, kicker=kicker)

    def divider(self, part_no: str, title: str, subtitle: str) -> None:
        section_divider(self.prs, self.layout, self.theme, self.style, part_no, title, subtitle)


def _deck(request: ESGRequest, scores: ESGScores, chart_images: dict) -> _Deck:
    from content_generator import (pillar_insights, score_verdict, pillar_headline,
                                   section_headlines, risks_opportunities,
                                   compliance_assessment, enriched_recommendations, roadmap_12m,
                                   SANS_SCORE_GLOBAL)
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    theme = pptx_theme(request.aesthetic_theme)
    style = pptx_style(request.aesthetic_theme)
    if getattr(request, "custom_colors", None):
        from branding import brand_pptx_theme
        theme = brand_pptx_theme(theme, request.custom_colors)
    t = L(request.language)
    ref = t["cover_refs_vsme"] if getattr(request, "reporting_framework", "csrd") == "vsme" \
        else t["cover_refs"]
    all_recs = enriched_recommendations(request, scores)
    return _Deck(
        prs=prs, layout=prs.slide_layouts[6], request=request, scores=scores,
        charts=chart_images, theme=theme, style=style, t=t, ref=ref,
        all_recs=all_recs, recs=all_recs if request.include_recommendations else [],
        ro=risks_opportunities(request, scores), gaps=compliance_assessment(request, scores),
        roadmap=roadmap_12m(request, scores),
        verdict=score_verdict(request, scores) or SANS_SCORE_GLOBAL[request.language].format(n=request.company.name),
        insights=pillar_insights(request, scores), headlines=pillar_headline(request, scores),
        section_heads=section_headlines(request, scores),
        header_color=theme["accent"] if style["header"] == "hairline" else theme["bg_primary"])


def _slide_cover(d: _Deck, logo_bytes: bytes | None) -> None:
    theme, style, t, request = d.theme, d.style, d.t, d.request
    slide = d.new_slide()
    subtitle_map = {
        PresentationType.EXECUTIVE_SUMMARY: t["pres_executive_summary"],
        PresentationType.INVESTOR_DECK: t["pres_investor_deck"],
        PresentationType.DETAILED_REPORT: t["pres_detailed_report"],
        PresentationType.STAKEHOLDER_BRIEF: t["pres_stakeholder_brief"],
        PresentationType.ANNUAL_REPORT: t["pres_annual_report"],
    }
    COVERS[style["cover"]](slide, theme, style, request, d.scores,
                           subtitle_map.get(request.presentation_type, t["pres_default"]), t)

    # Logo entreprise sur la couverture
    if logo_bytes:
        logo_pos = {
            "classic": (Inches(11.75), Inches(0.35)),
            "organic": (Inches(0.7), Inches(0.45)),
            "luxe": (Inches(6.17), Inches(0.55)),
            "minimal": (Inches(11.55), Inches(0.9)),
        }[style["cover"]]
        try:
            slide.shapes.add_picture(io.BytesIO(logo_bytes),
                                     logo_pos[0], logo_pos[1], height=Inches(1.0))
        except Exception:
            pass

    # Présentateur
    if request.company.presenter_name:
        line = f"{t['presented_by']} {request.company.presenter_name}"
        if request.company.presenter_title:
            line += f" — {request.company.presenter_title}"
        pres_y = Inches(6.9) if style["cover"] == "organic" else Inches(6.55)
        pres_align = PP_ALIGN.CENTER if style["cover"] == "luxe" else PP_ALIGN.LEFT
        pres_color = theme["muted"] if style["cover"] == "minimal" else theme["subtitle"]
        add_text(slide, line, Inches(0.7), pres_y, Inches(11.9), Inches(0.4),
                 font_size=12, italic=True, color=pres_color, font=d.fb, align=pres_align)


def _slide_cover_art(d: _Deck) -> None:
    """Illustration de couverture (générée localement)."""
    if "cover_art" not in d.charts:
        return
    theme, t, request = d.theme, d.t, d.request
    slide = d.new_slide()
    bg = theme["bg_primary"] if d.dark else theme["bg_secondary"]
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, bg)
    add_image_from_bytes(slide, d.charts["cover_art"], 0, 0, SLIDE_W, Inches(4.4))
    add_text(slide, maybe_upper(f"{t['pres_default']} {request.company.reporting_year}", d.style),
             Inches(0.7), Inches(4.9), Inches(11.9), Inches(0.9),
             font_size=32, bold=True, color=theme["text_dark"], font=d.ft)
    add_text(slide, f"{request.company.name}  •  {request.company.sector}",
             Inches(0.7), Inches(5.9), Inches(11.9), Inches(0.5),
             font_size=15, color=theme["muted"], font=d.fb)


def _slide_ceo_quote(d: _Deck) -> None:
    """Mot de la direction (citation pleine page)."""
    request = d.request
    if not request.company.ceo_quote:
        return
    theme, t = d.theme, d.t
    slide = d.new_slide()
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_primary"])
    add_bg_rect(slide, 0, SLIDE_H - Inches(0.12), SLIDE_W, Inches(0.12), theme["accent"])
    add_text(slide, t["quote_kicker"], Inches(0), Inches(1.0), SLIDE_W, Inches(0.45),
             font_size=13, bold=True, color=theme["accent"], align=PP_ALIGN.CENTER, font=d.fb)
    # Guillemet géant en filigrane
    add_text(slide, "“", Inches(0.9), Inches(1.0), Inches(3), Inches(2.5),
             font_size=160, bold=True, color=theme["card_bg"], font=d.ft)
    qt = request.company.ceo_quote.strip().strip('"“”')
    add_text(slide, f"« {qt} »" if request.language != "en" else f"“{qt}”",
             Inches(1.8), Inches(2.3), SLIDE_W - Inches(3.6), Inches(3.2),
             font_size=24, italic=True, color=theme["text_light"],
             align=PP_ALIGN.CENTER, font=d.ft)
    if request.company.presenter_name:
        attrib = request.company.presenter_name
        if request.company.presenter_title:
            attrib += f" — {request.company.presenter_title}"
        add_bg_rect(slide, SLIDE_W / 2 - Inches(0.75), Inches(5.7), Inches(1.5), Inches(0.04),
                    theme["accent"])
        add_text(slide, attrib, Inches(0), Inches(5.95), SLIDE_W, Inches(0.5),
                 font_size=14, bold=True, color=theme["subtitle"],
                 align=PP_ALIGN.CENTER, font=d.fb)


def _slide_contents(d: _Deck) -> None:
    """Sommaire : repère de lecture en trois actes."""
    theme, style, t, dark = d.theme, d.style, d.t, d.dark
    slide = d.new_slide()
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_primary"] if dark else theme["bg_secondary"])
    add_bg_rect(slide, 0, 0, Inches(0.14), SLIDE_H, theme["accent"])
    add_text(slide, t["toc_title"].upper(), Inches(0.65), Inches(0.55), Inches(8), Inches(0.8),
             font_size=36, bold=True, color=theme["text_dark"], font=d.ft)
    add_bg_rect(slide, Inches(0.7), Inches(1.45), Inches(1.8), Inches(0.06), theme["accent"])
    toc = [
        ("01", t["toc_part1"], [t["exec_title"], t["pillar_env"], t["pillar_soc"], t["pillar_gov"]]),
        ("02", t["toc_part2"], [t["benchmark_kicker"].title(), t["ro_kicker"].title(), t["strategic"]]),
        ("03", t["toc_part3"], [t["recommendations"], t["roadmap_title"], t["conclusion_title"]]),
    ]
    tw = Inches(3.95)
    for i, (num, act, items) in enumerate(toc):
        cx = Inches(0.65) + i * (tw + Inches(0.25))
        add_shape(slide, ROUNDED_RECT if style["card"] != "flat" else RECT,
                  cx, Inches(2.1), tw, Inches(4.6), fill=theme["card_bg"])
        add_text(slide, num, cx + Inches(0.35), Inches(2.35), Inches(2), Inches(0.9),
                 font_size=44, bold=True, color=theme["accent"], font=d.ft)
        add_text(slide, act.upper(), cx + Inches(0.35), Inches(3.35), tw - Inches(0.6), Inches(0.45),
                 font_size=15, bold=True, color=theme["text_dark"], font=d.fb)
        add_bg_rect(slide, cx + Inches(0.35), Inches(3.85), tw - Inches(0.7), Inches(0.02),
                    theme["accent"] if not dark else theme["muted"])
        for j, it in enumerate(items[:4]):
            add_text(slide, f"—  {it}", cx + Inches(0.35), Inches(4.05) + j * Inches(0.6),
                     tw - Inches(0.6), Inches(0.55), font_size=12,
                     color=theme["text_dark"] if not dark else theme["subtitle"], font=d.fb)


def _slide_dashboard(d: _Deck) -> None:
    """Tableau de bord : score global en héros, verdict, barres des piliers, radar."""
    import narrative as NR
    slide = d.new_slide()
    add_notes(slide, NR.company_paragraphs(d.request, d.ref))
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, d.theme["bg_primary"] if d.dark else d.theme["bg_secondary"])
    _dashboard_hero(d, slide)
    _dashboard_detail(d, slide)


def _dashboard_hero(d: _Deck, slide: Slide) -> None:
    """Colonne gauche : score global mis en scène (élément dominant)."""
    theme, t, request, scores = d.theme, d.t, d.request, d.scores
    white = RGBColor(0xFF, 0xFF, 0xFF)
    HP = Inches(4.75)
    add_bg_rect(slide, 0, 0, HP, SLIDE_H, theme["bg_primary"])
    add_bg_rect(slide, HP - Inches(0.08), 0, Inches(0.08), SLIDE_H, theme["accent"])
    add_text(slide, t["exec_kicker"].format(y=request.company.reporting_year),
             Inches(0.55), Inches(0.75), Inches(3.9), Inches(0.5),
             font_size=13, bold=True, color=theme["accent"], font=d.fb)
    add_text(slide, score_label(scores.total_esg_score), Inches(0.2), Inches(1.85), Inches(4.35), Inches(2.1),
             font_size=125, bold=True, color=white, align=PP_ALIGN.CENTER, font=d.ft)
    add_text(slide, "/ 100", Inches(0.2), Inches(3.95), Inches(4.35), Inches(0.55),
             font_size=22, color=theme["subtitle"], align=PP_ALIGN.CENTER, font=d.fb)
    # badge note
    add_shape(slide, ROUNDED_RECT, Inches(1.55), Inches(4.75), Inches(1.65), Inches(0.85), fill=theme["accent"])
    add_text(slide, scores.rating or NON_NOTE, Inches(1.55), Inches(4.9), Inches(1.65), Inches(0.6),
             font_size=30, bold=True, color=theme["bg_primary"], align=PP_ALIGN.CENTER, font=d.ft)
    add_text(slide, t["global_score_caption"], Inches(0.2), Inches(5.85), Inches(4.35), Inches(0.4),
             font_size=12, bold=True, color=theme["subtitle"], align=PP_ALIGN.CENTER, font=d.fb)
    # Évolution vs exercice précédent (dossier client multi-exercices)
    prev = getattr(request, "previous_scores", None)
    from content_generator import _ecart
    delta = _ecart(scores.total_esg_score, prev.get("total")) if prev else None
    if prev and delta is not None:
        dcolor = (RGBColor(0x4C, 0xAF, 0x50) if delta >= 0.5
                  else RGBColor(0xE7, 0x4C, 0x3C) if delta <= -0.5 else theme["subtitle"])
        dlabel = (f"+{delta:.0f} pts" if delta >= 0.5 else f"{delta:.0f} pts" if delta <= -0.5 else "=")
        add_text(slide, f"{dlabel}  vs {prev['year']}", Inches(0.2), Inches(6.3), Inches(4.35), Inches(0.4),
                 font_size=14, bold=True, color=dcolor, align=PP_ALIGN.CENTER, font=d.fb)


def _dashboard_detail(d: _Deck, slide: Slide) -> None:
    """Colonne droite : titre éditorial, verdict, barres des piliers, radar."""
    theme, t, scores, dark = d.theme, d.t, d.scores, d.dark
    RX = Inches(5.2)
    add_text(slide, t["exec_title"], RX, Inches(0.65), Inches(7.9), Inches(0.9),
             font_size=34, bold=True, color=theme["text_dark"], font=d.ft)
    add_bg_rect(slide, RX + Inches(0.03), Inches(1.62), Inches(1.6), Inches(0.06), theme["accent"])
    add_text(slide, d.verdict, RX, Inches(1.9), Inches(7.85), Inches(1.5),
             font_size=16, color=theme["text_dark"] if not dark else theme["subtitle"], font=d.fb)

    # ── Détail : barres piliers (gauche) + radar (droite) ───────────
    add_text(slide, t["pillars_caption"], RX, Inches(3.5), Inches(4), Inches(0.4),
             font_size=12, bold=True, color=theme["muted"], font=d.fb)
    bars = [(t["chart_env"], scores.environmental_score, theme["env"]),
            (t["chart_soc"], scores.social_score, theme["social"]),
            (t["chart_gov"], scores.governance_score, theme["gov"])]
    track = RGBColor(0x3A, 0x40, 0x4A) if dark else RGBColor(0xE2, 0xE8, 0xF0)
    bar_w = Inches(3.4)
    for i, (label, sc, col) in enumerate(bars):
        y = Inches(4.05) + i * Inches(0.92)
        add_text(slide, label, RX, y, Inches(3.4), Inches(0.32),
                 font_size=12.5, bold=True, color=theme["text_dark"], font=d.fb)
        add_text(slide, score_label(sc), RX + bar_w - Inches(0.6), y, Inches(0.6), Inches(0.32),
                 font_size=13, bold=True, color=col, align=PP_ALIGN.RIGHT, font=d.ft)
        add_shape(slide, ROUNDED_RECT, RX, y + Inches(0.36), bar_w, Inches(0.17), fill=track)
        if sc is not None:  # pilier non noté : piste vide et « — »
            fill_w = max(Inches(0.17), Inches(3.4) * max(0, min(100, sc)) / 100)
            add_shape(slide, ROUNDED_RECT, RX, y + Inches(0.36), fill_w, Inches(0.17), fill=col)

    if "radar" in d.charts:
        add_image_from_bytes(slide, d.charts["radar"],
                             Inches(9.15), Inches(3.55), height=Inches(3.55))


def _slide_consultant_note(d: _Deck) -> None:
    """L'analyse du consultant (note globale), si elle a été saisie."""
    notes = getattr(d.request, "consultant_notes", None) or {}
    if not notes.get("global"):
        return
    theme, t = d.theme, d.t
    slide = d.new_slide()
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_secondary"])
    add_bg_rect(slide, 0, 0, Inches(0.14), SLIDE_H, theme["accent"])
    add_text(slide, t["consultant_note"], Inches(0.7), Inches(0.8), Inches(11.9), Inches(0.5),
             font_size=14, bold=True, color=theme["accent"], font=d.fb)
    add_bg_rect(slide, Inches(0.75), Inches(1.45), Inches(1.8), Inches(0.05), theme["accent"])
    add_text(slide, notes["global"], Inches(0.75), Inches(2.0), Inches(11.8), Inches(4.6),
             font_size=19, italic=True, color=theme["text_dark"], font=d.ft)
    if d.request.company.presenter_name:
        add_text(slide, d.request.company.presenter_name, Inches(0.75), Inches(6.6),
                 Inches(11.8), Inches(0.4), font_size=12, bold=True,
                 color=theme["muted"], font=d.fb)


def _slide_positioning(d: _Deck) -> None:
    """Positionnement interne des piliers + échelle de maturité."""
    if "benchmark" not in d.charts:
        return
    from content_generator import benchmark_verdict, maturity_text
    bv = benchmark_verdict(d.request, d.scores)
    if bv is None:  # moins de deux piliers notés : rien à positionner
        return
    mat = maturity_text(d.request, d.scores)
    theme, t, dark = d.theme, d.t, d.dark
    slide = d.content_slide(bv["title"], kicker=t["benchmark_kicker"])
    add_image_from_bytes(slide, d.charts["benchmark"],
                         Inches(0.35), Inches(1.7), width=Inches(7.5))
    # Carte lecture métier (positionnement)
    cx, cw = Inches(8.15), Inches(4.85)
    add_shape(slide, ROUNDED_RECT, cx, Inches(1.75), cw, Inches(2.35),
              fill=theme["card_bg"], line_color=theme["accent"], line_width_pt=1.25)
    add_shape(slide, RECT, cx, Inches(1.75), Inches(0.09), Inches(2.35), fill=theme["accent"])
    add_text(slide, t["key_takeaway"], cx + Inches(0.3), Inches(1.93), cw - Inches(0.5), Inches(0.35),
             font_size=12, bold=True, color=theme["accent"] if not dark else theme["text_dark"], font=d.fb)
    add_text(slide, bv["insight"], cx + Inches(0.3), Inches(2.35), cw - Inches(0.55), Inches(1.7),
             font_size=14, color=theme["text_dark"], font=d.fb)
    # Échelle de maturité ESG (5 stades)
    add_text(slide, t["maturity_title"], cx + Inches(0.02), Inches(4.4), cw, Inches(0.35),
             font_size=12, bold=True, color=theme["muted"], font=d.fb)
    stages = [t["mat_initiated"], t["mat_structuring"], t["mat_structured"], t["mat_advanced"], t["mat_exemplary"]]
    seg_w = Inches(0.92); seg_h = Inches(0.5); gap = Inches(0.06)
    for i, st in enumerate(stages):
        sx = cx + i * (seg_w + gap)
        active = (i == mat["stage"])
        fill = theme["accent"] if active else theme["card_bg"]
        add_shape(slide, ROUNDED_RECT, sx, Inches(4.85), seg_w, seg_h,
                  fill=fill, line_color=theme["accent"] if not active else fill, line_width_pt=1.0)
        add_text(slide, str(i + 1), sx, Inches(4.9), seg_w, Inches(0.4),
                 font_size=14, bold=True, align=PP_ALIGN.CENTER,
                 color=(theme["bg_primary"] if active else theme["muted"]), font=d.ft)
    add_text(slide, stages[mat["stage"]], cx, Inches(5.5), cw, Inches(0.4),
             font_size=16, bold=True, color=theme["accent"] if not dark else theme["text_dark"], font=d.ft)
    add_text(slide, mat["next_hint"], cx, Inches(5.95), cw, Inches(0.7),
             font_size=12.5, color=theme["text_dark"], font=d.fb)


def _slide_trend(d: _Deck) -> None:
    """Trajectoire pluriannuelle, si le dossier client a un historique."""
    if "trend" not in d.charts:
        return
    slide = d.content_slide(d.t["trend_title"], kicker=d.t["trend_kicker"])
    add_image_from_bytes(slide, d.charts["trend"],
                         Inches(1.3), Inches(1.6), width=Inches(10.7))
    add_text(slide, d.t["cap_trend"], Inches(1.3), Inches(6.9), Inches(10.7), Inches(0.35),
             font_size=10, italic=True, color=d.theme["muted"], font=d.fb)


def _slide_coverage(d: _Deck) -> None:
    """Couverture des exigences de reporting (statuts : gap_status, source unique)."""
    if not d.gaps:
        return
    import gap_status as GS
    theme, t, dark = d.theme, d.t, d.dark
    slide = d.content_slide(t["gap_title"], kicker=t["benchmark_kicker"])
    row_h = Inches(0.68)
    for i, g in enumerate(d.gaps[:8]):
        gy = Inches(1.45) + i * row_h
        if i % 2 == 0:
            add_bg_rect(slide, Inches(0.3), gy, Inches(12.73), row_h, theme["card_bg"])
        add_text(slide, g["req"], Inches(0.5), gy + Inches(0.07), Inches(5.3), Inches(0.55),
                 font_size=12.5, bold=True, color=theme["text_dark"], font=d.fb)
        add_text(slide, g["ref"], Inches(5.85), gy + Inches(0.16), Inches(1.9), Inches(0.4),
                 font_size=10, color=theme["muted"], font=d.fb)
        chip_w = Inches(1.75)
        add_shape(slide, ROUNDED_RECT, Inches(7.85), gy + Inches(0.14), chip_w, Inches(0.4),
                  fill=RGBColor(*GS.rgb_triplet(g["status"], g["nature"])))
        add_text(slide, GS.libelle(t, g["status"], g["nature"]), Inches(7.85), gy + Inches(0.2), chip_w, Inches(0.3),
                 font_size=10.5, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF),
                 align=PP_ALIGN.CENTER, font=d.fb)
        add_text(slide, g["note"], Inches(9.8), gy + Inches(0.07), Inches(3.2), Inches(0.58),
                 font_size=10, color=theme["text_dark"] if not dark else theme["subtitle"], font=d.fb)


def _slide_hero_stat(d: _Deck) -> None:
    """Chiffre-choc : ancrage visuel de la présentation."""
    from content_generator import hero_stat
    hs = hero_stat(d.request, d.scores)
    theme = d.theme
    slide = d.new_slide()
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_primary"])
    add_bg_rect(slide, 0, 0, SLIDE_W, Inches(0.12), theme["accent"])
    # Chiffre géant centré + unité
    add_text(slide, hs["value"], Inches(0), Inches(1.7), SLIDE_W, Inches(2.9),
             font_size=230, bold=True, color=theme["accent"], align=PP_ALIGN.CENTER, font=d.ft)
    add_text(slide, hs["unit"], Inches(0), Inches(4.55), SLIDE_W, Inches(0.7),
             font_size=34, bold=True, color=theme["text_light"], align=PP_ALIGN.CENTER, font=d.fb)
    # Libellé du chiffre
    add_text(slide, hs["label"], Inches(1.5), Inches(5.35), SLIDE_W - Inches(3), Inches(0.6),
             font_size=20, color=theme["subtitle"], align=PP_ALIGN.CENTER, font=d.fb)
    # Trait + phrase éditoriale
    add_bg_rect(slide, SLIDE_W / 2 - Inches(0.9), Inches(6.15), Inches(1.8), Inches(0.05), theme["accent"])
    add_text(slide, hs["statement"], Inches(1.8), Inches(6.4), SLIDE_W - Inches(3.6), Inches(0.8),
             font_size=16, italic=True, color=theme["text_light"], align=PP_ALIGN.CENTER, font=d.fb)


def _env_kpis(env, k: dict) -> list:
    kpis = []
    if env.co2_emissions_tonnes is not None:
        kpis.append(("cloud", f"{env.co2_emissions_tonnes:,.0f} t", k["co2_total"]))
    if env.renewable_energy_percent is not None:
        kpis.append(("recycle", f"{env.renewable_energy_percent:.0f}%", k["renewable"]))
    if env.energy_consumption_mwh is not None:
        kpis.append(("bolt", f"{env.energy_consumption_mwh:,.0f}", k["energy"]))
    if env.water_consumption_m3 is not None:
        kpis.append(("drop", f"{env.water_consumption_m3:,.0f}", k["water"]))
    if env.waste_recycled_percent is not None:
        kpis.append(("leaf", f"{env.waste_recycled_percent:.0f}%", k["recycling"]))
    if env.biodiversity_initiatives is not None:
        kpis.append(("tree", f"{env.biodiversity_initiatives}", k["biodiversity"]))
    if env.scope3_emissions is not None:
        kpis.append(("cloud", f"{env.scope3_emissions:,.0f} t", k["scope3"]))
    if env.waste_generated_tonnes is not None:
        kpis.append(("recycle", f"{env.waste_generated_tonnes:,.0f} t", k["waste"]))
    return kpis


def _social_kpis(soc, k: dict) -> list:
    kpis = []
    if soc.total_employees is not None:
        kpis.append(("people", f"{soc.total_employees:,}", k["employees"]))
    if soc.female_employees_percent is not None:
        kpis.append(("people", f"{soc.female_employees_percent:.0f}%", k["women_workforce"]))
    if soc.training_hours_per_employee is not None:
        kpis.append(("cap", f"{soc.training_hours_per_employee:.0f} h", k["training"]))
    if soc.accident_frequency_rate is not None:
        kpis.append(("shield", f"{soc.accident_frequency_rate:.1f}", k["accident_rate"]))
    if soc.customer_satisfaction_score is not None:
        kpis.append(("heart", f"{soc.customer_satisfaction_score:.1f}/10", k["satisfaction"]))
    if soc.employee_turnover_percent is not None:
        kpis.append(("chart", f"{soc.employee_turnover_percent:.0f}%", k["turnover"]))
    if soc.disabled_employees_percent is not None:
        kpis.append(("heart", f"{soc.disabled_employees_percent:.1f}%", k["disabled"]))
    if soc.community_investment_eur is not None:
        kpis.append(("heart", f"{soc.community_investment_eur:,.0f} €", k["community"]))
    return kpis


def _gov_kpis(gov, k: dict) -> list:
    kpis = []
    if gov.board_members is not None:
        kpis.append(("columns", f"{gov.board_members}", k["board"]))
    if gov.female_board_percent is not None:
        kpis.append(("people", f"{gov.female_board_percent:.0f}%", k["women_board"]))
    if gov.independent_board_percent is not None:
        kpis.append(("badge", f"{gov.independent_board_percent:.0f}%", k["independent"]))
    if gov.esg_audit_conducted is not None:
        kpis.append(("badge", k["yes"] if gov.esg_audit_conducted else k["no"], k["audit"]))
    if gov.data_breaches is not None:
        kpis.append(("lock", f"{gov.data_breaches}", k["breaches"]))
    if gov.ethics_violations is not None:
        kpis.append(("scale", f"{gov.ethics_violations}", k["ethics"]))
    if gov.csr_budget_eur is not None:
        kpis.append(("chart", f"{gov.csr_budget_eur:,.0f} €", k["csr_budget"]))
    if gov.sustainability_committee is not None:
        kpis.append(("columns", k["yes"] if gov.sustainability_committee else k["no"], k["committee"]))
    if gov.corruption_cases is not None:
        kpis.append(("scale", f"{gov.corruption_cases}", k["corruption"]))
    return kpis


# Pilier -> (clé des libellés, attribut du score, extracteur des indicateurs)
_PILLARS = {
    "env": ("pillar_env", "environmental_score", _env_kpis),
    "social": ("pillar_soc", "social_score", _social_kpis),
    "gov": ("pillar_gov", "governance_score", _gov_kpis),
}


def _slide_pillar(d: _Deck, pillar: str) -> None:
    """Infographie d'un pilier ; le texte analytique du rapport en notes."""
    import narrative as NR
    label_key, score_attr, kpis_of = _PILLARS[pillar]
    data = {"env": d.request.environmental, "social": d.request.social,
            "gov": d.request.governance}[pillar]
    pillar_infographic(d.prs, d.layout, d.theme, d.style, pillar,
                       d.t[label_key], d.headlines[pillar],
                       getattr(d.scores, score_attr), kpis_of(data, d.t["kpi"]), d.t,
                       d.insights[pillar])
    paras = NR.pillar_paragraphs(d.request, d.scores, pillar)
    if d.request.include_recommendations:
        paras.append(NR.levers_sentence(d.request, d.recs, pillar))
    extra = NR.ghg_paragraph(d.request) if pillar == "env" else None
    add_notes(d.prs.slides[-1], paras + ([extra] if extra else []))


def _slide_materiality(d: _Deck) -> None:
    """Priorisation des enjeux (graphique + lecture métier)."""
    if "materiality" not in d.charts:
        return
    theme, t, dark = d.theme, d.t, d.dark
    slide = d.content_slide(d.section_heads["materiality"], kicker=t["materiality_title"])
    # Graphique (numéros + légende) à gauche
    add_image_from_bytes(slide, d.charts["materiality"],
                         Inches(0.35), Inches(1.75), height=Inches(4.9))
    # Carte « lecture métier » à droite
    cx, cw = Inches(9.35), Inches(3.65)
    add_shape(slide, ROUNDED_RECT, cx, Inches(2.0), cw, Inches(4.4),
              fill=theme["card_bg"], line_color=theme["accent"], line_width_pt=1.25)
    add_shape(slide, RECT, cx, Inches(2.0), Inches(0.09), Inches(4.4), fill=theme["accent"])
    add_text(slide, t["key_takeaway"], cx + Inches(0.3), Inches(2.2), cw - Inches(0.5), Inches(0.4),
             font_size=12, bold=True, color=theme["accent"] if not dark else theme["text_dark"], font=d.fb)
    add_text(slide, t["materiality_desc"], cx + Inches(0.3), Inches(2.7), cw - Inches(0.55), Inches(3.5),
             font_size=13.5, color=theme["text_dark"], font=d.fb)


# (supprimee) SLIDE « Objectifs & trajectoire » : son chiffre-choc etait
# « -42 % » (constante) ou une moyenne de cibles par pilier fabriquees
# (score + 15 / +10 / +5). Rien n'y venait du client. Voir esg_advanced.py.


def _slide_taxonomy(d: _Deck) -> None:
    """Taxonomie UE : part alignée dominante + graphique."""
    if "taxonomy" not in d.charts:
        return
    theme, t = d.theme, d.t
    slide = d.content_slide(d.section_heads["taxonomy"], kicker=t["taxonomy_title"])
    tx = d.request.taxonomy
    vals = [v for v in (tx.turnover_aligned_percent, tx.capex_aligned_percent,
                        tx.opex_aligned_percent) if v is not None]
    top = max(vals) if vals else 0
    add_text(slide, f"{top:.0f}%", Inches(0.45), Inches(1.7), Inches(5.4), Inches(1.9),
             font_size=96, bold=True, color=theme["env"], font=d.ft)
    add_text(slide, t["tax_kpi_cap"], Inches(0.6), Inches(3.75), Inches(5.3), Inches(0.9),
             font_size=15, bold=True, color=theme["text_dark"], font=d.fb)
    add_shape(slide, ROUNDED_RECT, Inches(0.55), Inches(4.7), Inches(5.35), Inches(2.3),
              fill=theme["card_bg"], line_color=theme["env"], line_width_pt=1.25)
    add_shape(slide, RECT, Inches(0.55), Inches(4.7), Inches(0.09), Inches(2.3), fill=theme["env"])
    add_text(slide, t["key_takeaway"], Inches(0.85), Inches(4.88), Inches(4.8), Inches(0.4),
             font_size=11.5, bold=True, color=theme["env"], font=d.fb)
    add_text(slide, t["tax_insight"], Inches(0.85), Inches(5.28), Inches(4.85), Inches(1.6),
             font_size=13, color=theme["text_dark"], font=d.fb)
    add_image_from_bytes(slide, d.charts["taxonomy"],
                         Inches(6.3), Inches(2.5), width=Inches(6.7))


def _slide_strategic(d: _Deck) -> None:
    """Analyse stratégique : points solides / à progresser."""
    import narrative as NR
    theme, t, request, scores, dark = d.theme, d.t, d.request, d.scores, d.dark
    slide = d.content_slide(d.section_heads["strategic"], kicker=t["strategic"])
    add_notes(slide, [NR.act1_intro(request, scores, d.gaps, d.ro["risks"]), NR.bench_intro(request),
                      NR.gaps_intro(request, d.gaps, d.ref)])
    red = RGBColor(0xE7, 0x4C, 0x3C)
    panel_shape = ROUNDED_RECT if d.style["card"] != "flat" else RECT
    for (px, pw, ptitle, pcolor, items) in [
        (Inches(0.3), Inches(6.2), t["strengths"], theme["env"], scores.strengths),
        (Inches(6.83), Inches(6.2), t["weaknesses"], red, scores.weaknesses),
    ]:
        # Panneau
        add_shape(slide, panel_shape, px, Inches(1.25), pw, Inches(5.75), fill=theme["card_bg"],
                  line_color=pcolor, line_width_pt=1.0)
        # En-tête chiffré : gros compte + libellé
        add_text(slide, f"{len(items)}", px + Inches(0.3), Inches(1.45), Inches(1.3), Inches(1.0),
                 font_size=46, bold=True, color=pcolor, font=d.ft)
        add_text(slide, ptitle.upper(), px + Inches(1.45), Inches(1.72), pw - Inches(1.6), Inches(0.7),
                 font_size=15, bold=True, color=theme["text_dark"], font=d.fb)
        add_bg_rect(slide, px + Inches(0.3), Inches(2.65), pw - Inches(0.6), Inches(0.02),
                    pcolor if not dark else theme["muted"])
        # Items : marqueur coloré + texte
        for i, item in enumerate(items[:5]):
            iy = Inches(2.95) + i * Inches(0.78)
            add_shape(slide, OVAL, px + Inches(0.32), iy + Inches(0.08), Inches(0.16), Inches(0.16), fill=pcolor)
            add_text(slide, item, px + Inches(0.68), iy, pw - Inches(0.95), Inches(0.72),
                     font_size=12.5, color=theme["text_dark"], font=d.fb)


def _slide_risks(d: _Deck) -> None:
    """Risques & opportunités majeurs (deux colonnes, risques cotés P1-P3)."""
    import narrative as NR
    ro = d.ro
    if not (ro["risks"] or ro["opportunities"]):
        return
    theme, t, dark = d.theme, d.t, d.dark
    slide = d.content_slide(t["ro_title"], kicker=t["ro_kicker"])
    add_notes(slide, [NR.risks_intro(d.request, ro["risks"])])
    red = RGBColor(0xE7, 0x4C, 0x3C)
    for (px, pw, phead, pcolor, sign, items) in [
        (Inches(0.3), Inches(6.2), t["risks_head"], red, "!", ro["risks"]),
        (Inches(6.83), Inches(6.2), t["opps_head"], theme["env"], "+", ro["opportunities"]),
    ]:
        _risk_column(d, slide, px, pw, phead, pcolor, sign, items)


def _risk_column(d: _Deck, slide: Slide, px: float, pw: float, phead: str,
                 pcolor: RGBColor, sign: str, items: list) -> None:
    """Un panneau (risques ou opportunités) : en-tête, puis quatre items au plus."""
    theme, dark = d.theme, d.dark
    panel_shape = ROUNDED_RECT if d.style["card"] != "flat" else RECT
    add_shape(slide, panel_shape, px, Inches(1.25), pw, Inches(5.75), fill=theme["card_bg"],
              line_color=pcolor, line_width_pt=1.0)
    # bandeau d'en-tête
    add_shape(slide, OVAL, px + Inches(0.3), Inches(1.5), Inches(0.62), Inches(0.62), fill=pcolor)
    add_text(slide, sign, px + Inches(0.3), Inches(1.54), Inches(0.62), Inches(0.55),
             font_size=26, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF), align=PP_ALIGN.CENTER, font=d.ft)
    add_text(slide, phead.upper(), px + Inches(1.05), Inches(1.62), pw - Inches(1.2), Inches(0.6),
             font_size=16, bold=True, color=theme["text_dark"], font=d.fb)
    add_bg_rect(slide, px + Inches(0.3), Inches(2.4), pw - Inches(0.6), Inches(0.02),
                pcolor if not dark else theme["muted"])
    for i, item in enumerate(items[:4]):
        iy = Inches(2.7) + i * Inches(1.05)
        # tag catégorie
        tag = item["tag"]
        tag_w = Inches(0.28) + Inches(0.11) * len(tag)
        add_shape(slide, ROUNDED_RECT, px + Inches(0.3), iy, tag_w, Inches(0.3), fill=pcolor)
        add_text(slide, tag, px + Inches(0.3), iy + Inches(0.02), tag_w, Inches(0.26),
                 font_size=9.5, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF),
                 align=PP_ALIGN.CENTER, font=d.fb)
        # chip de priorité (risques cotés P1-P3)
        if item.get("priority"):
            pc = {"P1": RGBColor(0xE7, 0x4C, 0x3C), "P2": RGBColor(0xD9, 0x77, 0x06),
                  "P3": RGBColor(0x7F, 0x8C, 0x8D)}[item["priority"]]
            add_shape(slide, OVAL, px + pw - Inches(0.75), iy, Inches(0.42), Inches(0.3), fill=pc)
            add_text(slide, item["priority"], px + pw - Inches(0.75), iy + Inches(0.03),
                     Inches(0.42), Inches(0.24), font_size=9.5, bold=True,
                     color=RGBColor(0xFF, 0xFF, 0xFF), align=PP_ALIGN.CENTER, font=d.fb)
        add_text(slide, item["text"], px + Inches(0.3), iy + Inches(0.38), pw - Inches(0.6), Inches(0.6),
                 font_size=12.5, color=theme["text_dark"], font=d.fb)


def _slide_priority_matrix(d: _Deck) -> None:
    """Matrice de priorisation effort/impact + lecture."""
    if "priority" not in d.charts:
        return
    from content_generator import priority_reading
    reading = priority_reading(d.request, d.scores)
    theme, t, dark = d.theme, d.t, d.dark
    slide = d.content_slide(t["prio_title"], kicker=t["prio_kicker"])
    add_image_from_bytes(slide, d.charts["priority"],
                         Inches(0.35), Inches(1.6), width=Inches(9.2))
    # Carte lecture métier à droite
    cx, cw = Inches(9.75), Inches(3.25)
    add_shape(slide, ROUNDED_RECT, cx, Inches(1.75), cw, Inches(4.6),
              fill=theme["card_bg"], line_color=theme["accent"], line_width_pt=1.25)
    add_shape(slide, RECT, cx, Inches(1.75), Inches(0.09), Inches(4.6), fill=theme["accent"])
    add_text(slide, t["key_takeaway"], cx + Inches(0.28), Inches(1.95), cw - Inches(0.5), Inches(0.35),
             font_size=12, bold=True, color=theme["accent"] if not dark else theme["text_dark"], font=d.fb)
    add_text(slide, reading, cx + Inches(0.28), Inches(2.4), cw - Inches(0.5), Inches(3.8),
             font_size=13, color=theme["text_dark"], font=d.fb)


def _slide_recommendations(d: _Deck) -> None:
    """Recommandations : cartes pleine largeur (numéro, titre, détail, horizon)."""
    if not d.request.include_recommendations:
        return
    import narrative as NR
    theme, t = d.theme, d.t
    recs = d.recs[:5]
    slide = d.content_slide(t["recommendations"])
    add_notes(slide, [NR.act2_intro(d.request, d.recs, d.roadmap), NR.recs_intro(d.request, d.recs)])
    add_text(slide, t["rec_intro"], Inches(0.6), Inches(1.2), Inches(12.1), Inches(0.5),
             font_size=13, color=theme["muted"], font=d.fb)

    n = len(recs)
    top0 = Inches(1.95)
    row_h = min(Inches(1.02), (Inches(5.15) - (n - 1) * Inches(0.14)) / max(1, n))
    panel_shape = ROUNDED_RECT if d.style["card"] == "rounded" else RECT
    for i, rec in enumerate(recs):
        pcolor = theme[rec["pillar"]]
        y = top0 + i * (row_h + Inches(0.14))
        # carte
        add_shape(slide, panel_shape, Inches(0.6), y, Inches(12.1), row_h,
                  fill=theme["card_bg"], line_color=pcolor, line_width_pt=1.25)
        # pastille numéro colorée
        add_shape(slide, OVAL, Inches(0.85), y + Inches(0.24), Inches(0.55), Inches(0.55), fill=pcolor)
        add_text(slide, str(i + 1), Inches(0.85), y + Inches(0.30), Inches(0.55), Inches(0.45),
                 font_size=18, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF), align=PP_ALIGN.CENTER, font=d.ft)
        # titre + détail
        add_text(slide, rec["title"], Inches(1.65), y + Inches(0.12), Inches(8.7), Inches(0.45),
                 font_size=15, bold=True, color=theme["text_dark"], font=d.ft)
        detail = rec["detail"]
        if rec.get("owner"):
            detail = f'{detail}  —  {rec["owner"]}'
        add_text(slide, detail, Inches(1.65), y + Inches(0.55), Inches(9.2), Inches(0.5),
                 font_size=11, color=theme["muted"], font=d.fb)
        # chip horizon
        chip_w = Inches(1.7)
        add_shape(slide, ROUNDED_RECT, Inches(10.75), y + Inches(0.28), chip_w, Inches(0.46), fill=pcolor)
        add_text(slide, rec["horizon"], Inches(10.75), y + Inches(0.35), chip_w, Inches(0.35),
                 font_size=11, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF), align=PP_ALIGN.CENTER, font=d.fb)


def _slide_roadmap(d: _Deck) -> None:
    """Feuille de route 12 mois : trois phases en colonnes."""
    if not any(ph["actions"] for ph in d.roadmap):
        return
    import narrative as NR
    theme, t, dark = d.theme, d.t, d.dark
    slide = d.content_slide(t["roadmap_title"], kicker=t["roadmap_kicker"])
    add_notes(slide, [NR.roadmap_intro(d.request, d.roadmap)])
    col_w, gap = Inches(4.05), Inches(0.28)
    x0 = Inches(0.35)
    for pi, ph in enumerate(d.roadmap):
        cx = x0 + pi * (col_w + gap)
        # En-tête de phase
        add_shape(slide, ROUNDED_RECT, cx, Inches(1.5), col_w, Inches(0.9),
                  fill=theme["bg_primary"] if not dark else theme["card_bg"])
        add_text(slide, ph["label"], cx + Inches(0.25), Inches(1.6), col_w - Inches(0.5), Inches(0.45),
                 font_size=19, bold=True, color=theme["accent"], font=d.ft)
        add_text(slide, ph["sub"], cx + Inches(0.25), Inches(2.05), col_w - Inches(0.5), Inches(0.35),
                 font_size=11, color=theme["subtitle"] if not dark else theme["muted"], font=d.fb)
        # Actions
        for ai, act in enumerate(ph["actions"][:4]):
            ay = Inches(2.6) + ai * Inches(1.02)
            pcol = theme[act["pillar"]]
            add_shape(slide, ROUNDED_RECT, cx, ay, col_w, Inches(0.9),
                      fill=theme["card_bg"], line_color=pcol, line_width_pt=1.0)
            add_shape(slide, RECT, cx, ay + Inches(0.12), Inches(0.07), Inches(0.66), fill=pcol)
            add_text(slide, act["title"], cx + Inches(0.28), ay + Inches(0.12), col_w - Inches(0.45), Inches(0.6),
                     font_size=12, bold=True, color=theme["text_dark"], font=d.fb)
            if act["quick_win"]:
                qw_w = Inches(1.15)
                add_shape(slide, ROUNDED_RECT, cx + col_w - qw_w - Inches(0.12), ay + Inches(0.58),
                          qw_w, Inches(0.26), fill=theme["accent"])
                add_text(slide, t["quick_win"], cx + col_w - qw_w - Inches(0.12), ay + Inches(0.6),
                         qw_w, Inches(0.22), font_size=8.5, bold=True,
                         color=theme["bg_primary"], align=PP_ALIGN.CENTER, font=d.fb)


# (supprimee) SLIDE « Alignement — ODD & Cadres de Reference » : elle
# affichait six ODD identiques pour tout dossier et une liste de cadres
# en dur (GRI, TCFD, CSRD, SFDR, ISO 14001/26000), sans qu'aucune donnee
# ne les fonde. SFDR ne vise pas les entreprises non financieres et
# ISO 26000 n'est pas certifiable. Verifie le 2026-09-03.


def _slide_conclusion(d: _Deck) -> None:
    """Clôture éditoriale : verdict + trois engagements prioritaires."""
    theme, t, request = d.theme, d.t, d.request
    commitments = d.all_recs[:3]
    slide = d.new_slide()
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_primary"])
    add_bg_rect(slide, 0, 0, Inches(0.18), SLIDE_H, theme["accent"])
    tl_color, sub_color = theme["text_light"], theme["subtitle"]

    add_text(slide, maybe_upper(t["conclusion_title"], d.style), Inches(0.65), Inches(0.7),
             Inches(11.5), Inches(0.9), font_size=30, bold=True, color=tl_color, font=d.ft)
    add_bg_rect(slide, Inches(0.68), Inches(1.62), Inches(1.8), Inches(0.06), theme["accent"])
    # Synthèse en grand (l'idée qui reste)
    add_text(slide, d.verdict, Inches(0.65), Inches(1.95), Inches(12.0), Inches(1.3),
             font_size=20, bold=True, color=tl_color, font=d.ft)

    # Engagements prioritaires (les prochaines étapes)
    add_text(slide, t["commitments"], Inches(0.65), Inches(3.55), Inches(8), Inches(0.4),
             font_size=13, bold=True, color=theme["accent"], font=d.fb)
    for i, eng in enumerate(commitments):
        y = Inches(4.15) + i * Inches(0.86)
        add_text(slide, f"{i + 1:02d}", Inches(0.65), y, Inches(0.9), Inches(0.7),
                 font_size=30, bold=True, color=theme["accent"], font=d.ft)
        add_text(slide, eng["title"], Inches(1.7), y + Inches(0.05), Inches(9.0), Inches(0.5),
                 font_size=16, bold=True, color=tl_color, font=d.fb)
        add_text(slide, eng["horizon"], Inches(10.9), y + Inches(0.08), Inches(1.9), Inches(0.4),
                 font_size=13, bold=True, color=sub_color, align=PP_ALIGN.RIGHT, font=d.fb)
        if i < len(commitments) - 1:
            add_bg_rect(slide, Inches(1.7), y + Inches(0.72), Inches(11.1), Inches(0.012),
                        RGBColor(0x55, 0x5B, 0x6B) if not d.dark else theme["card_bg"])

    add_text(slide, f"© {request.company.reporting_year} {request.company.name} — " + t["confidential"],
             Inches(0.65), Inches(7.0), Inches(11), Inches(0.4),
             font_size=9, italic=True, color=sub_color, font=d.fb)


def _folio(d: _Deck) -> None:
    """Foliotage discret sur toutes les diapositives sauf la couverture."""
    n_slides = len(d.prs.slides._sldIdLst)
    for idx, sl in enumerate(d.prs.slides):
        if idx == 0:
            continue
        add_text(sl, f"{d.request.company.name}   |   {idx + 1} / {n_slides}",
                 Inches(9.6), Inches(7.15), Inches(3.5), Inches(0.3),
                 font_size=8, color=d.theme["muted"], align=PP_ALIGN.RIGHT, font=d.fb)


def generate_pptx(request: ESGRequest, scores: ESGScores, content: dict,
                  chart_images: dict, logo_bytes: bytes | None = None) -> bytes:
    """Présentation de direction, dans l'ordre de lecture : ouverture, acte 1
    (diagnostic), acte 2 (plan d'action), clôture. Chaque diapositive est une
    fonction ; celles qui dépendent d'une donnée absente ne s'ajoutent pas."""
    d = _deck(request, scores, chart_images)
    t = d.t
    _slide_cover(d, logo_bytes)
    _slide_cover_art(d)
    _slide_ceo_quote(d)
    _slide_contents(d)
    _slide_dashboard(d)
    _slide_consultant_note(d)
    d.divider("01", t["div1_title"], t["div1_sub"])
    _slide_positioning(d)
    _slide_trend(d)
    _slide_coverage(d)
    _slide_hero_stat(d)
    for pillar in ("env", "social", "gov"):
        _slide_pillar(d, pillar)
    _slide_materiality(d)
    _slide_taxonomy(d)
    _slide_strategic(d)
    _slide_risks(d)
    d.divider("02", t["div2_title"], t["div2_sub"])
    _slide_priority_matrix(d)
    _slide_recommendations(d)
    _slide_roadmap(d)
    _slide_conclusion(d)
    _folio(d)

    buf = io.BytesIO()
    from typo import fix_pptx
    fix_pptx(d.prs, request.language)  # nombres à la française (typo.py)
    d.prs.save(buf)
    buf.seek(0)
    return buf.read()
