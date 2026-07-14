"""
Personnalisation visuelle par client (« brand kit »).

À partir de deux couleurs — primaire (surfaces sombres, titres) et accent
(surlignages, filets, chiffres clés) — dérive des variantes cohérentes des
thèmes PPTX, palettes PDF et couleurs de graphiques. Les couleurs des
piliers E/S/G restent sémantiques (vert/bleu/violet) pour la lisibilité.

`auto_brand(name)` produit une paire déterministe et harmonieuse depuis le
nom du client : trois clients ont ainsi trois identités visuelles distinctes
sans aucune saisie.
"""
import colorsys
import hashlib
import re

_HEX_RE = re.compile(r"^#?([0-9a-fA-F]{6})$")


def _parse(hexstr):
    m = _HEX_RE.match((hexstr or "").strip())
    if not m:
        return None
    h = m.group(1)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*[max(0, min(255, int(round(c)))) for c in rgb])


def _luminance(rgb):
    r, g, b = [c / 255 for c in rgb]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _adjust_l(rgb, l_target):
    h, l, s = colorsys.rgb_to_hls(*[c / 255 for c in rgb])
    r, g, b = colorsys.hls_to_rgb(h, l_target, s)
    return (r * 255, g * 255, b * 255)


def _mix(rgb, other, t):
    return tuple(a + (b - a) * t for a, b in zip(rgb, other))


def validate_colors(custom: dict):
    """Retourne (primary_rgb, accent_rgb) normalisés, ou None si invalide.
    La primaire est assombrie si trop claire (elle porte du texte blanc)."""
    if not isinstance(custom, dict):
        return None
    p = _parse(custom.get("primary"))
    a = _parse(custom.get("accent"))
    if p is None or a is None:
        return None
    if _luminance(p) > 0.45:
        p = _adjust_l(p, 0.22)
    # accent trop sombre → éclairci pour rester lisible sur la primaire
    if _luminance(a) < 0.35:
        a = _adjust_l(a, 0.62)
    return p, a


def auto_brand(name: str) -> dict:
    """Paire primaire/accent déterministe et harmonieuse depuis le nom."""
    h = int(hashlib.md5((name or "esg").encode()).hexdigest(), 16)
    hue = (h % 360) / 360.0
    accent_hue = ((h % 360) + 35 + (h >> 8) % 50) % 360 / 360.0
    p = colorsys.hls_to_rgb(hue, 0.20, 0.42)
    a = colorsys.hls_to_rgb(accent_hue, 0.55, 0.72)
    return {"primary": _to_hex(tuple(c * 255 for c in p)),
            "accent": _to_hex(tuple(c * 255 for c in a))}


def brand_pptx_theme(theme: dict, custom: dict) -> dict:
    """Variante du thème PPTX aux couleurs du client (RGBColor pptx)."""
    from pptx.dml.color import RGBColor
    v = validate_colors(custom)
    if not v:
        return theme
    p, a = v
    white = (255, 255, 255)
    t = dict(theme)
    t["bg_primary"] = RGBColor(*[int(c) for c in p])
    t["accent"] = RGBColor(*[int(c) for c in a])
    # Surfaces claires et texte dérivés de la primaire
    t["bg_secondary"] = RGBColor(*[int(c) for c in _mix(p, white, 0.94)])
    t["card_bg"] = RGBColor(*[int(c) for c in _mix(p, white, 0.86)])
    t["text_dark"] = RGBColor(*[int(c) for c in _adjust_l(p, 0.16)])
    t["subtitle"] = RGBColor(*[int(c) for c in _mix(p, white, 0.72)])
    return t


def brand_pdf_palette(pal: dict, custom: dict) -> dict:
    """Variante de la palette PDF aux couleurs du client (reportlab)."""
    from reportlab.lib import colors as rl
    v = validate_colors(custom)
    if not v:
        return pal
    p, a = v
    white = (255, 255, 255)
    out = dict(pal)
    out["primary"] = rl.Color(*[c / 255 for c in p])
    out["accent"] = rl.Color(*[c / 255 for c in a])
    out["secondary"] = rl.Color(*[c / 255 for c in _adjust_l(p, 0.35)])
    out["light_bg"] = rl.Color(*[c / 255 for c in _mix(p, white, 0.93)])
    return out


def brand_docx_hex(colors: dict, custom: dict) -> dict:
    """Variante des couleurs Word (hex sans '#') aux couleurs du client."""
    v = validate_colors(custom)
    if not v:
        return colors
    p, a = v
    white = (255, 255, 255)
    out = dict(colors)
    out["primary"] = _to_hex(p)[1:]
    out["accent"] = _to_hex(a)[1:]
    out["secondary"] = _to_hex(_adjust_l(p, 0.35))[1:]
    out["light"] = _to_hex(_mix(p, white, 0.93))[1:]
    return out


def brand_chart_colors(colors: dict, custom: dict) -> dict:
    """Variante des couleurs de graphiques : accent + primaire du client,
    piliers inchangés (sémantiques)."""
    v = validate_colors(custom)
    if not v:
        return colors
    p, a = v
    out = dict(colors)
    out["accent"] = _to_hex(a)
    if "primary" in out:
        out["primary"] = _to_hex(p)
    return out
