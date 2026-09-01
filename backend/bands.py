"""
Source de vérité des seuils, cibles et tranches pour le système de clauses
conditionnelles (bands -> composer -> clauses/fr.py).

Principe directeur (décision explicite, une source de vérité par donnée,
CLAUDE.md "Qualité de code") : les tranches narratives NE DOIVENT PAS décrire
un monde parallèle à celui du score. Chaque grille ci-dessous est recopiée
depuis les seuils RÉELS de esg_calculator.py (référencés en commentaire par
fichier:ligne au moment de l'écriture) — jamais réinventée. Si les seuils de
score changent, ce fichier doit changer avec eux, au même commit.

Ce module ne génère aucun texte : il classe des valeurs en tranches nommées.
La rédaction des clauses (clauses/fr.py) et leur sélection (composer.py) sont
des modules séparés qui lisent ce fichier, jamais l'inverse.
"""

from esg_calculator import SECTOR_CARBON_THRESHOLDS, _DEFAULT_CARBON_THRESHOLDS


# ── Neuf sections du rapport ────────────────────────────────────────────────
# materiality et climate_risk sont volontairement ABSENTES : elles ne
# reposent sur aucun indicateur chiffré dans le code actuel (materiality est
# un paragraphe méthodologique fixe CSRD/ESRS ; climate_risk est un texte
# conditionné uniquement par le secteur, via _climate_sector_risks). Elles
# restent en texte non conditionnel, hors du système de clauses. Ne pas les
# ajouter ici par erreur de complétude plus tard : c'est un choix documenté,
# pas un oubli.
INDICATEURS_PAR_SECTION = {
    "executive_summary": [
        "total_esg_score",   # esg_calculator.py: get_rating(), lignes 203-217
        "rating",            # dérivé de total_esg_score, mêmes bornes
    ],
    "environmental": [
        "co2_emissions_tonnes",      # intensité (co2/revenue), grille sectorielle — esg_calculator.py:74-80
        "renewable_energy_percent",  # esg_calculator.py:60-64
        "waste_recycled_percent",    # esg_calculator.py:67-71
        "biodiversity_initiatives",  # esg_calculator.py:95-96 (formule linéaire plafonnée)
        "energy_consumption_mwh",    # narratif brut, aucun seuil — content_generator.py:707-708
        "water_consumption_m3",      # narratif brut, aucun seuil — content_generator.py:709-710
        "waste_generated_tonnes",    # collecté, jamais utilisé dans le narratif actuel
        "scope_completeness",        # booléen (CATEGORIES) — composite scope1+2+3 renseignés, esg_calculator.py:83-86
    ],
    "social": [
        "female_employees_percent",     # esg_calculator.py:113-115
        "training_hours_per_employee",  # esg_calculator.py:126-128
        "accident_frequency_rate",      # esg_calculator.py:133-135 — voir DETTE.md
        "employee_turnover_percent",    # esg_calculator.py:120-122
        "disabled_employees_percent",   # narratif brut, aucun seuil
        "local_suppliers_percent",      # narratif brut, aucun seuil
        "customer_satisfaction_score",  # esg_calculator.py:140-142
        "total_employees",              # donnée contextuelle, aucun seuil
    ],
    "governance": [
        "female_board_percent",         # esg_calculator.py:161-163 — voir DETTE.md (attribution légale)
        "independent_board_percent",    # esg_calculator.py:168-170
        "ethics_violations",            # esg_calculator.py:174 (compteur à sens inversé)
        "data_breaches",                # esg_calculator.py:178 (compteur à sens inversé)
        "corruption_cases",             # absent du score — voir DETTE.md
        "esg_audit_conducted",          # esg_calculator.py:181-184 (booléen)
        "sustainability_committee",     # esg_calculator.py:187-190 (booléen)
        "csr_budget_eur",               # esg_calculator.py:194 (formule linéaire plafonnée)
    ],
    "materiality": [],  # cf. note en tête de fichier — hors système de clauses, décision documentée
    "targets": [
        "co2_emissions_tonnes",  # gate présence/absence, pas de tranche — content_generator.py:849-860
        "target_year",           # company.target_year, interpolé, aucun seuil
    ],
    "taxonomy": [
        "turnover_aligned_percent",  # narratif brut, aucun score dans esg_calculator.py
        "capex_aligned_percent",     # idem
        "opex_aligned_percent",      # idem
    ],
    "climate_risk": [],  # cf. note en tête de fichier — hors système de clauses, décision documentée
    "conclusion": [
        "total_esg_score",       # bandé 70/50 — content_generator.py:807-812
        "strengths_count",       # len(scores.strengths)
        "weaknesses_count",      # len(scores.weaknesses)
        "recommendations_count", # len(scores.recommendations)
    ],
}


# ── Nomenclature de tranche, uniforme, indexée sur le score ────────────────
TRANCHE_100 = "exemplaire"
TRANCHE_80 = "solide"
TRANCHE_60 = "satisfaisant"
TRANCHE_40 = "fragile"
TRANCHE_20 = "critique"

PLUS_HAUT_MIEUX = "plus_haut_mieux"
PLUS_BAS_MIEUX = "plus_bas_mieux"


# ── Grilles à 5 tranches, recopiées depuis les seuils de score réels ───────
# (Option A validée : le texte décrit le même monde que le score, jamais un
# monde parallèle. En cas de divergence future entre esg_calculator.py et ce
# dict, esg_calculator.py fait foi et ce fichier doit être resynchronisé.)
SEUILS = {
    "renewable_energy_percent": {
        "bornes": [(80, TRANCHE_100), (60, TRANCHE_80), (40, TRANCHE_60), (20, TRANCHE_40), (0, TRANCHE_20)],
        "sens": PLUS_HAUT_MIEUX,
        "source": "esg_calculator.py:61-63",
    },
    "waste_recycled_percent": {
        "bornes": [(80, TRANCHE_100), (60, TRANCHE_80), (40, TRANCHE_60), (20, TRANCHE_40), (0, TRANCHE_20)],
        "sens": PLUS_HAUT_MIEUX,
        "source": "esg_calculator.py:68-70",
    },
    "co2_emissions_tonnes": {
        # Cas spécial : PAS une grille unique. L'indicateur classé est
        # l'INTENSITÉ carbone (t CO2e / M€ CA), pas la tonne brute, bandée
        # par famille sectorielle (SECTOR_CARBON_THRESHOLDS). Voir classer().
        "bornes_par_secteur": SECTOR_CARBON_THRESHOLDS,
        "bornes_defaut": _DEFAULT_CARBON_THRESHOLDS,
        "sens": PLUS_BAS_MIEUX,
        "necessite_revenue": True,  # sans company.revenue_eur, aucune tranche possible
        "source": "esg_calculator.py:23-41, 74-80",
    },
    "biodiversity_initiatives": {
        # Bornes dérivées PAR CALCUL DIRECT de la formule existante
        # (min(100, n * 20)) : aucune nouvelle donnée introduite ici.
        "bornes": [(5, TRANCHE_100), (4, TRANCHE_80), (3, TRANCHE_60), (2, TRANCHE_40), (0, TRANCHE_20)],
        "sens": PLUS_HAUT_MIEUX,
        "formule_origine": "min(100, n * 20)",
        "source": "esg_calculator.py:96",
    },
    "training_hours_per_employee": {
        "bornes": [(40, TRANCHE_100), (30, TRANCHE_80), (20, TRANCHE_60), (10, TRANCHE_40), (0, TRANCHE_20)],
        "sens": PLUS_HAUT_MIEUX,
        "source": "esg_calculator.py:126-128",
    },
    "accident_frequency_rate": {
        "bornes": [(1, TRANCHE_100), (3, TRANCHE_80), (5, TRANCHE_60), (8, TRANCHE_40), (15, TRANCHE_20)],
        "sens": PLUS_BAS_MIEUX,
        "source": "esg_calculator.py:133-135",
        # DETTE D'EXACTITUDE (voir DETTE.md) : barème non recalibré vs.
        # moyenne nationale CNAM (~20). Non corrigé dans ce chantier.
    },
    "employee_turnover_percent": {
        "bornes": [(5, TRANCHE_100), (10, TRANCHE_80), (15, TRANCHE_60), (20, TRANCHE_40), (30, TRANCHE_20)],
        "sens": PLUS_BAS_MIEUX,
        "source": "esg_calculator.py:120-122",
    },
    "customer_satisfaction_score": {
        "bornes": [(8.5, TRANCHE_100), (7.5, TRANCHE_80), (6.5, TRANCHE_60), (5.5, TRANCHE_40), (0, TRANCHE_20)],
        "sens": PLUS_HAUT_MIEUX,
        "source": "esg_calculator.py:140-142",
    },
    "female_employees_percent": {
        "bornes": [(45, TRANCHE_100), (35, TRANCHE_80), (25, TRANCHE_60), (15, TRANCHE_40), (0, TRANCHE_20)],
        "sens": PLUS_HAUT_MIEUX,
        "source": "esg_calculator.py:113-115",
    },
    "female_board_percent": {
        "bornes": [(40, TRANCHE_100), (30, TRANCHE_80), (20, TRANCHE_60), (10, TRANCHE_40), (0, TRANCHE_20)],
        "sens": PLUS_HAUT_MIEUX,
        "source": "esg_calculator.py:161-163",
    },
    "independent_board_percent": {
        "bornes": [(60, TRANCHE_100), (50, TRANCHE_80), (40, TRANCHE_60), (30, TRANCHE_40), (0, TRANCHE_20)],
        "sens": PLUS_HAUT_MIEUX,
        "source": "esg_calculator.py:168-170",
    },
    "csr_budget_eur": {
        # Bornes dérivées PAR CALCUL DIRECT de min(100, budget / 500000 * 100).
        "bornes": [(500000, TRANCHE_100), (400000, TRANCHE_80), (300000, TRANCHE_60), (200000, TRANCHE_40), (0, TRANCHE_20)],
        "sens": PLUS_HAUT_MIEUX,
        "formule_origine": "min(100, budget / 500000 * 100)",
        "source": "esg_calculator.py:194",
    },
    "community_investment_eur": {
        # Bornes dérivées PAR CALCUL DIRECT de min(100, budget / 100000 * 20).
        "bornes": [(500000, TRANCHE_100), (400000, TRANCHE_80), (300000, TRANCHE_60), (200000, TRANCHE_40), (0, TRANCHE_20)],
        "sens": PLUS_HAUT_MIEUX,
        "formule_origine": "min(100, budget / 100000 * 20)",
        "source": "esg_calculator.py:146",
    },

    # ── Narratif brut sans tranche : citables tels quels (valeur factuelle),
    # jamais classés bon/moyen/mauvais faute de seuil défendable. ──────────
    "energy_consumption_mwh": {"sens": None, "source": "content_generator.py:707-708"},
    "water_consumption_m3": {"sens": None, "source": "content_generator.py:709-710"},
    "waste_generated_tonnes": {"sens": None, "source": "models.py:61, ppt_generator.py:847-848"},
    "disabled_employees_percent": {"sens": None, "source": "content_generator.py:759-760"},
    "local_suppliers_percent": {"sens": None, "source": "content_generator.py:757-758"},
    "total_employees": {"sens": None, "source": "content_generator.py:737-738"},
    "turnover_aligned_percent": {"sens": None, "source": "content_generator.py:872-873"},
    "capex_aligned_percent": {"sens": None, "source": "content_generator.py:874-875"},
    "opex_aligned_percent": {"sens": None, "source": "content_generator.py:876-877"},
}


# ── Indicateurs catégoriels (non numériques ou hors moule à 5 tranches) ────
CATEGORIES = {
    # Compteurs à sens inversé : 0 = meilleur. Formule de pénalité, pas une
    # grille de tranches nommées.
    "ethics_violations": {
        "type": "compteur_penalite",
        "formule_origine": "100 si n==0, sinon max(0, 100 - n*20)",
        "libelle_zero": "aucun manquement éthique enregistré",
        "libelle_nonzero": "manquement(s) éthique(s)",
        "source": "esg_calculator.py:174",
    },
    "data_breaches": {
        "type": "compteur_penalite",
        "formule_origine": "100 si n==0, sinon max(0, 100 - n*30)",
        "libelle_zero": "aucun incident cybersécurité déclaré",
        "libelle_nonzero": "incident(s) cybersécurité déclaré(s)",
        "source": "esg_calculator.py:178",
    },
    "corruption_cases": {
        "type": "compteur_binaire",
        "libelle_zero": "zéro cas de corruption enregistré",
        # DETTE D'EXACTITUDE (voir DETTE.md) : absent de calculate_governance_score,
        # un cas de corruption ne modifie donc pas le score. libelle_nonzero
        # volontairement None : le texte actuel ne dit rien si n>0 non plus,
        # on ne comble pas ce trou par une formulation inventée.
        "libelle_nonzero": None,
        "source": "content_generator.py:790-791",
    },
    # Booléens
    "esg_audit_conducted": {
        "type": "booleen",
        "score_si_vrai": 100, "score_si_faux": 20,
        "source": "esg_calculator.py:181-184",
    },
    "sustainability_committee": {
        "type": "booleen",
        "score_si_vrai": 100, "score_si_faux": 20,
        "source": "esg_calculator.py:187-190",
    },
    "scope_completeness": {
        # Ex-narratif "brut" (voir historique du fichier) : deux états
        # opposés (complet / incomplet) ne peuvent pas partager une même
        # liste "brut" sélectionnée par index fixe (composer.py prenait
        # toujours l'élément 0, donc toujours le même état quelle que soit
        # la donnée réelle — piège révélé en rédigeant les clauses
        # environmental). Reclassé booléen : la clause suit la donnée.
        "type": "booleen",
        # PAS un gate 100/20 comme les deux booléens ci-dessus : c'est un
        # composite (scope1+2+3 tous renseignés ou non), pas un champ direct
        # du modèle ; l'appelant doit le calculer avant de le passer à
        # composer_section(). Le score réel associé (esg_calculator.py:83-86)
        # est 80 si complet, 60 si seul co2_emissions_tonnes est renseigné —
        # pas un gate binaire 100/20, donc pas de score_si_vrai/faux ici.
        "source": "esg_calculator.py:83-86",
    },
}


# ── Cibles citables (source réelle uniquement, sans unité dans la valeur —
# l'unité s'écrit dans la clause). Aucune entrée n'est ajoutée sans source
# vérifiable : cf. DETTE.md pour les attributions légales non confirmées
# volontairement laissées EN DEHORS de ce dict. ────────────────────────────
CIBLES = {
    "co2_emissions_tonnes": {
        "valeur": 42,
        "source": (
            "Science Based Targets initiative (SBTi), trajectoire 1,5°C — "
            "réduction visée d'ici 2030 vs. année de référence (figure "
            "publique de la méthodologie SBTi, pas une donnée propre au "
            "client ; déjà citée content_generator.py:851-854)"
        ),
    },
    "independent_board_percent": {
        "valeur": 50,
        "source": "Code AFEP-MEDEF, seuil d'administrateurs indépendants (déjà cité content_generator.py:780)",
    },
    "energie_renouvelable": {
        "valeur": None,
        "source": (
            "Aucun seuil réglementaire ou sectoriel identifié, vérifiable "
            "en l'état, pour la part d'énergie renouvelable d'une "
            "entreprise (les objectifs nationaux de mix énergétique "
            "existent mais ne se transposent pas directement à une "
            "entreprise). Libellé neutre retenu, sans chiffre cible : "
            "\"objectif de transition énergétique\"."
        ),
    },
    # PAS d'entrée pour female_board_percent ni female_employees_percent :
    # l'attribution légale actuelle dans le code (Rixain / "objectif légal
    # 40%") n'est pas vérifiée — cf. DETTE.md. Rien n'est inscrit ici tant
    # que ce n'est pas sourcé pour de vrai.
}


def classer(indicateur: str, valeur, secteur: str = None):
    """Retourne le nom de tranche (une valeur de SEUILS[...]["bornes"]),
    ou None si :
    - la valeur est absente (None) ;
    - l'indicateur n'a pas de grille défendable (narratif brut) ;
    - l'indicateur est un compteur/booléen (-> voir CATEGORIES, pas ici) ;
    - il s'agit de co2_emissions_tonnes sans revenue_eur pour calculer
      l'intensité (jamais de crash : None proprement).

    Pour co2_emissions_tonnes, `valeur` DOIT être l'INTENSITÉ déjà calculée
    (co2_emissions_tonnes / revenue_eur * 1_000_000), pas la tonne brute.
    Si l'appelant n'a pas de revenue_eur, il ne doit pas appeler classer()
    pour cet indicateur — retourne None par défaut si valeur est None.
    """
    if valeur is None:
        return None

    if indicateur == "co2_emissions_tonnes":
        # Intensité déjà calculée par l'appelant (voir docstring). Grille
        # sectorielle si le secteur matche une famille connue, sinon la
        # grille générique — même logique que carbon_thresholds_for()
        # dans esg_calculator.py, sans la dupliquer (import direct du dict).
        s = (secteur or "").lower()
        bornes = SEUILS["co2_emissions_tonnes"]["bornes_defaut"]
        for key, th in SEUILS["co2_emissions_tonnes"]["bornes_par_secteur"].items():
            if key in s:
                bornes = th
                break
        for borne, score in bornes:
            if valeur <= borne:
                return {100: TRANCHE_100, 80: TRANCHE_80, 60: TRANCHE_60,
                        40: TRANCHE_40, 20: TRANCHE_20}[score]
        return TRANCHE_20

    entry = SEUILS.get(indicateur)
    if not entry or "bornes" not in entry:
        return None  # narratif brut sans tranche, ou pas dans SEUILS du tout

    higher_is_better = entry["sens"] == PLUS_HAUT_MIEUX
    for borne, nom in entry["bornes"]:
        if (valeur >= borne) if higher_is_better else (valeur <= borne):
            return nom
    return entry["bornes"][-1][1]
