"""Comparaison d'un exercice à l'autre, lot A : ce que le dossier conserve.

Avant le 2026-09-28, le dossier ne gardait que les SCORES de chaque exercice
(le formulaire est écrasé à chaque sauvegarde), et un exercice passé dont un
pilier n'était pas noté disparaissait en silence de la courbe et de
l'évolution N-1 (float(None) dans le validateur).
"""
import os
import sys

import pytest
from pydantic import ValidationError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_suite import dossier_a_transparente, FORM, client  # noqa: E402,F401
from models import ESGRequest                                 # noqa: E402


def _avec(**extra):
    d = dossier_a_transparente().model_dump()
    d.update(extra)
    return ESGRequest.model_validate(d)


def test_un_pilier_non_note_ne_fait_plus_disparaitre_l_exercice():
    r = _avec(score_history=[{"year": 2023, "env": 55, "social": None, "gov": 60, "total": None},
                             {"year": 2024, "env": 58, "social": 50, "gov": 60, "total": 55.9}],
              previous_scores={"year": 2024, "env": 58, "social": None, "gov": 60, "total": 58.9})
    assert [h["year"] for h in r.score_history or []] == [2023, 2024]
    assert r.score_history and r.score_history[0]["social"] is None
    assert r.previous_scores == {"year": 2024, "env": 58.0, "social": None, "gov": 60.0, "total": 58.9,
                                 "recalculated": False}


def test_score_hors_bornes_ou_annee_illisible():
    r = _avec(score_history=[{"year": "x", "env": 1}, {"year": 2024, "env": 250, "total": float("nan")}])
    assert r.score_history == [{"year": 2024, "env": None, "social": None, "gov": None, "total": None,
                                "recalculated": False}]


def test_donnees_de_l_exercice_precedent():
    r = _avec(previous_data={"year": 2024, "revenue_eur": 45e6,
                             "environmental": {"renewable_energy_percent": 35}})
    assert r.previous_data is not None
    assert r.previous_data.environmental.renewable_energy_percent == 35
    with pytest.raises(ValidationError, match="doit précéder"):
        _avec(previous_data={"year": 2025})
    with pytest.raises(ValidationError):            # mêmes validations que l'exercice courant
        _avec(previous_data={"year": 2024, "social": {"female_employees_percent": 140}})


def test_la_sauvegarde_conserve_les_indicateurs_de_chaque_exercice(client):  # noqa: F811
    cid = client.post("/api/clients", json={"form": FORM}).json()["id"]
    f2 = dict(FORM, company=dict(FORM["company"], reporting_year=2026),
              environmental={"co2_emissions_tonnes": 7000})
    hist = client.post("/api/clients", json={"id": cid, "form": f2}).json()["score_history"]
    assert [h["data"]["environmental"]["co2_emissions_tonnes"] for h in hist] == [8200, 7000]
    assert hist[0]["data"]["revenue_eur"] == 48e6
    assert "company" not in hist[0]["data"]          # ni identité ni mise en page


def test_page_coup_d_oeil_ecart_pilier_par_pilier():
    from esg_calculator import calculate_esg_scores
    from report_generator import page_context
    from i18n import L
    r = _avec(previous_scores={"year": 2024, "env": 60, "social": None, "gov": 70, "total": 65})
    ctx = page_context(r, calculate_esg_scores(r), L("fr"), "Rapport")
    assert ctx["delta"]["env"] is not None and ctx["delta"]["social"] is None
    assert ctx["prev_vals"] is None                   # radar N-1 : il faut les trois piliers


# ── Lot B : scores comparables ────────────────────────────────────────────

def test_score_precedent_recalcule_avec_la_grille_actuelle():
    """Le score stocké (ancienne grille) est remplacé par le recalcul des
    indicateurs conservés : ici 75,4 (grille d'avant le § 16) → non noté."""
    silencieuse = {"environmental": {"co2_emissions_tonnes": 8200}, "social": {"total_employees": 320},
                   "governance": {"sustainability_committee": True}}
    r = _avec(previous_scores={"year": 2024, "env": 60, "social": None, "gov": 100, "total": 75.4},
              score_history=[{"year": 2023, "env": 50, "social": 50, "gov": 50, "total": 50},
                             {"year": 2024, "env": 60, "social": None, "gov": 100, "total": 75.4}],
              previous_data={"year": 2024, "revenue_eur": 48e6, **silencieuse})
    assert r.previous_scores is not None
    assert r.previous_scores["total"] is None and r.previous_scores["recalculated"] is True
    hist = {h["year"]: h for h in r.score_history or []}
    assert hist[2024]["recalculated"] and not hist[2023]["recalculated"]


@pytest.mark.parametrize("lang,mention", [("fr", "selon la grille alors en vigueur"),
                                          ("en", "under the grid then in force")])
def test_score_non_recalcule_signale(lang, mention):
    from esg_calculator import calculate_esg_scores
    from content_generator import generate_esg_content
    from report_generator import trend_caption
    from i18n import L
    r = _avec(language=lang, previous_scores={"year": 2024, "env": 60, "social": 55, "gov": 70, "total": 61},
              score_history=[{"year": 2024, "env": 60, "social": 55, "gov": 70, "total": 61}])
    assert mention in generate_esg_content(r, calculate_esg_scores(r))["executive_summary"]
    assert "2024" in trend_caption(r, L(lang)) and mention in trend_caption(r, L(lang))
    avec_donnees = _avec(language=lang, previous_data={"year": 2024, "revenue_eur": 48e6,
                                                       "environmental": {"renewable_energy_percent": 30}})
    s = calculate_esg_scores(avec_donnees)
    assert mention not in generate_esg_content(avec_donnees, s)["executive_summary"]
