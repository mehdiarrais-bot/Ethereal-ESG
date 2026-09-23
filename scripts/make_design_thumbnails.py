#!/usr/bin/env python3
"""Régénère les vignettes des gabarits affichées par le sélecteur du frontend.

Chaque vignette montre la couverture et la page « ESG en un coup d'œil »
telles que le générateur PDF les produit réellement, sur la société fictive
de scripts/make_examples.py. À relancer après toute modification d'un
gabarit (report_designs.py, pdf_pages.py) :

    python scripts/make_design_thumbnails.py

Sortie : frontend/public/designs/<gabarit>.jpg (dépendance de dev : PyMuPDF).
"""
import io
import os
import sys

import fitz  # PyMuPDF
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "backend"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
OUT = os.path.join(ROOT, "frontend", "public", "designs")

from make_examples import DEMO                                   # noqa: E402
from models import AestheticTheme                                # noqa: E402
from esg_calculator import calculate_esg_scores                  # noqa: E402
from content_generator import generate_esg_content               # noqa: E402
from report_generator import generate_pdf_report                 # noqa: E402

PAGE_W = 300          # largeur d'une page dans la vignette (px)
GAP = 10


def page_image(doc, index: int) -> Image.Image:
    pix = doc[index].get_pixmap(dpi=90)
    im = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    return im.resize((PAGE_W, round(im.height * PAGE_W / im.width)), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    scores = calculate_esg_scores(DEMO)
    content = generate_esg_content(DEMO, scores)
    for theme in AestheticTheme:
        req = DEMO.model_copy(update={"aesthetic_theme": theme})
        doc = fitz.open(stream=generate_pdf_report(req, scores, content, {}), filetype="pdf")
        # page 1 = couverture ; la page « coup d'œil » suit le sommaire,
        # l'entreprise en bref et le mot de la direction
        glance = next(i for i in range(doc.page_count)
                      if "coup d" in doc[i].get_text() and i > 1)
        cover, g = page_image(doc, 0), page_image(doc, glance)
        sheet = Image.new("RGB", (PAGE_W * 2 + GAP, cover.height), "#d9d8d3")
        sheet.paste(cover, (0, 0))
        sheet.paste(g, (PAGE_W + GAP, 0))
        path = os.path.join(OUT, f"{theme.value}.jpg")
        sheet.save(path, quality=82, optimize=True)
        print(f"  {theme.value:16s} {os.path.getsize(path) // 1024:4d} Ko")


if __name__ == "__main__":
    main()
