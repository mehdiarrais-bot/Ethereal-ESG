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


def test_sept_figures_pour_un_dossier_complet():
    imgs = IL.build(_trois()["transport"])
    assert set(imgs) == {"ill_ruler_env", "ill_ruler_social", "ill_ruler_gov", "ill_waffle_env",
                         "ill_people", "ill_tf", "ill_board"}
    assert all(v.startswith(PNG) for v in imgs.values())


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
        "_start": ["ill_ruler_social"], "safety": ["ill_tf"], "talent": ["ill_people"]}
    assert IL.placements("social", ["mix"])["mix"] == ["ill_people"]
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
    for key in ("ill_tf", "ill_board", "ill_people"):
        assert _norm(IL.caption(r, key), lang) in texte, key
