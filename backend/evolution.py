"""Évolution d'un exercice à l'autre, indicateur par indicateur (DETTE § 0).

Compare les indicateurs saisis de l'exercice courant à ceux de l'exercice
précédent conservés dans le dossier (`request.previous_data`). Le sens d'une
évolution (« en progrès » / « en recul ») se lit dans `bands` — `SEUILS[..]
["sens"]` pour les grilles, type « compteur_penalite » de `CATEGORIES` pour
les compteurs — jamais dans une liste parallèle. Un indicateur sans sens
défini (consommation d'eau, effectif…) est décrit sans jugement : sa
variation peut tenir à l'activité autant qu'à la performance.

Tout est arithmétique sur les deux valeurs saisies : l'invariant du banc
`evolution_citee_exacte` vérifie chaque variation imprimée.
"""
from dataclasses import dataclass

from bands import SEUILS, CATEGORIES, PLUS_HAUT_MIEUX, PLUS_BAS_MIEUX
from narrative import num, pct
from narrative_texts import LABELS

SECTIONS = ("environmental", "social", "governance")
# Relatif sous lequel une variation est lue comme stable (arrondis de saisie).
STABLE = 0.005
NBSP = " "     # l'unité ne se sépare jamais de son nombre en fin de ligne
INTENSITE = "carbon_intensity"   # t CO₂e / M€ : comparable malgré la variation d'activité

T = {
    "fr": {"title": "Évolution depuis l'exercice {y}",
           "intro": "Par rapport à l'exercice {y}, {n} indicateurs sont comparables : {parts}.",
           "parts": {"up": ("{k} en progrès", "{k} en progrès"), "down": ("{k} en recul", "{k} en recul"),
                     "flat": ("{k} stable", "{k} stables"),
                     "neutral": ("{k} sans sens de lecture défini", "{k} sans sens de lecture défini")},
           "intro_one": "Par rapport à l'exercice {y}, un seul indicateur est comparable.",
           "main": " Principales évolutions : {items}.",
           "item": "{label} de {a} à {b} ({d})",
           "new": " Renseignés cette année seulement : {items}.",
           "gone": " Renseignés en {y} mais plus cette année : {items}.",
           "none": "Aucun indicateur n'est renseigné sur les deux exercices : l'évolution depuis {y} "
                   "ne peut pas être lue indicateur par indicateur.",
           "up": "en progrès", "down": "en recul", "flat": "stable", "neutral": "—",
           "yes": "oui", "no": "non", "intensity": "intensité carbone (t CO₂e / M€)",
           "cols": ("Indicateur", "{p}", "{c}", "Variation", "Lecture")},
    "en": {"title": "Change since fiscal year {y}",
           "intro": "Versus fiscal year {y}, {n} indicators are comparable: {parts}.",
           "parts": {"up": ("{k} improving", "{k} improving"), "down": ("{k} deteriorating", "{k} deteriorating"),
                     "flat": ("{k} stable", "{k} stable"),
                     "neutral": ("{k} with no defined direction", "{k} with no defined direction")},
           "intro_one": "Versus fiscal year {y}, only one indicator is comparable.",
           "main": " Main changes: {items}.",
           "item": "{label} from {a} to {b} ({d})",
           "new": " Reported this year only: {items}.",
           "gone": " Reported in {y} but no longer this year: {items}.",
           "none": "No indicator is reported for both years: the change since {y} cannot be read "
                   "indicator by indicator.",
           "up": "improving", "down": "deteriorating", "flat": "stable", "neutral": "—",
           "yes": "yes", "no": "no", "intensity": "carbon intensity (t CO₂e / €m)",
           "cols": ("Indicator", "{p}", "{c}", "Change", "Reading")},
}


@dataclass
class Change:
    field: str
    prev: float | bool
    cur: float | bool
    sens: str | None          # PLUS_HAUT_MIEUX / PLUS_BAS_MIEUX / None

    @property
    def delta(self) -> float | None:
        if isinstance(self.cur, bool) or isinstance(self.prev, bool):
            return None
        return self.cur - self.prev

    @property
    def reading(self) -> str:
        """« up », « down », « flat » ou « neutral »."""
        if isinstance(self.cur, bool):
            return "flat" if self.cur == self.prev else ("up" if self.cur else "down")
        d = self.delta or 0.0
        if abs(d) <= STABLE * max(abs(self.prev), 1e-9):
            return "flat"
        if self.sens is None:
            return "neutral"
        better = d > 0 if self.sens == PLUS_HAUT_MIEUX else d < 0
        return "up" if better else "down"


def _sens(field: str) -> str | None:
    if field in SEUILS:
        return SEUILS[field].get("sens")
    if CATEGORIES.get(field, {}).get("type") == "compteur_penalite":
        return PLUS_BAS_MIEUX
    return None


def _fields() -> list[str]:
    """Indicateurs comparables : tous ceux que le libellé et bands connaissent."""
    return [f for f in LABELS["fr"] if f in SEUILS or f in CATEGORIES]


def _value(data, field: str):
    for sec in SECTIONS:
        part = getattr(data, sec)
        if field in type(part).model_fields:
            return getattr(part, field)
    return None


def _intensity(co2, revenue):
    return co2 / revenue * 1e6 if co2 and revenue else None


def changes(request) -> tuple[list[Change], list[str], list[str]] | None:
    """(variations, apparus, disparus) ; None sans exercice précédent conservé."""
    p = getattr(request, "previous_data", None)
    if p is None:
        return None
    out, new, gone = [], [], []
    for f in _fields():
        before, now = _value(p, f), _value(request, f)
        if f == "co2_emissions_tonnes":
            # Tonnes : l'activité pèse autant que la performance. L'intensité,
            # quand elle est calculable les deux années, porte le sens de bands.
            ib = _intensity(before, p.revenue_eur)
            ia = _intensity(now, request.company.revenue_eur)
            if ib is not None and ia is not None:
                out.append(Change(INTENSITE, ib, ia, PLUS_BAS_MIEUX))
            if before is not None and now is not None:
                out.append(Change(f, before, now, None))
                continue
        if before is not None and now is not None:
            out.append(Change(f, before, now, _sens(f)))
        elif now is not None:
            new.append(f)
        elif before is not None:
            gone.append(f)
    return out, new, gone


def label(field: str, lang: str) -> str:
    if field == INTENSITE:
        return T[lang]["intensity"]
    return LABELS[lang][field]


ARTICLES = ("les ", "la ", "le ", "l'", "the ")


def table_label(field: str, lang: str) -> str:
    """Libellé de tableau : sans article, capitalisé (« Part d'énergie… »)."""
    s = label(field, lang)
    for a in ARTICLES:
        if s.startswith(a):
            s = s[len(a):]
            break
    return s[:1].upper() + s[1:]


UNITES = {"co2_emissions_tonnes": "t", "scope1_emissions": "t", "scope2_emissions": "t",
          "scope3_emissions": "t", "waste_generated_tonnes": "t", "energy_consumption_mwh": "MWh",
          "water_consumption_m3": "m³", "training_hours_per_employee": "h"}


def _n(v: float, lang: str) -> str:
    """Entier si la valeur l'est, sinon une décimale."""
    return num(v, lang, 0 if float(v).is_integer() else 1)


def fmt(field: str, v, lang: str) -> str:
    if isinstance(v, bool):
        return T[lang]["yes" if v else "no"]
    if field.endswith("_percent"):
        return f"{_n(v, lang)}%" if lang == "en" else f"{_n(v, lang)} %"
    if field.endswith("_eur"):
        return f"{num(v, lang)}{NBSP}€"
    unit = UNITES.get(field)
    return f"{_n(v, lang)}{NBSP}{unit}" if unit else _n(v, lang)


def fmt_delta(c: Change, lang: str) -> str:
    d = c.delta
    if d is None:
        return "—"
    # Trait d'union, pas « − » (U+2212) : hors du sous-ensemble des polices PDF.
    sign = "+" if d > 0 else "-" if d < 0 else ""
    if c.field.endswith("_percent"):
        return f"{sign}{_n(abs(d), lang)}{NBSP}{'pt' if abs(d) <= 1 else 'pts'}"
    return sign + fmt(c.field, abs(d), lang)


def _item(c: Change, lang: str) -> str:
    # « de … à … », pas « → » : la flèche est hors du sous-ensemble des polices PDF.
    return T[lang]["item"].format(label=label(c.field, lang), a=fmt(c.field, c.prev, lang),
                                  b=fmt(c.field, c.cur, lang), d=fmt_delta(c, lang))


def paragraph(request) -> str | None:
    res = changes(request)
    if res is None:
        return None
    ch, new, gone = res
    lang, x = request.language, T[request.language]
    y = request.previous_data.year
    if not ch:
        return x["none"].format(y=y)
    counts = {r: sum(1 for c in ch if c.reading == r) for r in ("up", "down", "flat", "neutral")}
    parts = ", ".join(x["parts"][r][k > 1].format(k=k) for r, k in counts.items() if k)
    out = (x["intro_one"].format(y=y) if len(ch) == 1 else
           x["intro"].format(y=y, n=len(ch), parts=parts))
    moved = sorted((c for c in ch if c.reading in ("up", "down")),
                   key=lambda c: -abs((c.delta or 0) / (abs(c.prev) or 1)))[:4]
    sep = " ; " if lang == "fr" else "; "
    if moved:
        out += x["main"].format(items=sep.join(_item(c, lang) for c in moved))
    if new:
        out += x["new"].format(items=", ".join(label(f, lang) for f in new))
    if gone:
        out += x["gone"].format(y=y, items=", ".join(label(f, lang) for f in gone))
    return out


def table(request) -> list[tuple[str, str, str, str, str]] | None:
    """En-tête + une ligne par indicateur comparable ; None sans comparaison."""
    res = changes(request)
    if not res or not res[0]:
        return None
    lang, x = request.language, T[request.language]
    head = tuple(c.format(p=request.previous_data.year, c=request.company.reporting_year)
                 for c in x["cols"])
    rows = [(table_label(c.field, lang), fmt(c.field, c.prev, lang),
             fmt(c.field, c.cur, lang), fmt_delta(c, lang), x[c.reading]) for c in res[0]]
    return [head] + rows


def title(request) -> str | None:
    p = getattr(request, "previous_data", None)
    return None if p is None else T[request.language]["title"].format(y=p.year)
