"""Cohérence du texte généré sur des centaines de profils (tests/coherence.py).

Chaque invariant est vérifié sur N profils × 2 langues. Un invariant connu
pour être violé est marqué xfail(strict) avec son paragraphe de DETTE.md :
le jour où la correction le rend vrai, le XPASS casse la suite et force à
retirer le marqueur. Les tests « mord » prouvent que chaque invariant
détecte bien la contradiction qu'il vise.
"""
import os
import sys
from functools import lru_cache
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import coherence as K  # noqa: E402

N = 300


@lru_cache(maxsize=None)
def _dossiers() -> tuple:
    return tuple(K.Dossier(K.profil(seed, lang)) for seed in range(N) for lang in ("fr", "en"))


def _violations(invariant):
    return [v for d in _dossiers() for v in invariant(d)]


SAINS = [K.fragilites_pas_sur_le_meilleur_pilier, K.enjeu_et_appui_exclusifs, K.point_fort_pas_point_faible, K.scores_cites_exacts,
         K.pilier_dominant_est_le_meilleur, K.aucun_artefact, K.faible_contre_appui,
         K.fort_contre_enjeu, K.risque_carbone_contre_appui, K.aucune_affirmation_non_declaree]


@pytest.mark.parametrize("invariant", SAINS, ids=lambda f: f.__name__)
def test_invariant(invariant):
    vs = _violations(invariant)
    assert not vs, f"{len(vs)} violation(s), dont : " + " | ".join(vs[:3])


# ── Chaque invariant mord ─────────────────────────────────────────────────

def _faux(**attrs):
    base = dict(issues=[], strengths=[], s=SimpleNamespace(strengths=[], weaknesses=[]),
                notes=lambda: {"env": 70.0, "social": 50.0}, textes=lambda: [])
    base.update(attrs)
    return SimpleNamespace(**base)


def _item(key, pillar="env", severity=1.0):
    return SimpleNamespace(key=key, pillar=pillar, severity=severity)


@pytest.mark.parametrize("invariant,faux", [
    (K.fragilites_pas_sur_le_meilleur_pilier, _faux(textes=lambda: [
        "Les fragilités se concentrent sur le pilier environnemental : x."])),
    (K.enjeu_et_appui_exclusifs, _faux(issues=[_item("mix")], strengths=[_item("mix_good")])),
    (K.point_fort_pas_point_faible, _faux(s=SimpleNamespace(strengths=["x"], weaknesses=["x"]))),
    (K.scores_cites_exacts, _faux(textes=lambda: ["Social (65/100) constitue la marge"])),
    (K.pilier_dominant_est_le_meilleur, _faux(textes=lambda: ["Social domine le profil ESG"])),
    (K.aucun_artefact, _faux(textes=lambda: ["Score de None/100"])),
    (K.faible_contre_appui, _faux(strengths=[_item("renewable_good")], s=SimpleNamespace(
        strengths=[], weaknesses=["Énergie renouvelable à renforcer"]))),
    (K.fort_contre_enjeu, _faux(issues=[_item("waste")], s=SimpleNamespace(
        strengths=["Taux de recyclage élevé (71%)"], weaknesses=[]))),
    (K.aucune_affirmation_non_declaree, _faux(textes=lambda: [
        "L'intégration d'un auditeur tiers est planifiée."])),
    (K.risque_carbone_contre_appui, _faux(strengths=[_item("intensity_good")],
                                         textes=lambda: ["Intensité carbone élevée : marge"])),
], ids=lambda x: getattr(x, "__name__", ""))
def test_chaque_invariant_mord(invariant, faux):
    assert invariant(faux), f"{invariant.__name__} ne détecte pas le cas construit"


def test_le_banc_couvre_des_profils_varies():
    ds = _dossiers()
    assert sum(d.s.total_esg_score is None for d in ds) > len(ds) * 0.1   # lacunaires
    assert sum(d.s.total_esg_score is not None for d in ds) > len(ds) * 0.4  # notés
    assert len({d.r.company.sector for d in ds}) == len(K.SECTEURS)


@pytest.mark.parametrize("secteur,co2,attendu", [
    ("Énergie", 5_808, False),      # 121 t/M€ : « solide » pour l'énergie
    ("Services", 5_808, True),      # 121 t/M€ : « fragile » pour les services
    ("Services", 3_600, True),      # 75 t/M€ : sous l'ancien seuil fixe, fragile en services
    ("Industrie manufacturière", 43_200, True),  # 900 t/M€ : critique partout
])
def test_risque_carbone_sur_la_grille_sectorielle(secteur, co2, attendu):
    """DETTE § 24 : le risque se lit sur la tranche sectorielle de bands.py."""
    from content_generator import risks_opportunities
    from esg_calculator import calculate_esg_scores
    r = K.profil(0).model_copy(update={"company": K.profil(0).company.model_copy(
        update={"sector": secteur, "revenue_eur": 48e6})})
    r.environmental = r.environmental.model_copy(update={"co2_emissions_tonnes": co2})
    texte = str(risks_opportunities(r, calculate_esg_scores(r)))
    assert ("Intensité carbone élevée" in texte) == attendu


def test_le_repli_aucun_point_fort_nest_pas_compte():
    """La phrase « aucun point fort marqué » occupe la liste mais n'est pas
    comptée : « un point fort consolidé » s'imprimait dans 48 profils sur 300."""
    from esg_calculator import AUCUN_POINT_FORT, strengths_count
    vides = [d for d in _dossiers() if d.s.strengths == [AUCUN_POINT_FORT[d.r.language]]]
    assert vides, "le banc ne produit plus de profil sans point fort"
    for d in vides:
        assert strengths_count(d.s) == 0
        c = d.content["conclusion"]
        assert "un point fort consolidé" not in c and "one consolidated strength" not in c, c
        assert "aucun point fort marqué" in c or "no marked strength" in c, c
