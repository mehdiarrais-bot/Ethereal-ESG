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


def test_images_du_readme_presentes():
    absentes = [p for p in _images_citees() if not os.path.isfile(os.path.join(ROOT, p))]
    assert not absentes, absentes
