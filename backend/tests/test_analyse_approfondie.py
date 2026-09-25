"""Analyse approfondie des piliers (analysis.py), chantier « textes » du 2026-09-26.

Demande : des rapports qui expliquent (causes, conséquences, leviers) et qui
se distinguent d'une entreprise à l'autre. Ce fichier verrouille :
  - la différenciation entre trois entreprises contrastées ;
  - le contexte sectoriel et les ratios calculés depuis les données ;
  - les garde-fous : aucun booléen inconnu lu comme « non », aucune
    affirmation interdite, parité FR/EN des textes ;
  - la présence de l'analyse dans le PDF, le Word et les notes du PPTX.
"""
import itertools
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_suite import (make_request, ENGAGEMENTS_FABRIQUES, ATTRIBUTIONS_LEGALES_FAUSSES,  # noqa: E402
                        MARQUEURS_DE_PROVENANCE, AFFIRMATIONS_INTERDITES, MARQUEURS_METHODO_INVENTEE)
from test_affirmations_reglementaires import CSRD_OBLIGATION_INCONDITIONNELLE  # noqa: E402
from esg_calculator import calculate_esg_scores                                 # noqa: E402
from models import CompanyInfo, EnvironmentalData, SocialData, GovernanceData    # noqa: E402
import analysis as AN                                                            # noqa: E402
from analysis_texts import A, SECTOR, COUNTERS                                   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _company(name, sector, revenue):
    return CompanyInfo(name=name, sector=sector, country="France", revenue_eur=revenue,
                       reporting_year=2025, target_year=2030)


def _trois(lang="fr"):
    """Industrie (dossier de référence), services, transport : profils opposés."""
    return {
        "industrie": make_request(lang),
        "services": make_request(
            lang, company=_company("Lumen Conseil", "Services aux entreprises", 9_000_000),
            environmental=EnvironmentalData(co2_emissions_tonnes=310, scope1_emissions=40,
                                            scope2_emissions=90, renewable_energy_percent=85,
                                            waste_recycled_percent=40),
            social=SocialData(total_employees=64, female_employees_percent=58,
                              training_hours_per_employee=35, accident_frequency_rate=1.2,
                              employee_turnover_percent=19),
            governance=GovernanceData(esg_audit_conducted=True, sustainability_committee=False,
                                      independent_board_percent=20, board_members=5,
                                      female_board_percent=40, data_breaches=0,
                                      ethics_violations=0)),
        "transport": make_request(
            lang, company=_company("NovaFlux Logistique", "Logistique & Transport", 120_000_000),
            environmental=EnvironmentalData(co2_emissions_tonnes=41000, scope1_emissions=36000,
                                            scope2_emissions=1800, renewable_energy_percent=8,
                                            waste_recycled_percent=55),
            social=SocialData(total_employees=1400, female_employees_percent=17,
                              training_hours_per_employee=9, accident_frequency_rate=31,
                              employee_turnover_percent=24),
            governance=GovernanceData(esg_audit_conducted=False, sustainability_committee=False,
                                      independent_board_percent=33, board_members=6,
                                      female_board_percent=33, data_breaches=2,
                                      ethics_violations=1)),
    }


def _texte(r, piliers=("env", "social", "gov")) -> str:
    s = calculate_esg_scores(r)
    texte = " ".join(p for pil in piliers for sec in AN.pillar_analysis(r, s, pil) for p in sec.paragraphs)
    return texte.replace(" ", " ").replace(" ", " ")   # espaces insécables des nombres


def _phrases(txt: str) -> set[str]:
    """Phrases d'au moins six mots, chiffres masqués : deux phrases qui ne
    diffèrent que par leurs nombres comptent comme identiques."""
    return {re.sub(r"[\d  ,.%]+", "#", x) for x in re.split(r"(?<=[.!?])\s+", txt)
            if len(x.split()) >= 6}


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_trois_entreprises_trois_analyses(lang):
    """Moins de 30 % de phrases communes entre deux entreprises contrastées,
    même en comptant comme identiques les phrases qui ne diffèrent que par
    leurs chiffres (mesure du 2026-09-26 : 14 à 26 %)."""
    textes = {n: _phrases(_texte(r)) for n, r in _trois(lang).items()}
    for a, b in itertools.combinations(textes, 2):
        commun = len(textes[a] & textes[b]) / len(textes[a] | textes[b])
        assert commun < 0.30, (lang, a, b, round(commun, 3))


def test_le_secteur_change_les_causes():
    t = {n: _texte(r) for n, r in _trois().items()}
    assert "gazole des poids lourds" in t["transport"]
    assert "électricité des bureaux" in t["services"]
    assert "matières premières et composants" in t["industrie"]
    assert "gazole" not in t["services"] and "gazole" not in t["industrie"]


def test_ratios_calcules_depuis_les_donnees():
    t = _texte(_trois()["transport"])
    assert "environ 336 salariés" in t                 # 24 % de 1 400
    assert "1,9 fois la moyenne nationale" in t        # 31 / 16,0
    assert "12 600 heures" in t                        # 9 h × 1 400
    assert "le Scope 1 en représente 95 %" in t        # 36 000 / 37 800
    assert "environ 238 salariées" in t                # 17 % de 1 400


def test_croisements_entre_indicateurs():
    t = {n: _texte(r) for n, r in _trois().items()}
    # Rotation élevée × formation faible : le cercle vicieux
    assert "se renforcent l'un l'autre" in t["transport"]
    # Formation élevée × rotation élevée : « forme mais ne retient pas »
    assert "forme, mais ne retient pas" in t["services"]
    # Vérification sans comité / ni l'un ni l'autre
    assert "aucune instance dédiée" in t["services"]
    assert "Ni comité de durabilité ni vérification externe" in t["transport"]


@pytest.mark.parametrize("comite, audit, absent", [
    (None, None, ["Ni comité", "aucune instance", "ne font pas l'objet"]),
    (True, None, ["Ni comité", "ne font pas l'objet", "ne sont pas"]),
    (None, True, ["Ni comité", "Aucun comité"]),
])
def test_booleen_inconnu_jamais_lu_comme_non(comite, audit, absent):
    """DETTE § 17 : une réponse absente n'est pas un « non »."""
    r = make_request(governance=GovernanceData(sustainability_committee=comite,
                                               esg_audit_conducted=audit,
                                               independent_board_percent=45))
    t = _texte(r, ("gov",))
    for marqueur in absent:
        assert marqueur not in t, (comite, audit, marqueur)


def test_pilier_sans_donnee_aucune_analyse():
    r = make_request(environmental=EnvironmentalData())
    assert AN.pillar_analysis(r, calculate_esg_scores(r), "env") == []


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_aucun_gabarit_non_rempli(lang):
    for r in _trois(lang).values():
        t = _texte(r)
        assert "{" not in t and "}" not in t and "None" not in t


def _tous_les_textes() -> str:
    out = []

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, (list, tuple)):
            for v in o:
                walk(v)
        elif isinstance(o, str):
            out.append(o)
    walk(A)
    walk(SECTOR)
    walk(COUNTERS)
    return " ".join(out).lower()


def test_aucune_affirmation_interdite_dans_les_textes():
    blob = _tous_les_textes()
    for m in (ENGAGEMENTS_FABRIQUES + ATTRIBUTIONS_LEGALES_FAUSSES + MARQUEURS_DE_PROVENANCE
              + AFFIRMATIONS_INTERDITES + MARQUEURS_METHODO_INVENTEE
              + CSRD_OBLIGATION_INCONDITIONNELLE):
        assert m.lower() not in blob, m


def test_mixite_de_l_effectif_dite_non_legale():
    """Aucun quota légal ne porte sur l'effectif total (DETTE § 4) : le repère
    est interne, et le texte le dit."""
    assert "non une obligation légale" in A["fr"]["mix_below"]
    assert "not a legal requirement" in A["en"]["mix_below"]


def test_parite_des_cles_fr_en():
    assert A["fr"].keys() == A["en"].keys()
    assert A["fr"]["gap"].keys() == A["en"]["gap"].keys()
    assert COUNTERS["fr"].keys() == COUNTERS["en"].keys()
    for fam, textes in SECTOR.items():
        assert textes["fr"].keys() == textes["en"].keys(), fam


def test_chaque_secteur_du_formulaire_a_son_contexte():
    with open(os.path.join(ROOT, "frontend", "src", "components", "steps", "StepCompany.jsx"),
              encoding="utf-8") as f:
        bloc = re.search(r"const SECTORS = \[(.*?)\]", f.read(), re.S)
    assert bloc
    secteurs = re.findall(r"'([^']+)'", bloc.group(1))
    assert len(secteurs) > 10
    sans = [s for s in secteurs if s != "Autre" and AN.family(s) == "general"]
    assert not sans, sans


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_analyse_dans_les_trois_livrables(lang):
    from test_parite import _pdf, _docx, _pptx_notes
    from content_generator import generate_esg_content
    from report_generator import generate_pdf_report
    from docx_generator import generate_word_report
    from ppt_generator import generate_pptx
    r = _trois(lang)["transport"]
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    titre = A[lang]["t_safety"]
    assert titre in _pdf(generate_pdf_report(r, s, c, {}))
    assert titre in _docx(generate_word_report(r, s, c, charts={}))
    assert titre in _pptx_notes(generate_pptx(r, s, c, {}))
