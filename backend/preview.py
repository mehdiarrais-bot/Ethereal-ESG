"""Image d'aperçu d'un gabarit (couverture + « coup d'œil » côte à côte, WebP).

Rendu PDF -> image par pypdfium2 (licence BSD/Apache : compatible avec un
logiciel diffusé « tous droits réservés », contrairement à PyMuPDF, AGPL,
qui reste une dépendance de développement des scripts). Sans pypdfium2,
`render` lève PreviewUnavailable : l'interface garde la vignette.
"""
import io

from PIL import Image

# Largeur d'une page dans l'aperçu, en pixels RÉELS : l'interface la demande
# d'après la taille affichée × la densité de l'écran (zoom Windows 150-200 %),
# sinon l'image est étirée et floue. Bornes : rendu lisible / poids raisonnable.
DEFAULT_WIDTH = 900
MIN_WIDTH, MAX_WIDTH = 300, 1600
GAP_RATIO = 0.03     # écart entre les pages, proportionnel, transparent : l'image
                     # prend le fond de l'interface sans en recopier la couleur
WEBP_QUALITY = 90    # WebP : transparence gardée, bien plus léger qu'un PNG HD


class PreviewUnavailable(RuntimeError):
    pass


def render(pdf: bytes, page_width: int = DEFAULT_WIDTH) -> bytes:
    """WebP des pages du PDF côte à côte, séparées par un écart transparent."""
    try:
        import pypdfium2 as pdfium
    except ImportError as e:  # installation sans la dépendance : dégradé propre
        raise PreviewUnavailable("pypdfium2 absent") from e
    width = max(MIN_WIDTH, min(MAX_WIDTH, int(page_width)))
    gap = round(width * GAP_RATIO)
    doc = pdfium.PdfDocument(pdf)
    pages = [page.render(scale=width / page.get_width()).to_pil().convert("RGB") for page in doc]
    h = max(p.height for p in pages)
    sheet = Image.new("RGBA", (width * len(pages) + gap * (len(pages) - 1), h), (0, 0, 0, 0))
    for i, p in enumerate(pages):
        sheet.paste(p, (i * (width + gap), 0))
    out = io.BytesIO()
    sheet.save(out, "WEBP", quality=WEBP_QUALITY, method=4)
    return out.getvalue()
