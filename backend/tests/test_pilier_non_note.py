"""Pilier sans indicateur : « non noté », jamais 50 (DETTE § 11, option C1).

Avant le 2026-09-25, `if not scores: return 50.0` donnait à un pilier vide
une note inventée, qui pesait dans le score global et la note lettrée
imprimés sur la couverture. Désormais : pilier None ; global = moyenne
pondérée des piliers notés (pondérations renormalisées) s'il y en a au moins
deux ; sinon ni score global ni note. Les livrables le disent.
"""
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import ESGRequest  # noqa: E402
from esg_calculator import (calculate_esg_scores, calculate_environmental_score,  # noqa: E402
                            calculate_social_score, calculate_governance_score,
                            global_score, PILLAR_WEIGHTS)
from models import EnvironmentalData, SocialData, GovernanceData  # noqa: E402

ENV = {"co2_emissions_tonnes": 800, "renewable_energy_percent": 30}
SOC = {"total_employees": 120, "female_employees_percent": 38, "training_hours_per_employee": 12}
GOV = {"board_members": 6, "female_board_percent": 33, "esg_audit_conducted": False}


def _dossier(env=None, soc=None, gov=None, lang="fr"):
    return ESGRequest.model_validate({
        "company": {"name": "Témoin", "sector": "Industrie", "country": "France",
                    "reporting_year": 2025, "revenue_eur": 12_000_000},
        "environmental": env or {}, "social": soc or {}, "governance": gov or {}, "language": lang})


def test_un_pilier_vide_n_est_pas_note():
    assert calculate_environmental_score(EnvironmentalData(), 1e7)[0] is None
    assert calculate_social_score(SocialData())[0] is None
    assert calculate_governance_score(GovernanceData())[0] is None


def test_score_global_inchange_avec_trois_piliers():
    s: dict[str, float | None] = {"env": 70.0, "social": 65.0, "gov": 75.0}
    attendu = round(70 * 0.40 + 65 * 0.35 + 75 * 0.25, 1)
    assert global_score(s) == attendu == 69.5


def test_score_global_renormalise_sur_deux_piliers():
    poids = PILLAR_WEIGHTS["env"] + PILLAR_WEIGHTS["gov"]
    attendu = round((70 * PILLAR_WEIGHTS["env"] + 75 * PILLAR_WEIGHTS["gov"]) / poids, 1)
    assert global_score({"env": 70.0, "social": None, "gov": 75.0}) == attendu


@pytest.mark.parametrize("piliers", [{}, {"env": ENV}, {"soc": SOC}, {"gov": GOV}])
def test_sous_deux_piliers_ni_score_global_ni_note(piliers):
    s = calculate_esg_scores(_dossier(**piliers))
    assert s.total_esg_score is None and s.rating is None


def test_un_pilier_non_note_n_est_ni_point_fort_ni_axe():
    s = calculate_esg_scores(_dossier(soc=SOC, gov=GOV))
    texte = " ".join(s.strengths + s.weaknesses).lower()
    assert "environnementale globale" not in texte


@pytest.mark.parametrize("lang", ["fr", "en"])
@pytest.mark.parametrize("piliers", [{}, {"env": ENV}, {"env": ENV, "soc": SOC}],
                         ids=["vide", "env", "env+soc"])
def test_livrables_d_un_dossier_partiel(lang, piliers):
    """Les cinq livrables se génèrent, ne montrent ni « None » ni score
    inventé, et disent l'abstention."""
    from test_suite import _textes_des_livrables
    r = _dossier(lang=lang, **piliers)
    textes = _textes_des_livrables(r)
    assert set(textes) >= {"pdf", "onepager", "pptx", "docx", "lettre"}
    for nom, texte in textes.items():
        # mot isolé : le XML du PowerPoint contient la balise <a:buNone/>
        assert not re.search(r"(?<![A-Za-z:])None", texte), nom
    tout = " ".join(textes.values())
    non_note = "n'est pas noté" if lang == "fr" else "is not rated"
    assert non_note in tout
    if len(piliers) < 2:
        assert ("n'obtient pas de score global" if lang == "fr" else "has no overall score") in tout


def test_graphiques_sans_pilier_invente():
    """Pas de radar avec un sommet à 0, pas d'image None transmise."""
    from chart_generator import radar_chart
    from main import build_advanced_charts
    r = _dossier(env=ENV, soc=SOC)
    s = calculate_esg_scores(r)
    assert radar_chart(s, r.aesthetic_theme) is None
    charts = build_advanced_charts(r, s, light_bg=True)
    assert all(v for v in charts.values())
    assert "benchmark" in charts                    # deux piliers : positionnement tracé
    seul = _dossier(env=ENV)
    assert "benchmark" not in build_advanced_charts(seul, calculate_esg_scores(seul), light_bg=True)


def test_api_rend_null_pour_un_pilier_non_note():
    from fastapi.testclient import TestClient
    from main import app
    r = TestClient(app).post("/api/calculate", json=_dossier(env=ENV).model_dump(mode="json"))
    assert r.status_code == 200
    corps = r.json()
    assert corps["social_score"] is None and corps["total_esg_score"] is None and corps["rating"] is None
    assert corps["environmental_score"] is not None
