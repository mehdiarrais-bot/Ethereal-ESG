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


def pdf_cover(pal, ts, request, scores, TR, type_label, logo_bytes):
    """Couverture pleine page dessinée au canvas (éditoriale, full-bleed)."""
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.lib.utils import ImageReader
    fb, fi, f = ts["font_bold"], ts["font_italic"], ts["font"]
    band = ("high" if scores.total_esg_score >= 75 else "good" if scores.total_esg_score >= 60
            else "mid" if scores.total_esg_score >= 45 else "low")
    tagline = pdf_txt(TR["cover_tag_" + band])
    name = pdf_txt(request.company.name.upper())
    meta = pdf_txt(f"{TR['exercise']} {request.company.reporting_year}   |   "
                   f"{request.company.sector}   |   {request.company.country}")
    kicker = pdf_txt(type_label.upper())
    light = colors.HexColor("#C6CFDE")

    def draw(canvas, doc):
        w, h = A4
        canvas.saveState()
        canvas.setFillColor(pal["primary"]); canvas.rect(0, 0, w, h, fill=1, stroke=0)
        canvas.setFillColor(pal["accent"]); canvas.rect(0, 0, 0.22 * cm, h, fill=1, stroke=0)
        M = 2.4 * cm
        canvas.setFillColor(pal["accent"]); canvas.setFont(fb, 13)
        canvas.drawString(M, h - 3.2 * cm, kicker)
        # Nom ajusté à la largeur
        size, maxw = 42, w - M - 2 * cm
        while size > 20 and stringWidth(name, fb, size) > maxw:
            size -= 1
        canvas.setFillColor(colors.white); canvas.setFont(fb, size)
        canvas.drawString(M, h - 5.5 * cm, name)
        canvas.setFillColor(pal["accent"]); canvas.rect(M, h - 6.4 * cm, 3 * cm, 4, fill=1, stroke=0)
        canvas.setFillColor(light); canvas.setFont(fi, 15)
        canvas.drawString(M, h - 7.35 * cm, tagline)
        # Score mis en scène (bas gauche)
        sc = f"{scores.total_esg_score:.0f}"
        canvas.setFillColor(pal["accent"]); canvas.setFont(fb, 76)
        canvas.drawString(M, 4.2 * cm, sc)
        canvas.setFont(f, 16); canvas.setFillColor(light)
        canvas.drawString(M + stringWidth(sc, fb, 76) + 6, 4.45 * cm, "/100")
        # Libellé du chiffre-clé (lisibilité immédiate)
        canvas.setFillColor(pal["accent"]); canvas.setFont(fb, 9)
        _slbl = pdf_txt(TR.get("score_global_short", "Score Global").upper())
        canvas.drawString(M + stringWidth(sc, fb, 76) + 6, 4.05 * cm, _slbl)
        canvas.setFont(f, 10.5); canvas.setFillColor(light)
        canvas.drawString(M, 3.15 * cm, meta)
        # Référentiels de reporting (attendu d'un rapport professionnel)
        canvas.setFont(fb, 9); canvas.setFillColor(pal["accent"])
        canvas.drawString(M, 1.7 * cm, pdf_txt(TR["cover_refs"]))
        if request.company.presenter_name:
            pl = f"{TR['presented_by']} {request.company.presenter_name}"
            if request.company.presenter_title:
                pl += f" - {request.company.presenter_title}"
            canvas.setFont(fi, 10.5); canvas.drawString(M, 2.5 * cm, pdf_txt(pl))
        # Badge note (bas droite)
        bw, bh = 3.2 * cm, 1.5 * cm
        bx, by = w - 2 * cm - bw, 3.55 * cm
        canvas.setFillColor(pal["accent"]); canvas.roundRect(bx, by, bw, bh, 8, fill=1, stroke=0)
        canvas.setFillColor(pal["primary"]); canvas.setFont(fb, 36)
        rt = pdf_txt(scores.rating)
        canvas.drawString(bx + (bw - stringWidth(rt, fb, 36)) / 2, by + bh / 2 - 13, rt)
        # Logo (haut droite)
        if logo_bytes:
            try:
                ir = ImageReader(io.BytesIO(logo_bytes))
                iw, ih = ir.getSize(); ratio = iw / max(1, ih)
                lh = 1.7 * cm; lw = min(5 * cm, lh * ratio)
                canvas.drawImage(ir, w - 2 * cm - lw, h - 2.2 * cm - lh, lw, lh, mask='auto')
            except Exception:
                pass
        canvas.restoreState()
    return draw


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


def section_header(story, title, color, pal, styles, ts, icon=None):
    """Themed section heading: rule / banner / goldrule / minimal.
    `icon` : nom d'icône visual_kit (pictogramme de catégorie ESG)."""
    if ts["uppercase"]:
        title = title.upper()
    mode = ts["header"]

    if icon:
        try:
            from visual_kit import icon_png
            ic = Image(io.BytesIO(icon_png(icon, 96, "#" + color.hexval()[2:])),
                       width=0.75 * cm, height=0.75 * cm)
            head = Table([[ic, Paragraph(title, styles["h1"])]],
                         colWidths=[1.1 * cm, 15.9 * cm])
            head.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (0, 0), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            story.append(head)
            if mode == "goldrule":
                story.append(HRFlowable(width="100%", thickness=0.8, color=pal["accent"]))
            elif mode == "minimal":
                story.append(HRFlowable(width="30%", thickness=0.7,
                                        color=colors.HexColor("#BDBDBD"), hAlign='LEFT'))
            else:
                story.append(HRFlowable(width="100%", thickness=2, color=color))
            story.append(Spacer(1, 0.3 * cm))
            return
        except Exception:
            pass  # repli : en-tête standard sans icône
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


def insight_callout(story, text, color, pal, ts):
    """Encadré coloré « lecture métier » — le message clé de la section."""
    label = "LECTURE" if ts["font"] != "Times-Roman" else "LECTURE"
    cell = [
        Paragraph(esc(text), ParagraphStyle("ic", fontSize=10.5, fontName=ts["font"],
                  textColor=pal["text"], leading=15)),
    ]
    t = Table([cell], colWidths=[16.5 * cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), pal["light_bg"]),
        ('LINEBEFORE', (0, 0), (0, -1), 3, color),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3 * cm))


def pdf_divider(story, part_no, title, subtitle, pal, ts):
    """Carton de transition quasi pleine page (rythme éditorial)."""
    num = Paragraph(f'<font color="#{pal["accent"].hexval()[2:]}">{esc(part_no)}</font>',
                    ParagraphStyle("dn", fontSize=90, fontName=ts["font_bold"], leading=96))
    ttl = Paragraph(esc(title).upper(), ParagraphStyle("dt", fontSize=30, fontName=ts["font_bold"],
                    textColor=colors.white, leading=34, spaceBefore=8))
    sub = Paragraph(esc(subtitle), ParagraphStyle("ds", fontSize=13, fontName=ts["font_italic"],
                    textColor=colors.HexColor("#C6CFDE"), leading=18, spaceBefore=10))
    cell = [Spacer(1, 6.5 * cm), num, ttl,
            HRFlowable(width="22%", thickness=3, color=pal["accent"], hAlign='LEFT',
                       spaceBefore=10, spaceAfter=6), sub]
    t = Table([[cell]], colWidths=[17 * cm], rowHeights=[20.5 * cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), pal["primary"]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('LINEBEFORE', (0, 0), (0, -1), 8, pal["accent"]),
    ]))
    story.append(PageBreak())
    story.append(t)
    story.append(PageBreak())


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

    _status_hex = {"good": "#2E7D32", "warn": "#D97706", "bad": "#E74C3C"}
    data, row = [], []
    for item in kpi_list:
        label, value = item[0], item[1]
        status = item[2] if len(item) > 2 else None
        val_markup = esc(value)
        if status in _status_hex:
            # pastille de statut (• = 0x95 WinAnsi) devant la valeur
            val_markup = f'<font color="{_status_hex[status]}" size="11">•</font> {val_markup}'
        row.append([Paragraph(esc(label).upper(), label_style),
                    Spacer(1, 3),
                    Paragraph(val_markup, value_style)])
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
    from content_generator import pillar_insights
    _pi = pillar_insights(request, scores)

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

    # Couverture pleine page (dessinée au canvas via onFirstPage) → contenu page 2
    story.append(PageBreak())
    add_heading_ez = None  # (placeholder, no-op)

    # ── Page 2 : « ESG en un coup d'œil » ─────────────────────────────────
    story.append(Paragraph(esc(type_label), styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=2, color=pal["accent"]))
    story.append(Spacer(1, 0.35 * cm))

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

    # ── Sommaire structuré par actes (repère de lecture) ──────────────────
    _toc_parts = [
        ("01", TR["toc_part1"], [TR["pdf_s1"], TR["pdf_s2"], TR["pdf_s3"], TR["pdf_s4"], TR["pdf_s5"]]),
        ("02", TR["toc_part2"], [TR["pdf_s6"], TR["pdf_diag"]]),
        ("03", TR["toc_part3"], [TR["pdf_s7"], TR["roadmap_title"], TR["pdf_s8"], TR["pdf_concl"]]),
    ]
    _tnum = ParagraphStyle("tn", fontSize=26, fontName=ts["font_bold"],
                           textColor=pal["accent"], leading=28)
    _tact = ParagraphStyle("ta", fontSize=10.5, fontName=ts["font_bold"],
                           textColor=pal["primary"], leading=13, spaceBefore=2, spaceAfter=6)
    _titem = ParagraphStyle("ti", fontSize=8, fontName=ts["font"],
                            textColor=pal["text"], leading=11.5)
    toc_cells = []
    for num, act, items in _toc_parts:
        cell = [Paragraph(num, _tnum), Paragraph(esc(act).upper(), _tact)]
        for it in items:
            cell.append(Paragraph(f'<font color="#{pal["accent"].hexval()[2:]}">—</font>  {esc(it)}', _titem))
        toc_cells.append(cell)
    toc_tbl = Table([toc_cells], colWidths=[5.66 * cm] * 3)
    toc_tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), pal["light_bg"]),
        ('LINEABOVE', (0, 0), (-1, 0), 2.5, pal["accent"]),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.white),
    ]))
    story.append(Paragraph(TR["toc_title"].upper() if ts["uppercase"] else TR["toc_title"],
                           styles["h2"]))
    story.append(toc_tbl)
    story.append(Spacer(1, 0.55 * cm))

    # ── Mot de la direction (citation éditoriale) ─────────────────────────
    if request.company.ceo_quote:
        _q = request.company.ceo_quote.strip().strip('"“”')
        _qtxt = f"« {_q} »" if request.language != "en" else f"“{_q}”"
        q_flow = [
            Paragraph(TR["quote_kicker"], ParagraphStyle(
                "qk", fontSize=8.5, fontName=ts["font_bold"],
                textColor=pal["accent"], spaceAfter=8)),
            Paragraph(esc(_qtxt), ParagraphStyle(
                "qt", fontSize=13, fontName=ts["font_italic"],
                textColor=colors.white, leading=19)),
        ]
        if request.company.presenter_name:
            _attrib = request.company.presenter_name
            if request.company.presenter_title:
                _attrib += f" — {request.company.presenter_title}"
            q_flow.append(Paragraph(esc(_attrib), ParagraphStyle(
                "qa", fontSize=9.5, fontName=ts["font_bold"],
                textColor=colors.HexColor("#C6CFDE"), spaceBefore=10)))
        q_tbl = Table([[q_flow]], colWidths=[17 * cm])
        q_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), pal["primary"]),
            ('LINEBEFORE', (0, 0), (0, -1), 5, pal["accent"]),
            ('LEFTPADDING', (0, 0), (-1, -1), 18),
            ('RIGHTPADDING', (0, 0), (-1, -1), 18),
            ('TOPPADDING', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
        ]))
        story.append(q_tbl)
        story.append(Spacer(1, 0.55 * cm))

    # ── Executive Summary ──────────────────────────────────────────────────
    section_header(story, TR["pdf_s1"], pal["secondary"], pal, styles, ts)

    exec_text = content.get("executive_summary",
        f"{request.company.name} présente son rapport ESG pour l'exercice {request.company.reporting_year}. "
        f"L'analyse des données extra-financières révèle un score ESG global de {scores.total_esg_score}/100, "
        f"correspondant à une notation {scores.rating}. Ce résultat reflète les engagements de l'entreprise "
        "en matière de responsabilité environnementale, sociale et de gouvernance d'entreprise."
    )
    story.append(Paragraph(esc(exec_text), styles["body"]))
    story.append(Spacer(1, 0.35 * cm))

    # ── Digest décisionnel (forces / axes / risques / opportunités) ───────
    from content_generator import risks_opportunities as _ro_fn, enriched_recommendations as _er_fn
    _dg_ro = _ro_fn(request, scores)
    _dg_recs = _er_fn(request, scores)[:3]
    _red = colors.HexColor("#E74C3C")

    def _digest_cell(head, items, col):
        hexc = "#" + col.hexval()[2:]
        flow = [Paragraph(f'<font color="{hexc}"><b>{esc(head).upper()}</b></font>',
                          ParagraphStyle("dgh", fontSize=8.5, fontName=ts["font_bold"], spaceAfter=4))]
        for it in items[:2]:
            flow.append(Paragraph(f'<font color="{hexc}">•</font>  {esc(it)}',
                        ParagraphStyle("dgi", fontSize=8, fontName=ts["font"],
                                       textColor=pal["text"], leading=10.5, spaceAfter=3)))
        return flow

    dg_tbl = Table([[
        _digest_cell(TR["digest_strengths"], scores.strengths, pal["env"]),
        _digest_cell(TR["digest_weak"], scores.weaknesses, _red),
    ], [
        _digest_cell(TR["digest_risks"], [r["text"] for r in _dg_ro["risks"]], _red),
        _digest_cell(TR["digest_opps"], [o["text"] for o in _dg_ro["opportunities"]], pal["env"]),
    ]], colWidths=[8.25 * cm, 8.25 * cm])
    dg_tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), pal["light_bg"]),
        ('INNERGRID', (0, 0), (-1, -1), 2, colors.white),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(dg_tbl)
    if _dg_recs:
        act_line = "   ".join(f"{i}. {r['title']}" for i, r in enumerate(_dg_recs, 1))
        story.append(Spacer(1, 0.15 * cm))
        story.append(Paragraph(
            f'<b>{esc(TR["digest_actions"]).upper()}</b>  —  {esc(act_line)}',
            ParagraphStyle("dga", fontSize=8, fontName=ts["font"], textColor=pal["primary"],
                           leading=11, backColor=pal["light_bg"], borderPadding=6)))
    story.append(Spacer(1, 0.5 * cm))

    # ── Environnement ─────────────────────────────────────────────────────
    section_header(story, TR["pdf_s2"], pal["env"], pal, styles, ts, icon="leaf")
    story.append(Paragraph(
        f"{TR['score_env_label']} : <b>{scores.environmental_score:.1f}/100</b>", styles["h2"]))
    insight_callout(story, _pi["env"], pal["env"], pal, ts)

    env_text = content.get("environmental",
        "L'analyse environnementale couvre les émissions de gaz à effet de serre, "
        "la consommation d'énergie et d'eau, la gestion des déchets et les initiatives biodiversité."
    )
    story.append(Paragraph(esc(env_text), styles["body"]))

    env = request.environmental
    def _st(v, good, warn, higher_better=True):
        """Statut d'un KPI : seuils good/warn (sens configurable)."""
        if v is None:
            return None
        ok = (v >= good) if higher_better else (v <= good)
        mid = (v >= warn) if higher_better else (v <= warn)
        return "good" if ok else ("warn" if mid else "bad")

    env_kpis = []
    if env.co2_emissions_tonnes is not None:
        _ci = (env.co2_emissions_tonnes / request.company.revenue_eur * 1e6
               if request.company.revenue_eur else None)
        env_kpis.append((TR["kpit"]["co2"], f"{env.co2_emissions_tonnes:,.0f}",
                         _st(_ci, 30, 100, higher_better=False)))
    if env.renewable_energy_percent is not None:
        env_kpis.append((TR["kpit"]["renewable"], f"{env.renewable_energy_percent:.1f}%",
                         _st(env.renewable_energy_percent, 50, 30)))
    if env.energy_consumption_mwh is not None: env_kpis.append((TR["kpit"]["energy"], f"{env.energy_consumption_mwh:,.0f}"))
    if env.water_consumption_m3 is not None: env_kpis.append((TR["kpit"]["water"], f"{env.water_consumption_m3:,.0f}"))
    if env.waste_recycled_percent is not None:
        env_kpis.append((TR["kpit"]["recycling"], f"{env.waste_recycled_percent:.1f}%",
                         _st(env.waste_recycled_percent, 60, 40)))
    if env.scope1_emissions is not None: env_kpis.append((TR["kpit"]["s1"], f"{env.scope1_emissions:,.0f}"))
    if env.scope2_emissions is not None: env_kpis.append((TR["kpit"]["s2"], f"{env.scope2_emissions:,.0f}"))
    if env.scope3_emissions is not None:
        env_kpis.append((TR["kpit"]["s3"], f"{env.scope3_emissions:,.0f}", "good"))

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
    section_header(story, TR["pdf_s3"], pal["social"], pal, styles, ts, icon="people")
    story.append(Paragraph(
        f"{TR['score_soc_label']} : <b>{scores.social_score:.1f}/100</b>", styles["h2"]))
    insight_callout(story, _pi["social"], pal["social"], pal, ts)

    soc_text = content.get("social",
        "La performance sociale englobe la gestion des ressources humaines, la diversité, "
        "la sécurité au travail, la formation et l'engagement avec les parties prenantes."
    )
    story.append(Paragraph(esc(soc_text), styles["body"]))

    soc = request.social
    soc_kpis = []
    if soc.total_employees is not None: soc_kpis.append((TR["kpit"]["employees"], f"{soc.total_employees:,}"))
    if soc.female_employees_percent is not None:
        soc_kpis.append((TR["kpit"]["women"], f"{soc.female_employees_percent:.1f}%",
                         _st(soc.female_employees_percent, 40, 35)))
    if soc.employee_turnover_percent is not None:
        soc_kpis.append((TR["kpit"]["turnover"], f"{soc.employee_turnover_percent:.1f}%",
                         _st(soc.employee_turnover_percent, 10, 20, higher_better=False)))
    if soc.training_hours_per_employee is not None:
        soc_kpis.append((TR["kpit"]["training"], f"{soc.training_hours_per_employee:.0f}",
                         _st(soc.training_hours_per_employee, 20, 10)))
    if soc.accident_frequency_rate is not None:
        soc_kpis.append((TR["kpit"]["accident"], f"{soc.accident_frequency_rate:.2f}",
                         _st(soc.accident_frequency_rate, 2, 5, higher_better=False)))
    if soc.customer_satisfaction_score is not None:
        soc_kpis.append((TR["kpit"]["satisfaction"], f"{soc.customer_satisfaction_score:.1f}",
                         _st(soc.customer_satisfaction_score, 8, 6)))

    if soc_kpis:
        story.append(Spacer(1, 0.3 * cm))
        story.append(kpi_table(soc_kpis, pal, ts))

    story.append(Spacer(1, 0.5 * cm))

    # ── Gouvernance ──────────────────────────────────────────────────────
    section_header(story, TR["pdf_s4"], pal["gov"], pal, styles, ts, icon="scale")
    story.append(Paragraph(
        f"{TR['score_gov_label']} : <b>{scores.governance_score:.1f}/100</b>", styles["h2"]))
    insight_callout(story, _pi["gov"], pal["gov"], pal, ts)

    gov_text = content.get("governance",
        "La gouvernance évalue la qualité de la direction, l'indépendance du conseil, "
        "l'éthique des affaires, la cybersécurité et les mécanismes de contrôle interne."
    )
    story.append(Paragraph(esc(gov_text), styles["body"]))

    gov = request.governance
    gov_kpis = []
    if gov.board_members is not None: gov_kpis.append((TR["kpit"]["board"], str(gov.board_members)))
    if gov.female_board_percent is not None:
        gov_kpis.append((TR["kpit"]["women_board"], f"{gov.female_board_percent:.1f}%",
                         _st(gov.female_board_percent, 40, 30)))
    if gov.independent_board_percent is not None:
        gov_kpis.append((TR["kpit"]["independent"], f"{gov.independent_board_percent:.1f}%",
                         _st(gov.independent_board_percent, 50, 33)))
    if gov.csr_budget_eur is not None: gov_kpis.append((TR["kpit"]["csr"], f"{gov.csr_budget_eur:,.0f}"))
    gov_kpis.append((TR["kpit"]["audit"],
                     TR["kpit"]["yes"] if gov.esg_audit_conducted else (TR["kpit"]["no"] if gov.esg_audit_conducted is not None else TR["kpit"]["na"]),
                     "good" if gov.esg_audit_conducted else ("bad" if gov.esg_audit_conducted is not None else None)))
    gov_kpis.append((TR["kpit"]["committee"],
                     TR["kpit"]["yes"] if gov.sustainability_committee else (TR["kpit"]["no"] if gov.sustainability_committee is not None else TR["kpit"]["na"]),
                     "good" if gov.sustainability_committee else ("bad" if gov.sustainability_committee is not None else None)))

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
    _img("materiality", 16.5, 9.5, TR["cap_materiality"])

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

    # ── ACTE 1 — Diagnostic ───────────────────────────────────────────────
    pdf_divider(story, "01", TR["div1_title"], TR["div1_sub"], pal, ts)

    # ── Forces & Faiblesses ───────────────────────────────────────────────
    section_header(story, TR["pdf_s6"], pal["accent"], pal, styles, ts)

    story.append(Paragraph(TR["strengths_ident"], styles["h2"]))
    for s in scores.strengths:
        story.append(Paragraph(f"•  {esc(s)}", styles["bullet"]))

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(TR["weaknesses_axes"], styles["h2"]))
    for w in scores.weaknesses:
        story.append(Paragraph(f"–  {esc(w)}", styles["bullet"]))

    # ── Diagnostic stratégique : benchmark sectoriel + maturité + R&O ─────
    from content_generator import benchmark_verdict, maturity_text, risks_opportunities
    _bv = benchmark_verdict(request, scores)
    _bm = _bv["bm"]
    _mt = maturity_text(request, scores)
    _ro = risks_opportunities(request, scores)
    _red = colors.HexColor("#E74C3C")

    story.append(PageBreak())
    section_header(story, TR["pdf_diag"], pal["primary"], pal, styles, ts)

    story.append(Paragraph(esc(_bv["title"]), styles["h2"]))
    story.append(Paragraph(TR["pdf_bench_sub"], styles["caption"]))
    story.append(Spacer(1, 0.2 * cm))

    _hstyle = ParagraphStyle("bh", fontSize=9, fontName=ts["font_bold"], textColor=colors.white, alignment=TA_CENTER)
    _cstyle = ParagraphStyle("bc", fontSize=9.5, fontName=ts["font"], textColor=pal["text"], alignment=TA_CENTER)
    _lstyle = ParagraphStyle("bl", fontSize=9.5, fontName=ts["font_bold"], textColor=pal["primary"])
    comp = {"env": scores.environmental_score, "social": scores.social_score,
            "gov": scores.governance_score, "global": scores.total_esg_score}
    pil_lbl = [("env", TR["pillar_env"]), ("social", TR["pillar_soc"]),
               ("gov", TR["pillar_gov"]), ("global", TR.get("score_global_short", "Global"))]
    bench_rows = [[Paragraph(TR["bench_metric_col"], _hstyle), Paragraph(TR["bench_you"], _hstyle),
                   Paragraph(TR["bench_sector"], _hstyle), Paragraph(TR["bench_delta_col"], _hstyle)]]
    for key, lbl in pil_lbl:
        d = _bm["deltas"][key]
        dcol = "#2E7D32" if d >= 0 else "#E74C3C"
        sign = "+" if d >= 0 else ""
        bench_rows.append([
            Paragraph(esc(lbl), _lstyle),
            Paragraph(f"{comp[key]:.0f}", _cstyle),
            Paragraph(f"{_bm['avg'][key]:.0f}", _cstyle),
            Paragraph(f'<font color="{dcol}"><b>{sign}{d:.0f}</b></font>', _cstyle),
        ])
    bt = Table(bench_rows, colWidths=[7 * cm, 3.2 * cm, 3.2 * cm, 3.1 * cm])
    bt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), pal["primary"]),
        ('BACKGROUND', (0, 1), (-1, -1), pal["light_bg"]),
        ('BACKGROUND', (0, -1), (-1, -1), pal["accent"]),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (0, -1), 10),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
    ]))
    story.append(bt)
    story.append(Spacer(1, 0.3 * cm))
    insight_callout(story, _bv["insight"], pal["accent"], pal, ts)

    _mat_lbl = TR.get("mat_" + _mt.get("key", "structured"), "")
    story.append(Paragraph(f'{esc(TR["pdf_maturity_sub"])} : <b>{esc(_mat_lbl)}</b> '
                           f'({_mt["stage"]}/5)', styles["h2"]))
    story.append(Paragraph(esc(_mt["next_hint"]), styles["body"]))
    story.append(Spacer(1, 0.4 * cm))

    # ── Analyse des écarts réglementaires (conforme / partiel / non conforme)
    from content_generator import compliance_assessment
    _gaps = compliance_assessment(request, scores)
    story.append(Paragraph(TR["gap_title"], styles["h2"]))
    _st_col = {"ok": "#2E7D32", "partial": "#D97706", "no": "#E74C3C", "na": "#7F8C8D"}
    _st_lbl = {"ok": TR["st_ok"], "partial": TR["st_partial"], "no": TR["st_no"], "na": TR["st_na"]}
    _gh = ParagraphStyle("gh", fontSize=8.5, fontName=ts["font_bold"], textColor=colors.white)
    _gc = ParagraphStyle("gc", fontSize=8.5, fontName=ts["font"], textColor=pal["text"], leading=11)
    _gb = ParagraphStyle("gb", fontSize=8.5, fontName=ts["font_bold"], textColor=pal["primary"], leading=11)
    gap_rows = [[Paragraph(TR["gap_req"], _gh), Paragraph(TR["gap_ref"], _gh),
                 Paragraph(TR["gap_status"], _gh), Paragraph(TR["gap_note"], _gh)]]
    for g in _gaps:
        gap_rows.append([
            Paragraph(esc(g["req"]), _gb),
            Paragraph(esc(g["ref"]), _gc),
            Paragraph(f'<font color="{_st_col[g["status"]]}"><b>• {esc(_st_lbl[g["status"]])}</b></font>', _gc),
            Paragraph(esc(g["note"]), _gc),
        ])
    gap_tbl = Table(gap_rows, colWidths=[5.4 * cm, 3.1 * cm, 2.8 * cm, 5.2 * cm])
    gap_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), pal["primary"]),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [pal["light_bg"], colors.white]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor("#E0E0E0")),
    ]))
    story.append(gap_tbl)
    story.append(Spacer(1, 0.45 * cm))

    # ── Risques : tableau impact / probabilité / priorité ────────────────
    story.append(Paragraph(TR["risks_head"], styles["h2"]))
    _prio_col = {"P1": "#E74C3C", "P2": "#D97706", "P3": "#7F8C8D"}
    _rc = ParagraphStyle("rc", fontSize=8.5, fontName=ts["font"], textColor=pal["text"],
                         leading=11, alignment=TA_CENTER)
    risk_rows = [[Paragraph(TR["risk_desc"], _gh), Paragraph(TR["risk_impact"], _gh),
                  Paragraph(TR["risk_lik"], _gh), Paragraph(TR["risk_prio"], _gh)]]
    for it in _ro["risks"]:
        pr = it.get("priority", "P2")
        risk_rows.append([
            Paragraph(f'<b>{esc(it["tag"])}</b> — {esc(it["text"])}',
                      ParagraphStyle("rd2", fontSize=8.5, fontName=ts["font"],
                                     textColor=pal["text"], leading=11)),
            Paragraph(esc(it.get("impact", "—")), _rc),
            Paragraph(esc(it.get("likelihood", "—")), _rc),
            Paragraph(f'<font color="{_prio_col[pr]}"><b>{pr}</b></font>', _rc),
        ])
    risk_tbl = Table(risk_rows, colWidths=[9.9 * cm, 2.4 * cm, 2.4 * cm, 1.8 * cm])
    risk_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), _red),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [pal["light_bg"], colors.white]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor("#E0E0E0")),
    ]))
    story.append(risk_tbl)
    story.append(Spacer(1, 0.35 * cm))

    # ── Opportunités : encadré synthétique ───────────────────────────────
    opp_flow = [Paragraph(f'<font color="#{pal["env"].hexval()[2:]}"><b>{esc(TR["opps_head"]).upper()}</b></font>',
                          ParagraphStyle("oh", fontSize=10.5, fontName=ts["font_bold"], spaceAfter=6))]
    for it in _ro["opportunities"]:
        opp_flow.append(Paragraph(
            f'<font color="#{pal["env"].hexval()[2:]}"><b>{esc(it["tag"])}</b></font> — {esc(it["text"])}',
            ParagraphStyle("oi", fontSize=9, fontName=ts["font"], textColor=pal["text"],
                           leading=12, spaceAfter=5)))
    ro_table = Table([[opp_flow]], colWidths=[16.5 * cm])
    ro_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), pal["light_bg"]),
        ('LINEBEFORE', (0, 0), (0, -1), 3, pal["env"]),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(ro_table)

    # ── ACTE 2 — Plan d'action ────────────────────────────────────────────
    pdf_divider(story, "02", TR["div2_title"], TR["div2_sub"], pal, ts)

    if request.include_recommendations:
        from content_generator import enriched_recommendations
        story.append(Spacer(1, 0.4 * cm))
        section_header(story, TR["pdf_s7"], pal["accent"], pal, styles, ts)
        pcol = {"env": pal["env"], "social": pal["social"], "gov": pal["gov"]}
        rows = []
        for i, rec in enumerate(enriched_recommendations(request, scores), 1):
            c = pcol.get(rec["pillar"], pal["secondary"])
            hexc = "#" + c.hexval()[2:]
            num = Paragraph(f'<font color="{hexc}"><b>{i}</b></font>', ParagraphStyle(
                "rn", fontSize=17, fontName=ts["font_bold"], alignment=TA_CENTER))
            body = [
                Paragraph(f'<b>{esc(rec["title"])}</b>',
                          ParagraphStyle("rt", fontSize=10, fontName=ts["font_bold"],
                                         textColor=pal["primary"], spaceAfter=2, leading=12.5)),
                Paragraph(esc(rec["detail"]), ParagraphStyle(
                    "rd", fontSize=8.5, fontName=ts["font"], textColor=pal["text"], leading=11)),
            ]
            meta_cell = [
                Paragraph(f'<font color="{hexc}"><b>{esc(rec.get("objective", ""))}</b></font>',
                          ParagraphStyle("ro", fontSize=8.5, fontName=ts["font"], leading=11, spaceAfter=3)),
                Paragraph(f'{esc(rec.get("owner", ""))}  ·  {esc(rec["horizon"])}',
                          ParagraphStyle("rw", fontSize=8, fontName=ts["font"],
                                         textColor=colors.HexColor("#7F8C8D"), leading=10.5)),
            ]
            rows.append([num, body, meta_cell])
        # Matrice de priorisation effort/impact (les numéros renvoient au tableau)
        if "priority" in chart_images:
            try:
                from content_generator import priority_reading
                pimg = Image(io.BytesIO(chart_images["priority"]), width=16.5 * cm, height=9.5 * cm)
                pimg.hAlign = 'CENTER'
                story.append(pimg)
                story.append(Paragraph(TR["cap_prio"], styles["caption"]))
                story.append(Spacer(1, 0.25 * cm))
                insight_callout(story, priority_reading(request, scores), pal["accent"], pal, ts)
            except Exception as e:
                print(f"Priority image error: {e}")
        _gh0 = ParagraphStyle("rh0", fontSize=8.5, fontName=ts["font_bold"], textColor=colors.white)
        _due = "Due" if request.language == "en" else "Échéance"
        rows.insert(0, ["", Paragraph("Action", _gh0),
                        Paragraph(f'{TR["objective_col"]}  ·  {TR["owner_col"]}  ·  {_due}', _gh0)])
        rec_table = Table(rows, colWidths=[1.2 * cm, 9.8 * cm, 5.5 * cm])
        rec_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor("#E0E0E0")),
            ('BACKGROUND', (0, 0), (-1, -1), pal["light_bg"]),
            ('BACKGROUND', (0, 0), (-1, 0), pal["primary"]),
            ('TOPPADDING', (0, 0), (-1, 0), 5),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
            ('LEFTPADDING', (1, 0), (1, -1), 6),
        ]))
        story.append(rec_table)

    # ── Feuille de route 12 mois (3 phases) ───────────────────────────────
    from content_generator import roadmap_12m
    _rm = roadmap_12m(request, scores)
    if any(ph["actions"] for ph in _rm):
        _pcol = {"env": pal["env"], "social": pal["social"], "gov": pal["gov"]}
        story.append(Spacer(1, 0.5 * cm))
        section_header(story, TR["roadmap_title"], pal["accent"], pal, styles, ts)
        _phead = ParagraphStyle("ph", fontSize=10.5, fontName=ts["font_bold"],
                                textColor=colors.white, alignment=TA_CENTER)
        _psub = ParagraphStyle("ps", fontSize=7.5, fontName=ts["font"],
                               textColor=colors.HexColor("#E8E8E8"), alignment=TA_CENTER)
        head_cells, body_cells = [], []
        for ph in _rm:
            head_cells.append([Paragraph(esc(ph["label"]), _phead),
                               Paragraph(esc(ph["sub"]), _psub)])
            acts = []
            for act in ph["actions"][:4]:
                hexc = "#" + _pcol.get(act["pillar"], pal["secondary"]).hexval()[2:]
                qw = f' <font color="#{pal["accent"].hexval()[2:]}" size="6"><b>[{esc(TR["quick_win"])}]</b></font>' if act["quick_win"] else ""
                acts.append(Paragraph(f'<font color="{hexc}">▪</font> {esc(act["title"])}{qw}',
                            ParagraphStyle("ra", fontSize=8.5, fontName=ts["font"],
                                           textColor=pal["text"], leading=11, spaceAfter=5)))
            body_cells.append(acts)
        cw = [5.5 * cm, 5.5 * cm, 5.5 * cm]
        htbl = Table([head_cells], colWidths=cw)
        htbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), pal["primary"]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.white),
        ]))
        btbl = Table([body_cells], colWidths=cw)
        btbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), pal["light_bg"]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.white),
        ]))
        story.append(htbl)
        story.append(btbl)

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

    # ── Note méthodologique (annexe : périmètre, référentiels, limites) ───
    if content.get("methodology"):
        story.append(Spacer(1, 0.6 * cm))
        story.append(Paragraph(TR["pdf_methodo"], styles["h2"]))
        meth = Table([[Paragraph(esc(content["methodology"]),
                                 ParagraphStyle("mn", fontSize=8.5, fontName=ts["font"],
                                                textColor=pal["text"], leading=12.5,
                                                alignment=TA_JUSTIFY))]],
                     colWidths=[16.5 * cm])
        meth.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), pal["light_bg"]),
            ('LINEBEFORE', (0, 0), (0, -1), 2.5, pal["secondary"]),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(meth)

    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=pal["secondary"]))
    story.append(Paragraph(
        esc(f"© {request.company.reporting_year} {request.company.name} — " + TR["gen_auto"]),
        styles["footer"]))

    decor = page_decorator(pal, ts, request.company.name,
                           minimal=(ts["header"] == "minimal"),
                           footer_label=TR["rep_default"])
    cover_draw = pdf_cover(pal, ts, request, scores, TR, type_label, logo_bytes)
    doc.build(story, onFirstPage=cover_draw, onLaterPages=decor)
    buf.seek(0)
    return buf.read()
