"""
Composition des paragraphes à partir de bands.py + clauses/fr.py.

Ce module NE contient aucun texte rédigé et NE décide d'aucun seuil : il lit
bands.py (indicateurs, tranches) et clauses/<lang>.py (bibliothèque de
phrases par indicateur/tranche), sélectionne les indicateurs les plus graves
par section et assemble le paragraphe. Tant que la bibliothèque de clauses
est vide (listes vides dans clauses/fr.py), sections_pretes() renvoie un
ensemble vide et l'appelant doit se replier sur l'ancien générateur
(_generate_fr / _generate_en dans content_generator.py) — c'est ce repli qui
permet de brancher section par section sans rien casser.

Non branché dans content_generator.py à ce stade (décision explicite) : la
banque est vide, l'ancien système reste seul actif.
"""

from bands import INDICATEURS_PAR_SECTION, SEUILS, CATEGORIES, classer

# Gravité des tranches, de la plus grave à la moins grave : sert à choisir
# quels indicateurs mettre en avant dans un paragraphe qui n'en cite que 2-3
# (jamais tous). Une tranche non trouvée (indicateur narratif brut, ou
# catégoriel) est considérée neutre et n'entre pas en compétition pour la
# priorité — elle peut toujours être citée factuellement, mais jamais comme
# "le plus grave".
GRAVITE = {"critique": 0, "fragile": 1, "satisfaisant": 2, "solide": 3, "exemplaire": 4}

NB_INDICATEURS_PAR_PARAGRAPHE = 3


def _valeur_indicateur(indicateur: str, donnees: dict):
    """Lit la valeur brute d'un indicateur dans le dict de données aplati
    fourni par l'appelant (voir composer_section). Ne fait aucun calcul
    métier ici (l'intensité carbone, par ex., doit être précalculée par
    l'appelant avant d'être passée dans `donnees`)."""
    return donnees.get(indicateur)


def indicateurs_ranges_par_gravite(section: str, donnees: dict, secteur: str = None) -> list:
    """Pour une section, renvoie les indicateurs de INDICATEURS_PAR_SECTION
    qui ont une valeur ET une tranche numérique (SEUILS avec "bornes"),
    triés du plus grave au moins grave. Les indicateurs catégoriels
    (CATEGORIES) et narratifs bruts (SEUILS sans "bornes") sont exclus de ce
    classement : ils n'ont pas de notion de "gravité" comparable entre eux
    sur la même échelle à 5 tranches."""
    candidats = []
    for indicateur in INDICATEURS_PAR_SECTION.get(section, []):
        if indicateur in CATEGORIES:
            continue  # pas de gravité comparable ; traité à part par l'appelant
        entry = SEUILS.get(indicateur)
        if not entry or "bornes" not in entry:
            continue  # narratif brut, pas de tranche
        valeur = _valeur_indicateur(indicateur, donnees)
        if valeur is None:
            continue
        tranche = classer(indicateur, valeur, secteur=secteur)
        if tranche is None:
            continue
        candidats.append((indicateur, tranche, GRAVITE[tranche]))
    candidats.sort(key=lambda c: c[2])
    return candidats


def composer_section(section: str, donnees: dict, clauses_lang: dict, secteur: str = None) -> str:
    """Compose le paragraphe d'une section à partir des 2-3 indicateurs les
    plus graves. Renvoie une chaîne vide si aucune clause n'est disponible
    pour aucun des indicateurs sélectionnés (banque vide, ou tranche non
    couverte) — c'est ce vide que sections_pretes() détecte pour piloter le
    repli sur l'ancien générateur."""
    ranked = indicateurs_ranges_par_gravite(section, donnees, secteur=secteur)
    phrases = []
    for indicateur, tranche, _gravite in ranked[:NB_INDICATEURS_PAR_PARAGRAPHE]:
        banque = clauses_lang.get(section, {}).get(indicateur, {}).get(tranche, [])
        if banque:
            phrases.append(banque[0])  # sélection déterministe : première clause dispo
    return " ".join(phrases)


def sections_pretes(clauses_lang: dict) -> set:
    """Renvoie l'ensemble des sections qui ont au moins une clause non vide
    quelque part dans la bibliothèque fournie (clauses/fr.py ou son
    équivalent EN). Une section absente de ce set doit rester générée par
    l'ancien système (content_generator._generate_fr / _generate_en) — c'est
    le mécanisme de repli explicitement demandé, tant que la banque n'est
    pas remplie section par section.

    clauses_lang mélange deux formes de valeur sous les clés "<section>"
    (dict indicateur -> tranche -> liste) : les clés "ouverture:<section>"
    et "cloture:<section>" (liste de phrases, indépendantes des
    indicateurs). Les deux comptent pour juger une section prête."""
    pretes = set()
    for cle, valeur in clauses_lang.items():
        section = cle.split(":", 1)[1] if ":" in cle else cle
        if section in pretes:
            continue
        if isinstance(valeur, list):
            if valeur:
                pretes.add(section)
        else:  # dict indicateur -> tranche -> liste
            for tranches in valeur.values():
                if any(tranches.get(t) for t in tranches):
                    pretes.add(section)
                    break
    return pretes
