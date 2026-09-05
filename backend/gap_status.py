"""Sémantique des statuts du tableau « Couverture des exigences de reporting ».

SOURCE DE VÉRITÉ UNIQUE. Avant ce module, la même information vivait en trois
exemplaires — `report_generator.py` (hex avec `#`), `ppt_generator.py`
(`RGBColor`), `docx_generator.py` (hex sans `#`) — trois fichiers portant la
même décision de sens dans trois formats. Les générateurs CONVERTISSENT
désormais depuis ce module ; ils ne redéfinissent plus.

Deux notions distinctes cohabitent dans le tableau, que l'ancien vocabulaire
écrasait sous « Conforme / Non conforme » :

- `PUBLICATION` : la ligne constate qu'une donnée est publiée ou non. Avoir un
  chiffre n'est PAS être conforme à une norme de publication — et « conforme »
  a une portée juridique dans un document qu'un cabinet remet à son client.
- `SEUIL` : la ligne situe l'entreprise par rapport à un seuil nommé.
- `NON_COUVERT` : l'outil ne collecte pas la donnée. L'absence est côté
  PRODUIT, pas côté client : le rapport ne doit pas imputer au client une
  lacune de l'outil.
"""

PUBLICATION = "publication"
SEUIL = "seuil"
NON_COUVERT = "non_couvert"

NATURES = (PUBLICATION, SEUIL, NON_COUVERT)

# Un constat de publication n'est ni un succès ni un échec : le vert
# #2E7D32 en a donc disparu. Une pastille verte se lit « conforme » même
# quand le mot a changé — le changement de vocabulaire serait resté lettre
# morte si la couleur avait continué de porter l'affirmation.
NEUTRE = "#37474F"
ALERTE = "#D97706"
MANQUE = "#E74C3C"
FRANCHI = "#2E7D32"        # admissible sur la seule nature SEUIL
NON_RENSEIGNE = "#7F8C8D"
HORS_PERIMETRE = "#5A6572"

_COULEURS = {
    (PUBLICATION, "ok"): NEUTRE,
    (PUBLICATION, "partial"): ALERTE,
    (PUBLICATION, "no"): MANQUE,
    (SEUIL, "ok"): FRANCHI,
    (SEUIL, "partial"): ALERTE,
    (SEUIL, "no"): MANQUE,
}

# `na` et `oos` restent DISTINCTS : « non renseigné » est une donnée inconnue,
# « hors périmètre VSME » est une exigence connue mais non requise par le
# référentiel retenu. Ne jamais les fusionner.
_COULEURS_PAR_CODE = {
    "na": NON_RENSEIGNE,
    "oos": HORS_PERIMETRE,
}

_CLES_LIBELLE = {
    (PUBLICATION, "ok"): "st_pub_ok",
    (PUBLICATION, "partial"): "st_pub_partial",
    (PUBLICATION, "no"): "st_pub_no",
    (SEUIL, "ok"): "st_seuil_ok",
    (SEUIL, "partial"): "st_seuil_partial",
    (SEUIL, "no"): "st_seuil_no",
}


def couleur(status: str, nature: str) -> str:
    """Couleur canonique d'un statut, en hexadécimal `#RRGGBB`."""
    if status == "na" and nature == NON_COUVERT:
        return NON_RENSEIGNE
    if status in _COULEURS_PAR_CODE:
        return _COULEURS_PAR_CODE[status]
    return _COULEURS[(nature, status)]


def cle_libelle(status: str, nature: str) -> str:
    """Clé i18n du libellé, choisie selon la NATURE de la ligne.

    C'est ici que se joue la correction : un même code `ok` se dit « Publié »
    sur une ligne de publication et « Au-dessus du seuil » sur une ligne de
    seuil. Un vocabulaire unique ne pouvait être honnête pour les deux.
    """
    if status == "na":
        return "st_non_couvert" if nature == NON_COUVERT else "st_na"
    if status == "oos":
        return "st_oos"
    return _CLES_LIBELLE[(nature, status)]


def libelle(TR: dict, status: str, nature: str) -> str:
    """Libellé traduit, prêt à imprimer."""
    return TR[cle_libelle(status, nature)]


def hex_sans_diese(status: str, nature: str) -> str:
    """Conversion pour python-docx, qui veut `RRGGBB`."""
    return couleur(status, nature).lstrip("#")


def rgb_triplet(status: str, nature: str) -> tuple:
    """Conversion pour python-pptx, qui veut trois entiers."""
    h = hex_sans_diese(status, nature)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
