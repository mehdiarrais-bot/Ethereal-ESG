"""Banque d'images locale : illustrations abstraites générées procéduralement.

Aucun appel réseau — les visuels sont dessinés avec Pillow, seedés par le nom
de l'entreprise pour que deux sociétés n'aient jamais la même illustration,
et déclinés selon le motif propre à chaque thème esthétique.
"""
import io
import hashlib
import random
import math
from PIL import Image, ImageDraw, ImageFilter
from models import AestheticTheme

# (couleur_haut, couleur_bas, couleur_motif_1, couleur_motif_2, motif)
ART_SPECS = {
    AestheticTheme.CORPORATE_BLUE:    ("#1B3A6B", "#2E86C1", "#F39C12", "#AEC6E8", "beams"),
    AestheticTheme.GREEN_NATURE:      ("#1A5C38", "#27AE60", "#F1C40F", "#A9DBBC", "circles"),
    AestheticTheme.DARK_PREMIUM:      ("#0D1117", "#1F252E", "#F7C948", "#58A6FF", "beams"),
    AestheticTheme.MINIMAL_WHITE:     ("#FAFAFA", "#EAEAEA", "#FF6F00", "#BDBDBD", "dots"),
    AestheticTheme.SUNSET_TERRACOTTA: ("#9A3412", "#E76F51", "#F4A261", "#FAE5D8", "circles"),
    AestheticTheme.OCEAN_DEEP:        ("#0F4C5C", "#277DA1", "#00BFA6", "#A8D8E0", "waves"),
    AestheticTheme.ROYAL_PURPLE:      ("#2B1055", "#5E35B1", "#FFD54F", "#B9A6E0", "beams"),
}


def _hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _lerp(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def _gradient(width, height, top, bottom):
    img = Image.new("RGB", (width, height))
    px = img.load()
    for y in range(height):
        row = _lerp(top, bottom, y / max(1, height - 1))
        for x in range(width):
            px[x, y] = row
    return img


def cover_art(theme: AestheticTheme, seed_text: str = "",
              width: int = 1600, height: int = 560) -> bytes:
    """Génère une illustration abstraite thématisée, unique par entreprise."""
    spec = ART_SPECS.get(theme, ART_SPECS[AestheticTheme.CORPORATE_BLUE])
    top, bottom, accent1, accent2, motif = spec
    top, bottom = _hex_rgb(top), _hex_rgb(bottom)
    accents = [_hex_rgb(accent1), _hex_rgb(accent2)]

    seed = int(hashlib.md5((seed_text + theme.value).encode()).hexdigest(), 16) % (2 ** 31)
    rng = random.Random(seed)

    base = _gradient(width, height, top, bottom)
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    if motif == "circles":
        # Cercles organiques translucides de tailles variées
        for _ in range(rng.randint(10, 16)):
            r = rng.randint(height // 8, height // 2)
            cx = rng.randint(-r // 2, width + r // 2)
            cy = rng.randint(-r // 2, height + r // 2)
            color = rng.choice(accents) + (rng.randint(25, 70),)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    elif motif == "waves":
        # Bandes sinusoïdales superposées
        for w in range(rng.randint(4, 6)):
            amp = rng.randint(height // 12, height // 5)
            period = rng.uniform(0.8, 2.2) * width
            phase = rng.uniform(0, 2 * math.pi)
            y0 = rng.randint(height // 4, height)
            color = rng.choice(accents) + (rng.randint(30, 70),)
            pts = [(x, y0 + amp * math.sin(2 * math.pi * x / period + phase))
                   for x in range(0, width + 20, 20)]
            pts += [(width, height), (0, height)]
            draw.polygon(pts, fill=color)

    elif motif == "beams":
        # Faisceaux diagonaux
        for _ in range(rng.randint(5, 8)):
            x0 = rng.randint(-width // 3, width)
            bw = rng.randint(width // 20, width // 6)
            slant = rng.randint(height // 2, height * 2)
            color = rng.choice(accents) + (rng.randint(18, 50),)
            draw.polygon([(x0, height), (x0 + bw, height),
                          (x0 + bw + slant, -50), (x0 + slant, -50)], fill=color)

    else:  # dots
        # Grille de points clairsemée
        step = width // rng.randint(18, 26)
        for gx in range(0, width + step, step):
            for gy in range(0, height + step, step):
                if rng.random() < 0.45:
                    r = rng.randint(3, max(4, step // 6))
                    color = rng.choice(accents) + (rng.randint(60, 130),)
                    draw.ellipse([gx - r, gy - r, gx + r, gy + r], fill=color)

    overlay = overlay.filter(ImageFilter.GaussianBlur(2))
    base = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")

    buf = io.BytesIO()
    base.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf.read()
