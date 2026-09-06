"""Affichage des scores : calculabilité et complétude.

SOURCE DE VÉRITÉ UNIQUE pour deux questions que tous les livrables posent :
« ce score est-il calculable ? » et « sur combien d'indicateurs ? ».

T2 — un pilier sans aucun indicateur déclaré **n'est pas calculable**. Il ne
vaut pas 50. Rendre 50 fabriquait un jugement à partir d'aucune donnée, ce qui
est une affirmation sans source — la famille de ce que l'étape A a retiré. La
note globale devient non calculable dès qu'un pilier l'est : pondérer 40/35/25
sur deux piliers refabriquerait le troisième.

T1 — le score s'accompagne du nombre d'indicateurs qui l'ont produit. Deux
précisions sans lesquelles le ratio serait trompeur :

1. il porte sur les indicateurs **qui entrent dans le barème**, pas sur les
   champs du formulaire ;
2. le questionnaire collecte 29 indicateurs, **18 seulement** entrent dans le
   calcul : 11 sont publiés dans le rapport sans y contribuer (cf. DETTE.md).

D'où deux formulations : une forme courte à côté du score, et une phrase
complète, dite **une fois**, dans la note méthodologique.
"""

# Nombre d'indicateurs qui entrent réellement dans le barème, par pilier.
# À tenir synchronisé avec esg_calculator : ces maxima sont le dénominateur
# imprimé dans les livrables.
NB_INDICATEURS = {"env": 5, "social": 6, "gov": 7}
TOTAL_INDICATEURS = sum(NB_INDICATEURS.values())          # 18

# Champs collectés par le questionnaire mais qui n'entrent dans aucun score.
# Publier « 14 sur 18 » sans le dire laisserait croire que le formulaire ne
# collecte que 18 choses.
NB_CHAMPS_COLLECTES = 29
NB_CHAMPS_HORS_BAREME = NB_CHAMPS_COLLECTES - TOTAL_INDICATEURS   # 11


def est_calculable(scores) -> bool:
    """La note globale est-elle calculable ? Faux dès qu'un pilier ne l'est pas."""
    return scores.total_esg_score is not None


def pilier_calculable(valeur) -> bool:
    return valeur is not None


def indicateurs_notes(scores) -> int:
    """Nombre d'indicateurs ayant réellement produit une note, tous piliers."""
    return sum((scores.completude or {}).get(p, 0) for p in NB_INDICATEURS)


def texte_score(scores, TR) -> str:
    """Le score global, ou la mention de non-calculabilité. Jamais un défaut."""
    if not est_calculable(scores):
        return TR["score_non_calculable"]
    return f"{scores.total_esg_score:.0f}"


def texte_note(scores, TR) -> str:
    """La note lettrée, ou la mention de non-calculabilité."""
    if not est_calculable(scores):
        return TR["note_non_calculable"]
    return scores.rating


def texte_pilier(valeur, TR) -> str:
    if not pilier_calculable(valeur):
        return TR["note_non_calculable"]
    return f"{valeur:.0f}"


def texte_completude(scores, TR) -> str:
    """Forme courte, à imprimer à côté du score."""
    return TR["completude_courte"].format(n=indicateurs_notes(scores),
                                          m=TOTAL_INDICATEURS)


def phrase_completude(TR) -> str:
    """Forme longue, à dire UNE FOIS dans la note méthodologique : elle est la
    seule à lever l'ambiguïté sur le dénominateur."""
    return TR["completude_methodo"].format(collectes=NB_CHAMPS_COLLECTES,
                                           notes=TOTAL_INDICATEURS,
                                           hors=NB_CHAMPS_HORS_BAREME)
