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
        "caveat_one": " Cet objectif est celui que l'entreprise a communiqué : ce rapport le "
                      "documente sans évaluer son alignement sur une trajectoire de référence.",
        "caveat_many": " Ces objectifs sont ceux que l'entreprise a communiqués : ce rapport les "
                       "documente sans évaluer leur alignement sur une trajectoire de référence.",
        "esrs": " La norme ESRS E1-4 demande de publier si et comment des cibles de réduction ont "
                "été fixées : la cible ci-dessus en constitue la déclaration.",
        "row_note": "Cible déclarée : −{r} entre {b} et {t} ({scopes})",
        "wp": "Trajectoire climat déclarée par l'entreprise : {r} de réduction des émissions entre "
              "{b} et {t} ({scopes}).",
        "esrs_absent": " La norme ESRS E1-4 demande de publier si et comment des cibles de réduction "
                       "des émissions ont été fixées — leur absence, documentée comme telle, relève de "
                       "cette même exigence de transparence.",
    },
    "en": {
        "declared": "{n} reports a target to reduce its greenhouse gas emissions by {r} between "
                    "{b} and {t} ({scopes}), an average annual decrease equivalent to {pace} of "
                    "{b} emissions.",
        "tonnes": " Applied to the {b} inventory, the target corresponds to about {tt} t CO₂e in {t}.",
        "caveat_one": " This is the target communicated by the company: this report documents it "
                      "without assessing its alignment with a reference pathway.",
        "caveat_many": " These are the targets communicated by the company: this report documents "
                       "them without assessing their alignment with a reference pathway.",
        "esrs": " ESRS E1-4 requires disclosing whether and how reduction targets have been set: "
                "the target above constitutes that disclosure.",
        "row_note": "Reported target: −{r} between {b} and {t} ({scopes})",
        "wp": "Climate pathway reported by the company: {r} emissions reduction between {b} and "
              "{t} ({scopes}).",
        "esrs_absent": " ESRS E1-4 requires disclosing whether and how emissions reduction targets "
                       "have been set — their absence, documented as such, falls under that same "
                       "transparency requirement.",
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


# ── Lot 2 : cibles par indicateur, à l'horizon company.target_year ────────

@dataclass
class IndicatorTarget:
    key: str                  # champ de TargetsData
    pillar: str
    target: float
    current: float | None     # valeur de l'exercice, si renseignée
    lower_is_better: bool

    @property
    def reached(self) -> bool:
        if self.current is None:
            return False
        return self.current <= self.target if self.lower_is_better else self.current >= self.target

    @property
    def gap(self) -> float | None:
        """Chemin restant, toujours positif ; None si non calculable ou atteint."""
        if self.current is None or self.reached:
            return None
        return abs(self.target - self.current)


# champ cible -> (section, champ mesuré, pilier, plus bas = mieux)
INDICATEURS = {
    "renewable_target_percent": ("environmental", "renewable_energy_percent", "env", False),
    "female_employees_target_percent": ("social", "female_employees_percent", "social", False),
    "training_hours_target": ("social", "training_hours_per_employee", "social", False),
    "accident_rate_target": ("social", "accident_frequency_rate", "social", True),
}

LIBELLES = {
    "fr": {"renewable_target_percent": "part d'énergie renouvelable",
           "female_employees_target_percent": "part de femmes dans l'effectif",
           "training_hours_target": "heures de formation par salarié",
           "accident_rate_target": "taux de fréquence des accidents du travail"},
    "en": {"renewable_target_percent": "share of renewable energy",
           "female_employees_target_percent": "share of women in the workforce",
           "training_hours_target": "training hours per employee",
           "accident_rate_target": "workplace accident frequency rate"},
}

TI = {
    "fr": {"item": "{label} : {t} ({etat})", "now": "{c} sur l'exercice",
           "gap_up": "{c} sur l'exercice, soit {d} à gagner d'ici {h}",
           "gap_down": "{c} sur l'exercice, soit {d} de baisse à obtenir d'ici {h}",
           "reached": "{c} sur l'exercice : cible déjà atteinte",
           "unknown": "valeur de l'exercice non renseignée",
           "intro": "Cibles déclarées par l'entreprise à horizon {h} : ",
           "no_climate": "Aucune trajectoire de réduction des émissions n'a été communiquée. ",
           "pillar": "L'entreprise s'est fixé, à horizon {h}, les cibles suivantes : {items}.",
           "rest": " Les autres objectifs chiffrés restent à définir."},
    "en": {"item": "{label}: {t} ({etat})", "now": "{c} this year",
           "gap_up": "{c} this year, i.e. {d} to gain by {h}",
           "gap_down": "{c} this year, i.e. a reduction of {d} to achieve by {h}",
           "reached": "{c} this year: target already met",
           "unknown": "value for the year not reported",
           "intro": "Targets reported by the company for {h}: ",
           "no_climate": "No emissions reduction pathway has been disclosed. ",
           "pillar": "The company has set itself the following targets for {h}: {items}.",
           "rest": " Other quantified targets remain to be defined."},
}


def indicator_targets(request, pillar: str | None = None) -> list[IndicatorTarget]:
    t = getattr(request, "targets", None)
    out = []
    for key, (section, field, pil, lower) in INDICATEURS.items():
        value = getattr(t, key, None) if t is not None else None
        if value is None or (pillar and pil != pillar):
            continue
        current = getattr(getattr(request, section), field)
        out.append(IndicatorTarget(key, pil, value, current, lower))
    return out


def fmt_value(key: str, v: float, lang: str) -> str:
    """Même unité que la saisie : %, heures, taux sans unité."""
    if key.endswith("_percent"):
        return pct(v, lang)
    if key == "training_hours_target":
        return f"{num(v, lang, 0 if v == int(v) else 1)} h"
    return num(v, lang, 1)


def _gap(key: str, d: float, lang: str) -> str:
    if key.endswith("_percent"):
        return f"{num(d, lang, 0 if d == int(d) else 1)} points"
    return fmt_value(key, d, lang)


def _item(request, it: IndicatorTarget) -> str:
    lang, x = request.language, TI[request.language]
    h = request.company.target_year
    if it.current is None:
        etat = x["unknown"]
    else:
        c = fmt_value(it.key, it.current, lang)
        if it.reached:
            etat = x["reached"].format(c=c)
        else:
            gap = it.gap
            assert gap is not None
            etat = x["gap_down" if it.lower_is_better else "gap_up"].format(
                c=c, d=_gap(it.key, gap, lang), h=h)
    return x["item"].format(label=LIBELLES[lang][it.key], t=fmt_value(it.key, it.target, lang), etat=etat)


def indicators_sentence(request, pillar: str | None = None) -> str | None:
    items = [_item(request, it) for it in indicator_targets(request, pillar)]
    if not items:
        return None
    x = TI[request.language]
    if pillar:
        return x["pillar"].format(h=request.company.target_year, items=" ; ".join(items)
                                  if request.language == "fr" else "; ".join(items))
    sep = " ; " if request.language == "fr" else "; "
    return x["intro"].format(h=request.company.target_year) + sep.join(items) + "."


def targets_paragraph(request) -> str | None:
    """Texte « Objectifs » dès qu'une cible est déclarée ; None sinon (le
    constat d'absence de content_generator reste alors le bon texte)."""
    c = climate_target(request)
    ind = indicators_sentence(request)
    if c is None and ind is None:
        return None
    x, lang = T[request.language], request.language
    if c is not None:
        f = _fields(request, c)
        out = x["declared"].format(**f)
        if c.target_tonnes is not None:
            out += x["tonnes"].format(tt=num(c.target_tonnes, lang), **f)
    else:
        out = TI[lang]["no_climate"].rstrip()
    if ind:
        out += " " + ind
    n = (c is not None) + len(indicator_targets(request))
    out += x["caveat_one" if n == 1 else "caveat_many"]
    return out + (x["esrs"] if c is not None else x["esrs_absent"])


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
    ind = indicators_sentence(request)
    if c is None and ind is None:
        return None
    lang = request.language
    parts = [T[lang]["wp"].format(**_fields(request, c))] if c is not None else [TI[lang]["no_climate"].strip()]
    if ind:
        parts.append(ind)
    return " ".join(parts) + TI[lang]["rest"]


# ── Recommandations : la cible du client remplace l'objectif proposé ──────
# Sans elle, l'outil propose un objectif (« 50 % d'énergie renouvelable ») ;
# avec elle, le proposer contredirait l'entreprise.
REC_CIBLE = {"renewable": "renewable_target_percent", "parity": "female_employees_target_percent",
             "training": "training_hours_target"}

TR = {
    "fr": {"renewable": ("Atteindre la cible de {t} d'énergie renouvelable fixée pour {h}",
                         "Maintenir la part d'énergie renouvelable au-dessus de la cible de {t} fixée pour {h}"),
           "parity": ("Atteindre la cible de {t} de femmes dans l'effectif fixée pour {h}",
                      "Maintenir la part de femmes au-dessus de la cible de {t} fixée pour {h}"),
           "training": ("Atteindre la cible de {t} de formation par salarié fixée pour {h}",
                        "Maintenir la formation au-dessus de la cible de {t} par salarié fixée pour {h}"),
           "objective": "Cible de l'entreprise : {t} en {h}",
           "weak_goal": "cible de l'entreprise : {t} en {h}"},
    "en": {"renewable": ("Reach the {t} renewable-energy target set for {h}",
                         "Keep the renewable-energy share above the {t} target set for {h}"),
           "parity": ("Reach the target of {t} women in the workforce set for {h}",
                      "Keep the share of women above the {t} target set for {h}"),
           "training": ("Reach the target of {t} of training per employee set for {h}",
                        "Keep training above the {t} per-employee target set for {h}"),
           "objective": "Company target: {t} by {h}",
           "weak_goal": "company target: {t} by {h}"},
}


def _cible_de(request, rec_key: str) -> IndicatorTarget | None:
    field = REC_CIBLE.get(rec_key)
    return next((it for it in indicator_targets(request) if it.key == field), None)


def recommendation_title(request, rec_key: str, lang: str) -> str | None:
    it = _cible_de(request, rec_key)
    if it is None:
        return None
    atteindre, maintenir = TR[lang][rec_key]
    return (maintenir if it.reached else atteindre).format(
        t=fmt_value(it.key, it.target, lang), h=request.company.target_year)


def recommendation_objective(request, rec_key: str, lang: str) -> str | None:
    it = _cible_de(request, rec_key)
    if it is None:
        return None
    return TR[lang]["objective"].format(t=fmt_value(it.key, it.target, lang), h=request.company.target_year)


def goals(request) -> dict[str, str]:
    """Textes que esg_calculator substitue à ses objectifs proposés."""
    lang = request.language
    out = {k: v for k in REC_CIBLE if (v := recommendation_title(request, k, lang))}
    it = _cible_de(request, "renewable")
    if it is not None:
        out["renewable_weak"] = TR[lang]["weak_goal"].format(
            t=fmt_value(it.key, it.target, lang), h=request.company.target_year)
    return out
