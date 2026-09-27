"""Stade de maturité : un seul rang, de 1 à 5, dans tous les livrables (DETTE § 18).

`esg_maturity` rend un stage de 0 à 4. Avant le 2026-09-27, le PDF, le Word,
la synthèse une page et la lettre imprimaient « Structurée (2/5) » quand la
diapositive allumait la case « 3 » ; le premier stade s'imprimait « (0/5) ».
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_suite import dossier_a_transparente                   # noqa: E402
from test_typo import _pdf_text, _docx_text                     # noqa: E402
from esg_calculator import calculate_esg_scores                 # noqa: E402
from esg_advanced import esg_maturity                           # noqa: E402
from content_generator import generate_esg_content, maturite_rang  # noqa: E402


@pytest.mark.parametrize("stage,rang", [(0, "1/5"), (2, "3/5"), (4, "5/5")])
def test_rang_affiche_de_1_a_5(stage, rang):
    assert maturite_rang({"stage": stage}) == rang


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_meme_rang_dans_chaque_livrable(lang):
    from report_generator import generate_pdf_report
    from docx_generator import generate_word_report
    from onepager_generator import generate_onepager_pdf
    from proposal_generator import generate_proposal_docx
    r = dossier_a_transparente().model_copy(update={"language": lang})
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    stage = esg_maturity(r, s)["stage"]
    juste, faux = f"({stage + 1}/5)", f"({stage}/5)"
    textes = {"pdf": _pdf_text(generate_pdf_report(r, s, c, {})),
              "word": _docx_text(generate_word_report(r, s, c)),
              "synthese": _pdf_text(generate_onepager_pdf(r, s)),
              "lettre": _docx_text(generate_proposal_docx(r, s))}
    for livrable, texte in textes.items():
        assert juste in texte and faux not in texte, (livrable, lang)
