"""
Kit visuel procédural (PIL) — illustrations et icônes dessinées localement,
sans aucune image externe. Sert à transformer les slides ESG en infographies
thématisées : motifs d'écologie / social / gouvernance + icônes + anneaux.

Tout est dessiné en supersampling (x4) puis réduit pour un rendu lisse.
"""
import io
import math
from PIL import Image, ImageDraw, ImageFilter

SS = 4  # supersampling


def _hex(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _lerp(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def _canvas(size):
    return Image.new("RGBA", (size * SS, size * SS), (0, 0, 0, 0))


def _finish(img, size):
    return img.resize((size, size), Image.LANCZOS)


# ══════════════════════════════════════════════════════════════════════════
# ICÔNES — géométriques, monoline épais, arrondies → rendu « designé »
# ══════════════════════════════════════════════════════════════════════════

def draw_icon(name: str, size: int, color, bg=None) -> Image.Image:
    """Icône RGBA transparente. `color` = hex ou tuple RGB."""
    if isinstance(color, str):
        color = _hex(color)
    c = color + (255,)
    img = _canvas(size)
    d = ImageDraw.Draw(img)
    S = size * SS
    lw = max(2, int(S * 0.075))

    def line(pts, w=lw, fill=c, joint="curve"):
        d.line(pts, fill=fill, width=w, joint=joint)
        r = w / 2
        for (x, y) in (pts[0], pts[-1]):
            d.ellipse([x - r, y - r, x + r, y + r], fill=fill)

    m = S * 0.16  # marge
    a, b = m, S - m  # bornes

    if name == "leaf":
        from PIL import ImageChops
        # vesica (intersection de deux disques) → feuille pointue, puis rotation 45°
        d1 = Image.new("L", (S, S), 0)
        d2 = Image.new("L", (S, S), 0)
        off = S * 0.30
        r = S * 0.62
        ImageDraw.Draw(d1).ellipse([S / 2 - r + off, S / 2 - r, S / 2 + r + off, S / 2 + r], fill=255)
        ImageDraw.Draw(d2).ellipse([S / 2 - r - off, S / 2 - r, S / 2 + r - off, S / 2 + r], fill=255)
        mask = ImageChops.darker(d1, d2).rotate(45, resample=Image.BICUBIC, center=(S / 2, S / 2))
        leafimg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        leafimg.paste(Image.new("RGBA", (S, S), c), (0, 0), mask)
        # nervure centrale
        dl = ImageDraw.Draw(leafimg)
        dl.line([(S * 0.3, S * 0.7), (S * 0.7, S * 0.3)], fill=(255, 255, 255, 210), width=max(2, lw // 2))
        for k in range(1, 4):
            t = k / 4
            mx, my = S * 0.3 + 0.4 * S * t, S * 0.7 - 0.4 * S * t
            dl.line([(mx, my), (mx + S * 0.09, my + S * 0.03)], fill=(255, 255, 255, 150), width=max(1, lw // 3))
            dl.line([(mx, my), (mx - S * 0.03, my - S * 0.09)], fill=(255, 255, 255, 150), width=max(1, lw // 3))
        img = leafimg

    elif name == "drop":
        cx = S / 2
        top = a
        d.polygon([(cx, top), (b - lw, S * 0.62), (a + lw, S * 0.62)], fill=c)
        d.ellipse([a + lw, S * 0.42, b - lw, b], fill=c)

    elif name == "bolt":
        d.polygon([(S * 0.55, a), (a + lw, S * 0.56), (S * 0.46, S * 0.56),
                   (S * 0.42, b), (b - lw, S * 0.42), (S * 0.54, S * 0.42)], fill=c)

    elif name == "recycle":
        # flèche circulaire « cycle » (renouvelable), propre et lisible
        cx, cy, r = S / 2, S / 2, (b - a) / 2
        d.arc([cx - r, cy - r, cx + r, cy + r], -60, 240, fill=c, width=lw)
        # tête de flèche à l'extrémité (-60°)
        ang = math.radians(-60)
        ex, ey = cx + r * math.cos(ang), cy + r * math.sin(ang)
        ah = lw * 2.0
        tang = ang + math.pi / 2  # tangente
        tip = (ex + ah * math.cos(tang), ey + ah * math.sin(tang))
        base1 = (ex - ah * math.cos(tang) + ah * math.cos(ang), ey - ah * math.sin(tang) + ah * math.sin(ang))
        base2 = (ex - ah * math.cos(tang) - ah * math.cos(ang), ey - ah * math.sin(tang) - ah * math.sin(ang))
        d.polygon([tip, base1, base2], fill=c)

    elif name == "globe":
        d.ellipse([a, a, b, b], outline=c, width=lw)
        cx, cy = S / 2, S / 2
        d.line([(a, cy), (b, cy)], fill=c, width=lw)
        d.ellipse([S * 0.34, a, S * 0.66, b], outline=c, width=max(2, lw - SS))

    elif name == "tree":
        # tronc + houppier (3 cercles)
        d.rectangle([S / 2 - lw, S * 0.55, S / 2 + lw, b], fill=c)
        d.ellipse([a, S * 0.28, S * 0.62, S * 0.72], fill=c)
        d.ellipse([S * 0.42, a, b, S * 0.6], fill=c)
        d.ellipse([S * 0.30, S * 0.12, S * 0.72, S * 0.55], fill=c)

    elif name == "people":
        # deux personnages (tête + épaules)
        for dx, sc in [(-S * 0.16, 0.9), (S * 0.16, 1.0)]:
            cx = S / 2 + dx
            hr = S * 0.11 * sc
            d.ellipse([cx - hr, a, cx + hr, a + 2 * hr], fill=c)
            d.pieslice([cx - hr * 1.7, a + 2 * hr + lw, cx + hr * 1.7, b + hr], 180, 360, fill=c)

    elif name == "heart":
        cx, cy = S / 2, S * 0.42
        r = (b - a) * 0.26
        d.ellipse([cx - 2 * r, cy - r, cx, cy + r], fill=c)
        d.ellipse([cx, cy - r, cx + 2 * r, cy + r], fill=c)
        d.polygon([(cx - 2 * r + lw / 2, cy + r * 0.5), (cx + 2 * r - lw / 2, cy + r * 0.5), (cx, b)], fill=c)

    elif name == "cap":  # graduation
        cx = S / 2
        d.polygon([(cx, a), (b, S * 0.4), (cx, S * 0.55), (a, S * 0.4)], fill=c)
        d.polygon([(a + S * 0.14, S * 0.46), (b - S * 0.14, S * 0.46),
                   (b - S * 0.18, S * 0.66), (a + S * 0.18, S * 0.66)], fill=c)
        d.line([(b - lw, S * 0.4), (b - lw, S * 0.66)], fill=c, width=lw)
        d.ellipse([b - lw * 1.8, S * 0.66, b + lw * 0.4, S * 0.66 + lw * 2.2], fill=c)

    elif name == "shield":
        cx = S / 2
        d.polygon([(cx, a), (b, S * 0.28), (b, S * 0.55),
                   (cx, b), (a, S * 0.55), (a, S * 0.28)], fill=c)
        # check blanc
        d.line([(S * 0.38, S * 0.5), (S * 0.47, S * 0.6), (S * 0.66, S * 0.36)],
               fill=(255, 255, 255, 235), width=int(lw * 1.1), joint="curve")

    elif name == "scale":  # balance
        cx = S / 2
        d.line([(cx, a), (cx, b - lw)], fill=c, width=lw)
        d.line([(a, S * 0.3), (b, S * 0.3)], fill=c, width=lw)
        d.line([(cx - S * 0.16, b - lw), (cx + S * 0.16, b - lw)], fill=c, width=lw)  # socle
        for sx in (a, b):
            d.arc([sx - S * 0.12, S * 0.3, sx + S * 0.12, S * 0.55], 0, 180, fill=c, width=lw)
            d.line([(sx, S * 0.3), (sx - S * 0.12, S * 0.42)], fill=c, width=max(2, lw - SS))
            d.line([(sx, S * 0.3), (sx + S * 0.12, S * 0.42)], fill=c, width=max(2, lw - SS))

    elif name == "columns":  # institution / bâtiment
        d.polygon([(a, S * 0.32), (S / 2, a), (b, S * 0.32)], fill=c)  # fronton
        d.rectangle([a, S * 0.34, b, S * 0.4], fill=c)
        for i in range(3):
            x = a + S * 0.12 + i * S * 0.28
            d.rectangle([x, S * 0.44, x + S * 0.1, S * 0.78], fill=c)
        d.rectangle([a, S * 0.8, b, b], fill=c)

    elif name == "lock":  # cybersécurité
        d.rounded_rectangle([a, S * 0.44, b, b], radius=int(S * 0.06), fill=c)
        d.arc([S * 0.28, S * 0.16, S * 0.72, S * 0.6], 180, 360, fill=c, width=lw)
        d.ellipse([S / 2 - lw, S * 0.6, S / 2 + lw, S * 0.72], fill=(255, 255, 255, 230))

    elif name == "badge":  # check / audit
        cx, cy, r = S / 2, S / 2, (b - a) / 2
        d.ellipse([a, a, b, b], fill=c)
        d.line([(S * 0.36, S * 0.52), (S * 0.46, S * 0.63), (S * 0.66, S * 0.38)],
               fill=(255, 255, 255, 240), width=int(lw * 1.2), joint="curve")

    elif name == "cloud":  # émissions
        d.ellipse([a, S * 0.42, S * 0.5, S * 0.74], fill=c)
        d.ellipse([S * 0.28, S * 0.3, S * 0.72, S * 0.7], fill=c)
        d.ellipse([S * 0.5, S * 0.42, b, S * 0.74], fill=c)
        d.rectangle([a + S * 0.08, S * 0.6, b - S * 0.08, S * 0.74], fill=c)

    elif name == "chart":  # croissance
        d.line([(a, b), (a, a)], fill=c, width=lw)
        d.line([(a, b), (b, b)], fill=c, width=lw)
        for i, h in enumerate([0.32, 0.5, 0.7]):
            x = a + S * 0.14 + i * S * 0.22
            d.rectangle([x, b - (b - a) * h, x + S * 0.12, b - lw], fill=c)

    else:  # dot fallback
        d.ellipse([a, a, b, b], fill=c)

    return _finish(img, size)


# ══════════════════════════════════════════════════════════════════════════
# ANNEAU DE SCORE — donut avec valeur au centre
# ══════════════════════════════════════════════════════════════════════════

def score_ring(value: float, size: int, color, track=(255, 255, 255, 60),
               text_color=(255, 255, 255, 255)) -> Image.Image:
    if isinstance(color, str):
        color = _hex(color)
    if isinstance(text_color, str):
        text_color = _hex(text_color) + (255,)
    img = _canvas(size)
    d = ImageDraw.Draw(img)
    S = size * SS
    w = int(S * 0.11)
    box = [w, w, S - w, S - w]
    d.arc(box, 0, 360, fill=track, width=w)
    sweep = 360 * max(0, min(100, value)) / 100
    d.arc(box, -90, -90 + sweep, fill=color + (255,), width=w)
    # extrémité arrondie
    ang = math.radians(-90 + sweep)
    r = (S - 2 * w) / 2
    cx, cy = S / 2 + r * math.cos(ang), S / 2 + r * math.sin(ang)
    d.ellipse([cx - w / 2, cy - w / 2, cx + w / 2, cy + w / 2], fill=color + (255,))
    return _finish(img, size)


# ══════════════════════════════════════════════════════════════════════════
# HÉROS PAR PILIER — bandeau illustré évocateur (abstrait mais crédible)
# ══════════════════════════════════════════════════════════════════════════

def pillar_hero(pillar: str, palette: dict, width: int = 900, height: int = 1400) -> bytes:
    """Illustration verticale pour le flanc gauche d'une slide de pilier.

    palette : dict de hex {top, bottom, accent, light}
    pillar  : 'env' | 'social' | 'gov'
    """
    top = _hex(palette["top"])
    bottom = _hex(palette["bottom"])
    accent = _hex(palette["accent"])
    light = _hex(palette["light"])

    W, H = width * 2, height * 2  # supersample x2 (grande image)
    img = Image.new("RGB", (W, H), top)
    px = img.load()
    for y in range(H):
        row = _lerp(top, bottom, y / (H - 1))
        for x in range(W):
            px[x, y] = row
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    if pillar == "env":
        # collines superposées + soleil + feuilles
        d.ellipse([W * 0.60, H * 0.22, W * 0.90, H * 0.36], fill=accent + (210,))  # soleil (sous le titre)
        for i, (yc, al) in enumerate([(0.62, 90), (0.72, 130), (0.82, 180), (0.92, 220)]):
            col = _lerp(light, bottom, i / 4) + (al,)
            pts = [(0, H * (yc + 0.06))]
            for x in range(0, W + 40, 40):
                yy = H * yc - math.sin(x / W * math.pi * (1.5 + i * 0.4)) * H * 0.05
                pts.append((x, yy))
            pts += [(W, H), (0, H)]
            d.polygon(pts, fill=col)
        # feuilles flottantes
        for (fx, fy, s, rot) in [(0.2, 0.2, 0.13, 20), (0.72, 0.4, 0.1, -15), (0.35, 0.42, 0.08, 40)]:
            leaf = draw_icon("leaf", int(W * s), "#ffffff")
            leaf = leaf.rotate(rot, expand=True)
            leaf.putalpha(leaf.getchannel("A").point(lambda a: int(a * 0.5)))
            ov.alpha_composite(leaf, (int(W * fx), int(H * fy)))

    elif pillar == "social":
        # réseau de personnes (nœuds reliés)
        import hashlib
        nodes = []
        seedbase = 7
        for i in range(9):
            hx = int(hashlib.md5(f"{i}x".encode()).hexdigest(), 16)
            hy = int(hashlib.md5(f"{i}y".encode()).hexdigest(), 16)
            nx = W * (0.12 + (hx % 1000) / 1000 * 0.76)
            ny = H * (0.1 + (hy % 1000) / 1000 * 0.8)
            nodes.append((nx, ny))
        for i, (x0, y0) in enumerate(nodes):
            for (x1, y1) in nodes[i + 1:]:
                if math.hypot(x1 - x0, y1 - y0) < W * 0.5:
                    d.line([(x0, y0), (x1, y1)], fill=light + (70,), width=int(W * 0.006))
        for (x, y) in nodes:
            r = W * 0.05
            d.ellipse([x - r, y - r, x + r, y + r], fill=light + (200,))
            hr = r * 0.42
            d.ellipse([x - hr, y - r * 0.55, x + hr, y - r * 0.55 + 2 * hr], fill=top + (255,))
            d.pieslice([x - r * 0.62, y - r * 0.05, x + r * 0.62, y + r * 0.7], 180, 360, fill=top + (255,))

    else:  # gov
        # colonnes classiques + halo
        d.polygon([(W * 0.16, H * 0.34), (W * 0.5, H * 0.2), (W * 0.84, H * 0.34)], fill=light + (210,))
        d.rectangle([W * 0.16, H * 0.34, W * 0.84, H * 0.4], fill=light + (210,))
        for i in range(4):
            x = W * 0.2 + i * W * 0.17
            d.rectangle([x, H * 0.42, x + W * 0.08, H * 0.72], fill=light + (180,))
            # cannelure
            d.line([(x + W * 0.04, H * 0.42), (x + W * 0.04, H * 0.72)], fill=top + (120,), width=int(W * 0.006))
        d.rectangle([W * 0.14, H * 0.74, W * 0.86, H * 0.8], fill=light + (210,))
        # balance en filigrane (poussée à droite pour dégager le titre)
        scale = draw_icon("scale", int(W * 0.34), "#ffffff")
        scale.putalpha(scale.getchannel("A").point(lambda a: int(a * 0.30)))
        ov.alpha_composite(scale, (int(W * 0.56), int(H * 0.05)))

    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

    # Scrims de lisibilité : dégradé sombre en haut (titre) + disque doux (anneau)
    scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    th = int(H * 0.27)
    for y in range(th):
        sd.line([(0, y), (W, y)], fill=(0, 0, 0, int(85 * (1 - y / th))))
    # disque sous l'anneau de score (bas-gauche)
    disc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(disc)
    cx, cy, r = int(W * 0.5), int(H * 0.75), int(W * 0.42)
    dd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, 0, 0, 55))
    disc = disc.filter(ImageFilter.GaussianBlur(int(W * 0.05)))
    img = Image.alpha_composite(img.convert("RGBA"), disc)
    img = Image.alpha_composite(img, scrim).convert("RGB")
    img = img.resize((width, height), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf.read()


def icon_png(name: str, size: int, color) -> bytes:
    img = draw_icon(name, size, color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def ring_png(value: float, size: int, color, text_color=(255, 255, 255)) -> bytes:
    img = score_ring(value, size, color, text_color=text_color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()
