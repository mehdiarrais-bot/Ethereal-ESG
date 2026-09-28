"""Audit ESG et comité de durabilité : non renseigné n'est pas « non » (DETTE § 17).

Avant le 2026-09-27, `if not gov.esg_audit_conducted` lisait None comme False :
un dossier sans donnée de gouvernance recevait « Absence d'audit ESG
indépendant », « Pas de comité de durabilité » et le risque « Reporting non
audité » — des faits jamais déclarés. Ce qui AFFIRME un fait exige désormais
`is False` ; les recommandations et les lacunes de reporting, elles, visent
légitimement une donnée absente.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_suite import dossier_a_transparente                          # noqa: E402
from esg_calculator import calculate_esg_scores                        # noqa: E402
from content_generator import (generate_esg_content, compliance_assessment,  # noqa: E402
                               risks_opportunities, pillar_headline)

FAITS = {"fr": ("Absence d'audit ESG indépendant", "Pas de comité de durabilité",
                "Reporting non audité", "Aucune assurance externe", "Pas de comité dédié"),
         "en": ("No independent ESG audit", "No sustainability committee",
                "Unaudited reporting", "No external assurance", "No dedicated committee")}


def _dossier(lang, valeur):
    r = dossier_a_transparente().model_copy(update={"language": lang})
    r.governance.esg_audit_conducted = valeur
    r.governance.sustainability_committee = valeur
    return r


def _tout_le_texte(r):
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    risques = [str(risks_opportunities(r, s))]
    lignes = [str(g) for g in compliance_assessment(r, s)]
    return " ".join([*s.weaknesses, c["governance"], *risques, *lignes,
                     *[str(v) for v in pillar_headline(r, s).values()]])


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_non_renseigne_naffirme_aucun_manque(lang):
    texte = _tout_le_texte(_dossier(lang, None))
    for fait in FAITS[lang]:
        assert fait not in texte, (lang, fait)


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_un_non_declare_reste_signale(lang):
    texte = _tout_le_texte(_dossier(lang, False))
    for fait in FAITS[lang][:3]:
        assert fait in texte, (lang, fait)


def test_couverture_non_renseignee_statut_na():
    r = _dossier("fr", None)
    lignes = {g["ref"]: g for g in compliance_assessment(r, calculate_esg_scores(r))}
    assert lignes["ESRS 2 GOV-1"]["status"] == "na"
    assert lignes["CSRD (assurance limitée)"]["status"] == "na"
    assert lignes["ESRS 2 GOV-1"]["note"] == "Donnée non renseignée"


def test_les_recommandations_visent_encore_la_donnee_absente():
    s = calculate_esg_scores(_dossier("fr", None))
    assert any("audit ESG" in x for x in s.recommendations)
