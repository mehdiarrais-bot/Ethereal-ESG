"""Répartition des photos d'un rapport : une photo n'apparaît qu'une fois.

Chaque emplacement photo du PDF (« place ») a un thème. La répartition est
planifiée une fois, dans l'ordre du document, à la création du Kit :
d'abord les photos fournies par l'entreprise pour ce thème, puis la banque
locale (assets/photos, domaine public / CC0, CREDITS.md), filtrée par
secteur pour que l'image corresponde à l'activité. Aucune photo n'est
attribuée deux fois ; un emplacement sans photo disponible reçoit une
composition graphique (tuile ou aplat du gabarit), jamais une répétition.

Demande du 2026-09-28 : « je ne veux pas qu'une même image soit utilisée
deux fois dans le même dossier ».
"""

# Photos de nature de la banque (repli du pilier environnement), dans l'ordre
# de préférence après celles du gabarit.
NATURE = ["mountain-lake", "alpine-lake", "fjord", "misty-conifers", "forest-green",
          "lake-mist", "pine-rows", "wheat-field", "hills-mist"]
GOVERNANCE = ["governance-1", "governance-2", "governance-3", "governance-4"]

# Emplacement -> thème. « client_company » : photo de l'entreprise seulement.
PLACES = {
    "cover": "sector", "glance": "sector", "back": "sector",
    "cover_environment": "nature", "glance_environment": "nature", "focus": "nature",
    "cover_social": "people", "glance_social": "people",
    "glance_governance": "governance",
    "company_section": "client_company",
}

# Photos fournies par l'entreprise (report_photos) utilisables par thème.
CLIENT_SLOTS = {
    "sector": ("cover", "company"), "nature": ("environment",), "people": ("social",),
    "governance": ("governance",), "client_company": ("company",),
}

# Emplacements de chaque mise en page (report_designs, layout « cover » /
# « glance »), dans l'ordre où ils apparaissent dans le document.
COVER_PLACES = {"mosaic": ["cover", "cover_environment", "cover_social"]}
GLANCE_PLACES = {
    "terre": ["glance_environment", "glance_social"],
    "galerie": ["glance_environment", "glance_social", "glance_governance"],
}


def document_places(cover_layout: str, glance_layout: str) -> list[str]:
    """Emplacements photo d'un rapport PDF, par ordre de priorité : la section
    « L'entreprise en bref » d'abord (elle n'accepte QUE la photo de
    l'entreprise ; servie après la couverture, elle la perdait au profit de
    celle-ci), puis l'ordre du document."""
    return (["company_section"] + COVER_PLACES.get(cover_layout, ["cover"])
            + GLANCE_PLACES.get(glance_layout, ["glance"]) + ["focus", "back"])


def bank_pool(theme: str, family: str, design_photos: dict) -> list[str]:
    """Photos de la banque candidates pour un thème, par ordre de préférence."""
    if theme == "sector":
        own = ([f"sector-{family}", f"sector-{family}-2", f"sector-{family}-3"]
               if family != "general" else [design_photos["cover"]])
        return own + ["sector-general", "sector-general-2", "sector-general-3"]
    if theme == "nature":
        first = [design_photos.get("environment"), design_photos.get("cover")]
        return [n for n in dict.fromkeys(first + NATURE) if n]
    if theme == "people":
        return [f"people-{family}", "people-general", "people-general-2"]
    if theme == "governance":
        return list(GOVERNANCE)
    return []


def allocate(places, client_photos: dict, family: str, design_photos: dict, load) -> dict:
    """{emplacement: (origine, octets)} ; origine « client:<slot> » ou
    « bank:<nom> ». `load(nom)` lit une photo de la banque (None si absente).
    Un emplacement sans photo disponible est absent du résultat."""
    used, plan = set(), {}
    for place in places:
        theme = PLACES[place]
        candidates = [(f"client:{s}", client_photos.get(s)) for s in CLIENT_SLOTS[theme]]
        candidates += [(f"bank:{n}", None) for n in bank_pool(theme, family, design_photos)]
        for origin, raw in candidates:
            if origin in used:
                continue
            if origin.startswith("bank:"):
                raw = load(origin[5:])
            if raw:
                used.add(origin)
                plan[place] = (origin, raw)
                break
    return plan
