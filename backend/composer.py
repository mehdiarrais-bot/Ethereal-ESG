"""
Composition des paragraphes à partir de bands.py + clauses/fr.py.

Ce module NE contient aucun texte rédigé et NE décide d'aucun seuil : il lit
bands.py (indicateurs, tranches) et clauses/<lang>.py (bibliothèque de
phrases par indicateur/tranche), sélectionne les indicateurs les plus graves
par section, substitue les placeholders ({n}, {score}, {an}, {value}, ...)
et assemble le paragraphe. La substitution est TOLÉRANTE : un placeholder
absent du contexte ne casse jamais la génération, il ressort tel quel entre
accolades (voir _ContexteTolerant). Tant que la bibliothèque de clauses est
vide (listes vides dans clauses/fr.py), sections_pretes() renvoie un
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


class _ContexteTolerant(dict):
    """dict de substitution qui ne lève jamais de KeyError : un placeholder
    absent du contexte ressort tel quel, entre accolades, au lieu de
    planter la génération (CLAUDE.md : échouer gracieusement en
    production). Le marqueur laissé en clair ({xxx}) reste repérable au
    test ou à la relecture, sans jamais interrompre un livrable en cours."""
    def __missing__(self, key):
        return "{" + key + "}"


def _substituer(gabarit: str, contexte: dict) -> str:
    """Remplace les placeholders {n}/{score}/{an}/{value}/... d'une clause
    par les valeurs du contexte fourni. Tolérant : jamais d'exception sur
    une clé manquante (voir _ContexteTolerant)."""
    return gabarit.format_map(_ContexteTolerant(contexte))


def _valeur_indicateur(indicateur: str, donnees: dict):
    """Lit la valeur brute d'un indicateur dans le dict de données aplati
    fourni par l'appelant (voir composer_section). Ne fait aucun calcul
    métier ici (l'intensité carbone, par ex., doit être précalculée par
    l'appelant avant d'être passée dans `donnees`)."""
    return donnees.get(indicateur)


def _tranche_categorielle(indicateur: str, valeur):
    """Pour un indicateur de CATEGORIES, renvoie la clé de clause à utiliser
    ("vrai"/"faux" pour un booléen, "zero"/"nonzero" pour un compteur), en
    fonction de la VALEUR RÉELLE — jamais un index fixe. C'est cette
    fonction qui corrige le piège trouvé en rédigeant scope_completeness :
    avant, composer_section() prenait toujours banque[0], donc toujours le
    même état quelle que soit la donnée. Renvoie None si la valeur est
    absente (pas de clause plutôt qu'une clause devinée)."""
    if valeur is None:
        return None
    cat = CATEGORIES.get(indicateur)
    if not cat:
        return None
    if cat["type"] == "booleen":
        return "vrai" if valeur else "faux"
    return "zero" if valeur == 0 else "nonzero"  # compteur_penalite / compteur_binaire


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


def composer_section(section: str, donnees: dict, clauses_lang: dict,
                      contexte: dict = None, secteur: str = None) -> str:
    """Compose le paragraphe d'une section :
    - les 2-3 indicateurs à grille (SEUILS) les plus graves ;
    - PLUS tous les indicateurs catégoriels (CATEGORIES) de la section qui
      ont une valeur et une clause disponible pour leur état réel — ils ne
      concourent pas sur la "gravité" (pas comparable à une grille à 5
      tranches, voir indicateurs_ranges_par_gravite) donc ne sont pas
      soumis à NB_INDICATEURS_PAR_PARAGRAPHE ; à revisiter si un jour une
      section catégorielle en compte beaucoup (gouvernance, plus tard).

    `contexte` porte les placeholders indépendants de l'indicateur (ex.
    {"n": nom_entreprise, "score": score_du_pilier, "an": annee}). Le
    placeholder {value} est ajouté automatiquement pour chaque clause avec
    la valeur brute de l'indicateur cité — pas la même valeur d'une clause
    à l'autre dans le même paragraphe.

    Renvoie une chaîne vide si aucune clause n'est disponible pour aucun
    indicateur sélectionné (banque vide, ou tranche/état non couvert) —
    c'est ce vide que sections_pretes() détecte pour piloter le repli sur
    l'ancien générateur."""
    contexte = contexte or {}
    phrases = []

    ranked = indicateurs_ranges_par_gravite(section, donnees, secteur=secteur)
    for indicateur, tranche, _gravite in ranked[:NB_INDICATEURS_PAR_PARAGRAPHE]:
        banque = clauses_lang.get(section, {}).get(indicateur, {}).get(tranche, [])
        if banque:
            phrases.append(_substituer(banque[0], {**contexte, "value": donnees.get(indicateur)}))

    for indicateur in INDICATEURS_PAR_SECTION.get(section, []):
        if indicateur not in CATEGORIES:
            continue
        valeur = _valeur_indicateur(indicateur, donnees)
        cle = _tranche_categorielle(indicateur, valeur)
        if cle is None:
            continue
        banque = clauses_lang.get(section, {}).get(indicateur, {}).get(cle, [])
        if banque:
            phrases.append(_substituer(banque[0], {**contexte, "value": valeur}))

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
