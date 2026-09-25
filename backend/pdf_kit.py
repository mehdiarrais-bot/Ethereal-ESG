"""Boîte à outils graphique des livrables PDF (rapport, synthèse une page).

Convertit un gabarit de report_designs en objets ReportLab : couleurs,
polices embarquées, photos recadrées, et fournit les primitives de dessin
partagées (texte espacé, image « cover », radar, en-têtes, pieds de page).

Les maquettes sources sont dessinées sur une page de 794 × 1123 px (A4 à
96 dpi). `Px` reprend ce repère — origine en haut à gauche, unités en px —
pour que les pages composées au canevas restent fidèles aux maquettes :
1 px = 0,75 pt.
"""
import io
import math
import os
import sys
from functools import lru_cache

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable, Paragraph

from report_designs import design, CLIENT_PHOTO_SLOTS
from models import decode_logo

PAGE_W, PAGE_H = A4
PX = PAGE_W / 794.0  # 1 px maquette -> points PDF

_FALLBACK_SANS = {"Light": "Helvetica", "Regular": "Helvetica",
                  "SemiBold": "Helvetica-Bold", "Italic": "Helvetica-Oblique"}
_FALLBACK_SERIF = {"Light": "Times-Roman", "Regular": "Times-Roman",
                   "SemiBold": "Times-Bold", "Italic": "Times-Italic"}
SERIF_FAMILIES = {"Newsreader", "InstrumentSerif", "LibreCaslonText"}


def assets_dir() -> str:
    """Dossier des polices et photos, en développement comme dans l'exécutable."""
    if getattr(sys, "frozen", False):
        return os.path.join(getattr(sys, "_MEIPASS"), "assets")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


@lru_cache(maxsize=None)
def font_family(family: str) -> dict:
    """Enregistre une famille embarquée ; repli base-14 si fichiers absents.
    Retourne {Light, Regular, SemiBold, Italic} -> nom de police ReportLab."""
    fallback = _FALLBACK_SERIF if family in SERIF_FAMILIES else _FALLBACK_SANS
    out = {}
    for style in ("Light", "Regular", "SemiBold", "Italic"):
        path = os.path.join(assets_dir(), "fonts", family, f"{family}-{style}.ttf")
        name = f"{family}-{style}"
        try:
            if name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(name, path))
            out[style] = name
        except Exception:
            out[style] = fallback[style]
    return out


def font_path(family: str, style: str = "Regular") -> str | None:
    """Chemin TTF d'une famille embarquée (pour matplotlib), None si absent."""
    p = os.path.join(assets_dir(), "fonts", family, f"{family}-{style}.ttf")
    return p if os.path.isfile(p) else None


@lru_cache(maxsize=None)
def bank_photo(name: str) -> bytes | None:
    path = os.path.join(assets_dir(), "photos", f"{name}.jpg")
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError:
        return None


# Glyphes absents des polices base-14 ou de nos sous-ensembles latins
_PDF_CHARS = str.maketrans({
    '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
    '⁰': '0', '✓': '+', '✗': 'x', '✅': '', '⚠': '',
    '️': '', '█': '', '░': '',
})


def clean(v) -> str:
    """Texte sûr pour les polices : glyphes indisponibles translittérés,
    nombres à la typographie de la langue du livrable (typo.py)."""
    from typo import fix
    s = fix(str(v)).translate(_PDF_CHARS)
    return s.encode('cp1252', 'ignore').decode('cp1252')


def esc(v) -> str:
    from xml.sax.saxutils import escape
    return escape(clean(v))


def hexc(c: colors.Color) -> str:
    return "#" + c.hexval()[2:]


def _lum(c: colors.Color) -> float:
    return 0.2126 * c.red + 0.7152 * c.green + 0.0722 * c.blue


class Kit:
    """Gabarit résolu pour une requête : couleurs, polices, photos."""

    def __init__(self, request):
        self.request = request
        self.d = design(request.aesthetic_theme)
        self.layout = self.d["layout"]
        self.c = {k: colors.HexColor(v) for k, v in self.d["colors"].items()}
        self._apply_brand(getattr(request, "custom_colors", None))
        disp = font_family(self.d["fonts"]["display"])
        body = font_family(self.d["fonts"]["body"])
        dw = self.d["fonts"].get("display_weight", "Regular")
        self.f = {
            "display": disp[dw], "display_i": disp["Italic"],
            "display_b": disp["SemiBold"],
            "body": body["Regular"], "body_l": body["Light"],
            "body_b": body["SemiBold"], "body_i": body["Italic"],
        }
        # Titres en italique (gabarit Annuel)
        self.title_font = self.f["display_i"] if self.d["fonts"].get("display_italic") \
            else self.f["display"]
        self.logo = decode_logo(request.company.logo_base64)
        self._client_photos = {}
        for slot, url in (getattr(request, "report_photos", None) or {}).items():
            raw = decode_logo(url)
            if raw and slot in CLIENT_PHOTO_SLOTS:
                self._client_photos[slot] = raw

    def _apply_brand(self, custom):
        if not custom:
            return
        from branding import validate_colors
        v = validate_colors(custom)
        if not v:
            return
        p, a = v
        prim = colors.Color(*[x / 255 for x in p])
        acc = colors.Color(*[x / 255 for x in a])
        self.c["primary"] = prim
        self.c["accent_on_primary"] = acc
        # l'accent est posé sur le papier clair : il doit rester lisible
        if _lum(acc) > 0.55:
            acc = colors.Color(acc.red * 0.62, acc.green * 0.62, acc.blue * 0.62)
        self.c["accent"] = acc

    # -- photos ---------------------------------------------------------
    def photo(self, slot: str) -> bytes | None:
        """Photo client de l'emplacement, sinon photo de la banque : pour la
        couverture, celle du secteur du client (sector-<famille>.jpg) si sa
        famille est reconnue, sinon celle du gabarit."""
        if slot in self._client_photos:
            return self._client_photos[slot]
        if slot == "cover" and "cover" in self.d["photos"]:
            from analysis import family
            fam = family(self.request.company.sector)
            sector = bank_photo(f"sector-{fam}") if fam != "general" else None
            if sector:
                return sector
        name = self.d["photos"].get(slot)
        return bank_photo(name) if name else None

    def has_client_photo(self, slot: str) -> bool:
        return slot in self._client_photos

    def uses_bank(self, slots=("cover", "environment")) -> bool:
        """Une photo d'illustration de la banque apparaît-elle ? (mention
        obligatoire dans la note méthodologique). Par défaut : couverture et
        environnement, les deux seuls emplacements comblés par la banque."""
        return any(s in self.d["photos"] and not self.has_client_photo(s) for s in slots)

    # -- styles de paragraphe -----------------------------------------------
    # Densité de composition de la séquence en cours (1 = normale). Réglée
    # par report_generator pour qu'une séquence ne finisse pas sur une page
    # presque vide : < 1 resserre les espacements, > 1 les desserre.
    density = 1.0

    def space(self, pt: float) -> float:
        return pt * self.density

    def ps(self, name, size, font="body", color="ink", leading=None, **kw) -> ParagraphStyle:
        col = self.c[color] if isinstance(color, str) else color
        for key in ("spaceBefore", "spaceAfter"):
            if key in kw:
                kw[key] = self.space(kw[key])
        lead = (leading or size * 1.4) * (1 + (self.density - 1) * 0.2)
        return ParagraphStyle(name, fontName=self.f.get(font, font), fontSize=size,
                              leading=lead, textColor=col, **kw)


# ═══════════════════════════════════════════════════════════════════════════
# Repère maquette (px, origine haut-gauche)
# ═══════════════════════════════════════════════════════════════════════════

class Px:
    """Canevas ReportLab piloté en coordonnées de maquette."""

    def __init__(self, canvas, kit: Kit):
        self.cv, self.k = canvas, kit

    @staticmethod
    def x(px):
        return px * PX

    @staticmethod
    def y(px):
        return PAGE_H - px * PX

    def color(self, c):
        return self.k.c[c] if isinstance(c, str) else c

    def rect(self, x, y, w, h, fill, radius: float = 0, stroke=None, lw=0.75, alpha=None):
        cv = self.cv
        cv.saveState()
        if alpha is not None:
            cv.setFillAlpha(alpha)
        if fill is not None:
            cv.setFillColor(self.color(fill))
        if stroke is not None:
            cv.setStrokeColor(self.color(stroke)); cv.setLineWidth(lw)
        args = (self.x(x), self.y(y + h), w * PX, h * PX)
        f, s = (1 if fill is not None else 0), (1 if stroke is not None else 0)
        if radius:
            cv.roundRect(*args, radius * PX, fill=f, stroke=s)
        else:
            cv.rect(*args, fill=f, stroke=s)
        cv.restoreState()

    def line(self, x1, y1, x2, y2, color="rule", lw=0.75, dash=None):
        cv = self.cv
        cv.saveState()
        cv.setStrokeColor(self.color(color)); cv.setLineWidth(lw)
        if dash:
            cv.setDash(*dash)
        cv.line(self.x(x1), self.y(y1), self.x(x2), self.y(y2))
        cv.restoreState()

    def text(self, x, y, s, font, size, color="ink", align="left", track=0.0,
             upper=False, max_w=None, min_size=None):
        """Texte sur une ligne ; `y` = ligne de base (px). `track` en em.
        `max_w` réduit le corps jusqu'à `min_size` pour tenir dans la largeur."""
        s = clean(s.upper() if upper else s)
        fname = self.k.f.get(font, font)
        size_pt = size * PX
        if max_w:
            floor = (min_size or size * 0.6) * PX
            while size_pt > floor and self.width(s, fname, size_pt, track) > max_w * PX:
                size_pt -= 0.5
        w = self.width(s, fname, size_pt, track)
        xx = self.x(x)
        if align == "right":
            xx -= w
        elif align == "center":
            xx -= w / 2
        cv = self.cv
        t = cv.beginText(xx, self.y(y))
        t.setFont(fname, size_pt)
        t.setCharSpace(track * size_pt)
        t.setFillColor(self.color(color))
        t.textOut(s)
        # L'espacement (opérateur Tc) persiste dans l'état graphique du PDF :
        # le remettre à zéro, sinon les paragraphes suivants en héritent.
        t.setCharSpace(0)
        cv.drawText(t)
        return w / PX

    @staticmethod
    def width(s, fname, size_pt, track=0.0):
        return stringWidth(s, fname, size_pt) + track * size_pt * max(0, len(s) - 1)

    def para(self, x, y, w, markup, style, max_h=None) -> float:
        """Paragraphe dont le HAUT est en `y` (px). Retourne sa hauteur (px)."""
        p = Paragraph(markup, style)
        _, h = p.wrap(w * PX, (max_h or 2000) * PX)
        p.drawOn(self.cv, self.x(x), self.y(y) - h)
        return h / PX

    def image(self, raw, x, y, w, h, radius=0):
        """Image recadrée pour remplir exactement la boîte (object-fit: cover)."""
        if not raw:
            self.rect(x, y, w, h, "panel", radius=radius)
            return
        ir = cover_crop(raw, round(w / h, 3))
        cv = self.cv
        cv.saveState()
        if radius:
            p = cv.beginPath()
            p.roundRect(self.x(x), self.y(y + h), w * PX, h * PX, radius * PX)
            cv.clipPath(p, stroke=0, fill=0)
        cv.drawImage(ir, self.x(x), self.y(y + h), w * PX, h * PX)
        cv.restoreState()

    def gradient_v(self, x, y, w, h, color, a_top, a_bottom, steps=24):
        """Voile vertical (ex. assombrir le haut d'une photo sous un texte)."""
        cv = self.cv
        cv.saveState()
        cv.setFillColor(self.color(color))
        for i in range(steps):
            a = a_top + (a_bottom - a_top) * i / (steps - 1)
            cv.setFillAlpha(max(0.0, min(1.0, a)))
            yy = y + h * i / steps
            cv.rect(self.x(x), self.y(yy + h / steps + 0.5), w * PX, (h / steps + 0.5) * PX,
                    fill=1, stroke=0)
        cv.restoreState()


_CROP_CACHE: dict = {}


def crop_jpeg(raw: bytes, ratio: float) -> bytes:
    """Photo recadrée au centre au rapport largeur/hauteur `ratio` (JPEG)."""
    key = (hash(raw), ratio)
    if key in _CROP_CACHE:
        return _CROP_CACHE[key]
    from PIL import Image as PILImage
    im = PILImage.open(io.BytesIO(raw)).convert("RGB")
    iw, ih = im.size
    if iw / ih > ratio:
        nw = int(ih * ratio)
        im = im.crop(((iw - nw) // 2, 0, (iw - nw) // 2 + nw, ih))
    else:
        nh = int(iw / ratio)
        top = max(0, int((ih - nh) * 0.45))
        im = im.crop((0, top, iw, top + nh))
    im.thumbnail((1400, 1400))  # ~200 dpi sur une pleine page A4
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=80)
    if len(_CROP_CACHE) > 64:
        _CROP_CACHE.clear()
    _CROP_CACHE[key] = buf.getvalue()
    return _CROP_CACHE[key]


def cover_crop(raw: bytes, ratio: float) -> ImageReader:
    """Comme crop_jpeg, pour un dessin au canevas (drawImage)."""
    return ImageReader(io.BytesIO(crop_jpeg(raw, ratio)))


# ═══════════════════════════════════════════════════════════════════════════
# Radar vectoriel à trois piliers (aucune référence externe tracée)
# ═══════════════════════════════════════════════════════════════════════════

def draw_radar(p: Px, cx, cy, r, values, labels, stroke="accent", fill_alpha=0.18,
               label_size=12, previous=None, prev_label=None):
    """Radar E/S/G. `values` sur 100. `previous` : scores N-1 du MÊME client
    (tracés en pointillés) — jamais une moyenne sectorielle."""
    cv = p.cv
    n = len(values)
    angles = [-math.pi / 2 + 2 * math.pi * i / n for i in range(n)]

    def pt(i, v):
        return (cx + r * v / 100 * math.cos(angles[i]), cy + r * v / 100 * math.sin(angles[i]))

    def poly(vals, fill=None, stroke_c="rule", lw=0.75, dash=None, alpha=None):
        pts = [pt(i, v) for i, v in enumerate(vals)]
        cv.saveState()
        path = cv.beginPath()
        path.moveTo(p.x(pts[0][0]), p.y(pts[0][1]))
        for xx, yy in pts[1:]:
            path.lineTo(p.x(xx), p.y(yy))
        path.close()
        cv.setStrokeColor(p.color(stroke_c)); cv.setLineWidth(lw)
        cv.setLineJoin(1)
        if dash:
            cv.setDash(*dash)
        if fill is not None:
            cv.setFillColor(p.color(fill)); cv.setFillAlpha(alpha if alpha is not None else 1)
        cv.drawPath(path, stroke=1, fill=1 if fill is not None else 0)
        cv.restoreState()

    for k, level in enumerate((100, 75, 50, 25)):
        poly([level] * n, stroke_c="muted" if k == 0 else "rule", lw=0.6 if k == 0 else 0.5)
    for i in range(n):
        x2, y2 = pt(i, 100)
        p.line(cx, cy, x2, y2, color="rule", lw=0.5)
    # Un pilier non noté n'a pas de sommet : on ne trace que les polygones
    # complets (un sommet posé à 0 dirait « score nul », ce qui est faux).
    if previous and all(v is not None for v in previous):
        poly(previous, stroke_c="muted", lw=1.0, dash=(3, 2.5))
    if all(v is not None for v in values):
        poly(values, fill=stroke, stroke_c=stroke, lw=1.6, alpha=fill_alpha)
    for i, v in enumerate(values):
        if v is None:
            continue
        x, y = pt(i, v)
        p.cv.setFillColor(p.color(stroke))
        p.cv.circle(p.x(x), p.y(y), 2.2, fill=1, stroke=0)
    for i, lab in enumerate(labels):
        x, y = pt(i, 122)
        align = "center" if abs(math.cos(angles[i])) < 0.2 else ("left" if math.cos(angles[i]) > 0 else "right")
        p.text(x, y + label_size * 0.35, lab, "body", label_size, color="muted", align=align)


# ═══════════════════════════════════════════════════════════════════════════
# En-têtes et pieds de page des pages courantes
# ═══════════════════════════════════════════════════════════════════════════

def initials(name: str) -> str:
    words = [w for w in clean(name).replace("-", " ").split() if w[:1].isalnum()]
    return "".join(w[0] for w in words[:2]).upper() or "·"


def draw_header(p: Px, kit: Kit, right_label: str, on_dark=False):
    name = kit.request.company.name
    ink = "on_primary" if on_dark else "muted"
    mode = kit.layout["header"]
    if mode == "centered":
        p.text(397, 58, f"{name}  ·  {right_label}", "body", 10, color=ink, align="center",
               track=0.18, upper=True, max_w=640)
        p.line(76, 70, 718, 70, color="rule", lw=0.6)
    elif mode == "monogram":
        p.rect(56, 40, 30, 30, "primary", radius=8)
        p.text(71, 60, initials(name), "body_b", 11, color="on_primary", align="center")
        p.text(96, 60, name, "body_b", 12, color="ink", max_w=420)
        p.text(738, 60, right_label, "body", 11, color="muted", align="right")
    elif mode == "plain":
        p.text(64, 58, name, "body_b", 10, color="ink", max_w=420)
        p.text(730, 58, right_label, "body", 10, color="muted", align="right")
    else:  # caps
        p.text(56, 56, name, "body", 9.5, color=ink, track=0.14, upper=True, max_w=400)
        p.text(738, 56, right_label, "body", 9.5, color=ink, align="right", track=0.14,
               upper=True)


def draw_footer(p: Px, kit: Kit, footer_label: str, page_no: int, on_dark=False):
    """Pied de page. Le motif « | page N » est vérifié par la suite de tests
    (pagination continue) : ne pas le modifier sans adapter le test."""
    col = "on_primary" if on_dark else "muted"
    if not on_dark:
        p.line(56, 1086, 738, 1086, color="rule", lw=0.5)
    p.text(56, 1104, kit.request.company.name, "body", 9, color=col, max_w=380)
    p.text(738, 1104, f"{footer_label} | page {page_no}", "body", 9, color=col, align="right")


def paint_paper(p: Px, kit: Kit):
    p.rect(0, 0, 794, 1123, "paper")


class FullPage(Flowable):
    """Page entière composée au canevas (couverture, chapitres, focus…).
    À poser dans un cadre sans marge couvrant toute la page."""

    def __init__(self, kit: Kit, drawer, *args):
        super().__init__()
        self.kit, self.drawer, self.args = kit, drawer, args

    def wrap(self, aW, aH):
        # Hauteur FIXE d'une page : sur une page déjà entamée, la page
        # composée ne tient pas et passe d'elle-même à la page suivante.
        return aW, PAGE_H - 2

    def draw(self):
        cv = self.canv
        cv.saveState()
        # les pages composées ont une mise en page fixe : densité neutre
        dens, self.kit.density = self.kit.density, 1.0
        try:
            # le cadre place l'origine en bas à gauche de la page
            self.drawer(Px(cv, self.kit), self.kit, *self.args)
        finally:
            self.kit.density = dens
        cv.restoreState()


class Anchor(Flowable):
    """Repère invisible : note la page où tombe une section (sommaire)."""

    def __init__(self, key, registry: dict):
        super().__init__()
        self.key, self.registry = key, registry

    def wrap(self, aW, aH):
        return 0, 0

    def draw(self):
        self.registry.setdefault(self.key, self.canv.getPageNumber())
