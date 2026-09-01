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
