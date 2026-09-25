"""Taille des fonctions des générateurs PowerPoint et Word (chantier 4).

generate_pptx faisait 660 lignes et generate_word_report 528 : une fonction
par diapositive ou par section depuis le 2026-09-25 (sortie vérifiée
identique, XML compris, sur 19 dossiers). Ce test empêche de les regonfler.
"""
import ast
import os

import pytest

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_LIGNES = 40  # CLAUDE.md : signaler toute fonction de plus de 40 lignes

# Antérieures au chantier et hors de son périmètre : à découper plus tard.
EXCEPTIONS = {
    ("ppt_generator.py", "pillar_infographic"),
    ("ppt_generator.py", "content_slide"),
}


def _fonctions(fichier: str) -> list[tuple[str, int]]:
    with open(os.path.join(BACKEND, fichier), encoding="utf-8") as f:
        arbre = ast.parse(f.read())
    return [(n.name, n.end_lineno - n.lineno + 1) for n in arbre.body  # type: ignore[operator]
            if isinstance(n, ast.FunctionDef)]


@pytest.mark.parametrize("fichier", ["ppt_generator.py", "docx_generator.py"])
def test_aucune_fonction_de_plus_de_40_lignes(fichier):
    trop_longues = [(nom, n) for nom, n in _fonctions(fichier)
                    if n > MAX_LIGNES and (fichier, nom) not in EXCEPTIONS]
    assert not trop_longues, trop_longues


@pytest.mark.parametrize("fichier,fonction", [("ppt_generator.py", "generate_pptx"),
                                              ("docx_generator.py", "generate_word_report")])
def test_le_generateur_ne_fait_qu_enchainer_les_sections(fichier, fonction):
    assert dict(_fonctions(fichier))[fonction] <= MAX_LIGNES
