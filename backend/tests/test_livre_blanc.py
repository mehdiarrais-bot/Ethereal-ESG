"""Livre blanc PDF (DETTE § 19).

Avant le 2026-09-27, la section « Vision stratégique » imprimait des cibles
que le client n'avait jamais données (« score cible +15 », « parité 40 % »,
« +50 % renouvelable ») et levait un TypeError dès qu'un pilier n'était pas
noté (`None + 15`). Elle dit désormais que les objectifs restent à définir.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_suite import dossier_a_transparente              # noqa: E402
from test_typo import _pdf_text                            # noqa: E402
from esg_calculator import calculate_esg_scores            # noqa: E402
from content_generator import generate_esg_content         # noqa: E402
from report_generator import generate_pdf_report           # noqa: E402
from models import ReportType, GovernanceData              # noqa: E402

CIBLES_FABRIQUEES = ("cible :", "Parité 40", "+50% renouvelable", "Target E score",
                     "40% gender balance", "+50% renewable")


def _livre_blanc(lang, gouvernance_vide):
    r = dossier_a_transparente().model_copy(
        update={"report_type": ReportType.WHITE_PAPER, "language": lang})
    if gouvernance_vide:  # 1 indicateur sur 8 : pilier non noté
        r.governance = GovernanceData(sustainability_committee=True)
    s = calculate_esg_scores(r)
    return s, _pdf_text(generate_pdf_report(r, s, generate_esg_content(r, s), {}))


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_livre_blanc_genere_avec_un_pilier_non_note(lang):
    s, texte = _livre_blanc(lang, gouvernance_vide=True)
    assert s.governance_score is None
    assert ("Aucun objectif chiffré" if lang == "fr" else "No quantified target") in texte


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_livre_blanc_sans_cible_fabriquee(lang):
    _, texte = _livre_blanc(lang, gouvernance_vide=False)
    for cible in CIBLES_FABRIQUEES:
        assert cible not in texte, (lang, cible)
