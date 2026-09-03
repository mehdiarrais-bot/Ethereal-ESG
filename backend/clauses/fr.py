"""
Bibliothèque de clauses françaises — squelette VIDE, généré depuis bands.py.

Les clés (sections, indicateurs, tranches) sont calculées à l'import à partir
de bands.INDICATEURS_PAR_SECTION / bands.SEUILS / bands.CATEGORIES : elles ne
peuvent donc pas diverger de bands.py par construction — on ne les recopie
jamais à la main ici. Seul le contenu des listes (les phrases) est écrit à la
main, chantier par chantier, section par section.

Trois formes de sous-dict selon le type d'indicateur (voir bands.py) :
- indicateur à grille 5 tranches (SEUILS avec "bornes") :
    {"exemplaire": [], "solide": [], "satisfaisant": [], "fragile": [], "critique": []}
- indicateur catégoriel (CATEGORIES : compteur ou booléen) :
    {"zero": [], "nonzero": []}                 pour compteur_penalite / compteur_binaire
    {"vrai": [], "faux": []}                    pour booleen
- indicateur narratif brut (SEUILS sans "bornes", ex. energy_consumption_mwh) :
    {"brut": []}                                 une seule liste, citation factuelle sans jugement

Tant que toutes les listes sont vides, composer.sections_pretes() renvoie un
ensemble vide et l'ancien générateur (content_generator._generate_fr) reste
seul actif — ce fichier n'est pas branché ailleurs à ce stade.
"""

from bands import INDICATEURS_PAR_SECTION, SEUILS, CATEGORIES

TRANCHES_NUMERIQUES = ("exemplaire", "solide", "satisfaisant", "fragile", "critique")


def _squelette_indicateur(indicateur: str) -> dict:
    if indicateur in CATEGORIES:
        cat = CATEGORIES[indicateur]
        if cat["type"] == "booleen":
            return {"vrai": [], "faux": []}
        return {"zero": [], "nonzero": []}  # compteur_penalite / compteur_binaire

    entry = SEUILS.get(indicateur)
    if entry and "bornes" in entry:
        return {tranche: [] for tranche in TRANCHES_NUMERIQUES}
    if entry and "bornes_par_secteur" in entry:
        return {tranche: [] for tranche in TRANCHES_NUMERIQUES}  # co2_emissions_tonnes

    return {"brut": []}  # narratif brut sans seuil, ou indicateur non trouvé dans SEUILS


def _squelette_section(section: str) -> dict:
    return {indicateur: _squelette_indicateur(indicateur)
            for indicateur in INDICATEURS_PAR_SECTION.get(section, [])}


# ── Squelette complet, une entrée par section de bands.INDICATEURS_PAR_SECTION.
# Sections "ouverture:<section>" et "cloture:<section>" : phrases d'entrée et
# de sortie de paragraphe, indépendantes des indicateurs (toujours vides ici,
# pas de clé par indicateur puisqu'elles ne dépendent d'aucun seuil). ──────
CLAUSES = {}
for _section in INDICATEURS_PAR_SECTION:
    CLAUSES[f"ouverture:{_section}"] = []
    CLAUSES[_section] = _squelette_section(_section)
    CLAUSES[f"cloture:{_section}"] = []
del _section


# ══════════════════════════════════════════════════════════════════════════
# Section ENVIRONMENTAL — rédigée et validée.
# Les clés remplies ci-dessous doivent correspondre exactement au squelette
# généré au-dessus ; c'est vérifié par les tests anti-divergence
# (tests/test_bands.py). Aucune clause ne cite un seuil chiffré en dur :
# les bornes vivent dans bands.py, une seule fois.
# ══════════════════════════════════════════════════════════════════════════

CLAUSES["ouverture:environmental"] = [
    "Le pilier Environnement de {n} obtient {score}/100 sur l'exercice {an}.",
    "Sur le volet environnemental, {n} atteint {score}/100 au titre de l'exercice {an}.",
    "La performance environnementale de {n} s'établit à {score}/100 pour l'exercice {an}.",
]

CLAUSES["environmental"] = {
    # {value} porte ici l'INTENSITÉ carbone (t CO₂e/M€ de CA), arrondie à
    # l'entier par l'appelant — pas la tonne brute. Les clauses énoncent
    # cette valeur et sa conséquence : aucune ne situe l'entreprise par
    # rapport à un secteur, une moyenne ou un standard externe. La grille
    # qui produit la tranche est interne et non sourcée ; elle est declarée
    # une seule fois, dans la note méthodologique du rapport.
    "co2_emissions_tonnes": {
        "exemplaire": [
            "L'intensité carbone s'établit à {value} t CO₂e par million d'euros de chiffre d'affaires, un niveau bas qui limite l'exposition au renchérissement du carbone.",
            "À {value} t CO₂e par million d'euros de chiffre d'affaires, l'efficacité carbone de {n} constitue un atout.",
        ],
        "solide": [
            "L'intensité carbone s'établit à {value} t CO₂e par million d'euros de chiffre d'affaires, signe d'un modèle déjà sobre en émissions.",
            "Les émissions de {n} représentent {value} t CO₂e par million d'euros de chiffre d'affaires, une efficacité carbone solide.",
        ],
        "satisfaisant": [
            "L'intensité carbone atteint {value} t CO₂e par million d'euros de chiffre d'affaires, un niveau intermédiaire : ni avantage ni retard marqué.",
            "Les émissions de {n} représentent {value} t CO₂e par million d'euros de chiffre d'affaires.",
        ],
        "fragile": [
            "L'intensité carbone atteint {value} t CO₂e par million d'euros de chiffre d'affaires, un niveau à surveiller : l'exposition au coût du carbone constitue un point de vigilance.",
            "À {value} t CO₂e par million d'euros de chiffre d'affaires, l'intensité carbone expose {n} au renchérissement du carbone.",
        ],
        "critique": [
            "L'intensité carbone atteint {value} t CO₂e par million d'euros de chiffre d'affaires, un niveau élevé : exposition majeure au prix du carbone, à traiter en priorité.",
            "À {value} t CO₂e par million d'euros de chiffre d'affaires, la décarbonation est l'enjeu environnemental central de {n}.",
        ],
    },
    "renewable_energy_percent": {
        "exemplaire": [
            "La part d'énergie renouvelable atteint {value} %, un niveau qui ancre durablement la transition énergétique de {n}.",
            "Avec {value} % d'énergie renouvelable, {n} a très largement engagé la bascule de son mix énergétique.",
        ],
        "solide": [
            "La part d'énergie renouvelable s'élève à {value} %, une trajectoire de transition bien engagée.",
            "À {value} % d'énergie renouvelable, {n} affiche un mix déjà nettement décarboné.",
        ],
        "satisfaisant": [
            "La part d'énergie renouvelable atteint {value} %, une base correcte que la trajectoire de transition doit consolider.",
            "Avec {value} % d'énergie renouvelable, {n} a amorcé la transition de son mix sans l'avoir encore approfondie.",
        ],
        "fragile": [
            "La part d'énergie renouvelable reste limitée à {value} %, un levier de progrès prioritaire pour l'objectif de transition énergétique.",
            "À {value} % d'énergie renouvelable, le mix énergétique de {n} reste largement dépendant des sources conventionnelles.",
        ],
        "critique": [
            "La part d'énergie renouvelable n'atteint que {value} %, un retard marqué au regard de l'objectif de transition énergétique.",
            "Avec seulement {value} % d'énergie renouvelable, la décarbonation du mix énergétique de {n} reste à construire.",
        ],
    },
    "waste_recycled_percent": {
        "exemplaire": [
            "Le taux de recyclage atteint {value} %, une performance d'économie circulaire remarquable.",
            "Avec {value} % de déchets recyclés, {n} inscrit pleinement son activité dans une logique circulaire.",
        ],
        "solide": [
            "Le taux de recyclage s'élève à {value} %, une valorisation matière élevée.",
            "À {value} % de déchets recyclés, {n} affiche une valorisation matière solide.",
        ],
        "satisfaisant": [
            "Le taux de recyclage atteint {value} %, un niveau correct qui laisse une marge de valorisation.",
            "Avec {value} % de déchets recyclés, {n} valorise une part significative de ses déchets sans épuiser le potentiel circulaire.",
        ],
        "fragile": [
            "Le taux de recyclage reste limité à {value} %, un axe de progrès en matière d'économie circulaire.",
            "À {value} % de déchets recyclés, la valorisation matière de {n} reste limitée.",
        ],
        "critique": [
            "Le taux de recyclage n'atteint que {value} %, une gestion des déchets à repenser en priorité.",
            "Avec seulement {value} % de déchets recyclés, la valorisation matière de {n} reste largement à développer.",
        ],
    },
    "biodiversity_initiatives": {
        "exemplaire": [
            "{n} porte {value} initiatives en faveur de la biodiversité, un engagement soutenu sur ce volet encore peu structuré réglementairement.",
            "Avec {value} initiatives biodiversité, {n} anticipe des exigences qui restent aujourd'hui largement qualitatives.",
        ],
        "solide": [
            "{n} conduit {value} initiatives en faveur de la biodiversité, un engagement tangible sur le sujet.",
            "Avec {value} initiatives biodiversité, {n} traite ce volet de manière active.",
        ],
        "satisfaisant": [
            "{n} recense {value} initiatives en faveur de la biodiversité, un premier socle à étoffer.",
            "Avec {value} initiatives biodiversité, {n} a engagé le sujet sans encore le structurer pleinement.",
        ],
        # Pluriel assumé, "deux" en toutes lettres : la borne fragile de
        # biodiversity_initiatives est [2, 3), donc value vaut TOUJOURS 2 à
        # cette tranche. Pas de "(s)" de publipostage (interdit, verrouillé
        # par test_no_mail_merge_plurals), et pas de "2.0" si la donnée
        # arrivait en flottant.
        "fragile": [
            "{n} ne recense que deux initiatives en faveur de la biodiversité, un volet à développer.",
            "Avec deux initiatives biodiversité seulement, l'engagement de {n} sur ce sujet reste embryonnaire.",
        ],
        "critique": [
            "Aucune ou presque initiative en faveur de la biodiversité n'est recensée, un angle mort à ouvrir.",
            "Le volet biodiversité n'est pas encore investi par {n}, un sujet à mettre à l'agenda.",
        ],
    },
    "energy_consumption_mwh": {
        "brut": [
            "La consommation énergétique déclarée s'élève à {value} MWh sur l'exercice.",
            "{n} déclare une consommation de {value} MWh au titre de l'exercice {an}.",
        ],
    },
    "water_consumption_m3": {
        "brut": [
            "Les prélèvements d'eau déclarés atteignent {value} m³ sur l'exercice.",
            "{n} déclare {value} m³ d'eau prélevée au titre de l'exercice {an}.",
        ],
    },
    "waste_generated_tonnes": {
        "brut": [
            "Le volume de déchets produits s'établit à {value} tonnes sur l'exercice.",
            "{n} déclare {value} tonnes de déchets générés au titre de l'exercice {an}.",
        ],
    },
    "scope_completeness": {
        "vrai": [
            "Le bilan carbone couvre les trois scopes d'émissions (1, 2 et 3), une complétude qui renforce la crédibilité du reporting.",
            "Les trois scopes d'émissions sont renseignés, ce qui donne au bilan carbone une portée complète.",
        ],
        "faux": [
            "Le bilan carbone est incomplet : tous les scopes d'émissions ne sont pas renseignés, ce qui limite la portée du reporting climatique.",
            "Certains scopes d'émissions ne sont pas renseignés, une lacune qui restreint la portée du bilan carbone.",
        ],
    },
}

CLAUSES["cloture:environmental"] = [
    "L'empreinte environnementale constitue le principal levier de création de valeur durable pour {n}.",
    "La trajectoire environnementale de {n} se joue sur la décarbonation et la sobriété des ressources.",
    "Ces indicateurs environnementaux orientent les priorités du plan d'action de {n}.",
]
