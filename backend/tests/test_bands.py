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

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bands import (
    INDICATEURS_PAR_SECTION, SEUILS, CATEGORIES, classer,
    TRANCHE_100, TRANCHE_80, TRANCHE_60, TRANCHE_40, TRANCHE_20,
    PLUS_HAUT_MIEUX,
)
from composer import (sections_pretes, composer_section, composer_paragraphe,
                      _substituer, _tranche_categorielle, _formater_valeur,
                      NB_BRUTS_PAR_PARAGRAPHE)
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


SECTIONS_REDIGEES = {"environmental"}


def test_seules_les_sections_redigees_ont_des_clauses():
    """Migration section par section : toute section NON listée dans
    SECTIONS_REDIGEES doit rester entièrement vide, pour qu'elle continue
    de tomber sur l'ancien générateur. Ce test attrape une injection
    accidentelle ailleurs, et rappelle d'ajouter la section ici quand on la
    rédige volontairement."""
    for cle, valeur in CLAUSES.items():
        section = cle.split(":", 1)[1] if ":" in cle else cle
        if section in SECTIONS_REDIGEES:
            continue
        if isinstance(valeur, list):
            assert valeur == [], f"{cle} n'est pas vide"
        else:
            for indicateur, tranches in valeur.items():
                for tranche, phrases in tranches.items():
                    assert phrases == [], f"{cle}.{indicateur}.{tranche} n'est pas vide"


def test_toute_section_declaree_redigee_a_bien_des_clauses():
    """Contrepartie du test précédent, BOUCLÉE sur SECTIONS_REDIGEES et non
    codée en dur sur une section : sans ça, l'allowlist deviendrait une
    échappatoire — ajouter une section à SECTIONS_REDIGEES sans écrire ses
    clauses la dispenserait du test "doit être vide" sans rien exiger en
    retour, et le trou passerait en silence."""
    for section in SECTIONS_REDIGEES:
        assert CLAUSES[f"ouverture:{section}"], f"ouverture:{section} est vide"
        assert CLAUSES[f"cloture:{section}"], f"cloture:{section} est vide"
        assert CLAUSES[section], f"{section} n'a aucun indicateur"
        for indicateur, tranches in CLAUSES[section].items():
            assert any(tranches.values()), f"{section}.{indicateur} est vide"


# ── 5. Repli : banque vide -> ensemble vide, paragraphe vide ───────────────

# Banque volontairement vide, construite ici et indépendante de la vraie :
# sert à vérifier le mécanisme de repli, qui doit rester valable pour les
# sections pas encore rédigées.
BANQUE_VIDE = {"ouverture:environmental": [], "environmental": {}, "cloture:environmental": []}


def test_sections_pretes_vide_sur_banque_vide():
    assert sections_pretes(BANQUE_VIDE) == set()


def test_sections_pretes_reflete_les_sections_reellement_redigees():
    """Sur la vraie banque : environmental a basculé sur le nouveau
    système, les 8 autres sections restent sur l'ancien générateur."""
    assert sections_pretes(CLAUSES) == SECTIONS_REDIGEES


def test_composer_section_renvoie_chaine_vide_sur_banque_vide():
    donnees = {"renewable_energy_percent": 5, "waste_recycled_percent": 10,
               "co2_emissions_tonnes": None, "biodiversity_initiatives": 0,
               "energy_consumption_mwh": None, "water_consumption_m3": None,
               "waste_generated_tonnes": None, "scope_completeness": None}
    assert composer_section("environmental", donnees, BANQUE_VIDE) == ""


def test_composer_section_sur_section_sans_indicateurs_renvoie_chaine_vide():
    assert composer_section("materiality", {}, CLAUSES) == ""


@pytest.mark.parametrize("section,donnees", [
    ("social", {"female_employees_percent": 34.0, "training_hours_per_employee": 22.0,
                "accident_frequency_rate": 6.2, "employee_turnover_percent": 12.0,
                "customer_satisfaction_score": 7.8, "total_employees": 320}),
    ("governance", {"female_board_percent": 25.0, "independent_board_percent": 45.0,
                    "ethics_violations": 0, "data_breaches": 1, "corruption_cases": 0,
                    "esg_audit_conducted": False, "sustainability_committee": True,
                    "csr_budget_eur": 120000.0}),
])
def test_section_non_redigee_ne_produit_rien_sur_la_vraie_banque(section, donnees):
    """LE test de repli qui compte vraiment : une section pas encore
    rédigée, avec de VRAIES données qui classent et déclenchent des
    catégoriels, sur la VRAIE banque CLAUSES — doit rendre "" pour que la
    section retombe proprement sur l'ancien générateur.

    Le vérifier sur une banque stub ne prouve pas ce scénario : c'est
    précisément la vraie banque, avec environmental rempli à côté, qui doit
    rester muette sur les 8 sections restantes."""
    assert section not in SECTIONS_REDIGEES  # sinon le test ne teste plus rien
    assert composer_section(section, donnees, CLAUSES) == ""
    assert composer_paragraphe(section, donnees, CLAUSES,
                               contexte={"n": "Acme", "score": "55", "an": 2025}) == ""


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


# ── 8. Mise en forme des nombres injectés dans les clauses ─────────────────

def test_formatage_flottant_entier_perd_sa_decimale():
    """Pydantic type la plupart des champs en float : sans mise en forme,
    {value} rendrait "42.0 %". Un flottant de valeur entière doit perdre
    sa décimale."""
    assert _formater_valeur(42.0) == "42"
    assert _formater_valeur(320.0) == "320"


def test_formatage_flottant_non_entier_garde_sa_decimale():
    """6.2 (taux de fréquence accidents) doit rester 6.2 : la décimale est
    porteuse de sens, elle ne s'arrondit pas."""
    assert _formater_valeur(6.2) == "6.2"
    assert _formater_valeur(1234.5) == "1,234.5"


def test_formatage_reproduit_le_separateur_de_lancien_generateur():
    """Séparateur anglais volontaire pendant la migration, pour ne pas
    mélanger "12 000" et "12,000" dans un même rapport selon la section.
    Défaut préexistant consigné dans DETTE.md, à corriger sur tout le
    système d'un seul coup — ce test verrouille le choix en attendant."""
    assert _formater_valeur(12000.0) == "12,000"


def test_formatage_laisse_les_booleens_intacts():
    """bool est une sous-classe de int : sans garde-fou, True serait rendu
    "1" dans une clause."""
    assert _formater_valeur(True) is True
    assert _formater_valeur(False) is False


def test_formatage_laisse_none_et_texte_intacts():
    assert _formater_valeur(None) is None
    assert _formater_valeur("Acme") == "Acme"


# ── 9. Indicateurs "brut" : ancrage chiffré, plafonné, jamais sur du vide ──

def _clauses_env_de_test():
    """Banque minimale : un classé, deux bruts, un catégoriel — de quoi
    observer l'ordre, le plafond et les exclusions."""
    import copy
    t = copy.deepcopy(CLAUSES)
    t["environmental"]["renewable_energy_percent"]["critique"] = ["RENOUV {value}%."]
    t["environmental"]["energy_consumption_mwh"]["brut"] = ["ENERGIE {value} MWh."]
    t["environmental"]["water_consumption_m3"]["brut"] = ["EAU {value} m3."]
    t["environmental"]["scope_completeness"]["faux"] = ["SCOPE incomplet."]
    return t


def test_brut_sans_valeur_ne_produit_aucune_clause():
    """Jamais de "None MWh consommés"."""
    resultat = composer_section(
        "environmental", {"energy_consumption_mwh": None}, _clauses_env_de_test())
    assert resultat == ""


def test_brut_a_zero_ne_produit_aucune_clause():
    """0 MWh déclaré est un artefact de saisie, pas un fait à citer — même
    règle que l'ancien générateur (content_generator.py:707)."""
    resultat = composer_section(
        "environmental", {"energy_consumption_mwh": 0}, _clauses_env_de_test())
    assert resultat == ""


def test_indicateur_classe_a_zero_sort_bien_lui():
    """ASYMÉTRIE VOLONTAIRE avec les bruts : 0 % de renouvelable est un
    vrai constat (tranche critique), pas une donnée absente. Ce test
    verrouille la distinction pour qu'on ne l'"harmonise" pas par erreur."""
    resultat = composer_section(
        "environmental", {"renewable_energy_percent": 0}, _clauses_env_de_test())
    assert resultat == "RENOUV 0%."


def test_plafond_des_bruts_respecte():
    """Deux bruts renseignés, un seul cité (NB_BRUTS_PAR_PARAGRAPHE) : le
    paragraphe ne doit pas redevenir une énumération."""
    assert NB_BRUTS_PAR_PARAGRAPHE == 1
    resultat = composer_section(
        "environmental",
        {"energy_consumption_mwh": 12000.0, "water_consumption_m3": 45000.0},
        _clauses_env_de_test())
    assert resultat == "ENERGIE 12,000 MWh."
    assert "EAU" not in resultat


def test_brut_selectionne_par_ordre_de_declaration():
    """L'ordre de bands.INDICATEURS_PAR_SECTION fait la priorité : si
    l'énergie est absente, l'eau prend la place libérée."""
    resultat = composer_section(
        "environmental",
        {"energy_consumption_mwh": None, "water_consumption_m3": 45000.0},
        _clauses_env_de_test())
    assert resultat == "EAU 45,000 m3."


def test_co2_grille_sectorielle_entre_bien_dans_le_classement():
    """co2_emissions_tonnes est classé sur une grille SECTORIELLE
    (bornes_par_secteur, pas bornes). Le filtre de
    indicateurs_ranges_par_gravite() ne testait que "bornes" : le carbone
    était écarté du classement et ses clauses étaient inatteignables, alors
    que classer() savait le ranger. Ce test verrouille la cohérence entre
    les deux filtres."""
    from composer import indicateurs_ranges_par_gravite
    intensite = 8200 / 48_000_000 * 1e6  # 170.8 t/M€ CA
    classes = indicateurs_ranges_par_gravite(
        "environmental", {"co2_emissions_tonnes": intensite},
        secteur="Industrie manufacturière")
    assert [c[0] for c in classes] == ["co2_emissions_tonnes"]
    assert classes[0][1] == "satisfaisant"


def test_ordre_du_paragraphe_classe_puis_brut_puis_categoriel():
    """Position validée : analyse (classés) -> ancrage chiffré (brut) ->
    commentaire méta sur le reporting (catégoriel), avant la clôture."""
    resultat = composer_section(
        "environmental",
        {"renewable_energy_percent": 0.0, "energy_consumption_mwh": 12000.0,
         "scope_completeness": False},
        _clauses_env_de_test())
    assert resultat == "RENOUV 0%. ENERGIE 12,000 MWh. SCOPE incomplet."
