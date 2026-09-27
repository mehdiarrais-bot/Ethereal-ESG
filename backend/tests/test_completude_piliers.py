"""Complétude de la grille imprimée à côté de chaque score (DETTE § 16).

Un pilier n'est noté qu'à partir de MIN_INDICATEURS_PILIER indicateurs de sa
grille ; au-delà, un dossier qui ne déclare que ses meilleurs chiffres reste
notable. Le garde-fou est la complétude « notés/total » imprimée à côté de
chaque score, dans chaque livrable qui imprime un score de pilier.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_suite import make_request                                    # noqa: E402
from test_typo import _pdf_text, _docx_text, _pptx_text                # noqa: E402
from esg_calculator import (calculate_esg_scores, coverage_text,       # noqa: E402
                            MIN_INDICATEURS_PILIER, GRILLE_INDICATEURS)
from content_generator import generate_esg_content                     # noqa: E402
from i18n import L                                                     # noqa: E402

PILIERS = ("env", "social", "gov")


def _attendus(scores, lang, cle):
    return [coverage_text(scores, p, L(lang)[cle]) for p in PILIERS]


def test_la_couverture_suit_la_grille():
    s = calculate_esg_scores(make_request())
    for p in PILIERS:
        notes, total = s.indicator_coverage[p]
        assert total == len(GRILLE_INDICATEURS[p]) and 0 <= notes <= total


def test_sous_le_seuil_le_pilier_nest_pas_note():
    s = calculate_esg_scores(make_request())
    for p, attr in zip(PILIERS, ("environmental_score", "social_score", "governance_score")):
        sous_seuil = s.indicator_coverage[p][0] < MIN_INDICATEURS_PILIER
        assert (getattr(s, attr) is None) == sous_seuil, p


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_chaque_livrable_imprime_la_completude(lang):
    from report_generator import generate_pdf_report
    from onepager_generator import generate_onepager_pdf
    from docx_generator import generate_word_report
    from ppt_generator import generate_pptx
    r = make_request(lang)
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    longs, courts = _attendus(s, lang, "coverage"), _attendus(s, lang, "coverage_short")
    textes = {
        "pdf": (_pdf_text(generate_pdf_report(r, s, c, {})), longs + courts),
        "word": (_docx_text(generate_word_report(r, s, c)), longs),
        "synthese": (_pdf_text(generate_onepager_pdf(r, s)), longs),
        "pptx": (_pptx_text(generate_pptx(r, s, c, {})), courts),
    }
    for livrable, (texte, attendus) in textes.items():
        for a in attendus:
            assert a in texte or a.upper() in texte, (livrable, lang, a)


@pytest.mark.parametrize("lang,seuil", [("fr", "à partir de 3 indicateurs"),
                                        ("en", "only from 3 indicators")])
def test_la_note_methodologique_declare_le_seuil_comme_interne(lang, seuil):
    r = make_request(lang)
    note = generate_esg_content(r, calculate_esg_scores(r))["methodology"]
    assert seuil in note
    assert ("seuil interne" if lang == "fr" else "internal threshold") in note
