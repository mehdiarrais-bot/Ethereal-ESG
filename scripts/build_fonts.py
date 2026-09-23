"""Produit les polices statiques embarquées dans backend/assets/fonts/.

ReportLab ne sait pas choisir une graisse dans une police variable : il lit
l'instance par défaut. Ce script fige donc chaque famille (téléchargée depuis
github.com/google/fonts, licence SIL OFL 1.1) en quatre fichiers statiques —
Light, Regular, SemiBold, Italic — puis les réduit au jeu de caractères latin
utile aux livrables FR/EN.

Usage (depuis la racine du dépôt) :
    python scripts/build_fonts.py <dossier_des_ttf_variables>

Le dossier source doit contenir les fichiers nommés comme dans FAMILIES
(ex. « Newsreader.ttf », « Newsreader-Italic.ttf ») et les « OFL-<id>.txt ».
"""
import os
import shutil
import sys

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

OUT = os.path.join(os.path.dirname(__file__), "..", "backend", "assets", "fonts")

# id google/fonts -> (nom de famille, fichier droit, fichier italique, axes fixes)
FAMILIES = {
    "newsreader": ("Newsreader", "Newsreader.ttf", "Newsreader-Italic.ttf", {"opsz": 36}),
    "instrumentserif": ("InstrumentSerif", "InstrumentSerif-Regular.ttf",
                        "InstrumentSerif-Italic.ttf", {}),
    "instrumentsans": ("InstrumentSans", "InstrumentSans.ttf", "InstrumentSans-Italic.ttf",
                       {"wdth": 100}),
    "hankengrotesk": ("HankenGrotesk", "HankenGrotesk.ttf", "HankenGrotesk-Italic.ttf", {}),
    "librecaslontext": ("LibreCaslonText", "LibreCaslonText.ttf",
                        "LibreCaslonText-Italic.ttf", {}),
    "albertsans": ("AlbertSans", "AlbertSans.ttf", "AlbertSans-Italic.ttf", {}),
    "sourcesans3": ("SourceSans3", "SourceSans3.ttf", "SourceSans3-Italic.ttf", {}),
}

# Graisse demandée -> graisse effective bornée par l'axe de la police
STYLES = {"Light": 300, "Regular": 400, "SemiBold": 600}

# Latin de base + Latin-1 + Latin étendu A + ponctuation typographique, €, ≤ ≥ −,
# formes géométriques (si la police les dessine)
UNICODES = (list(range(0x20, 0x7F)) + list(range(0xA0, 0x180))
            + list(range(0x2010, 0x2060)) + [0x20AC, 0x2122, 0x2190, 0x2192,
                                              0x2212, 0x2264, 0x2265, 0x2248, 0x00D7]
            + list(range(0x25A0, 0x25D0)))  # ■ ▪ ● pastilles de statut


def _subset(font: TTFont) -> TTFont:
    opts = subset.Options()
    opts.layout_features = ["kern", "liga", "lnum", "tnum", "pnum"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    sub = subset.Subsetter(options=opts)
    sub.populate(unicodes=UNICODES)
    sub.subset(font)
    return font


def _static(src: str, axes: dict, weight: int | None) -> TTFont:
    font = TTFont(src)
    if "fvar" not in font:
        return font
    loc = dict(axes)
    wght = next((a for a in font["fvar"].axes if a.axisTag == "wght"), None)
    if wght is not None:
        loc["wght"] = max(wght.minValue, min(wght.maxValue, weight or wght.defaultValue))
    for a in font["fvar"].axes:
        loc.setdefault(a.axisTag, a.defaultValue)
    return instancer.instantiateVariableFont(font, loc, updateFontNames=False)


def main(src_dir: str) -> None:
    os.makedirs(OUT, exist_ok=True)
    for fid, (name, upright, italic, axes) in FAMILIES.items():
        dest = os.path.join(OUT, name)
        os.makedirs(dest, exist_ok=True)
        for style, weight in STYLES.items():
            f = _subset(_static(os.path.join(src_dir, upright), axes, weight))
            f.save(os.path.join(dest, f"{name}-{style}.ttf"))
        f = _subset(_static(os.path.join(src_dir, italic), axes, 400))
        f.save(os.path.join(dest, f"{name}-Italic.ttf"))
        shutil.copy(os.path.join(src_dir, f"OFL-{fid}.txt"), os.path.join(dest, "OFL.txt"))
        print("ok", name)


if __name__ == "__main__":
    main(sys.argv[1])
