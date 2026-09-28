"""Étape B, lot 1 : trajectoire climat déclarée par le client (DETTE § 0bis).

Une cible COMPLÈTE (réduction, année de référence, année cible) est citée
comme déclarée par l'entreprise, avec l'arithmétique qui en découle, et
jamais évaluée. Une saisie partielle vaut absence : aucune valeur par défaut.
"""
import os
import sys
from typing import Any

import pytest
from pydantic import ValidationError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_suite import dossier_a_transparente                      # noqa: E402
from test_typo import _pdf_text, _docx_text, _pptx_text             # noqa: E402
from esg_calculator import calculate_esg_scores                     # noqa: E402
from content_generator import generate_esg_content, compliance_assessment  # noqa: E402
from models import TargetsData, ReportType                          # noqa: E402
import targets as TG                                                # noqa: E402

CIBLE: dict[str, Any] = dict(climate_reduction_percent=42, climate_base_year=2025, climate_target_year=2030,
             climate_scopes="1-2")


def _dossier(lang="fr", **cible):
    r = dossier_a_transparente().model_copy(update={"language": lang})
    r.targets = TargetsData(**cible)
    return r


def test_arithmetique_de_la_cible():
    c = TG.climate_target(_dossier(**CIBLE))
    assert c is not None
    assert c.annual_pace == pytest.approx(8.4)            # 42 % sur 5 ans
    assert c.base_tonnes == 1200 + 2100                   # scopes 1-2 de l'exercice 2025
    assert c.target_tonnes == pytest.approx(3300 * 0.58)


@pytest.mark.parametrize("lang,attendus", [
    ("fr", ("déclare un objectif de réduction", "42 %", "entre 2025 et 2030", "scopes 1 et 2",
            "8,4 %", "1 914 t CO₂e", "sans évaluer son alignement")),
    ("en", ("reports a target to reduce", "42%", "between 2025 and 2030", "Scopes 1 and 2",
            "8.4%", "1,914 t CO₂e", "without assessing its alignment")),
])
def test_texte_objectifs_cite_la_cible(lang, attendus):
    r = _dossier(lang, **CIBLE)
    texte = generate_esg_content(r, calculate_esg_scores(r))["targets"].replace(" ", " ")
    for a in attendus:
        assert a in texte, (lang, a, texte)


@pytest.mark.parametrize("partielle", [
    {}, dict(climate_reduction_percent=42), dict(climate_reduction_percent=42, climate_target_year=2030),
])
def test_cible_partielle_vaut_absence(partielle):
    r = _dossier(**partielle)
    assert TG.climate_target(r) is None
    texte = generate_esg_content(r, calculate_esg_scores(r))["targets"]
    assert "n'a pas communiqué d'objectifs" in texte


def _cible(**modif) -> TG.ClimateTarget:
    c = TG.climate_target(_dossier(**{**CIBLE, **modif}))
    assert c is not None
    return c


def test_tonnes_seulement_si_reference_et_perimetre_connus():
    assert _cible(climate_base_year=2022).base_tonnes is None
    assert _cible(climate_scopes=None).base_tonnes is None
    assert _cible(climate_scopes="1-2-3").base_tonnes == 8200


def test_ligne_esrs_e1_4():
    sans = _dossier()
    avec = _dossier(**CIBLE)
    ligne = lambda r: next(g for g in compliance_assessment(r, calculate_esg_scores(r))  # noqa: E731
                           if g["ref"] == "ESRS E1-4")
    assert ligne(sans)["status"] == "na"
    assert ligne(avec)["status"] == "ok" and "Cible déclarée" in ligne(avec)["note"]


@pytest.mark.parametrize("donnees,message", [
    (dict(climate_base_year=2030, climate_target_year=2028), "suivre l'année de référence"),
    (dict(climate_scopes="2-3"), "pattern"),
])
def test_validation_de_la_cible(donnees, message):
    with pytest.raises(ValidationError, match=message):
        TargetsData(**donnees)


def test_reference_posterieure_a_l_exercice_refusee():
    r = dossier_a_transparente()
    d = r.model_dump()
    d["targets"] = dict(climate_base_year=2027)
    with pytest.raises(ValidationError, match="ne peut pas suivre l'exercice"):
        type(r).model_validate(d)


def test_ancien_dossier_sans_objectifs_se_relit():
    d = dossier_a_transparente().model_dump()
    d.pop("targets")
    r = type(dossier_a_transparente()).model_validate(d)
    assert TG.climate_target(r) is None


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_chaque_livrable_cite_la_cible(lang):
    from report_generator import generate_pdf_report
    from docx_generator import generate_word_report
    r = _dossier(lang, **CIBLE)
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    marque = "entre 2025 et 2030" if lang == "fr" else "between 2025 and 2030"
    assert marque in _pdf_text(generate_pdf_report(r, s, c, {})).replace("\n", " ")
    assert marque in _docx_text(generate_word_report(r, s, c))
    wp = r.model_copy(update={"report_type": ReportType.WHITE_PAPER})
    assert marque in _pdf_text(generate_pdf_report(wp, s, c, {})).replace("\n", " ")


def test_import_csv_et_questionnaire_portent_la_cible():
    from import_data import build_form, template_csv
    from questionnaire_generator import generate_questionnaire_html
    f = build_form([("Réduction visée des émissions", "42"), ("Année de référence de la cible", "2025"),
                    ("Année cible de la réduction", "2030"), ("Périmètre de la cible", "1, 2 et 3")])
    assert f["sections"]["targets"] == dict(climate_reduction_percent=42.0, climate_base_year=2025,
                                            climate_target_year=2030, climate_scopes="1-2-3")
    assert "Reduction visee des emissions;42" in template_csv()
    for lang, libelle in (("fr", "Périmètre de la cible"), ("en", "Target scope")):
        assert libelle in generate_questionnaire_html("X", 2025, lang=lang)


# ── Lot 2 : cibles par indicateur ─────────────────────────────────────────

INDICATEURS: dict[str, Any] = dict(renewable_target_percent=60, female_employees_target_percent=30,
                                   training_hours_target=30, accident_rate_target=4.5)


@pytest.mark.parametrize("lang,attendus", [
    ("fr", ("Aucune trajectoire de réduction des émissions", "part d'énergie renouvelable : 60 %",
            "42 % sur l'exercice, soit 18 points à gagner d'ici 2030", "cible déjà atteinte",
            "22 h sur l'exercice, soit 8 h à gagner", "1,7 de baisse à obtenir")),
    ("en", ("No emissions reduction pathway", "share of renewable energy: 60%",
            "42% this year, i.e. 18 points to gain by 2030", "target already met",
            "22 h this year, i.e. 8 h to gain", "a reduction of 1.7 to achieve")),
])
def test_cibles_par_indicateur_et_ecart(lang, attendus):
    r = _dossier(lang, **INDICATEURS)
    texte = generate_esg_content(r, calculate_esg_scores(r))["targets"].replace("\xa0", " ")
    for a in attendus:
        assert a in texte, (lang, a, texte)


def test_valeur_de_l_exercice_absente():
    r = _dossier(renewable_target_percent=60)
    r.environmental = r.environmental.model_copy(update={"renewable_energy_percent": None})
    assert "valeur de l'exercice non renseignée" in (TG.targets_paragraph(r) or "")


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_la_cible_client_remplace_l_objectif_propose(lang):
    from content_generator import enriched_recommendations
    r = _dossier(lang, renewable_target_percent=60)
    s = calculate_esg_scores(r)
    tout = " ".join(s.recommendations + s.weaknesses).replace("\xa0", " ")
    assert "50%" not in tout, tout                        # plus d'objectif proposé à 50 %
    assert ("60 %" if lang == "fr" else "60%") in tout
    reco = next(x for x in enriched_recommendations(r, s) if x["key"] == "renewable")
    assert "60" in reco["title"] and "2030" in reco["objective"]


def test_sans_cible_l_objectif_propose_reste():
    s = calculate_esg_scores(_dossier())
    assert any("50%" in x for x in s.recommendations)


def test_lecture_du_pilier_cite_ses_cibles():
    import narrative as NR
    r = _dossier(**INDICATEURS)
    s = calculate_esg_scores(r)
    env = NR.pillar_paragraphs(r, s, "env")[1]
    soc = NR.pillar_paragraphs(r, s, "social")[1]
    assert "énergie renouvelable" in env and "formation" not in env.split("cibles suivantes")[-1]
    assert "heures de formation" in soc and "énergie renouvelable" not in soc.split("cibles suivantes")[-1]
