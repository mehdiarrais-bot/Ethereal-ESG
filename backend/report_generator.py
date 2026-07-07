import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, Image, HRFlowable, PageBreak,
                                 KeepTogether)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from xml.sax.saxutils import escape as _xml_escape
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from models import ESGRequest, ESGScores, AestheticTheme, ReportType
from i18n import L

# ── Enregistrement de polices TrueType système (Windows) ────────────────────
# Chaque famille : (regular, bold, italic) → repli sur les polices PDF de base
# si les fichiers sont introuvables (Linux/Mac ou installation minimale).
_FONT_DIRS = [
    r"C:\Windows\Fonts",
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts"),
    "/usr/share/fonts/truetype/msttcorefonts",
    "/usr/share/fonts/truetype/dejavu",
]
_FONT_FILES = {
    "SegoeUI": ("segoeui.ttf", "segoeuib.ttf", "segoeuii.ttf"),
    "Georgia": ("georgia.ttf", "georgiab.ttf", "georgiai.ttf"),
}
_FALLBACKS = {
    "SegoeUI": ("Helvetica", "Helvetica-Bold", "Helvetica-Oblique"),
    "Georgia": ("Times-Roman", "Times-Bold", "Times-Italic"),
}
_registered = {}


def resolve_family(family: str) -> tuple:
    """Retourne (regular, bold, italic) : TTF système si dispo, sinon base-14."""
    if family in _registered:
        return _registered[family]
    result = _FALLBACKS[family]
    files = _FONT_FILES[family]
    for d in _FONT_DIRS:
        paths = [os.path.join(d, f) for f in files]
        if all(os.path.isfile(p) for p in paths):
            try:
                names = (family, family + "-Bold", family + "-Italic")
                for name, path in zip(names, paths):
                    pdfmetrics.registerFont(TTFont(name, path))
                result = names
                break
            except Exception:
                result = _FALLBACKS[family]
                break
    _registered[family] = result
    return result


# Glyphes absents des polices PDF (indices/exposants Unicode, symboles)
_PDF_CHARS = str.maketrans({
    '\u2080': '0', '\u2081': '1', '\u2082': '2', '\u2083': '3', '\u2084': '4',
    '\u2070': '0', '\u00b9': '1',  # ³ et ² existent en latin-1, on les garde
    '\u2713': '+', '\u2717': 'x', '\u2705': '', '\u26a0': '', '\ufe0f': '',
    '\u2192': '>', '\u2588': '', '\u2591': '',
})


def pdf_txt(v) -> str:
    """Texte brut sûr pour canvas.drawString (translittéré, latin-1)."""
    s = str(v).translate(_PDF_CHARS)
    return s.encode('cp1252', 'ignore').decode('cp1252')


def esc(v) -> str:
    """Adapte une chaîne aux Paragraph reportlab : glyphes indisponibles
    translittérés, caractères hors latin-1 retirés, puis échappement XML."""
    s = str(v).translate(_PDF_CHARS)
    s = s.encode('cp1252', 'ignore').decode('cp1252')
    return _xml_escape(s)

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
        "secondary": colors.HexColor("#4A5568"),
        "accent": colors.HexColor("#F7C948"),
        "env": colors.HexColor("#3FB950"),
        "social": colors.HexColor("#58A6FF"),
        "gov": colors.HexColor("#BC8CFF"),
        "light_bg": colors.HexColor("#E8EBF0"),
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
    AestheticTheme.SUNSET_TERRACOTTA: {
        "primary": colors.HexColor("#9A3412"),
        "secondary": colors.HexColor("#E76F51"),
        "accent": colors.HexColor("#F4A261"),
        "env": colors.HexColor("#2A9D8F"),
        "social": colors.HexColor("#E76F51"),
        "gov": colors.HexColor("#6D597A"),
        "light_bg": colors.HexColor("#FAE5D8"),
        "text": colors.HexColor("#4A2C22"),
    },
    AestheticTheme.OCEAN_DEEP: {
        "primary": colors.HexColor("#0F4C5C"),
        "secondary": colors.HexColor("#277DA1"),
        "accent": colors.HexColor("#00BFA6"),
        "env": colors.HexColor("#43AA8B"),
        "social": colors.HexColor("#277DA1"),
        "gov": colors.HexColor("#577590"),
        "light_bg": colors.HexColor("#DCF1F5"),
        "text": colors.HexColor("#123B44"),
    },
    AestheticTheme.ROYAL_PURPLE: {
        "primary": colors.HexColor("#2B1055"),
        "secondary": colors.HexColor("#5E35B1"),
        "accent": colors.HexColor("#D4A017"),
        "env": colors.HexColor("#2E9E62"),
        "social": colors.HexColor("#4A5FC1"),
        "gov": colors.HexColor("#8E24AA"),
        "light_bg": colors.HexColor("#EDE6F7"),
        "text": colors.HexColor("#2E2145"),
    },
}


# Design language per theme: fonts + header/cover/table styling
PDF_STYLES = {
    AestheticTheme.CORPORATE_BLUE: {
        "family": "SegoeUI",
        "font": "Helvetica", "font_bold": "Helvetica-Bold", "font_italic": "Helvetica-Oblique",
        "header": "rule", "cover": "classic", "kpi": "filled", "uppercase": False,
        "title_size": 28, "h1_size": 20, "body_leading": 16,
    },
    AestheticTheme.GREEN_NATURE: {
        "family": "SegoeUI",
        "font": "Helvetica", "font_bold": "Helvetica-Bold", "font_italic": "Helvetica-Oblique",
        "header": "banner", "cover": "banner", "kpi": "filled", "uppercase": False,
        "title_size": 30, "h1_size": 15, "body_leading": 17,
    },
    AestheticTheme.DARK_PREMIUM: {
        "family": "Georgia",
        "font": "Times-Roman", "font_bold": "Times-Bold", "font_italic": "Times-Italic",
        "header": "goldrule", "cover": "luxe", "kpi": "dark", "uppercase": True,
        "title_size": 30, "h1_size": 19, "body_leading": 17,
    },
    AestheticTheme.MINIMAL_WHITE: {
        "family": "SegoeUI",
        "font": "Helvetica", "font_bold": "Helvetica-Bold", "font_italic": "Helvetica-Oblique",
        "header": "minimal", "cover": "minimal", "kpi": "outline", "uppercase": True,
        "title_size": 34, "h1_size": 13, "body_leading": 18,
    },
    AestheticTheme.SUNSET_TERRACOTTA: {
        "family": "Georgia",
        "font": "Helvetica", "font_bold": "Helvetica-Bold", "font_italic": "Helvetica-Oblique",
        "header": "banner", "cover": "banner", "kpi": "filled", "uppercase": False,
        "title_size": 30, "h1_size": 15, "body_leading": 17,
    },
    AestheticTheme.OCEAN_DEEP: {
        "family": "SegoeUI",
        "font": "Helvetica", "font_bold": "Helvetica-Bold", "font_italic": "Helvetica-Oblique",
        "header": "rule", "cover": "classic", "kpi": "filled", "uppercase": False,
        "title_size": 28, "h1_size": 20, "body_leading": 16,
    },
    AestheticTheme.ROYAL_PURPLE: {
        "family": "Georgia",
        "font": "Times-Roman", "font_bold": "Times-Bold", "font_italic": "Times-Italic",
        "header": "goldrule", "cover": "luxe", "kpi": "dark", "uppercase": True,
        "title_size": 30, "h1_size": 19, "body_leading": 17,
    },
}


def page_decorator(pal, ts, company_name: str, minimal: bool = False, footer_label: str = "Rapport ESG"):
    """En-tête et pied de page dessinés sur chaque page."""
    font = ts["font"]
    name = pdf_txt(company_name)

    def draw(canvas, doc):
        w, h = A4
        canvas.saveState()
        if minimal:
            # Minimal : simple pastille accent en haut à gauche
            canvas.setFillColor(pal["accent"])
            canvas.rect(2 * cm, h - 1.1 * cm, 0.9 * cm, 0.14 * cm, fill=1, stroke=0)
        else:
            # Bandeau plein + liseré accent
            canvas.setFillColor(pal["primary"])
            canvas.rect(0, h - 0.5 * cm, w, 0.5 * cm, fill=1, stroke=0)
            canvas.setFillColor(pal["accent"])
            canvas.rect(0, h - 0.62 * cm, w, 0.12 * cm, fill=1, stroke=0)
        # Pied de page : filet + société à gauche, pagination à droite
        canvas.setStrokeColor(pal["accent"] if not minimal else colors.HexColor("#D0D0D0"))
        canvas.setLineWidth(0.6)
        canvas.line(2 * cm, 1.55 * cm, w - 2 * cm, 1.55 * cm)
        canvas.setFillColor(colors.HexColor("#8A8A8A"))
        try:
            canvas.setFont(font, 7.5)
        except Exception:
            canvas.setFont("Helvetica", 7.5)
        canvas.drawString(2 * cm, 1.15 * cm, name)
        canvas.drawRightString(w - 2 * cm, 1.15 * cm, footer_label + f"  |  page {canvas.getPageNumber()}")
        canvas.restoreState()

    return draw


def build_styles(pal: dict, ts: dict) -> dict:
    f, fb, fi = resolve_family(ts["family"]) if ts.get("family") else \
        (ts["font"], ts["font_bold"], ts["font_italic"])
    ts = dict(ts, font=f, font_bold=fb, font_italic=fi)
    return {
        "title": ParagraphStyle("title", fontSize=ts["title_size"], textColor=pal["primary"],
                                 spaceAfter=8, fontName=fb, alignment=TA_LEFT,
                                 leading=ts["title_size"] * 1.15),
        "h1": ParagraphStyle("h1", fontSize=ts["h1_size"], textColor=pal["primary"],
                              spaceAfter=6, spaceBefore=18, fontName=fb,
                              leading=ts["h1_size"] * 1.25),
        "h1_light": ParagraphStyle("h1_light", fontSize=ts["h1_size"], textColor=colors.white,
                                    fontName=fb, leading=ts["h1_size"] * 1.25),
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
        "_ts": ts,  # ts avec les polices résolues, pour les usages en aval
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
    if kpi_style == "dark":
        value_color, label_color = colors.white, colors.HexColor("#CFC7E8")
        box_bg = pal["primary"]
        grid_color = colors.HexColor("#5A4A85")
    elif kpi_style == "outline":
        value_color, label_color = pal["primary"], colors.HexColor("#9E9E9E")
        box_bg = colors.white
        grid_color = colors.HexColor("#E0E0E0")
    else:
        value_color, label_color = pal["primary"], pal["secondary"]
        box_bg = pal["light_bg"]
        grid_color = colors.white

    label_style = ParagraphStyle("kl", fontSize=7.5, leading=10, fontName=ts["font_bold"],
                                 textColor=label_color, alignment=TA_CENTER)
    value_style = ParagraphStyle("kv", fontSize=16, leading=19, fontName=ts["font_bold"],
                                 textColor=value_color, alignment=TA_CENTER)

    data, row = [], []
    for label, value in kpi_list:
        row.append([Paragraph(esc(label).upper(), label_style),
                    Spacer(1, 3),
                    Paragraph(esc(value), value_style)])
        if len(row) == 3:
            data.append(row)
            row = []
    if row:
        while len(row) < 3:
            row.append("")
        data.append(row)

    t = Table(data, colWidths=[5.5 * cm] * 3)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), box_bg),
        ('BOX', (0, 0), (-1, -1), 0.75, pal["accent"] if kpi_style == "dark" else grid_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, grid_color),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    return t


def generate_pdf_report(request: ESGRequest, scores: ESGScores, content: dict,
                         chart_images: dict, logo_bytes: bytes = None) -> bytes:
    buf = io.BytesIO()
    pal = PALETTE.get(request.aesthetic_theme, PALETTE[AestheticTheme.CORPORATE_BLUE])
    ts = PDF_STYLES.get(request.aesthetic_theme, PDF_STYLES[AestheticTheme.CORPORATE_BLUE])
    styles = build_styles(pal, ts)
    ts = styles["_ts"]  # polices résolues (TTF système ou base-14)
    TR = L(request.language)

    doc = SimpleDocTemplate(buf, pagesize=A4,
                             leftMargin=2 * cm, rightMargin=2 * cm,
                             topMargin=2.2 * cm, bottomMargin=2.2 * cm)
    story = []

    # ── Cover (varies per theme) ──────────────────────────────────────────
    type_labels = {
        "white_paper": TR["rep_white_paper"],
        "full_report": TR["rep_full_report"],
        "executive_summary_pdf": TR["rep_executive_summary_pdf"],
    }
    type_label = type_labels.get(request.report_type.value, TR["rep_default"])
    meta_line = esc(f"{TR['exercise']} {request.company.reporting_year}  •  {TR['sector']} : {request.company.sector}  •  {request.company.country}")

    if ts["cover"] == "luxe":
        # Dark Premium: full dark block, centered serif, gold accents
        cover_cells = [
            [Paragraph(type_label.upper(), ParagraphStyle(
                "ck", fontSize=11, fontName=ts["font"], textColor=pal["accent"],
                alignment=TA_CENTER, spaceAfter=14))],
            [Paragraph(esc(request.company.name.upper()), ParagraphStyle(
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
            ('BACKGROUND', (0, 0), (-1, -1), pal["primary"]),
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
        banner = Table([[Paragraph(esc(request.company.name), ParagraphStyle(
            "ct", fontSize=30, fontName=ts["font_bold"], textColor=colors.white,
            leading=36))]], colWidths=[17 * cm])
        banner.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), pal["primary"]),
            ('TOPPADDING', (0, 0), (-1, -1), 28),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 28),
            ('LEFTPADDING', (0, 0), (-1, -1), 18),
        ]))
        sub = Table([[Paragraph(esc(type_label) + " — " + meta_line, ParagraphStyle(
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
        story.append(Paragraph(esc(request.company.name), styles["title"]))
        story.append(Spacer(1, 0.2 * cm))
        story.append(HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#BDBDBD")))
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph(meta_line, styles["body"]))
        story.append(Spacer(1, 1 * cm))
    else:
        # Corporate: classic left-aligned with thick accent rule
        story.append(Spacer(1, 2 * cm))
        story.append(Paragraph(esc(request.company.name.upper()), styles["title"]))
        story.append(HRFlowable(width="100%", thickness=4, color=pal["accent"]))
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph(type_label, styles["h1"]))
        story.append(Paragraph(meta_line, styles["body"]))
        story.append(Spacer(1, 0.5 * cm))

    # Logo entreprise
    if logo_bytes:
        try:
            logo_img = Image(io.BytesIO(logo_bytes))
            ratio = logo_img.imageWidth / max(1, logo_img.imageHeight)
            logo_img.drawHeight = 2 * cm
            logo_img.drawWidth = min(8 * cm, 2 * cm * ratio)
            logo_img.hAlign = 'CENTER' if ts["cover"] == "luxe" else 'LEFT'
            story.insert(1, logo_img)
            story.insert(2, Spacer(1, 0.4 * cm))
        except Exception:
            pass

    # Présentateur
    if request.company.presenter_name:
        pres_line = f"{TR['presented_by']} {request.company.presenter_name}"
        if request.company.presenter_title:
            pres_line += f" — {request.company.presenter_title}"
        story.append(Paragraph(esc(pres_line), ParagraphStyle(
            "pres", fontSize=11, fontName=ts["font_italic"],
            textColor=pal["secondary"],
            alignment=TA_CENTER if ts["cover"] == "luxe" else TA_LEFT)))
        story.append(Spacer(1, 0.4 * cm))

    # Illustration de couverture (générée localement)
    if "cover_art" in chart_images:
        try:
            art = Image(io.BytesIO(chart_images["cover_art"]), width=17 * cm, height=5.5 * cm)
            art.hAlign = 'CENTER'
            story.append(art)
            story.append(Spacer(1, 0.5 * cm))
        except Exception:
            pass

    # Score summary table
    score_data = [
        [Paragraph(TR["score_env_short"], styles["kpi_label"]),
         Paragraph(TR["score_soc_short"], styles["kpi_label"]),
         Paragraph(TR["score_gov_short"], styles["kpi_label"]),
         Paragraph(TR["score_global_short"], ParagraphStyle(
             "kpi_label_w", fontSize=9, textColor=colors.white,
             fontName=ts["font_bold"], alignment=TA_CENTER))],
        [Paragraph(f"<font color='#{pal['env'].hexval()[2:]}'><b>{scores.environmental_score:.1f}</b></font>",
                   ParagraphStyle("sv", fontSize=24, leading=28, fontName=ts["font_bold"],
                                  alignment=TA_CENTER)),
         Paragraph(f"<font color='#{pal['social'].hexval()[2:]}'><b>{scores.social_score:.1f}</b></font>",
                   ParagraphStyle("sv2", fontSize=24, leading=28, fontName=ts["font_bold"],
                                  alignment=TA_CENTER)),
         Paragraph(f"<font color='#{pal['gov'].hexval()[2:]}'><b>{scores.governance_score:.1f}</b></font>",
                   ParagraphStyle("sv3", fontSize=24, leading=28, fontName=ts["font_bold"],
                                  alignment=TA_CENTER)),
         Paragraph(f"<font color='#{pal['accent'].hexval()[2:]}'><b>{scores.total_esg_score:.1f}</b></font>",
                   ParagraphStyle("sv4", fontSize=24, leading=28, fontName=ts["font_bold"],
                                  alignment=TA_CENTER))],
        [Paragraph("/100", styles["caption"]), Paragraph("/100", styles["caption"]),
         Paragraph("/100", styles["caption"]),
         Paragraph(f"{TR['note']} : {scores.rating}", ParagraphStyle(
             "rating", fontSize=12, leading=14, fontName=ts["font_bold"],
             textColor=colors.white, alignment=TA_CENTER))],
    ]
    score_table = Table(score_data, colWidths=[4 * cm] * 4)
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), pal["light_bg"]),
        ('BACKGROUND', (3, 0), (3, -1), pal["primary"]),
        ('TEXTCOLOR', (3, 0), (3, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, pal["secondary"]),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.5 * cm))

    # Charts
    if "radar" in chart_images:
        img = Image(io.BytesIO(chart_images["radar"]), width=7 * cm, height=7 * cm)
        img.hAlign = 'CENTER'
        story.append(img)
        story.append(Paragraph(TR["cap_radar"], styles["caption"]))
        story.append(Spacer(1, 0.3 * cm))

    story.append(PageBreak())

    # ── Executive Summary ──────────────────────────────────────────────────
    section_header(story, TR["pdf_s1"], pal["secondary"], pal, styles, ts)

    exec_text = content.get("executive_summary",
        f"{request.company.name} présente son rapport ESG pour l'exercice {request.company.reporting_year}. "
        f"L'analyse des données extra-financières révèle un score ESG global de {scores.total_esg_score}/100, "
        f"correspondant à une notation {scores.rating}. Ce résultat reflète les engagements de l'entreprise "
        "en matière de responsabilité environnementale, sociale et de gouvernance d'entreprise."
    )
    story.append(Paragraph(esc(exec_text), styles["body"]))
    story.append(Spacer(1, 0.5 * cm))

    # ── Environnement ─────────────────────────────────────────────────────
    section_header(story, TR["pdf_s2"], pal["env"], pal, styles, ts)
    story.append(Paragraph(
        f"{TR['score_env_label']} : <b>{scores.environmental_score:.1f}/100</b>", styles["h2"]))

    env_text = content.get("environmental",
        "L'analyse environnementale couvre les émissions de gaz à effet de serre, "
        "la consommation d'énergie et d'eau, la gestion des déchets et les initiatives biodiversité."
    )
    story.append(Paragraph(esc(env_text), styles["body"]))

    env = request.environmental
    env_kpis = []
    if env.co2_emissions_tonnes is not None: env_kpis.append((TR["kpit"]["co2"], f"{env.co2_emissions_tonnes:,.0f}"))
    if env.renewable_energy_percent is not None: env_kpis.append((TR["kpit"]["renewable"], f"{env.renewable_energy_percent:.1f}%"))
    if env.energy_consumption_mwh is not None: env_kpis.append((TR["kpit"]["energy"], f"{env.energy_consumption_mwh:,.0f}"))
    if env.water_consumption_m3 is not None: env_kpis.append((TR["kpit"]["water"], f"{env.water_consumption_m3:,.0f}"))
    if env.waste_recycled_percent is not None: env_kpis.append((TR["kpit"]["recycling"], f"{env.waste_recycled_percent:.1f}%"))
    if env.scope1_emissions is not None: env_kpis.append((TR["kpit"]["s1"], f"{env.scope1_emissions:,.0f}"))
    if env.scope2_emissions is not None: env_kpis.append((TR["kpit"]["s2"], f"{env.scope2_emissions:,.0f}"))
    if env.scope3_emissions is not None: env_kpis.append((TR["kpit"]["s3"], f"{env.scope3_emissions:,.0f}"))

    if env_kpis:
        story.append(Spacer(1, 0.3 * cm))
        story.append(kpi_table(env_kpis, pal, ts))

    if "emissions_pie" in chart_images:
        story.append(Spacer(1, 0.3 * cm))
        img = Image(io.BytesIO(chart_images["emissions_pie"]), width=8 * cm, height=7 * cm)
        img.hAlign = 'CENTER'
        story.append(img)
        story.append(Paragraph(TR["cap_pie"], styles["caption"]))

    story.append(Spacer(1, 0.5 * cm))

    # ── Social ────────────────────────────────────────────────────────────
    section_header(story, TR["pdf_s3"], pal["social"], pal, styles, ts)
    story.append(Paragraph(
        f"{TR['score_soc_label']} : <b>{scores.social_score:.1f}/100</b>", styles["h2"]))

    soc_text = content.get("social",
        "La performance sociale englobe la gestion des ressources humaines, la diversité, "
        "la sécurité au travail, la formation et l'engagement avec les parties prenantes."
    )
    story.append(Paragraph(esc(soc_text), styles["body"]))

    soc = request.social
    soc_kpis = []
    if soc.total_employees is not None: soc_kpis.append((TR["kpit"]["employees"], f"{soc.total_employees:,}"))
    if soc.female_employees_percent is not None: soc_kpis.append((TR["kpit"]["women"], f"{soc.female_employees_percent:.1f}%"))
    if soc.employee_turnover_percent is not None: soc_kpis.append((TR["kpit"]["turnover"], f"{soc.employee_turnover_percent:.1f}%"))
    if soc.training_hours_per_employee is not None: soc_kpis.append((TR["kpit"]["training"], f"{soc.training_hours_per_employee:.0f}"))
    if soc.accident_frequency_rate is not None: soc_kpis.append((TR["kpit"]["accident"], f"{soc.accident_frequency_rate:.2f}"))
    if soc.customer_satisfaction_score is not None: soc_kpis.append((TR["kpit"]["satisfaction"], f"{soc.customer_satisfaction_score:.1f}"))

    if soc_kpis:
        story.append(Spacer(1, 0.3 * cm))
        story.append(kpi_table(soc_kpis, pal, ts))

    story.append(Spacer(1, 0.5 * cm))

    # ── Gouvernance ──────────────────────────────────────────────────────
    section_header(story, TR["pdf_s4"], pal["gov"], pal, styles, ts)
    story.append(Paragraph(
        f"{TR['score_gov_label']} : <b>{scores.governance_score:.1f}/100</b>", styles["h2"]))

    gov_text = content.get("governance",
        "La gouvernance évalue la qualité de la direction, l'indépendance du conseil, "
        "l'éthique des affaires, la cybersécurité et les mécanismes de contrôle interne."
    )
    story.append(Paragraph(esc(gov_text), styles["body"]))

    gov = request.governance
    gov_kpis = []
    if gov.board_members is not None: gov_kpis.append((TR["kpit"]["board"], str(gov.board_members)))
    if gov.female_board_percent is not None: gov_kpis.append((TR["kpit"]["women_board"], f"{gov.female_board_percent:.1f}%"))
    if gov.independent_board_percent is not None: gov_kpis.append((TR["kpit"]["independent"], f"{gov.independent_board_percent:.1f}%"))
    if gov.csr_budget_eur is not None: gov_kpis.append((TR["kpit"]["csr"], f"{gov.csr_budget_eur:,.0f}"))
    gov_kpis.append((TR["kpit"]["audit"], TR["kpit"]["yes"] if gov.esg_audit_conducted else (TR["kpit"]["no"] if gov.esg_audit_conducted is not None else TR["kpit"]["na"])))
    gov_kpis.append((TR["kpit"]["committee"], TR["kpit"]["yes"] if gov.sustainability_committee else (TR["kpit"]["no"] if gov.sustainability_committee is not None else TR["kpit"]["na"])))

    if gov_kpis:
        story.append(Spacer(1, 0.3 * cm))
        story.append(kpi_table(gov_kpis, pal, ts))

    story.append(PageBreak())

    # ── 5. Analyses de Durabilité (CSRD / ESRS) ───────────────────────────
    def _img(key, w_cm, h_cm, caption=None):
        if key in chart_images:
            try:
                im = Image(io.BytesIO(chart_images[key]), width=w_cm * cm, height=h_cm * cm)
                im.hAlign = 'CENTER'
                story.append(im)
                if caption:
                    story.append(Paragraph(caption, styles["caption"]))
                story.append(Spacer(1, 0.3 * cm))
            except Exception:
                pass

    section_header(story, TR["pdf_s5"], pal["secondary"], pal, styles, ts)

    story.append(Paragraph(TR["sub_materiality"], styles["h2"]))
    story.append(Paragraph(esc(content.get("materiality", "")), styles["body"]))
    _img("materiality", 11, 9.2, TR["cap_materiality"])

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(TR["sub_targets"], styles["h2"]))
    story.append(Paragraph(esc(content.get("targets", "")), styles["body"]))
    _img("targets", 15, 7.9, TR["cap_targets"])
    _img("carbon_trajectory", 15, 7.5, TR["cap_carbon"])

    if content.get("taxonomy"):
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph(TR["sub_taxonomy"], styles["h2"]))
        story.append(Paragraph(esc(content["taxonomy"]), styles["body"]))
        _img("taxonomy", 14, 6.3, TR["cap_taxonomy"])

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(TR["sub_climate"], styles["h2"]))
    story.append(Paragraph(esc(content.get("climate_risk", "")), styles["body"]))

    story.append(PageBreak())

    # ── Forces & Faiblesses ───────────────────────────────────────────────
    section_header(story, TR["pdf_s6"], pal["accent"], pal, styles, ts)

    story.append(Paragraph(TR["strengths_ident"], styles["h2"]))
    for s in scores.strengths:
        story.append(Paragraph(f"•  {esc(s)}", styles["bullet"]))

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(TR["weaknesses_axes"], styles["h2"]))
    for w in scores.weaknesses:
        story.append(Paragraph(f"–  {esc(w)}", styles["bullet"]))

    if request.include_recommendations:
        story.append(Spacer(1, 0.4 * cm))
        section_header(story, TR["pdf_s7"], pal["accent"], pal, styles, ts)
        for i, rec in enumerate(scores.recommendations, 1):
            story.append(Paragraph(f"<b>{i}.</b>  {esc(rec)}", styles["bullet"]))

    # ── Alignement référentiels ───────────────────────────────────────────
    story.append(Spacer(1, 0.5 * cm))
    section_header(story, TR["pdf_s8"], pal["secondary"], pal, styles, ts)

    ref_text = TR["ref_text"]
    story.append(Paragraph(ref_text, styles["body"]))

    # ── Section spécifique White Paper : Vision Stratégique ──────────────
    if request.report_type.value == "white_paper":
        story.append(Spacer(1, 0.5 * cm))
        section_header(story, TR["pdf_s9_wp"], pal["accent"], pal, styles, ts)
        story.append(Paragraph(TR["wp_intro"], styles["body"]))
        story.append(Spacer(1, 0.3 * cm))
        # Objectifs 2027
        obj_data = [
            [Paragraph("<b>" + TR["wp_horizon"].format(y=max(request.company.target_year, request.company.reporting_year + 1)) + "</b>",
                       ParagraphStyle("ot", fontSize=11, fontName=ts["font_bold"],
                                      textColor=pal["primary"]))],
        ]
        if request.language == "en":
            pillars_obj = [
                ("Environmental", f"Target E score: {min(100, scores.environmental_score + 15):.0f}/100 | +50% renewable | Scope 3 measured"),
                ("Social", f"Target S score: {min(100, scores.social_score + 10):.0f}/100 | 40% gender balance | 30h training/year"),
                ("Governance", f"Target G score: {min(100, scores.governance_score + 5):.0f}/100 | Annual audit | Sustainability committee"),
            ]
        else:
            pillars_obj = [
                ("Environnement", f"Score E cible : {min(100, scores.environmental_score + 15):.0f}/100 | +50% renouvelable | Scope 3 mesuré"),
                ("Social", f"Score S cible : {min(100, scores.social_score + 10):.0f}/100 | Parité 40% | 30h formation/an"),
                ("Gouvernance", f"Score G cible : {min(100, scores.governance_score + 5):.0f}/100 | Audit annuel | Comité durable"),
            ]
        for label, obj in pillars_obj:
            story.append(Paragraph(f"<b>• {label} :</b> {obj}", styles["bullet"]))


    # ── Conclusion ────────────────────────────────────────────────────────
    story.append(PageBreak())
    section_header(story, TR["pdf_concl_wp"] if request.report_type.value == "white_paper" else TR["pdf_concl"], pal["primary"], pal, styles, ts)

    conclusion = content.get("conclusion",
        f"{request.company.name} démontre une démarche ESG globale avec un score de "
        f"{scores.total_esg_score}/100 (note {scores.rating}). L'organisation s'engage "
        "à poursuivre ses efforts de transformation durable et à maintenir une transparence "
        "totale dans son reporting extra-financier, conformément aux meilleures pratiques internationales."
    )
    story.append(Paragraph(esc(conclusion), styles["body"]))

    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=pal["secondary"]))
    story.append(Paragraph(
        esc(f"© {request.company.reporting_year} {request.company.name} — " + TR["gen_auto"]),
        styles["footer"]))

    decor = page_decorator(pal, ts, request.company.name,
                           minimal=(ts["header"] == "minimal"),
                           footer_label=TR["rep_default"])
    doc.build(story, onFirstPage=decor, onLaterPages=decor)
    buf.seek(0)
    return buf.read()
