"""Gabarits éditoriaux des livrables : source unique de vérité du design.

Six gabarits, tirés des maquettes validées le 2026-09-23 (Aurora, Annuel,
Institutionnel, Portrait, Terre, Galerie). Chaque générateur — PDF, PPTX,
Word, synthèse une page, lettre de mission, graphiques — CONVERTIT ces
jetons dans son propre format ; aucun ne redéfinit une couleur de thème.

Jetons de couleur (hexadécimal, avec « # ») :
  paper      fond de page
  surface    fond des cartes / encarts
  panel      fond teinté des encadrés (citation, méthodologie)
  ink        texte principal
  muted      texte secondaire, légendes
  rule       filets fins
  primary    aplats sombres (bandeaux, tuile du score global)
  on_primary texte posé sur `primary`
  accent     chiffres clés, surtitres, filets d'accent
  accent_on_primary  accent lisible sur `primary`
  env / social / gov  couleurs sémantiques des piliers
  env_soft / social_soft / gov_soft  fonds teintés des piliers

Polices : familles embarquées dans assets/fonts (OFL), déclinées en
Light / Regular / SemiBold / Italic. `office_*` : polices système sûres pour
PPTX et Word, qui ne peuvent pas embarquer de TTF.

Photos : la banque locale (assets/photos) ne fournit que deux emplacements,
la couverture (reprise en quatrième de couverture et en bandeau) et
l'environnement (paysage, forêt : sujet cohérent avec le pilier). Les autres
emplacements (entreprise, social, gouvernance) ne montrent QUE des photos
fournies par l'entreprise ; à défaut, la page se compose sans photo
(typographie, pictogramme du pilier). Décision du 2026-09-24 : une photo
d'illustration sans rapport avec le sujet de la page (façade vitrée pour
« l'entreprise », champ de blé pour « social ») lisait comme aléatoire.
"""
from models import AestheticTheme

# Emplacements photo que l'entreprise peut renseigner elle-même
CLIENT_PHOTO_SLOTS = ("cover", "company", "environment", "social", "governance")
# Emplacements que la banque locale peut combler (cf. note ci-dessus)
BANK_SLOTS = ("cover", "environment")

DESIGNS: dict[AestheticTheme, dict] = {
    AestheticTheme.AURORA: {
        "label": {"fr": "Aurora", "en": "Aurora"},
        "tagline": {"fr": "Vert forêt sur ivoire, couverture photo scindée",
                    "en": "Forest green on ivory, split photo cover"},
        "colors": {
            "paper": "#F3F0E8", "surface": "#FBFAF6", "panel": "#E6E6DC",
            "ink": "#1E2B26", "muted": "#5F6B64", "rule": "#CBCDC1",
            "primary": "#1F3D33", "on_primary": "#F3F0E8",
            "accent": "#2E5A4B", "accent_on_primary": "#C9D8C5",
            "env": "#2F6B4F", "social": "#3D6A8A", "gov": "#6B5B86",
            "env_soft": "#E1E6DA", "social_soft": "#E0E5E8", "gov_soft": "#E6E2EA",
        },
        "fonts": {"display": "Newsreader", "body": "AlbertSans", "display_italic": False,
                  "display_weight": "Regular"},
        "office": {"display": "Georgia", "body": "Segoe UI"},
        "layout": {"cover": "split", "glance": "aurora", "header": "caps",
                   "kpi": "hairline", "radius": 0},
        "photos": {"cover": "mountain-lake", "environment": "lake-mist"},
    },
    AestheticTheme.ANNUEL: {
        "label": {"fr": "Annuel", "en": "Annual"},
        "tagline": {"fr": "Rapport annuel classique, italiques et doubles filets",
                    "en": "Classic annual report, italics and double rules"},
        "colors": {
            "paper": "#F7F3EA", "surface": "#FBF8F1", "panel": "#EFE7D6",
            "ink": "#2B2620", "muted": "#6D6457", "rule": "#CFC5B3",
            "primary": "#2B2620", "on_primary": "#F7F3EA",
            "accent": "#9A6418", "accent_on_primary": "#E4B572",
            "env": "#236436", "social": "#23588A", "gov": "#624581",
            "env_soft": "#E7E7D6", "social_soft": "#E4E4E0", "gov_soft": "#EAE3E2",
        },
        "fonts": {"display": "Newsreader", "body": "SourceSans3", "display_italic": True,
                  "display_weight": "Regular"},
        "office": {"display": "Georgia", "body": "Calibri"},
        "layout": {"cover": "editorial", "glance": "annuel", "header": "centered",
                   "kpi": "double_rule", "radius": 0},
        "photos": {"cover": "wheat-field", "environment": "hills-mist"},
    },
    AestheticTheme.INSTITUTIONNEL: {
        "label": {"fr": "Institutionnel", "en": "Institutional"},
        "tagline": {"fr": "Bleu nuit et corail, cartes arrondies",
                    "en": "Midnight blue and coral, rounded cards"},
        "colors": {
            "paper": "#EEF1F5", "surface": "#FFFFFF", "panel": "#E3E8EF",
            "ink": "#172A41", "muted": "#475366", "rule": "#C9D1DC",
            "primary": "#182E4B", "on_primary": "#FFFFFF",
            "accent": "#C55C43", "accent_on_primary": "#E77B60",
            "env": "#09672E", "social": "#0E5794", "gov": "#65418A",
            "env_soft": "#E6F1EA", "social_soft": "#E5EEF7", "gov_soft": "#EEE8F4",
        },
        "fonts": {"display": "InstrumentSerif", "body": "InstrumentSans",
                  "display_italic": False, "display_weight": "Regular"},
        "office": {"display": "Georgia", "body": "Segoe UI"},
        "layout": {"cover": "band", "glance": "institutionnel", "header": "monogram",
                   "kpi": "cards", "radius": 10},
        "photos": {"cover": "fjord", "environment": "alpine-lake"},
    },
    AestheticTheme.PORTRAIT: {
        "label": {"fr": "Portrait", "en": "Portrait"},
        "tagline": {"fr": "Grande photo pleine page et carte blanche",
                    "en": "Full-bleed photo with a white card"},
        "colors": {
            "paper": "#F4F2EE", "surface": "#FFFFFF", "panel": "#E9E6E0",
            "ink": "#23262B", "muted": "#6A6E75", "rule": "#DCD8D0",
            "primary": "#23262B", "on_primary": "#F4F2EE",
            "accent": "#7E5A42", "accent_on_primary": "#D8BFA8",
            "env": "#255940", "social": "#2E5072", "gov": "#56436C",
            "env_soft": "#E3E7E2", "social_soft": "#E2E6EA", "gov_soft": "#E7E3EA",
        },
        "fonts": {"display": "LibreCaslonText", "body": "HankenGrotesk",
                  "display_italic": False, "display_weight": "Regular"},
        "office": {"display": "Georgia", "body": "Segoe UI"},
        "layout": {"cover": "photo_card", "glance": "portrait", "header": "caps",
                   "kpi": "list", "radius": 0},
        "photos": {"cover": "forest-green", "environment": "misty-conifers"},
    },
    AestheticTheme.TERRE: {
        "label": {"fr": "Terre", "en": "Earth"},
        "tagline": {"fr": "Tons argile et sauge, tuiles photo par pilier",
                    "en": "Clay and sage tones, photo tiles per pillar"},
        "colors": {
            "paper": "#EFEAE1", "surface": "#F6F2EB", "panel": "#E5DED2",
            "ink": "#2A2723", "muted": "#6E675D", "rule": "#CFC7BA",
            "primary": "#3B342D", "on_primary": "#EFEAE1",
            "accent": "#89543C", "accent_on_primary": "#DDB79F",
            "env": "#39553F", "social": "#744029", "gov": "#554568",
            "env_soft": "#E3E5DC", "social_soft": "#EADFD3", "gov_soft": "#E4DFE6",
        },
        "fonts": {"display": "HankenGrotesk", "body": "HankenGrotesk",
                  "display_italic": False, "display_weight": "Light"},
        "office": {"display": "Segoe UI Light", "body": "Segoe UI"},
        "layout": {"cover": "duo", "glance": "terre", "header": "caps",
                   "kpi": "hairline", "radius": 3},
        "photos": {"cover": "hills-mist", "environment": "pine-rows"},
    },
    AestheticTheme.GALERIE: {
        "label": {"fr": "Galerie", "en": "Gallery"},
        "tagline": {"fr": "Blanc galerie, mosaïque photo et barres fines",
                    "en": "Gallery white, photo mosaic and thin bars"},
        "colors": {
            "paper": "#FBFBFA", "surface": "#FFFFFF", "panel": "#F0F1F1",
            "ink": "#1D2226", "muted": "#646B72", "rule": "#E4E6E8",
            "primary": "#1D2226", "on_primary": "#FBFBFA",
            "accent": "#255F62", "accent_on_primary": "#9CC7C6",
            "env": "#3D7055", "social": "#43668A", "gov": "#6C5984",
            "env_soft": "#E8EFEA", "social_soft": "#E8EDF2", "gov_soft": "#EEEBF1",
        },
        "fonts": {"display": "AlbertSans", "body": "AlbertSans",
                  "display_italic": False, "display_weight": "Light"},
        "office": {"display": "Segoe UI Light", "body": "Segoe UI"},
        "layout": {"cover": "mosaic", "glance": "galerie", "header": "plain",
                   "kpi": "hairline", "radius": 0},
        "photos": {"cover": "alpine-lake", "environment": "lake-mist"},
    },
}

DEFAULT_DESIGN = AestheticTheme.AURORA

# Anciens thèmes (avant le 2026-09-23) -> gabarit le plus proche. Les dossiers
# clients déjà enregistrés portent encore ces valeurs : elles restent lisibles.
LEGACY_THEMES = {
    "corporate_blue": AestheticTheme.INSTITUTIONNEL.value,
    "ocean_deep": AestheticTheme.INSTITUTIONNEL.value,
    "green_nature": AestheticTheme.AURORA.value,
    "dark_premium": AestheticTheme.PORTRAIT.value,
    "royal_purple": AestheticTheme.ANNUEL.value,
    "minimal_white": AestheticTheme.GALERIE.value,
    "sunset_terracotta": AestheticTheme.TERRE.value,
}


def design(theme) -> dict:
    """Gabarit d'un thème (valeur d'enum ou chaîne, anciennes valeurs admises)."""
    if not isinstance(theme, AestheticTheme):
        theme = AestheticTheme(LEGACY_THEMES.get(str(theme), str(theme)))
    return DESIGNS.get(theme, DESIGNS[DEFAULT_DESIGN])


def colors_of(theme) -> dict:
    return design(theme)["colors"]
