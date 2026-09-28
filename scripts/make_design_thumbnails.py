#!/usr/bin/env python3
"""Régénère les vignettes des gabarits affichées par le sélecteur du frontend.

Chaque vignette montre la couverture et la page « ESG en un coup d'œil »
telles que le générateur PDF les produit réellement, sur la société fictive
de scripts/make_examples.py. À relancer après toute modification d'un
gabarit (report_designs.py, pdf_pages.py) :

    python scripts/make_design_thumbnails.py

Sortie : frontend/public/designs/<gabarit>.webp. Mêmes pages et même mise en
page que l'aperçu vivant (report_generator.preview_pdf + preview.render) : la
vignette et le rendu réel se superposent exactement pendant le fondu.
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "backend"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
OUT = os.path.join(ROOT, "frontend", "public", "designs")

from make_examples import DEMO                                   # noqa: E402
from models import AestheticTheme                                # noqa: E402
from esg_calculator import calculate_esg_scores                  # noqa: E402
from report_generator import preview_pdf                         # noqa: E402
import preview                                                   # noqa: E402

# Largeur d'une page de vignette, en pixels réels : nette jusqu'à un écran
# à 200 % pour la taille d'affichage du sélecteur.
PAGE_WIDTH = 720


def main():
    os.makedirs(OUT, exist_ok=True)
    scores = calculate_esg_scores(DEMO)
    for theme in AestheticTheme:
        req = DEMO.model_copy(update={"aesthetic_theme": theme})
        image = preview.render(preview_pdf(req, scores), PAGE_WIDTH)
        path = os.path.join(OUT, f"{theme.value}.webp")
        with open(path, "wb") as f:
            f.write(image)
        print(f"  {theme.value:16s} {os.path.getsize(path) // 1024:4d} Ko")


if __name__ == "__main__":
    main()
