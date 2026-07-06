import io
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
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
        "muted": RGBColor(0x6B, 0x7C, 0x93),
        "card_bg": RGBColor(0xEB, 0xF2, 0xFB),
    },
    AestheticTheme.GREEN_NATURE: {
        "bg_primary": RGBColor(0x1A, 0x5C, 0x38),
        "bg_secondary": RGBColor(0xF3, 0xFB, 0xF5),
        "accent": RGBColor(0xF1, 0xC4, 0x0F),
        "env": RGBColor(0x2E, 0xCC, 0x71),
        "social": RGBColor(0x34, 0x98, 0xDB),
        "gov": RGBColor(0xE6, 0x7E, 0x22),
        "text_light": RGBColor(0xFF, 0xFF, 0xFF),
        "text_dark": RGBColor(0x1A, 0x33, 0x25),
        "subtitle": RGBColor(0xA9, 0xDB, 0xBC),
        "muted": RGBColor(0x5E, 0x8C, 0x72),
        "card_bg": RGBColor(0xDD, 0xF3, 0xE4),
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
        "subtitle": RGBColor(0x8B, 0x94, 0x9E),
        "muted": RGBColor(0x8B, 0x94, 0x9E),
        "card_bg": RGBColor(0x1F, 0x25, 0x2E),
    },
    AestheticTheme.MINIMAL_WHITE: {
        "bg_primary": RGBColor(0x21, 0x21, 0x21),
        "bg_secondary": RGBColor(0xFF, 0xFF, 0xFF),
        "accent": RGBColor(0xFF, 0x6F, 0x00),
        "env": RGBColor(0x43, 0xA0, 0x47),
        "social": RGBColor(0x1E, 0x88, 0xE5),
        "gov": RGBColor(0x8E, 0x24, 0xAA),
        "text_light": RGBColor(0xFF, 0xFF, 0xFF),
        "text_dark": RGBColor(0x21, 0x21, 0x21),
        "subtitle": RGBColor(0x9E, 0x9E, 0x9E),
        "muted": RGBColor(0x9E, 0x9E, 0x9E),
        "card_bg": RGBColor(0xFF, 0xFF, 0xFF),
    },
    AestheticTheme.SUNSET_TERRACOTTA: {
        "bg_primary": RGBColor(0x9A, 0x34, 0x12),
        "bg_secondary": RGBColor(0xFD, 0xF3, 0xEC),
        "accent": RGBColor(0xF4, 0xA2, 0x61),
        "env": RGBColor(0x2A, 0x9D, 0x8F),
        "social": RGBColor(0xE7, 0x6F, 0x51),
        "gov": RGBColor(0x6D, 0x59, 0x7A),
        "text_light": RGBColor(0xFF, 0xFF, 0xFF),
        "text_dark": RGBColor(0x4A, 0x2C, 0x22),
        "subtitle": RGBColor(0xF2, 0xC9, 0xB0),
        "muted": RGBColor(0xA8, 0x70, 0x5F),
        "card_bg": RGBColor(0xFA, 0xE5, 0xD8),
    },
    AestheticTheme.OCEAN_DEEP: {
        "bg_primary": RGBColor(0x0F, 0x4C, 0x5C),
        "bg_secondary": RGBColor(0xEF, 0xF9, 0xFB),
        "accent": RGBColor(0x00, 0xBF, 0xA6),
        "env": RGBColor(0x43, 0xAA, 0x8B),
        "social": RGBColor(0x27, 0x7D, 0xA1),
        "gov": RGBColor(0x57, 0x75, 0x90),
        "text_light": RGBColor(0xFF, 0xFF, 0xFF),
        "text_dark": RGBColor(0x12, 0x3B, 0x44),
        "subtitle": RGBColor(0xA8, 0xD8, 0xE0),
        "muted": RGBColor(0x5C, 0x8A, 0x96),
        "card_bg": RGBColor(0xDC, 0xF1, 0xF5),
    },
    AestheticTheme.ROYAL_PURPLE: {
        "bg_primary": RGBColor(0x2B, 0x10, 0x55),
        "bg_secondary": RGBColor(0x24, 0x10, 0x47),
        "accent": RGBColor(0xFF, 0xD5, 0x4F),
        "env": RGBColor(0x2E, 0x9E, 0x62),
        "social": RGBColor(0x7E, 0x9B, 0xF5),
        "gov": RGBColor(0xC0, 0x8C, 0xF5),
        "text_light": RGBColor(0xF2, 0xED, 0xFB),
        "text_dark": RGBColor(0xF2, 0xED, 0xFB),
        "subtitle": RGBColor(0xB9, 0xA6, 0xE0),
        "muted": RGBColor(0xB9, 0xA6, 0xE0),
        "card_bg": RGBColor(0x3A, 0x21, 0x70),
    },
}

# Design language per theme: fonts, header style, card style, cover layout
STYLES = {
    AestheticTheme.CORPORATE_BLUE: {
        "font_title": "Calibri", "font_body": "Calibri",
        "header": "band", "card": "flat", "cover": "classic",
        "dark_slides": False, "uppercase_titles": False,
    },
    AestheticTheme.GREEN_NATURE: {
        "font_title": "Trebuchet MS", "font_body": "Trebuchet MS",
        "header": "pill", "card": "rounded", "cover": "organic",
        "dark_slides": False, "uppercase_titles": False,
    },
    AestheticTheme.DARK_PREMIUM: {
        "font_title": "Georgia", "font_body": "Georgia",
        "header": "hairline", "card": "dark", "cover": "luxe",
        "dark_slides": True, "uppercase_titles": True,
    },
    AestheticTheme.MINIMAL_WHITE: {
        "font_title": "Segoe UI", "font_body": "Segoe UI",
        "header": "minimal", "card": "outline", "cover": "minimal",
        "dark_slides": False, "uppercase_titles": True,
    },
    AestheticTheme.SUNSET_TERRACOTTA: {
        "font_title": "Cambria", "font_body": "Calibri",
        "header": "pill", "card": "rounded", "cover": "organic",
        "dark_slides": False, "uppercase_titles": False,
    },
    AestheticTheme.OCEAN_DEEP: {
        "font_title": "Segoe UI", "font_body": "Segoe UI",
        "header": "band", "card": "flat", "cover": "classic",
        "dark_slides": False, "uppercase_titles": False,
    },
    AestheticTheme.ROYAL_PURPLE: {
        "font_title": "Georgia", "font_body": "Georgia",
        "header": "hairline", "card": "dark", "cover": "luxe",
        "dark_slides": True, "uppercase_titles": True,
    },
}

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)

RECT = 1
ROUNDED_RECT = 5
OVAL = 9


def add_shape(slide, shape_type, left, top, width, height, fill: RGBColor = None,
              line_color: RGBColor = None, line_width_pt: float = None):
    shape = slide.shapes.add_shape(shape_type, left, top, width, height)
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


def add_bg_rect(slide, left, top, width, height, color: RGBColor):
    return add_shape(slide, RECT, left, top, width, height, fill=color)


def add_text(slide, text, left, top, width, height, font_size=18,
             bold=False, color: RGBColor = RGBColor(0, 0, 0),
             align=PP_ALIGN.LEFT, italic=False, word_wrap=True,
             font: str = None):
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
    if font:
        run.font.name = font
    return txBox


def add_image_from_bytes(slide, img_bytes, left, top, width=None, height=None):
    img_io = io.BytesIO(img_bytes)
    slide.shapes.add_picture(img_io, left, top, width, height)


def maybe_upper(text: str, style: dict) -> str:
    return text.upper() if style["uppercase_titles"] else text


def content_slide(prs, blank_layout, theme, style, title, color: RGBColor):
    """Create a content slide with a themed header. Returns the slide."""
    slide = prs.slides.add_slide(blank_layout)
    title = maybe_upper(title, style)
    ft = style["font_title"]

    if style["header"] == "band":
        # Corporate: full-width colored band + accent side bar
        add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_secondary"])
        add_bg_rect(slide, 0, 0, SLIDE_W, Inches(1.1), color)
        add_bg_rect(slide, 0, Inches(1.1), Inches(0.07), SLIDE_H - Inches(1.1), theme["accent"])
        add_text(slide, title, Inches(0.3), Inches(0.15), Inches(12), Inches(0.8),
                 font_size=26, bold=True, color=theme["text_light"], font=ft)

    elif style["header"] == "pill":
        # Nature: light bg, rounded pill title block, decorative circles
        add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_secondary"])
        c1 = add_shape(slide, OVAL, Inches(11.8), Inches(-1.2), Inches(3), Inches(3), fill=theme["card_bg"])
        c2 = add_shape(slide, OVAL, Inches(12.6), Inches(6.4), Inches(2), Inches(2), fill=theme["card_bg"])
        add_shape(slide, ROUNDED_RECT, Inches(0.3), Inches(0.25), Inches(7.2), Inches(0.75), fill=color)
        add_text(slide, title, Inches(0.6), Inches(0.32), Inches(6.8), Inches(0.6),
                 font_size=22, bold=True, color=theme["text_light"], font=ft)

    elif style["header"] == "hairline":
        # Premium: dark bg everywhere, serif title, thin gold hairline
        add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_primary"])
        add_text(slide, title, Inches(0.5), Inches(0.3), Inches(12), Inches(0.7),
                 font_size=24, bold=False, color=color, font=ft)
        add_bg_rect(slide, Inches(0.5), Inches(1.05), Inches(12.3), Inches(0.02), theme["accent"])

    else:  # minimal
        # Minimal: white bg, small color chip + uppercase title, thin underline
        add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_secondary"])
        add_bg_rect(slide, Inches(0.5), Inches(0.42), Inches(0.22), Inches(0.22), color)
        add_text(slide, title, Inches(0.9), Inches(0.28), Inches(11.5), Inches(0.55),
                 font_size=18, bold=True, color=theme["text_dark"], font=ft)
        add_bg_rect(slide, Inches(0.5), Inches(1.0), Inches(2.2), Inches(0.02), theme["text_dark"])

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

def cover_classic(slide, theme, style, request, scores, subtitle):
    ft, fb = style["font_title"], style["font_body"]
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_primary"])
    add_bg_rect(slide, 0, 0, Inches(0.15), SLIDE_H, theme["accent"])
    add_shape(slide, OVAL, Inches(10.5), Inches(-1.5), Inches(4), Inches(4),
              fill=RGBColor(0xFF, 0xFF, 0xFF))
    add_text(slide, request.company.name.upper(), Inches(0.6), Inches(1.2), Inches(9), Inches(1.2),
             font_size=40, bold=True, color=theme["text_light"], font=ft)
    add_text(slide, subtitle, Inches(0.6), Inches(2.5), Inches(9), Inches(0.7),
             font_size=22, color=theme["subtitle"], font=fb)
    add_text(slide, f"Exercice {request.company.reporting_year}  •  {request.company.sector}  •  {request.company.country}",
             Inches(0.6), Inches(3.3), Inches(10), Inches(0.5),
             font_size=14, color=theme["subtitle"], font=fb)
    add_bg_rect(slide, Inches(10.5), Inches(5.5), Inches(2.2), Inches(1.5), theme["accent"])
    add_text(slide, f"ESG {scores.rating}", Inches(10.5), Inches(5.5), Inches(2.2), Inches(1.5),
             font_size=28, bold=True, color=theme["bg_primary"], align=PP_ALIGN.CENTER, font=ft)
    add_text(slide, f"Score Global : {scores.total_esg_score}/100",
             Inches(0.6), Inches(5.8), Inches(6), Inches(0.5),
             font_size=14, color=theme["subtitle"], font=fb)


def cover_organic(slide, theme, style, request, scores, subtitle):
    ft, fb = style["font_title"], style["font_body"]
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_secondary"])
    # Overlapping organic circles top-right
    add_shape(slide, OVAL, Inches(9.8), Inches(-2.2), Inches(5.5), Inches(5.5), fill=theme["card_bg"])
    add_shape(slide, OVAL, Inches(11.2), Inches(-0.8), Inches(3.6), Inches(3.6), fill=theme["env"])
    add_shape(slide, OVAL, Inches(10.4), Inches(1.6), Inches(1.4), Inches(1.4), fill=theme["accent"])
    # Title in deep green on light bg
    add_text(slide, request.company.name, Inches(0.7), Inches(1.6), Inches(9), Inches(1.3),
             font_size=42, bold=True, color=theme["bg_primary"], font=ft)
    add_text(slide, subtitle, Inches(0.7), Inches(2.9), Inches(9), Inches(0.7),
             font_size=20, color=theme["muted"], font=fb)
    add_text(slide, f"Exercice {request.company.reporting_year}  •  {request.company.sector}  •  {request.company.country}",
             Inches(0.7), Inches(3.7), Inches(10), Inches(0.5),
             font_size=13, color=theme["muted"], font=fb)
    # Bottom rounded band with score
    add_shape(slide, ROUNDED_RECT, Inches(0.7), Inches(5.3), Inches(11.9), Inches(1.5),
              fill=theme["bg_primary"])
    add_text(slide, f"Score ESG : {scores.total_esg_score}/100", Inches(1.2), Inches(5.75),
             Inches(6), Inches(0.6), font_size=22, bold=True, color=theme["text_light"], font=ft)
    add_shape(slide, OVAL, Inches(10.2), Inches(5.45), Inches(1.2), Inches(1.2), fill=theme["accent"])
    add_text(slide, scores.rating, Inches(10.2), Inches(5.75), Inches(1.2), Inches(0.6),
             font_size=22, bold=True, color=theme["bg_primary"], align=PP_ALIGN.CENTER, font=ft)


def cover_luxe(slide, theme, style, request, scores, subtitle):
    ft, fb = style["font_title"], style["font_body"]
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_primary"])
    # Thin gold frame
    m, t = Inches(0.4), Inches(0.015)
    gold = theme["accent"]
    add_bg_rect(slide, m, m, SLIDE_W - m - m, t, gold)
    add_bg_rect(slide, m, SLIDE_H - m, SLIDE_W - m - m, t, gold)
    add_bg_rect(slide, m, m, t, SLIDE_H - m - m, gold)
    add_bg_rect(slide, SLIDE_W - m, m, t, SLIDE_H - m - m + t, gold)
    # Centered serif composition
    add_text(slide, subtitle.upper(), Inches(1), Inches(1.5), Inches(11.33), Inches(0.5),
             font_size=13, color=theme["accent"], align=PP_ALIGN.CENTER, font=fb)
    add_text(slide, request.company.name.upper(), Inches(1), Inches(2.3), Inches(11.33), Inches(1.4),
             font_size=44, bold=False, color=theme["text_light"], align=PP_ALIGN.CENTER, font=ft)
    add_bg_rect(slide, Inches(5.9), Inches(3.9), Inches(1.5), Inches(0.02), gold)
    add_text(slide, f"Exercice {request.company.reporting_year}  •  {request.company.sector}  •  {request.company.country}",
             Inches(1), Inches(4.2), Inches(11.33), Inches(0.5),
             font_size=13, italic=True, color=theme["subtitle"], align=PP_ALIGN.CENTER, font=ft)
    add_text(slide, f"— {scores.rating} —", Inches(1), Inches(5.1), Inches(11.33), Inches(0.8),
             font_size=34, bold=True, color=gold, align=PP_ALIGN.CENTER, font=ft)
    add_text(slide, f"Score ESG {scores.total_esg_score}/100", Inches(1), Inches(5.95),
             Inches(11.33), Inches(0.5), font_size=14, color=theme["subtitle"],
             align=PP_ALIGN.CENTER, font=fb)


def cover_minimal(slide, theme, style, request, scores, subtitle):
    ft, fb = style["font_title"], style["font_body"]
    add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_secondary"])
    add_bg_rect(slide, Inches(0.7), Inches(1.1), Inches(0.35), Inches(0.35), theme["accent"])
    add_text(slide, subtitle.upper(), Inches(0.7), Inches(1.7), Inches(11), Inches(0.5),
             font_size=12, bold=True, color=theme["muted"], font=fb)
    add_text(slide, request.company.name, Inches(0.65), Inches(2.3), Inches(11.5), Inches(1.6),
             font_size=52, bold=True, color=theme["text_dark"], font=ft)
    add_bg_rect(slide, Inches(0.7), Inches(4.2), Inches(11.9), Inches(0.015),
                RGBColor(0xBD, 0xBD, 0xBD))
    add_text(slide, f"Exercice {request.company.reporting_year}", Inches(0.7), Inches(4.5),
             Inches(4), Inches(0.4), font_size=13, color=theme["muted"], font=fb)
    add_text(slide, request.company.sector, Inches(4.7), Inches(4.5), Inches(4), Inches(0.4),
             font_size=13, color=theme["muted"], font=fb)
    add_text(slide, request.company.country, Inches(8.7), Inches(4.5), Inches(4), Inches(0.4),
             font_size=13, color=theme["muted"], font=fb)
    add_text(slide, f"{scores.total_esg_score}", Inches(0.6), Inches(5.1), Inches(4), Inches(1.2),
             font_size=64, bold=True, color=theme["accent"], font=ft)
    add_text(slide, f"/100 — Note {scores.rating}", Inches(3.0), Inches(5.75), Inches(5), Inches(0.5),
             font_size=16, color=theme["muted"], font=fb)


COVERS = {"classic": cover_classic, "organic": cover_organic,
          "luxe": cover_luxe, "minimal": cover_minimal}


def generate_pptx(request: ESGRequest, scores: ESGScores, content: dict,
                  chart_images: dict, logo_bytes: bytes = None) -> bytes:
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    theme = THEMES.get(request.aesthetic_theme, THEMES[AestheticTheme.CORPORATE_BLUE])
    style = STYLES.get(request.aesthetic_theme, STYLES[AestheticTheme.CORPORATE_BLUE])
    ft, fb = style["font_title"], style["font_body"]
    ptype = request.presentation_type
    blank_layout = prs.slide_layouts[6]

    # ── SLIDE 1: Cover ──────────────────────────────────────────────────
    slide = prs.slides.add_slide(blank_layout)
    subtitle_map = {
        PresentationType.EXECUTIVE_SUMMARY: "Rapport ESG — Synthèse Exécutive",
        PresentationType.INVESTOR_DECK: "ESG Investor Deck",
        PresentationType.DETAILED_REPORT: "Rapport ESG Détaillé",
        PresentationType.STAKEHOLDER_BRIEF: "Communication Parties Prenantes",
        PresentationType.ANNUAL_REPORT: "Rapport Annuel ESG / RSE",
    }
    COVERS[style["cover"]](slide, theme, style, request, scores,
                           subtitle_map.get(ptype, "Rapport ESG"))

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
        line = f"Présenté par {request.company.presenter_name}"
        if request.company.presenter_title:
            line += f" — {request.company.presenter_title}"
        pres_y = Inches(6.9) if style["cover"] == "organic" else Inches(6.55)
        pres_align = PP_ALIGN.CENTER if style["cover"] == "luxe" else PP_ALIGN.LEFT
        pres_color = theme["muted"] if style["cover"] == "minimal" else theme["subtitle"]
        add_text(slide, line, Inches(0.7), pres_y, Inches(11.9), Inches(0.4),
                 font_size=12, italic=True, color=pres_color, font=fb, align=pres_align)

    # ── SLIDE 1bis: Illustration de couverture (générée localement) ──────
    if "cover_art" in chart_images:
        slide = prs.slides.add_slide(blank_layout)
        bg = theme["bg_primary"] if style["dark_slides"] else theme["bg_secondary"]
        add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, bg)
        add_image_from_bytes(slide, chart_images["cover_art"], 0, 0, SLIDE_W, Inches(4.4))
        add_text(slide, maybe_upper(f"Rapport ESG {request.company.reporting_year}", style),
                 Inches(0.7), Inches(4.9), Inches(11.9), Inches(0.9),
                 font_size=32, bold=True, color=theme["text_dark"], font=ft)
        add_text(slide, f"{request.company.name}  •  {request.company.sector}",
                 Inches(0.7), Inches(5.9), Inches(11.9), Inches(0.5),
                 font_size=15, color=theme["muted"], font=fb)

    # ── SLIDE 2: Tableau de Bord ESG ────────────────────────────────────
    header_color = theme["accent"] if style["header"] == "hairline" else theme["bg_primary"]
    slide = content_slide(prs, blank_layout, theme, style, "Tableau de Bord ESG", header_color)

    pillars = [
        ("E — Environnement", scores.environmental_score, theme["env"], Inches(0.3)),
        ("S — Social", scores.social_score, theme["social"], Inches(4.55)),
        ("G — Gouvernance", scores.governance_score, theme["gov"], Inches(8.8)),
    ]
    for label, score, color, left in pillars:
        kpi_card(slide, left, Inches(1.3), Inches(4.0), Inches(2.4), theme, style, color)
        lbl_indent = Inches(0.42) if style["card"] == "rounded" else Inches(0.2)
        add_text(slide, label, left + lbl_indent, Inches(1.5),
                 Inches(3.5), Inches(0.5), font_size=13, bold=True, color=theme["text_dark"], font=fb)
        add_text(slide, f"{score:.1f}", left + Inches(0.2), Inches(2.0),
                 Inches(2.0), Inches(0.9), font_size=44, bold=True, color=color, font=ft)
        add_text(slide, "/100", left + Inches(1.6), Inches(2.4),
                 Inches(1.5), Inches(0.4), font_size=14, color=theme["muted"], font=fb)

    sep_color = theme["accent"] if style["header"] != "minimal" else RGBColor(0xBD, 0xBD, 0xBD)
    add_bg_rect(slide, Inches(0.3), Inches(3.9), Inches(12.7), Inches(0.03), sep_color)
    add_text(slide, f"Score ESG Global : {scores.total_esg_score}/100  —  Note : {scores.rating}",
             Inches(0.3), Inches(4.05), Inches(12.7), Inches(0.6),
             font_size=20, bold=True, color=theme["text_dark"], align=PP_ALIGN.CENTER, font=ft)

    if "radar" in chart_images:
        add_image_from_bytes(slide, chart_images["radar"],
                             Inches(1.2), Inches(4.75), height=Inches(2.55))
    if "bars" in chart_images:
        add_image_from_bytes(slide, chart_images["bars"],
                             Inches(5.6), Inches(4.8), height=Inches(2.5))

    # ── SLIDE 3: Environnement ───────────────────────────────────────────
    slide = content_slide(prs, blank_layout, theme, style, "🌍  Pilier Environnemental", theme["env"])

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

    has_pie = "emissions_pie" in chart_images
    kpi_grid(slide, env_kpis, theme, style, theme["env"], ncols=2 if has_pie else 3)
    add_text(slide, f"Score E — {scores.environmental_score:.0f}/100",
             Inches(9.3), Inches(6.9), Inches(3.7), Inches(0.5),
             font_size=16, bold=True, color=theme["env"], align=PP_ALIGN.RIGHT, font=ft)

    if has_pie:
        add_image_from_bytes(slide, chart_images["emissions_pie"],
                             Inches(9.0), Inches(1.4), width=Inches(4.1))

    # ── SLIDE 4: Social ──────────────────────────────────────────────────
    slide = content_slide(prs, blank_layout, theme, style, "👥  Pilier Social", theme["social"])

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

    kpi_grid(slide, soc_kpis, theme, style, theme["social"])
    add_text(slide, f"Score S — {scores.social_score:.0f}/100",
             Inches(9.3), Inches(6.9), Inches(3.7), Inches(0.5),
             font_size=16, bold=True, color=theme["social"], align=PP_ALIGN.RIGHT, font=ft)

    # ── SLIDE 5: Gouvernance ─────────────────────────────────────────────
    slide = content_slide(prs, blank_layout, theme, style, "⚖️  Pilier Gouvernance", theme["gov"])

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
    if gov.esg_audit_conducted is not None:
        gov_kpis.append(("Audit ESG conduit", "Oui ✓" if gov.esg_audit_conducted else "Non ✗"))
    if gov.sustainability_committee is not None:
        gov_kpis.append(("Comité durabilité", "Oui ✓" if gov.sustainability_committee else "Non ✗"))

    kpi_grid(slide, gov_kpis, theme, style, theme["gov"])
    add_text(slide, f"Score G — {scores.governance_score:.0f}/100",
             Inches(9.3), Inches(6.9), Inches(3.7), Inches(0.5),
             font_size=16, bold=True, color=theme["gov"], align=PP_ALIGN.RIGHT, font=ft)

    # ── SLIDE 6: Forces & Faiblesses ────────────────────────────────────
    slide = content_slide(prs, blank_layout, theme, style, "Analyse Stratégique ESG", header_color)

    red = RGBColor(0xE7, 0x4C, 0x3C)
    panel_shape = ROUNDED_RECT if style["card"] == "rounded" else RECT
    for (px, pw, ptitle, pcolor, items) in [
        (Inches(0.3), Inches(6.0), "✅  Points Forts", theme["env"], scores.strengths),
        (Inches(6.9), Inches(6.1), "⚠️  Axes d'Amélioration", red, scores.weaknesses),
    ]:
        if style["card"] == "outline":
            add_shape(slide, RECT, px, Inches(1.2), pw, Inches(5.8), fill=theme["card_bg"],
                      line_color=RGBColor(0xE0, 0xE0, 0xE0), line_width_pt=1.0)
            add_text(slide, "  " + ptitle, px, Inches(1.3), pw, Inches(0.5),
                     font_size=14, bold=True, color=pcolor, font=ft)
        else:
            add_shape(slide, panel_shape, px, Inches(1.2), pw, Inches(5.8), fill=theme["card_bg"])
            add_shape(slide, panel_shape, px, Inches(1.2), pw, Inches(0.55), fill=pcolor)
            add_text(slide, "  " + ptitle, px, Inches(1.2), pw, Inches(0.55),
                     font_size=14, bold=True, color=theme["text_light"], font=ft)
        for i, item in enumerate(items):
            add_text(slide, f"• {item}", px + Inches(0.2), Inches(1.95) + i * Inches(0.85),
                     pw - Inches(0.4), Inches(0.8), font_size=12, color=theme["text_dark"], font=fb)

    # ── SLIDE 7: Recommandations ─────────────────────────────────────────
    if request.include_recommendations:
        slide = content_slide(prs, blank_layout, theme, style, "Recommandations Prioritaires", header_color)

        rec_colors = [theme["env"], theme["social"], theme["gov"], theme["accent"],
                      theme["env"], theme["social"]]
        for i, rec in enumerate(scores.recommendations[:6]):
            row = Inches(1.2) + (i % 3) * Inches(2.0)
            col = Inches(0.3) + (i // 3) * Inches(6.5)
            num_color = rec_colors[i]
            kpi_card(slide, col, row, Inches(6.1), Inches(1.8), theme, style, num_color)
            add_text(slide, str(i + 1), col + Inches(0.1), row + Inches(0.5),
                     Inches(0.5), Inches(0.8), font_size=22, bold=True,
                     color=num_color, align=PP_ALIGN.CENTER, font=ft)
            add_text(slide, rec, col + Inches(0.7), row + Inches(0.25),
                     Inches(5.2), Inches(1.3), font_size=11, color=theme["text_dark"], font=fb)

    # ── SLIDE 8: Alignement ODD ──────────────────────────────────────────
    slide = content_slide(prs, blank_layout, theme, style,
                          "Alignement — ODD & Cadres de Référence", header_color)

    odds = [
        ("ODD 7", "Énergie propre", theme["accent"]),
        ("ODD 8", "Travail décent", theme["social"]),
        ("ODD 10", "Inégalités réduites", theme["gov"]),
        ("ODD 12", "Conso. responsable", theme["env"]),
        ("ODD 13", "Action climatique", theme["env"]),
        ("ODD 16", "Paix & Institutions", theme["gov"]),
    ]
    odd_shape = ROUNDED_RECT if style["card"] == "rounded" else RECT
    for idx, (odd_num, odd_label, odd_color) in enumerate(odds):
        col = Inches(0.3) + (idx % 3) * Inches(4.3)
        row = Inches(1.3) + (idx // 3) * Inches(1.8)
        if style["card"] == "outline":
            add_shape(slide, RECT, col, row, Inches(4.0), Inches(1.6), fill=theme["card_bg"],
                      line_color=odd_color, line_width_pt=1.5)
            txt_color, sub_color = odd_color, theme["text_dark"]
        else:
            add_shape(slide, odd_shape, col, row, Inches(4.0), Inches(1.6), fill=odd_color)
            txt_color = sub_color = RGBColor(0xFF, 0xFF, 0xFF)
        add_text(slide, odd_num, col + Inches(0.15), row + Inches(0.1),
                 Inches(3.7), Inches(0.6), font_size=18, bold=True, color=txt_color, font=ft)
        add_text(slide, odd_label, col + Inches(0.15), row + Inches(0.75),
                 Inches(3.7), Inches(0.7), font_size=13, color=sub_color, font=fb)

    frameworks = ["GRI Standards", "TCFD", "CSRD / DPEF", "SFDR", "ISO 14001 / 26000"]
    add_bg_rect(slide, Inches(0.3), Inches(5.1), Inches(12.7), Inches(0.03), sep_color)
    add_text(slide, "Cadres reportés : " + "  |  ".join(frameworks),
             Inches(0.3), Inches(5.3), Inches(12.7), Inches(0.6),
             font_size=13, bold=True, color=theme["text_dark"], align=PP_ALIGN.CENTER, font=fb)

    # ── SLIDE 9: Conclusion ──────────────────────────────────────────────
    slide = prs.slides.add_slide(blank_layout)
    if style["cover"] == "minimal":
        add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_secondary"])
        concl_title_color, concl_text_color = theme["text_dark"], theme["muted"]
        add_bg_rect(slide, Inches(0.6), Inches(0.7), Inches(0.3), Inches(0.3), theme["accent"])
        title_top = Inches(1.2)
    else:
        add_bg_rect(slide, 0, 0, SLIDE_W, SLIDE_H, theme["bg_primary"])
        add_bg_rect(slide, 0, 0, Inches(0.15), SLIDE_H, theme["accent"])
        concl_title_color, concl_text_color = theme["text_light"], theme["subtitle"]
        title_top = Inches(0.8)

    add_text(slide, maybe_upper("Conclusion & Engagements", style), Inches(0.6), title_top,
             Inches(11), Inches(1.0), font_size=30, bold=True, color=concl_title_color, font=ft)

    conclusion_text = content.get("conclusion",
        f"{request.company.name} affiche un score ESG global de {scores.total_esg_score}/100 "
        f"(note {scores.rating}), témoignant d'une démarche structurée de développement durable. "
        "La société s'engage à renforcer ses performances sur les axes identifiés "
        "et à maintenir la transparence de son reporting extra-financier."
    )
    add_text(slide, conclusion_text, Inches(0.6), Inches(2.2),
             Inches(11.5), Inches(2.8), font_size=14, color=concl_text_color, font=fb)

    add_text(slide, f"Score ESG : {scores.total_esg_score}/100  —  Note : {scores.rating}",
             Inches(0.6), Inches(5.0), Inches(10), Inches(0.7),
             font_size=22, bold=True, color=theme["accent"], font=ft)

    add_text(slide, f"© {request.company.reporting_year} {request.company.name} — Document confidentiel",
             Inches(0.6), Inches(6.7), Inches(11), Inches(0.4),
             font_size=9, italic=True, color=concl_text_color, font=fb)

    buf = io.BytesIO()
    prs.save(buf)
    buf.seek(0)
    return buf.read()
