"""Objectifs déclarés par le client (DETTE § 0bis, étape B).

Une cible n'existe pour les livrables que COMPLÈTE : réduction, année de
référence et année cible. Une saisie partielle est traitée comme absente —
jamais complétée par une valeur par défaut (le « -42 % à 2030 » inventé,
supprimé le 2026-09-03, en était une).

Tout ce qui sort d'ici est arithmétique sur les chiffres saisis : aucune
affirmation d'alignement (1,5 °C, SBTi, ESRS) — règle 9 de CLAUDE.md.
"""
from dataclasses import dataclass

from narrative import num, pct

SCOPES = {"fr": {"1-2": "scopes 1 et 2", "1-2-3": "scopes 1, 2 et 3", None: "périmètre non précisé"},
          "en": {"1-2": "Scopes 1 and 2", "1-2-3": "Scopes 1, 2 and 3", None: "scope not specified"}}

T = {
    "fr": {
        "declared": "{n} déclare un objectif de réduction de ses émissions de gaz à effet de serre "
                    "de {r} entre {b} et {t} ({scopes}), soit une baisse moyenne équivalente à {pace} "
                    "des émissions de {b} chaque année.",
        "tonnes": " Rapportée au bilan {b}, la cible correspond à environ {tt} t CO₂e en {t}.",
        "caveat": " Cet objectif est celui que l'entreprise a communiqué : ce rapport le documente "
                  "sans évaluer son alignement sur une trajectoire de référence.",
        "esrs": " La norme ESRS E1-4 demande de publier si et comment des cibles de réduction ont "
                "été fixées : la cible ci-dessus en constitue la déclaration.",
        "row_note": "Cible déclarée : −{r} entre {b} et {t} ({scopes})",
        "wp": "Trajectoire climat déclarée par l'entreprise : {r} de réduction des émissions entre "
              "{b} et {t} ({scopes}). Les autres objectifs chiffrés restent à définir.",
    },
    "en": {
        "declared": "{n} reports a target to reduce its greenhouse gas emissions by {r} between "
                    "{b} and {t} ({scopes}), an average annual decrease equivalent to {pace} of "
                    "{b} emissions.",
        "tonnes": " Applied to the {b} inventory, the target corresponds to about {tt} t CO₂e in {t}.",
        "caveat": " This is the target communicated by the company: this report documents it "
                  "without assessing its alignment with a reference pathway.",
        "esrs": " ESRS E1-4 requires disclosing whether and how reduction targets have been set: "
                "the target above constitutes that disclosure.",
        "row_note": "Reported target: −{r} between {b} and {t} ({scopes})",
        "wp": "Climate pathway reported by the company: {r} emissions reduction between {b} and "
              "{t} ({scopes}). Other quantified targets remain to be defined.",
    },
}


@dataclass
class ClimateTarget:
    reduction: float          # % de réduction visé
    base_year: int
    target_year: int
    scopes: str | None        # "1-2", "1-2-3" ou None (non précisé)
    base_tonnes: float | None  # émissions de l'année de référence, si connues

    @property
    def annual_pace(self) -> float:
        """Baisse linéaire moyenne, en % des émissions de l'année de référence."""
        return self.reduction / (self.target_year - self.base_year)

    @property
    def target_tonnes(self) -> float | None:
        return None if self.base_tonnes is None else self.base_tonnes * (1 - self.reduction / 100)


def _base_tonnes(request, scopes: str | None) -> float | None:
    """Émissions de l'année de référence, seulement si c'est l'exercice du
    rapport (l'outil ne connaît pas les bilans antérieurs) et si le
    périmètre de la cible est couvert par le bilan saisi."""
    t = request.targets
    if t.climate_base_year != request.company.reporting_year:
        return None
    e = request.environmental
    if scopes == "1-2" and e.scope1_emissions is not None and e.scope2_emissions is not None:
        return e.scope1_emissions + e.scope2_emissions
    if scopes == "1-2-3":
        parts = (e.scope1_emissions, e.scope2_emissions, e.scope3_emissions)
        if all(p is not None for p in parts):
            return sum(p for p in parts if p is not None)
    return None


def climate_target(request) -> ClimateTarget | None:
    t = getattr(request, "targets", None)
    if t is None or None in (t.climate_reduction_percent, t.climate_base_year, t.climate_target_year):
        return None
    return ClimateTarget(t.climate_reduction_percent, t.climate_base_year, t.climate_target_year,
                         t.climate_scopes, _base_tonnes(request, t.climate_scopes))


def _pct1(v: float, lang: str) -> str:
    """Pourcentage à une décimale : « 4,2 % » / « 4.2% »."""
    return f"{num(v, lang, 1)}%" if lang == "en" else f"{num(v, lang, 1)} %"


def _fields(request, c: ClimateTarget) -> dict:
    lang = request.language
    return dict(n=request.company.name, r=pct(c.reduction, lang), b=c.base_year, t=c.target_year,
                scopes=SCOPES[lang][c.scopes], pace=_pct1(c.annual_pace, lang))


def targets_paragraph(request) -> str | None:
    """Texte « Objectifs » quand une cible climat est déclarée ; None sinon."""
    c = climate_target(request)
    if c is None:
        return None
    x, f = T[request.language], _fields(request, c)
    out = x["declared"].format(**f)
    if c.target_tonnes is not None:
        out += x["tonnes"].format(tt=num(c.target_tonnes, request.language), **f)
    return out + x["caveat"] + x["esrs"]


def compliance_note(request) -> tuple[str, str] | None:
    """Constat FR/EN de la ligne ESRS E1-4 quand une cible est déclarée."""
    c = climate_target(request)
    if c is None:
        return None
    notes = []
    for lang in ("fr", "en"):
        f = _fields(request.model_copy(update={"language": lang}), c)
        notes.append(T[lang]["row_note"].format(**f))
    return notes[0], notes[1]


def white_paper_sentence(request) -> str | None:
    c = climate_target(request)
    return None if c is None else T[request.language]["wp"].format(**_fields(request, c))
