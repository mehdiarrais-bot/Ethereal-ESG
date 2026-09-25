"""Affirmations réglementaires relevées le 2026-09-25 (règle 9 de CLAUDE.md).

1. Mixité de l'effectif : aucun quota légal (DETTE § 4). Le registre des
   risques la classait « Réglementaire » (« Parité sous la cible : risque
   réglementaire et d'attractivité »), repris dans la synthèse une page.
2. Femmes au conseil : le quota de 40 % relève de la loi Copé-Zimmermann
   (art. L225-18-1 du Code de commerce), pas de la loi Rixain. Corrigé dans
   les livrables le 2026-09-03, resté faux dans l'écran de saisie.
3. Vérification par un tiers : exigée des seules entreprises soumises à la
   CSRD. Depuis la directive (UE) 2026/470 (JO du 26.2.2026), le champ est
   > 450 M€ de CA net ET > 1 000 salariés en moyenne ; le livrable la
   présentait comme « requise par la CSRD » pour tout client.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_suite import make_request  # noqa: E402
from esg_calculator import calculate_esg_scores  # noqa: E402
from content_generator import (generate_esg_content, risks_opportunities,  # noqa: E402
                               _esrs_gaps, _REC_META)
from models import GovernanceData  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CSRD_OBLIGATION_INCONDITIONNELLE = [
    "requise par la CSRD", "désormais requise par la CSRD", "sécuriser la conformité CSRD",
    "required by the CSRD", "now required by CSRD", "secure CSRD readiness",
]


def _textes(obj) -> str:
    if isinstance(obj, dict):
        return " ".join(_textes(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return " ".join(_textes(v) for v in obj)
    return obj if isinstance(obj, str) else ""


# Seule la mixité déclenche un risque : il n'est pas évincé par la limite de quatre.
_GOUV_SANS_RISQUE = GovernanceData(esg_audit_conducted=True, sustainability_committee=True,
                                   data_breaches=0, independent_board_percent=45)


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_mixite_effectif_jamais_reglementaire(lang):
    req = make_request(lang=lang, governance=_GOUV_SANS_RISQUE)
    risques = risks_opportunities(req, calculate_esg_scores(req))["risks"]
    mixite = [r for r in risques if any(m in r["text"].lower()
                                        for m in ("mixité", "parité", "gender"))]
    assert mixite, risques
    for r in mixite:
        assert r["tag"] not in ("Réglementaire", "Regulatory"), r
        assert "réglementaire" not in r["text"].lower() and "regulatory" not in r["text"].lower(), r


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_verification_tiers_conditionnee_au_champ_csrd(lang):
    req = make_request(lang=lang)  # esg_audit_conducted=False : la lacune est listée
    texte = _textes(generate_esg_content(req, calculate_esg_scores(req)))
    for formule in CSRD_OBLIGATION_INCONDITIONNELLE:
        assert formule not in texte, formule
    # La lacune et l'action « audit » disent à qui l'obligation s'applique.
    conditionnel = "soumises à la CSRD" if lang == "fr" else "subject to the CSRD"
    lacune = [g for g in _esrs_gaps(req, lang == "en") if "CSRD" in g]
    assert lacune and all(conditionnel in g for g in lacune), lacune
    audit = _REC_META["audit"][3 if lang == "fr" else 4]
    assert conditionnel in audit, audit


def test_saisie_femmes_au_conseil_cite_cope_zimmermann():
    with open(os.path.join(ROOT, "frontend", "src", "components", "steps", "StepGovernance.jsx"),
              encoding="utf-8") as f:
        src = f.read()
    assert "Rixain" not in src
    assert "L225-18-1" in src


# ── 4. La CSRD présentée comme une obligation du client (DETTE § 13) ──────
# Depuis la directive (UE) 2026/470 (> 450 M€ de CA ET > 1 000 salariés) et
# le report de la loi n° 2025-391 (grandes entreprises : exercices ouverts à
# compter de 2027), la clientèle PME/ETI n'est, sauf exception, pas soumise :
# le livrable prédisait pourtant une « non-conformité CSRD à venir » (P1).
CSRD_PRESUMEE_APPLICABLE = [
    "non-conformité CSRD", "conformité CSRD", "Exigences CSRD croissantes",
    "exigé par l'ESRS E1 de la CSRD", "requis par la CSRD",
    "CSRD non-compliance", "CSRD compliance", "Rising CSRD requirements",
    "required under CSRD", "required by the CSRD",
    # lettre de mission : présumait la CSRD applicable « au marché PME/ETI »
    "exigences CSRD/VSME applicables", "CSRD/VSME requirements applicable",
]


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_aucun_livrable_ne_presume_la_csrd_applicable(lang):
    from test_suite import _textes_des_livrables
    from models import EnvironmentalData
    # Scope 3 absent : le cas qui déclenchait le risque « non-conformité ».
    env = EnvironmentalData(co2_emissions_tonnes=3300, scope1_emissions=1200, scope2_emissions=2100)
    textes = _textes_des_livrables(make_request(lang=lang, environmental=env))
    for nom, texte in textes.items():
        for formule in CSRD_PRESUMEE_APPLICABLE:
            assert formule not in texte, (nom, formule)


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_scope3_manquant_est_une_lacune_de_fiabilite(lang):
    from models import EnvironmentalData
    env = EnvironmentalData(co2_emissions_tonnes=3300, scope1_emissions=1200, scope2_emissions=2100)
    req = make_request(lang=lang, environmental=env)
    risques = risks_opportunities(req, calculate_esg_scores(req))["risks"]
    scope3 = [r for r in risques if "Scope 3" in r["text"]]
    assert scope3 and all(r["tag"] in ("Fiabilité", "Reliability") for r in scope3), scope3


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_note_methodologique_cite_le_champ_verifie_de_la_csrd(lang):
    req = make_request(lang=lang)
    note = generate_esg_content(req, calculate_esg_scores(req))["methodology"]
    for repere in ("2025-391", "2026/470", "19 March 2027" if lang == "en" else "19 mars 2027"):
        assert repere in note, repere
    assert ("ne se prononce pas" if lang == "fr" else "does not assess") in note


# ── 5. Mixité de l'effectif : repères internes déclarés (option D1) ───────
@pytest.mark.parametrize("lang", ["fr", "en"])
def test_reperes_de_mixite_declares_internes(lang):
    from esg_calculator import MIXITE_EFFECTIF_REPERE
    req = make_request(lang=lang)
    note = generate_esg_content(req, calculate_esg_scores(req))["methodology"]
    assert ("repères internes" if lang == "fr" else "internal benchmarks") in note
    assert f"{MIXITE_EFFECTIF_REPERE} %" in note or f"{MIXITE_EFFECTIF_REPERE}%" in note
    assert ("aucun quota légal" if lang == "fr" else "no legal quota") in note


def test_seuil_de_mixite_source_unique():
    """Le 40 % de mixité de l'effectif n'est écrit qu'une fois (esg_calculator)."""
    import re as _re
    for fichier in ("esg_calculator.py", "content_generator.py"):
        with open(os.path.join(ROOT, "backend", fichier), encoding="utf-8") as f:
            src = f.read()
        assert not _re.search(r"female_employees_percent\s*(<|>=)\s*40\b", src), fichier
