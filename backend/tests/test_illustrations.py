"""Illustrations des piliers (illustrations.py) : dessinées depuis les données.

Chaque figure représente un chiffre du dossier ; aucune n'apparaît sans la
donnée qui la fonde, et la position sur la grille est celle du score.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_suite import make_request                                   # noqa: E402
from test_analyse_approfondie import _trois                           # noqa: E402
from models import EnvironmentalData, SocialData, GovernanceData      # noqa: E402
from bands import classer                                             # noqa: E402
import illustrations as IL                                            # noqa: E402

PNG = b"\x89PNG"


LOT1 = {"ill_ruler_env", "ill_ruler_social", "ill_ruler_gov", "ill_waffle_env", "ill_people",
        "ill_tf", "ill_board"}
LOT4 = {"ill_issue_map", "ill_chain", "ill_ratios", "ill_completeness", "ill_scopes",
        "ill_checklist", "ill_stake", "ill_roadmap", "ill_mixboard", "ill_quadrant",
        "ill_timeline", "ill_first"}


def test_dix_neuf_figures_au_catalogue():
    assert len(LOT1 | LOT4) == 19
    assert set(IL._CAPTIONS) | {"ill_ruler_env", "ill_ruler_social", "ill_ruler_gov"} == LOT1 | LOT4


def test_figures_d_un_dossier_complet():
    """Le transporteur n'a déclaré aucun indicateur d'ancrage : seule
    ill_stake manque."""
    imgs = IL.build(_trois()["transport"])
    assert set(imgs) == (LOT1 | LOT4) - {"ill_stake"}
    assert all(v.startswith(PNG) for v in imgs.values())


def test_ancrage_territorial_avec_ses_donnees():
    r = make_request(social=SocialData(total_employees=80, local_suppliers_percent=62,
                                       customer_satisfaction_score=8.1))
    assert "ill_stake" in IL.build(r)


def test_bilan_complet_pas_de_figure_de_couverture():
    """Tous les scopes mesurés : le camembert existant suffit ; un scope
    manquant n'est jamais dessiné avec une taille inventée."""
    assert "ill_scopes" not in IL.build(make_request())   # Scopes 1, 2 et 3 renseignés


def test_quadrant_lit_les_seuils_de_la_grille():
    import illustrations_more as M
    from bands import SEUILS
    h = dict((n, b) for b, n in SEUILS["training_hours_per_employee"]["bornes"])["satisfaisant"]
    t = dict((n, b) for b, n in SEUILS["employee_turnover_percent"]["bornes"])["satisfaisant"]
    assert (h, t) == (20, 15)
    assert M._SOCIAL_BANDS["training_hours_per_employee"] is SEUILS["training_hours_per_employee"]["bornes"]


def test_emplacements_hors_piliers():
    assert IL.spot("overview") == ["ill_issue_map", "ill_chain"]
    assert set(IL.spot("company") + IL.spot("roadmap") + IL.spot("horizon")
               + IL.spot("first_days")) <= LOT4


def test_aucune_figure_sans_sa_donnee():
    r = make_request(social=SocialData(total_employees=50),
                     governance=GovernanceData(independent_board_percent=45),
                     environmental=EnvironmentalData(co2_emissions_tonnes=100))
    imgs = IL.build(r)
    for absente in ("ill_people", "ill_tf", "ill_board", "ill_waffle_env", "ill_ruler_social",
                    "ill_ruler_gov", "ill_ruler_env"):   # règles : au moins deux indicateurs
        assert absente not in imgs, absente


@pytest.mark.parametrize("key, value, sector", [
    ("training_hours_per_employee", 9, None),
    ("female_employees_percent", 17, None),
    ("accident_frequency_rate", 31, None),
    ("employee_turnover_percent", 24, None),
    ("renewable_energy_percent", 85, None),
    ("independent_board_percent", 33, None),
    ("co2_emissions_tonnes", 342, "Logistique & Transport"),
    ("co2_emissions_tonnes", 34, "Services aux entreprises"),
])
def test_le_marqueur_tombe_dans_la_tranche_du_score(key, value, sector):
    """La règle et le score lisent la même grille (bands.py)."""
    segs, higher = IL._segments(key, value, sector)
    x = IL._position(value, segs, higher)
    tranche = classer(key, value, sector)
    assert tranche is not None
    attendu = IL._ORDER.index(tranche)
    assert attendu <= x <= attendu + 1, (key, value, x, attendu)


def test_ancrage_des_figures():
    assert IL.placements("social", ["safety", "talent", "mix"]) == {
        "_start": ["ill_ruler_social"], "safety": ["ill_tf"],
        "talent": ["ill_people", "ill_quadrant"], "mix": ["ill_mixboard"]}
    assert IL.placements("social", ["mix"])["mix"] == ["ill_people", "ill_mixboard"]
    assert IL.placements("env", ["ghg", "waste"])["waste"] == ["ill_waffle_env"]


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_legendes_dans_le_word(lang):
    from test_parite import _docx, _norm
    from esg_calculator import calculate_esg_scores
    from content_generator import generate_esg_content
    from docx_generator import generate_word_report
    r = _trois(lang)["transport"]
    s = calculate_esg_scores(r)
    texte = _norm(_docx(generate_word_report(r, s, generate_esg_content(r, s),
                                             charts=IL.build(r))), lang)
    for key in ("ill_tf", "ill_board", "ill_people", "ill_issue_map", "ill_ratios",
                "ill_first", "ill_quadrant"):
        assert _norm(IL.caption(r, key), lang) in texte, key
