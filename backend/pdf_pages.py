"""Pages composées au canevas du rapport PDF, déclinées par gabarit.

Chaque fonction reçoit (p: Px, kit: Kit, g: dict) — `g` est le contexte de
page préparé par report_generator (scores, métriques réelles, libellés).
Aucune donnée n'est inventée ici : une métrique absente n'est pas affichée,
et le radar ne trace que les trois piliers du client (N-1 en pointillés
quand l'historique existe), jamais une référence sectorielle.
"""
from pdf_kit import (Px, Kit, draw_radar, draw_header, draw_footer, paint_paper, esc, hexc,
                     SERIF_FAMILIES)


# ═══════════════════════════════════════════════════════════════════════════
# Petits blocs réutilisés
# ═══════════════════════════════════════════════════════════════════════════

_PILLAR_ICON = {"env": "leaf", "social": "people", "gov": "scale"}


def photo_or_tile(p: Px, k: Kit, slot, pillar, label, x, y, w, h, radius=0):
    """Photo fournie par l'entreprise pour l'emplacement ; sinon (ou banque
    pour l'environnement) une tuile sobre : fond du pilier et pictogramme.
    Jamais une photo d'illustration sans rapport avec le pilier."""
    raw = k.photo(slot)
    if raw:
        p.image(raw, x, y, w, h, radius=radius)
        return
    from visual_kit import icon_png
    from reportlab.lib.utils import ImageReader
    import io
    p.rect(x, y, w, h, pillar, radius=radius)
    size = min(w, h) * 0.34
    ir = ImageReader(io.BytesIO(icon_png(_PILLAR_ICON[pillar], 256, hexc(k.c[pillar + "_soft"]))))
    p.cv.drawImage(ir, p.x(x + (w - size) / 2), p.y(y + h / 2 + size / 2 - 8), size * 0.75,
                   size * 0.75, mask="auto")
    p.text(x + w / 2, y + h / 2 + size / 2 + 18, label, "body", 11, color=pillar + "_soft",
           align="center", track=0.14, upper=True)


def _delta(g, key):
    d = (g.get("delta") or {}).get(key)
    if d is None:
        return ""
    return f"{d:+.0f} pts " + g["TR"]["ed_vs"].format(y=g["prev_year"])


def _pillars(g):
    TR = g["TR"]
    return [("env", TR["ed_env"], g["e"]), ("social", TR["ed_soc"], g["s"]),
            ("gov", TR["ed_gov"], g["g"])]


def _global_line(g):
    d = _delta(g, "total")
    return f"{g['TR']['note']} {g['rating']}" + (f" · {d}" if d else "")


def _radar(p, g, cx, cy, r, stroke="accent", label_size=12, alpha=0.18):
    TR = g["TR"]
    draw_radar(p, cx, cy, r, [g["e"], g["s"], g["g"]],
               [TR["ed_env"], TR["ed_soc"], TR["ed_gov"]], stroke=stroke,
               label_size=label_size, previous=g.get("prev_vals"), fill_alpha=alpha)


def _legend(p, g, x, y, stroke="accent", gap=24, horizontal=False):
    """Légende du radar : le client, et ses scores N-1 s'ils existent."""
    p.rect(x, y - 5, 20, 2.4, stroke)
    w = p.text(x + 28, y, g["name"], "body", 11.5, color="muted", max_w=230)
    if not g.get("prev_vals"):
        return
    x2, y2 = (x + 28 + w + 24, y) if horizontal else (x, y + gap)
    p.line(x2, y2 - 4, x2 + 20, y2 - 4, color="muted", lw=1.2, dash=(3, 2.5))
    p.text(x2 + 28, y2, g["TR"]["ed_prev"].format(y=g["prev_year"]), "body", 11.5, color="muted")


def _metric_rows(p, g, x, y, w, items, value_font="display", size=22, row_h=54, cols=3):
    """Grille de métriques réelles : valeur en grand, libellé dessous."""
    if not items:
        return
    cw = w / cols
    for i, (val, lab) in enumerate(items):
        cx, cy = x + (i % cols) * cw, y + (i // cols) * row_h
        p.text(cx, cy + size, val, value_font, size, color="ink", max_w=cw - 10)
        p.para(cx, cy + size + 6, cw - 12, esc(lab), p.k.ps("mr", 11 * 0.75, color="muted",
                                                            leading=13.5 * 0.75))


def _metric_list(p, g, x, y, w, items, row_h: float = 40, size: float = 14):
    """Liste libellé / valeur séparée par des filets (gabarit Portrait)."""
    for i, (val, lab) in enumerate(items):
        yy = y + i * row_h
        p.text(x, yy + 25, lab[:1].upper() + lab[1:], "body", size, color="ink", max_w=w - 110)
        p.text(x + w, yy + 25, val, "body_b", size, color="ink", align="right")
        p.line(x, yy + row_h, x + w, yy + row_h, color="rule", lw=0.6)


# ═══════════════════════════════════════════════════════════════════════════
# « ESG en un coup d'œil » — une variante par gabarit (maquettes B E F G H
# et Aurora)
# ═══════════════════════════════════════════════════════════════════════════

def glance_aurora(p: Px, k: Kit, g):
    TR = g["TR"]
    paint_paper(p, k)
    draw_header(p, k, TR["ed_report_year"].format(y=g["year"]))
    p.text(56, 122, "01", "display", 34, color="accent")
    p.text(56, 170, TR["ed_glance"], "display", 42, color="ink", max_w=680)
    p.para(56, 190, 560, esc(g["verdict"]), k.ps("v", 14.5 * 0.75, color="muted", leading=22 * 0.75))
    p.image(k.photo("cover"), 56, 272, 682, 200)
    # Quatre colonnes à filets
    y0, h = 500, 128
    p.line(56, y0, 738, y0, color="ink", lw=0.8)
    p.line(56, y0 + h, 738, y0 + h, color="ink", lw=0.8)
    cw = 682 / 4
    for i, (key, lab, val) in enumerate(_pillars(g)):
        x = 56 + i * cw
        if i:
            p.line(x, y0 + 16, x, y0 + h - 16, color="rule", lw=0.6)
        p.text(x + 16, y0 + 30, lab, "body", 10.5, color="muted", track=0.12, upper=True, max_w=cw - 24)
        p.text(x + 16, y0 + 88, f"{val:.0f}", "display", 50, color=key)
        p.text(x + 16, y0 + 112, _delta(g, key) or "/100", "body", 11, color="muted")
    x = 56 + 3 * cw
    p.rect(x, y0, cw, h, "primary")
    p.text(x + 16, y0 + 30, TR["ed_global"], "body", 10.5, color="accent_on_primary", track=0.12,
           upper=True, max_w=cw - 24)
    p.text(x + 16, y0 + 88, f"{g['t']:.0f}", "display", 50, color="on_primary")
    p.text(x + 16, y0 + 112, _global_line(g), "body", 11, color="on_primary", max_w=cw - 24)
    # Radar et métriques
    _radar(p, g, 215, 830, 120)
    _legend(p, g, 80, 1030, horizontal=True)
    x, w = 440, 298
    p.text(x, 690, TR["ed_env"], "body", 10.5, color="env", track=0.12, upper=True)
    _metric_list(p, g, x, 698, w, g["env_m"], row_h=36, size=12.5)
    y = 698 + 36 * max(1, len(g["env_m"])) + 30
    p.text(x, y, TR["ed_soc"], "body", 10.5, color="social", track=0.12, upper=True)
    _metric_list(p, g, x, y + 8, w, g["soc_m"], row_h=36, size=12.5)
    if g["gov_line"]:
        y += 8 + 36 * max(1, len(g["soc_m"])) + 30
        p.text(x, y, TR["ed_gov"], "body", 10.5, color="gov", track=0.12, upper=True)
        p.para(x, y + 8, w, esc(g["gov_line"]), k.ps("gl", 12.5 * 0.75, color="ink", leading=18 * 0.75))


def glance_annuel(p: Px, k: Kit, g):
    TR = g["TR"]
    paint_paper(p, k)
    draw_header(p, k, TR["ed_report_year"].format(y=g["year"]))
    p.text(397, 112, TR["ed_act1"], "display_i", 15, color="accent", align="center")
    p.text(397, 172, TR["ed_glance"], "display_i", 52, color="ink", align="center", max_w=640)
    p.rect(373, 192, 48, 2, "accent")
    p.para(157, 212, 480, esc(g["verdict"]),
           k.ps("v", 16 * 0.75, font="display", color="muted", leading=24 * 0.75, alignment=1))
    p.image(k.photo("cover"), 76, 296, 642, 180)
    p.rect(76, 296, 642, 180, None, stroke="rule", lw=0.8)
    # Tableau à doubles filets
    y0, h = 506, 132
    for yy in (y0, y0 + 3, y0 + h - 3, y0 + h):
        p.line(76, yy, 718, yy, color="ink", lw=0.7)
    cw = 642 / 4
    for i, (key, lab, val) in enumerate(_pillars(g)):
        x = 76 + i * cw
        if i:
            p.line(x, y0 + 3, x, y0 + h - 3, color="rule", lw=0.6)
        p.text(x + cw / 2, y0 + 30, lab, "body", 11, color="muted", align="center", track=0.14,
               upper=True, max_w=cw - 16)
        p.text(x + cw / 2, y0 + 90, f"{val:.0f}", "display", 54, color=key, align="center")
        p.text(x + cw / 2, y0 + 114, _delta(g, key) or "/100", "body", 12, color="muted", align="center")
    x = 76 + 3 * cw
    p.rect(x, y0 + 3, cw, h - 6, "primary")
    p.text(x + cw / 2, y0 + 30, TR["ed_global"], "body", 11, color="accent_on_primary",
           align="center", track=0.14, upper=True, max_w=cw - 16)
    p.text(x + cw / 2, y0 + 90, f"{g['t']:.0f}", "display", 54, color="on_primary", align="center")
    p.text(x + cw / 2, y0 + 114, _global_line(g), "body", 12, color="on_primary", align="center",
           max_w=cw - 12)
    _radar(p, g, 397, 820, 118, label_size=13)
    _legend(p, g, 250, 1010, horizontal=True)


def glance_institutionnel(p: Px, k: Kit, g):
    TR = g["TR"]
    paint_paper(p, k)
    draw_header(p, k, TR["ed_report_year"].format(y=g["year"]))
    p.text(56, 126, "01 · " + TR["toc_part1"], "body_b", 12.5, color="accent", track=0.06, upper=True)
    p.text(56, 180, TR["ed_glance"], "display", 56, color="ink", max_w=680)
    p.para(56, 198, 540, esc(g["verdict"]), k.ps("v", 15 * 0.75, color="muted", leading=23 * 0.75))
    p.image(k.photo("cover"), 56, 276, 682, 170, radius=16)
    cw, gap, y0, h = (682 - 36) / 4, 12, 460, 132
    for i, (key, lab, val) in enumerate(_pillars(g)):
        x = 56 + i * (cw + gap)
        p.rect(x, y0, cw, h, "surface", radius=14)
        p.cv.setFillColor(k.c[key]); p.cv.circle(p.x(x + 20), p.y(y0 + 27), 3.4, fill=1, stroke=0)
        p.text(x + 30, y0 + 31, lab, "body_b", 12.5, color="ink", max_w=cw - 40)
        p.text(x + 16, y0 + 92, f"{val:.0f}", "display", 56, color=key)
        d = _delta(g, key)
        if d:
            tw = p.width(d, k.f["body"], 11 * 0.75) / 0.75
            p.rect(x + 16, y0 + 102, tw + 16, 19, f"{key}_soft", radius=9.5)
            p.text(x + 24, y0 + 116, d, "body", 11, color=key)
    x = 56 + 3 * (cw + gap)
    p.rect(x, y0, cw, h, "primary", radius=14)
    p.text(x + 16, y0 + 31, TR["ed_global"], "body_b", 12.5, color="on_primary", max_w=cw - 60)
    p.rect(x + cw - 44, y0 + 14, 30, 22, "accent_on_primary", radius=6)
    p.text(x + cw - 29, y0 + 30, g["rating"], "body_b", 12.5, color="primary", align="center")
    p.text(x + 16, y0 + 92, f"{g['t']:.0f}", "display", 56, color="on_primary")
    d = _delta(g, "total")
    if d:
        p.text(x + 16, y0 + 116, d, "body", 11, color="on_primary")
    # Panneau radar
    y1 = y0 + h + 14
    p.rect(56, y1, 682, 1060 - y1, "surface", radius=16)
    _radar(p, g, 250, y1 + 200, 118, stroke="accent", label_size=12, alpha=0.2)
    x = 470
    p.text(x, y1 + 50, TR["ed_glance"], "body_b", 13, color="ink", max_w=250)
    _legend(p, g, x, y1 + 82)
    items = (g["env_m"][:2] + g["soc_m"][:2])
    _metric_rows(p, g, x, y1 + 140, 250, items, size=24, row_h=74, cols=2)


def glance_portrait(p: Px, k: Kit, g):
    TR = g["TR"]
    paint_paper(p, k)
    p.image(k.photo("company") or k.photo("cover"), 0, 0, 794, 440)
    p.gradient_v(0, 0, 794, 110, "primary", 0.45, 0.0)
    p.text(56, 44, g["name"], "body", 10, color="on_primary", track=0.12, upper=True, max_w=400)
    p.text(738, 44, TR["ed_report_year"].format(y=g["year"]), "body", 10, color="on_primary",
           align="right", track=0.12, upper=True)
    p.rect(56, 338, 440, 196, "surface")
    p.text(86, 376, "01 · " + TR["toc_part1"], "body", 11, color="accent", track=0.14, upper=True)
    p.text(86, 422, TR["ed_glance"], "display", 38, color="ink", max_w=380)
    p.para(86, 438, 380, esc(g["verdict"]), k.ps("v", 13.5 * 0.75, color="muted", leading=20 * 0.75),
           max_h=90)
    p.text(738, 486, TR["ed_global"], "body", 11, color="muted", align="right", track=0.14, upper=True)
    w = p.text(700, 546, "/100", "body", 15, color="muted", align="right")
    p.text(738 - w - 44, 546, f"{g['t']:.0f}", "display", 64, color="ink", align="right")
    p.text(738, 568, _global_line(g), "body", 12.5, color="muted", align="right")
    cw = (682 - 40) / 2
    cols = (("env", TR["ed_env"], g["e"], g["env_m"]), ("social", TR["ed_soc"], g["s"], g["soc_m"]))
    for i, (key, lab, val, items) in enumerate(cols):
        x = 56 + i * (cw + 40)
        p.text(x, 628, lab, "display", 20, color="ink")
        p.text(x + cw, 632, f"{val:.0f}", "display", 36, color=key, align="right")
        p.rect(x, 644, cw, 2, key)
        _metric_list(p, g, x, 648, cw, items[:3], row_h=42, size=13)
    p.line(56, 836, 738, 836, color="ink", lw=0.8)
    _radar(p, g, 190, 950, 76, stroke="ink", label_size=11, alpha=0.08)
    x = 340
    p.text(x, 880, TR["ed_gov"], "display", 18, color="ink")
    p.text(738, 884, f"{g['g']:.0f}", "display", 26, color="gov", align="right")
    if g["gov_line"]:
        p.para(x, 896, 398, esc(g["gov_line"]), k.ps("gl", 12.5 * 0.75, color="muted", leading=18 * 0.75))
    _legend(p, g, x, 990, stroke="ink", horizontal=True)


def glance_terre(p: Px, k: Kit, g):
    TR = g["TR"]
    paint_paper(p, k)
    draw_header(p, k, f"{TR['exercise']} {g['year']}")
    p.text(56, 120, "01 — " + TR["toc_part1"], "body", 13, color="accent")
    p.text(56, 170, TR["ed_glance"], "display", 48, color="ink", max_w=520)
    w = p.text(738, 168, "/100", "body", 15, color="muted", align="right")
    p.text(738 - w - 6, 168, f"{g['t']:.0f}", "display", 62, color="ink", align="right")
    p.text(738, 190, _global_line(g), "body", 12.5, color="muted", align="right")
    cw, y0 = (682 - 14) / 2, 214
    tiles = (("env", "environment", TR["ed_env"], g["e"], g["env_m"]),
             ("social", "social", TR["ed_soc"], g["s"], g["soc_m"]))
    for i, (key, slot, lab, val, items) in enumerate(tiles):
        x = 56 + i * (cw + 14)
        p.rect(x, y0, cw, 430, f"{key}_soft", radius=3)
        photo_or_tile(p, k, slot, key, lab, x, y0, cw, 190)
        p.text(x + 20, y0 + 232, lab, "body", 12, color=key, track=0.1, upper=True)
        p.text(x + cw - 20, y0 + 240, f"{val:.0f}", "display", 44, color=key, align="right")
        d = _delta(g, key)
        if d:
            p.text(x + 20, y0 + 256, d, "body", 12.5, color="muted")
        p.line(x + 20, y0 + 280, x + cw - 20, y0 + 280, color="rule", lw=0.6)
        _metric_rows(p, g, x + 20, y0 + 292, cw - 40, items[:3], size=22, row_h=60)
    p.line(56, 676, 738, 676, color="rule", lw=0.7)
    _radar(p, g, 250, 850, 118)
    x = 500
    p.text(x, 760, TR["ed_gov"], "body", 12, color="ink", track=0.1, upper=True)
    p.text(738, 764, f"{g['g']:.0f}", "display", 32, color="gov", align="right")
    if g["gov_line"]:
        p.para(x, 778, 238, esc(g["gov_line"]), k.ps("gl", 12.5 * 0.75, color="muted", leading=18 * 0.75))
    _legend(p, g, x, 900)


def glance_galerie(p: Px, k: Kit, g):
    TR = g["TR"]
    paint_paper(p, k)
    draw_header(p, k, TR["ed_report_year"].format(y=g["year"]))
    p.text(64, 130, "01 · " + TR["toc_part1"], "body", 12.5, color="accent", track=0.14, upper=True)
    p.text(64, 180, TR["ed_glance"], "display", 48, color="ink", max_w=660)
    big_w = (666 - 8) * 1.6 / 2.6
    p.image(k.photo("environment"), 64, 210, big_w, 308)
    sx, sw = 64 + big_w + 8, 666 - big_w - 8
    photo_or_tile(p, k, "social", "social", TR["ed_soc"], sx, 210, sw, 150)
    photo_or_tile(p, k, "governance", "gov", TR["ed_gov"], sx, 368, sw, 150)
    y0 = 560
    p.text(64, y0 + 10, TR["ed_global"], "body", 11, color="muted", track=0.14, upper=True)
    p.text(64, y0 + 82, f"{g['t']:.0f}", "display", 70, color="ink")
    p.text(64, y0 + 106, _global_line(g), "body", 12.5, color="muted", max_w=200)
    x, w = 290, 440
    for i, (key, lab, val) in enumerate(_pillars(g)):
        yy = y0 + 22 + i * 34
        p.text(x, yy, lab, "body", 13.5, color="ink", max_w=120)
        p.rect(x + 130, yy - 6, w - 180, 3, "rule")
        p.rect(x + 130, yy - 6, (w - 180) * max(0, min(100, val)) / 100, 3, key)
        p.text(x + w, yy, f"{val:.0f}", "body_b", 13.5, color="ink", align="right")
    p.line(64, 716, 730, 716, color="ink", lw=0.8)
    _radar(p, g, 210, 880, 110, label_size=13, alpha=0.12)
    items = (g["env_m"][:2] + g["soc_m"][:2])
    _metric_rows(p, g, 420, 760, 310, items, size=28, row_h=86, cols=2)
    _legend(p, g, 420, 1000, horizontal=True)


GLANCE = {"aurora": glance_aurora, "annuel": glance_annuel,
          "institutionnel": glance_institutionnel, "portrait": glance_portrait,
          "terre": glance_terre, "galerie": glance_galerie}


def glance_page(p: Px, k: Kit, g):
    GLANCE[k.layout["glance"]](p, k, g)
    draw_footer(p, k, g["footer_label"], p.cv.getPageNumber())


# ═══════════════════════════════════════════════════════════════════════════
# Couvertures
# ═══════════════════════════════════════════════════════════════════════════

def _cover_meta(g):
    TR = g["TR"]
    c = g["company"]
    return f"{TR['exercise']} {c.reporting_year}  ·  {c.sector}  ·  {c.country}"


def _presenter(g):
    c = g["company"]
    if not c.presenter_name:
        return ""
    s = f"{g['TR']['presented_by']} {c.presenter_name}"
    return s + (f" — {c.presenter_title}" if c.presenter_title else "")


def _logo(p, k, x, y, max_w, h, align="left"):
    if not k.logo:
        return
    try:
        from reportlab.lib.utils import ImageReader
        import io
        ir = ImageReader(io.BytesIO(k.logo))
        iw, ih = ir.getSize()
        w = min(max_w, h * iw / max(1, ih))
        hh = w * ih / max(1, iw)
        xx = x - w if align == "right" else x
        p.cv.drawImage(ir, p.x(xx), p.y(y + hh), w * 0.75, hh * 0.75, mask="auto")
    except Exception:
        pass


def cover_split(p, k, g):
    TR = g["TR"]
    paint_paper(p, k)
    p.image(k.photo("cover"), 318, 0, 476, 1123)
    p.gradient_v(318, 0, 476, 120, "primary", 0.35, 0.0)
    p.text(760, 52, TR["ed_report_year"].format(y=g["year"]), "body", 10, color="on_primary",
           align="right", track=0.08)
    p.para(42, 40, 240, esc(g["name"].upper()),
           k.ps("cn", 11 * 0.75, font="body_b", color="ink", leading=15 * 0.75, charSpace=1.6))
    _logo(p, k, 42, 96, 150, 44)
    h = p.para(42, 250, 262, esc(g["type_label"]),
               k.ps("ct", 56 * 0.75, font="display", color="ink", leading=60 * 0.75))
    y = 250 + h + 28
    p.rect(42, y, 46, 1.2, "ink")
    p.para(42, y + 26, 220, esc(g["tagline"]), k.ps("tg", 12.5 * 0.75, color="muted", leading=19 * 0.75))
    p.text(42, 890, TR["ed_global"], "body", 10, color="muted", track=0.12, upper=True)
    w = p.text(42, 948, f"{g['t']:.0f}", "display", 52, color="accent")
    p.text(42 + w + 8, 948, f"/100  ·  {TR['note']} {g['rating']}", "body", 13, color="muted")
    pres = _presenter(g)
    if pres:
        p.para(42, 972, 262, esc(pres), k.ps("pr", 10.5 * 0.75, font="body_i", color="muted"))
    p.text(42, 1060, TR["ed_pillars"], "body", 9.5, color="muted", max_w=260)
    p.text(42, 1082, g["refs"], "body_b", 9.5, color="accent")


def cover_editorial(p, k, g):
    TR = g["TR"]
    paint_paper(p, k)
    p.text(397, 58, TR["ed_report_year"].format(y=g["year"]), "body", 10.5, color="muted",
           align="center", track=0.18, upper=True)
    p.line(76, 72, 718, 72, color="rule", lw=0.6)
    _logo(p, k, 718, 86, 140, 40, align="right")
    p.image(k.photo("cover"), 76, 140, 642, 470)
    p.rect(76, 140, 642, 470, None, stroke="rule", lw=0.8)
    p.text(397, 690, g["name"], "display_i", 58, color="ink", align="center", max_w=640, min_size=30)
    p.rect(373, 712, 48, 2, "accent")
    p.text(397, 750, g["type_label"], "body", 12, color="muted", align="center", track=0.18, upper=True,
           max_w=640)
    p.para(147, 772, 500, esc(g["tagline"]),
           k.ps("tg", 17 * 0.75, font="display_i", color="ink", leading=24 * 0.75, alignment=1))
    for yy in (870, 873, 947, 950):
        p.line(196, yy, 598, yy, color="ink", lw=0.6)
    p.text(397, 897, TR["ed_global"], "body", 10.5, color="muted", align="center", track=0.14, upper=True)
    p.text(397, 934, f"{g['t']:.0f}/100  ·  {TR['note']} {g['rating']}", "display", 26, color="accent",
           align="center")
    p.text(397, 990, _cover_meta(g), "body", 11, color="muted", align="center", max_w=640)
    pres = _presenter(g)
    if pres:
        p.text(397, 1012, pres, "body_i", 11, color="muted", align="center", max_w=640)
    p.text(397, 1080, g["refs"], "body_b", 10, color="accent", align="center")


def cover_band(p, k, g):
    TR = g["TR"]
    paint_paper(p, k)
    draw_header(p, k, f"{TR['exercise']} {g['year']}")
    _logo(p, k, 738, 90, 140, 40, align="right")
    p.text(56, 170, g["type_label"], "body_b", 13, color="accent", track=0.06, upper=True, max_w=680)
    h = p.para(56, 186, 682, esc(g["name"]),
               k.ps("cn", 74 * 0.75, font="display", color="ink", leading=76 * 0.75))
    p.para(56, 196 + h, 560, esc(g["tagline"]), k.ps("tg", 17 * 0.75, color="muted", leading=25 * 0.75))
    y0 = 430
    p.image(k.photo("cover"), 56, y0, 682, 520, radius=16)
    p.rect(80, y0 + 520 - 116, 300, 92, "surface", radius=14)
    p.text(100, y0 + 520 - 86, TR["ed_global"], "body_b", 12, color="ink")
    p.text(100, y0 + 520 - 40, f"{g['t']:.0f}", "display", 46, color="ink")
    p.text(170, y0 + 520 - 42, "/100", "body", 14, color="muted")
    p.rect(300, y0 + 520 - 100, 58, 40, "accent", radius=8)
    p.text(329, y0 + 520 - 72, g["rating"], "body_b", 20, color="surface", align="center")
    p.text(56, 1000, _cover_meta(g), "body", 11.5, color="muted", max_w=680)
    pres = _presenter(g)
    if pres:
        p.text(56, 1022, pres, "body_i", 11.5, color="muted", max_w=680)
    p.text(56, 1080, g["refs"], "body_b", 10.5, color="accent")


def cover_photo_card(p, k, g):
    TR = g["TR"]
    p.image(k.photo("cover"), 0, 0, 794, 1123)
    p.gradient_v(0, 0, 794, 140, "primary", 0.5, 0.0)
    p.text(56, 50, g["name"], "body", 10.5, color="on_primary", track=0.12, upper=True, max_w=420)
    p.text(738, 50, TR["ed_report_year"].format(y=g["year"]), "body", 10.5, color="on_primary",
           align="right", track=0.12, upper=True)
    x, y, w = 56, 600, 520
    p.rect(x, y, w, 420, "surface")
    _logo(p, k, x + w - 30, y + 30, 120, 34, align="right")
    p.text(x + 34, y + 50, g["type_label"], "body", 11, color="accent", track=0.14, upper=True, max_w=w - 200)
    h = p.para(x + 34, y + 70, w - 68, esc(g["name"]),
               k.ps("cn", 44 * 0.75, font="display", color="ink", leading=50 * 0.75))
    yy = y + 70 + h + 12
    yy += p.para(x + 34, yy, w - 68, esc(g["tagline"]),
                 k.ps("tg", 15 * 0.75, color="muted", leading=22 * 0.75)) + 22
    p.line(x + 34, yy, x + w - 34, yy, color="rule", lw=0.7)
    ww = p.text(x + 34, yy + 58, f"{g['t']:.0f}", "display", 48, color="ink")
    p.text(x + 34 + ww + 8, yy + 56, f"/100  ·  {TR['note']} {g['rating']}", "body", 14, color="muted")
    p.text(x + 34, yy + 88, _cover_meta(g), "body", 10.5, color="muted", max_w=w - 68)
    pres = _presenter(g)
    if pres:
        p.text(x + 34, yy + 108, pres, "body_i", 10.5, color="muted", max_w=w - 68)
    p.text(x + 34, y + 400, g["refs"], "body_b", 10, color="accent")


def cover_duo(p, k, g):
    TR = g["TR"]
    paint_paper(p, k)
    draw_header(p, k, f"{TR['exercise']} {g['year']}")
    p.image(k.photo("cover"), 56, 84, 682, 520, radius=3)
    _logo(p, k, 56, 630, 160, 40)
    p.text(56, 700, g["type_label"], "body", 13, color="accent", max_w=460)
    h = p.para(56, 716, 470, esc(g["name"]),
               k.ps("cn", 54 * 0.75, font="display", color="ink", leading=56 * 0.75))
    p.para(56, 730 + h, 440, esc(g["tagline"]), k.ps("tg", 15 * 0.75, color="muted", leading=22 * 0.75))
    w = p.text(738, 760, "/100", "body", 15, color="muted", align="right")
    p.text(738 - w - 6, 760, f"{g['t']:.0f}", "display", 72, color="ink", align="right")
    p.text(738, 784, f"{TR['note']} {g['rating']}", "body", 13, color="muted", align="right")
    cw = (682 - 28) / 3
    for i, (key, lab, val) in enumerate(_pillars(g)):
        x = 56 + i * (cw + 14)
        p.rect(x, 900, cw, 110, f"{key}_soft", radius=3)
        p.text(x + 18, 930, lab, "body", 11, color=key, track=0.1, upper=True, max_w=cw - 30)
        p.text(x + 18, 990, f"{val:.0f}", "display", 44, color=key)
    p.text(56, 1050, _cover_meta(g), "body", 10.5, color="muted", max_w=520)
    p.text(738, 1050, g["refs"], "body_b", 10.5, color="accent", align="right")
    pres = _presenter(g)
    if pres:
        p.text(56, 1072, pres, "body_i", 10.5, color="muted", max_w=680)


def cover_mosaic(p, k, g):
    TR = g["TR"]
    paint_paper(p, k)
    draw_header(p, k, TR["ed_report_year"].format(y=g["year"]))
    _logo(p, k, 730, 84, 140, 36, align="right")
    p.text(64, 150, g["type_label"], "body", 12.5, color="accent", track=0.14, upper=True, max_w=560)
    h = p.para(64, 166, 666, esc(g["name"]),
               k.ps("cn", 62 * 0.75, font="display", color="ink", leading=64 * 0.75))
    y0 = max(300, 186 + h)
    big_w = (666 - 8) * 1.6 / 2.6
    p.image(k.photo("cover"), 64, y0, big_w, 470)
    sx, sw = 64 + big_w + 8, 666 - big_w - 8
    p.image(k.photo("environment"), sx, y0, sw, 231)
    photo_or_tile(p, k, "social", "social", TR["ed_soc"], sx, y0 + 239, sw, 231)
    y1 = y0 + 470 + 40
    p.para(64, y1, 360, esc(g["tagline"]), k.ps("tg", 15 * 0.75, color="muted", leading=22 * 0.75))
    p.text(730, y1 + 20, TR["ed_global"], "body", 10.5, color="muted", align="right", track=0.14, upper=True)
    w = p.text(730, y1 + 86, "/100", "body", 15, color="muted", align="right")
    p.text(730 - w - 6, y1 + 86, f"{g['t']:.0f}", "display", 64, color="ink", align="right")
    p.text(730, y1 + 108, f"{TR['note']} {g['rating']}", "body", 12.5, color="muted", align="right")
    p.text(64, 1050, _cover_meta(g), "body", 10.5, color="muted", max_w=560)
    pres = _presenter(g)
    if pres:
        p.text(64, 1072, pres, "body_i", 10.5, color="muted", max_w=560)
    p.text(730, 1072, g["refs"], "body_b", 10.5, color="accent", align="right")


COVERS = {"split": cover_split, "editorial": cover_editorial, "band": cover_band,
          "photo_card": cover_photo_card, "duo": cover_duo, "mosaic": cover_mosaic}


def cover_page(p: Px, k: Kit, g):
    COVERS[k.layout["cover"]](p, k, g)


# ═══════════════════════════════════════════════════════════════════════════
# Pages communes aux six gabarits (couleurs, polices et photos varient)
# ═══════════════════════════════════════════════════════════════════════════

def toc_page(p: Px, k: Kit, g, parts, pages: dict):
    """Sommaire (maquette Aurora). `pages` : clé -> numéro relevé à la passe 1."""
    TR = g["TR"]
    paint_paper(p, k)
    draw_header(p, k, TR["ed_report_year"].format(y=g["year"]))
    p.text(56, 150, TR["toc_title"], k.title_font, 44, color="ink")
    y = 200
    for num, act, items in parts:
        p.text(56, y + 18, f"{num} — {act}", "body", 10.5, color="accent", track=0.14, upper=True)
        y += 34
        for key, label in items:
            p.text(56, y + 26, label, "display", 17, color="ink", max_w=560)
            pg = pages.get(key)
            if pg:
                p.text(738, y + 26, f"{pg:02d}", "body", 11, color="muted", align="right")
            p.line(56, y + 42, 738, y + 42, color="rule", lw=0.5)
            y += 46
        y += 18
    p.rect(56, 1000, 34, 0.9, "muted")
    p.para(104, 990, 420, esc(g["tagline"]),
           k.ps("tl", 12 * 0.75, font="display_i", color="muted", leading=17 * 0.75))
    draw_footer(p, k, g["footer_label"], p.cv.getPageNumber())


def focus_page(p: Px, k: Kit, g):
    """Focus environnement : photo de nature (thème du pilier), chiffre-clé
    et lecture de l'empreinte carbone."""
    TR = g["TR"]
    hs = g["hero"]
    paint_paper(p, k)
    draw_header(p, k, TR["ed_report_year"].format(y=g["year"]))
    p.image(k.photo("environment"), 56, 90, 330, 960, radius=k.layout["radius"])
    x, w = 424, 314
    p.text(x, 150, TR["ed_focus"], "body", 11, color="muted", track=0.14, upper=True)
    y = 166 + p.para(x, 166, w, esc(hs["statement"]),
                     k.ps("fs", 25 * 0.75, font="display", color="ink", leading=33 * 0.75))
    p.line(x, y + 24, x + w, y + 24, color="rule", lw=0.7)
    p.text(x, y + 100, f"{hs['value']}{hs['unit']}".replace(" ", ""), "display", 64, color="accent",
           max_w=w)
    y += 116 + p.para(x, y + 116, w, esc(hs["label"]),
                      k.ps("fl", 14 * 0.75, color="muted", leading=20 * 0.75))
    for text in (g.get("env_headline"), g.get("ghg_text")):
        if text:
            y += 26 + p.para(x, y + 26, w, esc(text),
                             k.ps("ft", 13 * 0.75, color="ink", leading=20 * 0.75), max_h=1040 - y)
    draw_footer(p, k, g["footer_label"], p.cv.getPageNumber())


def divider_page(p: Px, k: Kit, g, num, title, subtitle, intro, figures):
    """Carton de chapitre typographique : pas de photo d'illustration, mais
    ce que contient le chapitre et ses chiffres clés."""
    p.rect(0, 0, 794, 1123, "primary")
    p.text(56, 56, g["name"], "body", 10, color="accent_on_primary", track=0.14, upper=True,
           max_w=400)
    p.text(56, 330, num, "display", 150, color="accent_on_primary")
    h = p.para(56, 360, 600, esc(title), k.ps("dt", 50 * 0.75, font=k.title_font,
                                               color="on_primary", leading=56 * 0.75))
    y = 360 + h + 20
    p.rect(56, y, 64, 2, "accent_on_primary")
    y += 22 + p.para(56, y + 22, 560, esc(subtitle),
                     k.ps("ds", 20 * 0.75, font="display_i", color="accent_on_primary",
                          leading=28 * 0.75))
    p.para(56, y + 40, 600, esc(intro), k.ps("di", 14.5 * 0.75, color="on_primary",
                                              leading=23 * 0.75))
    cw = 682 / len(figures)
    p.line(56, 880, 738, 880, color="accent_on_primary", lw=0.6)
    for i, (val, lab) in enumerate(figures):
        x = 56 + i * cw
        p.text(x, 950, val, "display", 46, color="on_primary")
        p.text(x, 976, lab, "body", 11, color="accent_on_primary", track=0.08, upper=True,
               max_w=cw - 14)
    draw_footer(p, k, g["footer_label"], p.cv.getPageNumber(), on_dark=True)


def back_cover(p: Px, k: Kit, g):
    """Quatrième de couverture : la photo de couverture, en écho."""
    p.image(k.photo("cover"), 0, 0, 794, 1123)
    p.gradient_v(0, 0, 794, 520, "paper", 0.88, 0.0)
    p.gradient_v(0, 960, 794, 163, "primary", 0.0, 0.55)
    p.para(56, 40, 300, esc(g["name"].upper()),
           k.ps("bn", 10.5 * 0.75, font="body_b", color="ink", charSpace=1.4))
    p.para(56, 180, 480, esc(g["TR"]["ed_closing"]),
           k.ps("cl", 40 * 0.75, font=k.title_font, color="ink", leading=48 * 0.75))
    draw_footer(p, k, g["footer_label"], p.cv.getPageNumber(), on_dark=True)
