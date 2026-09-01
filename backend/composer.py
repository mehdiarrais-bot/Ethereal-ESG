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

# Un seul fait chiffré "brut" par paragraphe : le paragraphe porte déjà
# jusqu'à NB_INDICATEURS_PAR_PARAGRAPHE phrases analytiques plus les
# clauses catégorielles. Au-delà d'un chiffre brut, le paragraphe redevient
# une énumération ("X MWh. Y m³. Z tonnes."), le défaut mécanique que le
# système de clauses vise justement à supprimer. Constante nommée : la
# passer à 2 ne demande aucune modification de logique.
NB_BRUTS_PAR_PARAGRAPHE = 1


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


def _formater_valeur(v):
    """Met en forme une valeur numérique pour insertion dans une clause.

    Pydantic type la plupart des champs en float : sans mise en forme,
    {value} rendrait "42.0 %" ou "12000.0 MWh". Règle retenue : un
    flottant de valeur entière perd sa décimale, un flottant non entier
    la garde (6.2 reste 6.2, c'est une décimale porteuse de sens).

    Le séparateur de milliers reproduit VOLONTAIREMENT celui de l'ancien
    générateur (format ",", donc "12,000" — séparateur anglais dans un
    texte français). C'est un défaut préexistant, consigné dans DETTE.md :
    il doit être corrigé sur tout le système d'un seul coup (ancien
    générateur + composer), pas section par section, sinon un même rapport
    mélangerait "12 000" et "12,000" selon la section pendant la migration.

    Les booléens sont laissés tels quels : bool est une sous-classe de int
    en Python, sans ce garde-fou True serait rendu "1"."""
    if isinstance(v, bool):
        return v
    if isinstance(v, float) and v.is_integer():
        return f"{v:,.0f}"
    if isinstance(v, (int, float)):
        return f"{v:,}"
    return v


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
        # "bornes_par_secteur" compte autant que "bornes" : co2_emissions_tonnes
        # est classé sur une grille SECTORIELLE et n'a donc pas de clé
        # "bornes". Sans ce second test il était écarté du classement alors
        # que classer() sait parfaitement le ranger — ses clauses devenaient
        # inatteignables. Même critère que la détection des "brut" plus bas :
        # les deux filtres doivent rester cohérents.
        if not entry or ("bornes" not in entry and "bornes_par_secteur" not in entry):
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
    """Compose le paragraphe d'une section, dans cet ordre :
    1. les 2-3 indicateurs à grille (SEUILS) les plus graves — l'analyse ;
    2. au plus NB_BRUTS_PAR_PARAGRAPHE indicateur "brut" — l'ancrage
       chiffré, choisi par ordre de déclaration dans
       bands.INDICATEURS_PAR_SECTION ;
    3. les indicateurs catégoriels (CATEGORIES) de la section qui ont une
       valeur et une clause pour leur état réel — commentaire méta, en fin
       de paragraphe. Ils ne concourent pas sur la "gravité" (pas
       comparable à une grille à 5 tranches, voir
       indicateurs_ranges_par_gravite) donc ne sont pas soumis à
       NB_INDICATEURS_PAR_PARAGRAPHE ; à revisiter si une section
       catégorielle en compte beaucoup un jour (gouvernance, plus tard).

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

    # 1. Indicateurs classés : l'analyse, du plus grave au moins grave.
    ranked = indicateurs_ranges_par_gravite(section, donnees, secteur=secteur)
    for indicateur, tranche, _gravite in ranked[:NB_INDICATEURS_PAR_PARAGRAPHE]:
        banque = clauses_lang.get(section, {}).get(indicateur, {}).get(tranche, [])
        if banque:
            phrases.append(_substituer(
                banque[0], {**contexte, "value": _formater_valeur(donnees.get(indicateur))}))

    # 2. Indicateurs "brut" : l'ancrage chiffré, plafonné (voir
    #    NB_BRUTS_PAR_PARAGRAPHE). Sélection par ORDRE DE DÉCLARATION dans
    #    bands.INDICATEURS_PAR_SECTION : cet ordre est une décision
    #    éditoriale visible dans la source de vérité, changer la priorité
    #    revient à réordonner la liste, sans toucher au code.
    bruts_retenus = 0
    for indicateur in INDICATEURS_PAR_SECTION.get(section, []):
        if bruts_retenus >= NB_BRUTS_PAR_PARAGRAPHE:
            break
        if indicateur in CATEGORIES:
            continue
        entry = SEUILS.get(indicateur)
        if entry and ("bornes" in entry or "bornes_par_secteur" in entry):
            continue  # indicateur classé, déjà traité en 1.
        valeur = _valeur_indicateur(indicateur, donnees)
        # ASYMÉTRIE VOLONTAIRE, NE PAS "HARMONISER" : pour un brut, on
        # exclut les valeurs falsy (None ET 0) — une consommation déclarée
        # à 0 MWh est un artefact de saisie, pas un fait à citer (même
        # règle que l'ancien générateur, content_generator.py:707). Pour un
        # indicateur CLASSÉ au contraire, 0 est une valeur pleine de sens
        # (0 % de renouvelable = tranche "critique", un vrai constat) et
        # seul None est écarté, par classer().
        if not valeur:
            continue
        banque = clauses_lang.get(section, {}).get(indicateur, {}).get("brut", [])
        if banque:
            phrases.append(_substituer(
                banque[0], {**contexte, "value": _formater_valeur(valeur)}))
            bruts_retenus += 1

    # 3. Indicateurs catégoriels : commentaire méta (complétude du
    #    reporting, existence d'un audit...), en fin de paragraphe.
    for indicateur in INDICATEURS_PAR_SECTION.get(section, []):
        if indicateur not in CATEGORIES:
            continue
        valeur = _valeur_indicateur(indicateur, donnees)
        cle = _tranche_categorielle(indicateur, valeur)
        if cle is None:
            continue
        banque = clauses_lang.get(section, {}).get(indicateur, {}).get(cle, [])
        if banque:
            phrases.append(_substituer(
                banque[0], {**contexte, "value": _formater_valeur(valeur)}))

    return " ".join(phrases)


def composer_paragraphe(section: str, donnees: dict, clauses_lang: dict,
                        contexte: dict = None, secteur: str = None) -> str:
    """Paragraphe complet d'une section : phrase d'ouverture, corps
    (composer_section), phrase de clôture.

    Fonction distincte de composer_section() à dessein : celle-ci ne
    s'occupe QUE des indicateurs, celle-là de l'assemblage éditorial. Les
    séparer garde chaque responsabilité testable seule.

    Sélection déterministe de la première clause disponible, comme partout
    ailleurs dans ce module. Conséquence assumée à ce stade : deux clients
    dont les données tombent dans les mêmes tranches reçoivent le même
    texte. L'ancien générateur faisait varier les formulations avec un
    tirage indexé sur le nom (_pick/_seed) ; réintroduire cette variété
    dans le composer est un choix éditorial à part entière, à décider
    explicitement, pas à glisser ici en passant."""
    contexte = contexte or {}
    morceaux = []

    ouverture = clauses_lang.get(f"ouverture:{section}", [])
    if ouverture:
        morceaux.append(_substituer(ouverture[0], contexte))

    corps = composer_section(section, donnees, clauses_lang,
                             contexte=contexte, secteur=secteur)
    if corps:
        morceaux.append(corps)

    cloture = clauses_lang.get(f"cloture:{section}", [])
    if cloture:
        morceaux.append(_substituer(cloture[0], contexte))

    return " ".join(morceaux)


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
