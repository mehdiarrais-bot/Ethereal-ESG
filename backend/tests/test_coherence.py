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
         K.fort_contre_enjeu]


@pytest.mark.parametrize("invariant", SAINS, ids=lambda f: f.__name__)
def test_invariant(invariant):
    vs = _violations(invariant)
    assert not vs, f"{len(vs)} violation(s), dont : " + " | ".join(vs[:3])


@pytest.mark.xfail(strict=True, reason="DETTE § 24 : risque carbone au seuil fixe de 100 t/M€, "
                   "point d'appui sur la grille sectorielle de bands.py")
def test_risque_carbone_contre_appui():
    assert not _violations(K.risque_carbone_contre_appui)


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
