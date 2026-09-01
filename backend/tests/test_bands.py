"""
Tests du socle de clauses conditionnelles (bands.py / composer.py /
clauses/fr.py). Ne teste AUCUNE clause rédigée — la banque est vide à ce
stade, ces tests couvrent uniquement la mécanique : classement en tranches,
absence de tranche inventée, et surtout l'anti-divergence entre bands.py et
clauses/fr.py (le bug "clé qui diverge silencieusement" déjà vécu ailleurs
dans ce projet, avec le CLAUDE.md et les libellés VSME fabriqués).

Lancer depuis backend/ :  python -m pytest tests/ -q
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bands import (
    INDICATEURS_PAR_SECTION, SEUILS, CATEGORIES, classer,
    TRANCHE_100, TRANCHE_80, TRANCHE_60, TRANCHE_40, TRANCHE_20,
    PLUS_HAUT_MIEUX,
)
from composer import sections_pretes, composer_section, _substituer, _tranche_categorielle
from clauses.fr import CLAUSES, TRANCHES_NUMERIQUES


# ── 1. classer() range correctement, dans les deux sens ────────────────────
# Note : score_metric()/classer() sont inclusifs sur la borne (>= ou <=,
# selon le sens), donc la valeur de la borne appartient à sa propre tranche
# par construction — c'est cette valeur qui est testée ci-dessous.

def test_classer_toutes_les_tranches_plus_haut_mieux():
    """Pour chaque indicateur à grille (sens=plus_haut_mieux), la valeur de
    chaque borne doit classer exactement dans la tranche nommée à cette
    borne."""
    for indicateur, entry in SEUILS.items():
        if "bornes" not in entry or entry["sens"] != PLUS_HAUT_MIEUX:
            continue
        for borne, tranche_attendue in entry["bornes"]:
            resultat = classer(indicateur, borne)
            assert resultat == tranche_attendue, (
                f"{indicateur}={borne} -> {resultat!r}, attendu {tranche_attendue!r}")


def test_classer_toutes_les_tranches_plus_bas_mieux():
    """Même vérification côté plus_bas_mieux (ex. accident_frequency_rate,
    employee_turnover_percent) : sens inverse, pas de raison de le supposer
    couvert par le test précédent."""
    trouve_au_moins_un = False
    for indicateur, entry in SEUILS.items():
        if "bornes" not in entry or entry["sens"] == PLUS_HAUT_MIEUX:
            continue
        trouve_au_moins_un = True
        for borne, tranche_attendue in entry["bornes"]:
            resultat = classer(indicateur, borne)
            assert resultat == tranche_attendue, (
                f"{indicateur}={borne} -> {resultat!r}, attendu {tranche_attendue!r}")
    assert trouve_au_moins_un, "aucun indicateur plus_bas_mieux trouvé : le test ne couvre rien"


def test_classer_accident_frequency_rate_explicite():
    """Cas nommé explicitement par la consigne : les deux sens sur un même
    indicateur emblématique (plus_bas_mieux)."""
    assert classer("accident_frequency_rate", 1) == TRANCHE_100
    assert classer("accident_frequency_rate", 3) == TRANCHE_80
    assert classer("accident_frequency_rate", 5) == TRANCHE_60
    assert classer("accident_frequency_rate", 8) == TRANCHE_40
    assert classer("accident_frequency_rate", 15) == TRANCHE_20
    # Au-delà de la pire borne : reste dans la pire tranche, ne casse pas.
    assert classer("accident_frequency_rate", 50) == TRANCHE_20


# ── 2. Narratif brut (sens=None) -> toujours None, jamais de tranche inventée

def test_narratif_brut_ne_produit_jamais_de_tranche():
    trouve_au_moins_un = False
    for indicateur, entry in SEUILS.items():
        if entry.get("sens") is not None:
            continue
        trouve_au_moins_un = True
        assert classer(indicateur, 42) is None, (
            f"{indicateur} est narratif brut (sens=None) mais classer() a "
            f"renvoyé une tranche pour la valeur 42")
        assert classer(indicateur, 0) is None
        assert classer(indicateur, 999999) is None
    assert trouve_au_moins_un, "aucun indicateur narratif brut trouvé : le test ne couvre rien"


def test_valeur_absente_renvoie_none_pour_tout_indicateur():
    """None en entrée -> None en sortie, quel que soit l'indicateur (y
    compris ceux à grille)."""
    for indicateur in SEUILS:
        assert classer(indicateur, None) is None


# ── 3. co2_emissions_tonnes : jamais de crash sans revenue_eur ─────────────

def test_co2_sans_revenue_ne_crash_pas():
    """Reproduit le flux réel : sans company.revenue_eur, l'appelant ne peut
    pas calculer l'intensité et doit passer None à classer() — vérifie que
    ça renvoie proprement None, pas une exception."""
    assert classer("co2_emissions_tonnes", None, secteur="industrie") is None
    assert classer("co2_emissions_tonnes", None, secteur=None) is None


def test_co2_avec_intensite_classe_par_secteur():
    """Avec une intensité déjà calculée, la grille sectorielle s'applique
    (secteur connu) ou la grille par défaut (secteur inconnu/absent) — sans
    crash dans les deux cas."""
    assert classer("co2_emissions_tonnes", 5, secteur="services") == TRANCHE_100
    assert classer("co2_emissions_tonnes", 5, secteur=None) == TRANCHE_100  # grille défaut
    assert classer("co2_emissions_tonnes", 5, secteur="secteur inconnu xyz") == TRANCHE_100


# ── 4. Anti-divergence : bands.py <-> clauses/fr.py ─────────────────────────

def _cles_attendues(indicateur: str) -> set:
    """Reproduit la logique de clauses/fr.py._squelette_indicateur, mais de
    façon indépendante (pas un import de cette fonction privée) : si les
    deux divergent un jour, ce test doit le voir, pas le masquer en
    réutilisant le même code."""
    if indicateur in CATEGORIES:
        if CATEGORIES[indicateur]["type"] == "booleen":
            return {"vrai", "faux"}
        return {"zero", "nonzero"}
    entry = SEUILS.get(indicateur)
    if entry and ("bornes" in entry or "bornes_par_secteur" in entry):
        return set(TRANCHES_NUMERIQUES)
    return {"brut"}


def test_toute_section_indicateur_de_bands_a_ses_cles_dans_clauses():
    """Tout indicateur de INDICATEURS_PAR_SECTION doit avoir une entrée dans
    CLAUSES[section] avec exactement les bonnes clés de tranche."""
    for section, indicateurs in INDICATEURS_PAR_SECTION.items():
        assert section in CLAUSES, f"section {section!r} absente de CLAUSES"
        for indicateur in indicateurs:
            assert indicateur in CLAUSES[section], (
                f"indicateur {indicateur!r} (section {section!r}) absent de clauses/fr.py")
            cles_reelles = set(CLAUSES[section][indicateur].keys())
            cles_attendues = _cles_attendues(indicateur)
            assert cles_reelles == cles_attendues, (
                f"{section}.{indicateur} : clés {cles_reelles} != attendues {cles_attendues}")


def test_toute_cle_de_clauses_correspond_a_un_indicateur_reel_de_bands():
    """Sens inverse : aucune clé de clauses/fr.py ne doit exister sans
    indicateur correspondant dans bands.py (ex. faute de frappe, indicateur
    renommé côté bands.py sans mise à jour de clauses/fr.py — impossible en
    théorie vu que clauses/fr.py est généré depuis bands.py, mais ce test
    protège si quelqu'un fige le squelette en dur un jour)."""
    for section, indicateurs in CLAUSES.items():
        if section.startswith("ouverture:") or section.startswith("cloture:"):
            continue
        assert section in INDICATEURS_PAR_SECTION, (
            f"section {section!r} présente dans CLAUSES mais absente de bands.INDICATEURS_PAR_SECTION")
        for indicateur, cles in indicateurs.items():
            assert indicateur in INDICATEURS_PAR_SECTION[section], (
                f"{section}.{indicateur} présent dans clauses/fr.py mais absent de bands.py")
            assert set(cles.keys()) == _cles_attendues(indicateur)


def test_materiality_et_climate_risk_absentes_du_systeme_de_clauses():
    """Décision documentée (pas un oubli) : ces deux sections n'ont aucun
    indicateur chiffré et restent hors du système de clauses."""
    assert INDICATEURS_PAR_SECTION["materiality"] == []
    assert INDICATEURS_PAR_SECTION["climate_risk"] == []
    assert CLAUSES["materiality"] == {}
    assert CLAUSES["climate_risk"] == {}


def test_toutes_les_listes_du_squelette_sont_vides():
    """Le socle ne doit contenir aucune clause rédigée à ce stade."""
    for cle, valeur in CLAUSES.items():
        if isinstance(valeur, list):
            assert valeur == [], f"{cle} n'est pas vide"
        else:
            for indicateur, tranches in valeur.items():
                for tranche, phrases in tranches.items():
                    assert phrases == [], f"{cle}.{indicateur}.{tranche} n'est pas vide"


# ── 5. Repli : banque vide -> ensemble vide, paragraphe vide ───────────────

def test_sections_pretes_vide_sur_banque_vide():
    assert sections_pretes(CLAUSES) == set()


def test_composer_section_renvoie_chaine_vide_sur_banque_vide():
    donnees = {"renewable_energy_percent": 5, "waste_recycled_percent": 10,
               "co2_emissions_tonnes": None, "biodiversity_initiatives": 0,
               "energy_consumption_mwh": None, "water_consumption_m3": None,
               "waste_generated_tonnes": None, "scope_completeness": None}
    assert composer_section("environmental", donnees, CLAUSES) == ""


def test_composer_section_sur_section_sans_indicateurs_renvoie_chaine_vide():
    assert composer_section("materiality", {}, CLAUSES) == ""


# ── 6. Substitution de placeholders : tolérante, jamais d'exception ────────

def test_substitution_placeholder_connu():
    assert _substituer("Bonjour {n}, score {score}.", {"n": "Acme", "score": 65}) == \
        "Bonjour Acme, score 65."


def test_substitution_placeholder_manquant_ne_casse_pas():
    """Exigence non négociable : un placeholder absent du contexte ne lève
    jamais d'exception, il ressort tel quel entre accolades (marqueur
    visible au test/à la relecture), et la génération continue."""
    resultat = _substituer("Bonjour {n}, année {an}, indicateur {xyz_inconnu}.", {"n": "Acme"})
    assert resultat == "Bonjour Acme, année {an}, indicateur {xyz_inconnu}."


def test_composer_section_ne_leve_jamais_sur_contexte_incomplet():
    """Bout en bout : une clause avec des placeholders et un contexte
    incomplet ne doit jamais faire planter composer_section()."""
    import copy
    test_clauses = copy.deepcopy(CLAUSES)
    test_clauses["environmental"]["renewable_energy_percent"]["critique"] = [
        "{n} atteint {value}% en {an}, un score de {score}/100."]
    donnees = {"renewable_energy_percent": 5}
    resultat = composer_section("environmental", donnees, test_clauses, contexte={"n": "Acme"})
    assert resultat == "Acme atteint 5% en {an}, un score de {score}/100."


# ── 7. scope_completeness : catégoriel booléen, jamais un index fixe ───────

def test_scope_completeness_est_categoriel_booleen():
    assert CATEGORIES["scope_completeness"]["type"] == "booleen"
    assert "scope_completeness" not in SEUILS


def test_tranche_categorielle_booleen_suit_la_valeur_reelle():
    assert _tranche_categorielle("scope_completeness", True) == "vrai"
    assert _tranche_categorielle("scope_completeness", False) == "faux"
    assert _tranche_categorielle("scope_completeness", None) is None


def test_composer_section_scope_completeness_choisit_selon_la_donnee():
    """Le piège trouvé en rédigeant les clauses environmental : avant, une
    liste à deux états opposés sous "brut" renvoyait toujours l'élément 0,
    donc toujours le même état quelle que soit la donnée réelle. Vérifie
    que ce n'est plus le cas : faux -> clause faux, jamais vrai, et
    inversement."""
    import copy
    test_clauses = copy.deepcopy(CLAUSES)
    test_clauses["environmental"]["scope_completeness"]["vrai"] = ["Bilan complet (scope 1+2+3)."]
    test_clauses["environmental"]["scope_completeness"]["faux"] = ["Bilan incomplet."]

    resultat_faux = composer_section("environmental", {"scope_completeness": False}, test_clauses)
    assert resultat_faux == "Bilan incomplet."

    resultat_vrai = composer_section("environmental", {"scope_completeness": True}, test_clauses)
    assert resultat_vrai == "Bilan complet (scope 1+2+3)."

    resultat_absent = composer_section("environmental", {"scope_completeness": None}, test_clauses)
    assert resultat_absent == ""


def test_clauses_fr_scope_completeness_a_les_cles_vrai_faux():
    """Régénéré depuis bands.py : plus de clé "brut" pour cet indicateur."""
    assert set(CLAUSES["environmental"]["scope_completeness"].keys()) == {"vrai", "faux"}
