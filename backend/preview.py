"""Image d'aperçu d'un gabarit (couverture + « coup d'œil » côte à côte, PNG).

Rendu PDF -> image par pypdfium2 (licence BSD/Apache : compatible avec un
logiciel diffusé « tous droits réservés », contrairement à PyMuPDF, AGPL,
qui reste une dépendance de développement des scripts). Sans pypdfium2,
`render` lève PreviewUnavailable : l'interface garde la vignette.
"""
import io

from PIL import Image

PAGE_WIDTH = 460     # px par page dans l'aperçu (lisible sur l'écran du sélecteur)
GAP = 14             # px entre les deux pages, transparents : l'image prend le
                     # fond de l'interface sans en recopier la couleur


class PreviewUnavailable(RuntimeError):
    pass


def render(pdf: bytes) -> bytes:
    """PNG des pages du PDF, côte à côte, séparées par un espace transparent."""
    try:
        import pypdfium2 as pdfium
    except ImportError as e:  # installation sans la dépendance : dégradé propre
        raise PreviewUnavailable("pypdfium2 absent") from e
    doc = pdfium.PdfDocument(pdf)
    pages = []
    for page in doc:
        scale = PAGE_WIDTH / page.get_width()
        pages.append(page.render(scale=scale).to_pil().convert("RGB"))
    h = max(p.height for p in pages)
    sheet = Image.new("RGBA", (PAGE_WIDTH * len(pages) + GAP * (len(pages) - 1), h), (0, 0, 0, 0))
    for i, p in enumerate(pages):
        sheet.paste(p, (i * (PAGE_WIDTH + GAP), 0))
    out = io.BytesIO()
    sheet.save(out, "PNG", optimize=True)
    return out.getvalue()
