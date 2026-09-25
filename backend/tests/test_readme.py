"""README : chaque image citée existe dans le dépôt.

Les captures de docs/img ont été refaites le 2026-09-25 (thème « Reporting »,
six gabarits) ; un renommage ou une suppression ne doit pas laisser le README
pointer vers une image absente.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _images_citees() -> list[str]:
    with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as f:
        texte = f.read()
    return re.findall(r'(?:src="|\]\()((?:docs|examples)/[^")]+\.(?:png|jpg|jpeg|gif|svg))', texte)


def test_readme_cite_des_captures():
    assert len(_images_citees()) >= 9


def test_exemple_de_grille_carbone_conforme_au_code():
    """Le README annonçait « 40 / 60 / 70 » : 70 n'existe pas dans la grille
    (notes 100/80/60/40/20). L'exemple est recalculé depuis esg_calculator."""
    from esg_calculator import carbon_thresholds_for, score_metric
    with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as f:
        texte = re.sub(r"\s+", " ", f.read())
    m = re.search(r"(\d+) t CO₂e par M€ de chiffre d'affaires valent (\d+)/100 dans les services, "
                  r"(\d+) dans l'industrie, (\d+) dans l'énergie", texte)
    assert m, "exemple de grille carbone introuvable dans le README"
    intensite, *annonces = (int(g) for g in m.groups())
    calcules = [score_metric(intensite, carbon_thresholds_for(s)[0], higher_is_better=False)
                for s in ("Services", "Industrie manufacturière", "Énergie")]
    assert annonces == calcules


def test_images_du_readme_presentes():
    absentes = [p for p in _images_citees() if not os.path.isfile(os.path.join(ROOT, p))]
    assert not absentes, absentes
