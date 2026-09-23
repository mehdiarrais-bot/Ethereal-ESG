"""Bandeau photo des livrables Office (couverture PPTX, page de garde Word).

Reprend la photo de couverture du gabarit — celle fournie par l'entreprise,
sinon celle de la banque locale (assets/photos, domaine public / CC0) — et
la recadre au format bandeau. Aucun appel réseau.
"""
import io

from PIL import Image


def cover_banner(request, width: int = 1600, height: int = 560) -> bytes | None:
    """Photo de couverture recadrée au centre en width × height (JPEG)."""
    from pdf_kit import Kit
    raw = Kit(request).photo("cover")
    if not raw:
        return None
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    ratio = width / height
    iw, ih = im.size
    if iw / ih > ratio:
        nw = int(ih * ratio)
        im = im.crop(((iw - nw) // 2, 0, (iw - nw) // 2 + nw, ih))
    else:
        nh = int(iw / ratio)
        top = (ih - nh) // 2
        im = im.crop((0, top, iw, top + nh))
    im = im.resize((width, height), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=85)
    return buf.getvalue()
