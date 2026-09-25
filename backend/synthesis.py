"""Diagnostic d'ensemble et conclusion propres au dossier.

Repère dans les données les enjeux (fragilités) et les points d'appui,
les classe par gravité, en tire le profil de l'entreprise, les liens entre
piliers, ce qui se passerait « si rien ne change » d'ici l'horizon fixé, et
les actions des 90 premiers jours. Tout vient des indicateurs saisis, des
tranches de bands.py et du contexte sectoriel (analysis_texts.SECTOR).

La gravité est une échelle interne de hiérarchisation (écart à la grille ou
à la référence nationale), jamais imprimée comme une note.
"""
from dataclasses import dataclass

from analysis import _Ctx, _scopes, _BAD, _GOOD
from esg_calculator import MIXITE_EFFECTIF_REPERE, TF_NATIONAL_2024
from narrative import completeness
from synthesis_texts import ISSUES, STRENGTHS, LINKS, T

TOP = 3                 # enjeux développés dans le diagnostic et la conclusion
MIX_ALERTE = 25         # en dessous : la mixité devient un enjeu majeur (tranche fragile)


@dataclass
class Issue:
    key: str
    pillar: str
    severity: float
    title: str
    name: str
    cause: str
    csq: str
    horizon: str
    action: str


@dataclass
class Strength:
    key: str
    pillar: str
    title: str
    name: str
    text: str


# ── Détection des enjeux ──────────────────────────────────────────────────

def _issue(c, key, pillar, severity, fields=None, **overrides) -> Issue:
    x = ISSUES[c.lang][key]
    f = fields or {}
    val = {k: (overrides.get(k) or x.get(k, "")).format(**f)
           for k in ("title", "name", "cause", "csq", "horizon", "action")}
    return Issue(key, pillar, severity, **val)


def _social_issues(c) -> list[Issue]:
    s, out = c.soc, []
    x = ISSUES[c.lang]
    tf, to, h, f = (s.accident_frequency_rate, s.employee_turnover_percent,
                    s.training_hours_per_employee, s.female_employees_percent)
    bt, bh = c.band("employee_turnover_percent", to), c.band("training_hours_per_employee", h)
    if tf is not None and tf > TF_NATIONAL_2024:
        turn = x["safety"]["turnover"].format(to=c.p(to)) if bt in _BAD else ""
        out.append(_issue(c, "safety", "social", 2 + min(2.0, (tf - TF_NATIONAL_2024) / 16),
                          dict(r=c.n(tf / TF_NATIONAL_2024, 1), tf=c.n(tf, 1),
                               label=c.sec["label"], safety=c.sec["safety"], turnover=turn)))
    if bt in _BAD:
        dep = (x["retention"]["departures"].format(dep=c.n(round(to / 100 * c.staff)))
               if c.staff else "")
        train = (x["retention"]["training_low"] if bh in _BAD else
                 x["retention"]["training_high"] if bh in _GOOD else "").format(h=c.hours(h or 0))
        out.append(_issue(c, "retention", "social", 1.5 + (0.5 if bt == "critique" else 0),
                          dict(to=c.p(to), departures=dep, label=c.sec["label"],
                               talent=c.sec["talent"], training=train)))
    if bh in _BAD:
        out.append(_issue(c, "skills", "social", 1.2 + (0.3 if bh == "critique" else 0),
                          dict(h=c.hours(h), label=c.sec["label"], talent=c.sec["talent"])))
    if f is not None and f < MIX_ALERTE:
        ctx = c.sec["mix"] or x["mix"]["generic"]
        out.append(_issue(c, "mix", "social", 1.4 if f < 15 else 1.0,
                          dict(f=c.p(f), context=ctx)))
    return out


def _env_issues(c) -> list[Issue]:
    e, out = c.env, []
    x = ISSUES[c.lang]
    known = _scopes(c)
    total = sum(v for _, v in known)
    shares = {k: v / total * 100 for k, v in known} if total else {}
    dom = max(known, key=lambda kv: kv[1])[0] if len(known) >= 2 else None
    if e.co2_emissions_tonnes and c.rev:
        i = e.co2_emissions_tonnes / c.rev * 1e6
        band = c.band("co2_emissions_tonnes", round(i))
        if band in _BAD:
            domin = x["carbon_intensity"]["dominant"].format(n=dom, p=c.p(shares[dom])) if dom else ""
            out.append(_issue(c, "carbon_intensity", "env", 3.0 if band == "critique" else 2.5,
                              dict(i=c.n(i), t=c.tranche(band), label=c.sec["label"],
                                   dominant=domin)))
    if not e.co2_emissions_tonnes and not known:
        out.append(_issue(c, "carbon_unmeasured", "env", 2.0))
    elif e.scope3_emissions is None and known:
        out.append(_issue(c, "scope3", "env", 1.4,
                          dict(s3_missing=c.sec["s3_missing"], s3=c.sec["s3"])))
    ren = e.renewable_energy_percent
    if c.band("renewable_energy_percent", ren) in _BAD:
        scope = (x["renewable"]["scope2"].format(p2=c.p(shares["2"])) if shares.get("2", 0) >= 30
                 else x["renewable"]["scope1"] if dom == "1" else "")
        out.append(_issue(c, "renewable", "env", 1.0 + shares.get("2", 0) / 50,
                          dict(p=c.p(ren), scope=scope)))
    rec = e.waste_recycled_percent
    if c.band("waste_recycled_percent", rec) in _BAD:
        out.append(_issue(c, "waste", "env", 0.9,
                          dict(p=c.p(rec), label=c.sec["label"], waste=c.sec["waste"])))
    return out


def _gov_issues(c) -> list[Issue]:
    g, out = c.gov, []
    x = ISSUES[c.lang]
    com, aud = g.sustainability_committee, g.esg_audit_conducted
    s = x["steering"]
    if com is False and aud is False:
        out.append(_issue(c, "steering", "gov", 1.8, title=s["title_both"], cause=s["cause_both"],
                          csq=s["csq_both"],
                          action=s["action_committee"] + " " + s["action_audit"]))
    elif com is False:
        out.append(_issue(c, "steering", "gov", 1.1, title=s["title_committee"],
                          cause=s["cause_committee"], csq=s["csq_committee"],
                          action=s["action_committee"]))
    elif aud is False:
        out.append(_issue(c, "steering", "gov", 1.1, title=s["title_audit"],
                          cause=s["cause_audit"], csq=s["csq_audit"], action=s["action_audit"]))
    if c.band("independent_board_percent", g.independent_board_percent) in _BAD:
        out.append(_issue(c, "independence", "gov", 1.1, dict(p=c.p(g.independent_board_percent))))
    counts = {k: getattr(g, k) or 0 for k in ("corruption_cases", "data_breaches",
                                              "ethics_violations")}
    if any(counts.values()):
        i = x["integrity"]
        csq, sev = [], 0.0
        if counts["corruption_cases"]:
            csq.append(i["csq_corruption"])
            sev = 3.5
        if counts["data_breaches"]:
            core = i["core"].format(label=c.sec["label"]) if c.fam == "numerique" else ""
            csq.append(i["csq_breach"].format(core=core))
            sev = max(sev, 2.2 if c.fam == "numerique" else 1.6)
        if counts["ethics_violations"]:
            csq.append(i["csq_ethics"])
            sev = max(sev, 1.4)
        listed = [c.counter(k, n) for k, n in counts.items() if n]
        sep = " ; " if c.lang == "fr" else "; "
        out.append(_issue(c, "integrity", "gov", sev, dict(counts=sep.join(listed)),
                          csq=" ".join(csq)))
    return out


def issues(request, scores) -> list[Issue]:
    """Enjeux du dossier, du plus grave au moins grave."""
    c = _Ctx(request, scores)
    found = _env_issues(c) + _social_issues(c) + _gov_issues(c)
    return sorted(found, key=lambda i: -i.severity)


# ── Points d'appui ────────────────────────────────────────────────────────

def strengths(request, scores) -> list[Strength]:
    c = _Ctx(request, scores)
    S = STRENGTHS[c.lang]
    e, s, g = c.env, c.soc, c.gov
    out = []

    def add(key, pillar, **f):
        title, name, text = S[key]
        out.append(Strength(key, pillar, title.format(**f), name, text))

    if e.co2_emissions_tonnes and c.rev:
        band = c.band("co2_emissions_tonnes", round(e.co2_emissions_tonnes / c.rev * 1e6))
        if band in _GOOD:
            add("intensity_good", "env", t=c.tranche(band))
    tf = s.accident_frequency_rate
    if c.band("accident_frequency_rate", tf) in _GOOD:
        add("safety_good", "social", tf=c.n(tf or 0, 1))
    if g.sustainability_committee is True and g.esg_audit_conducted is True:
        add("steering_good", "gov")
    if c.band("renewable_energy_percent", e.renewable_energy_percent) in _GOOD:
        add("renewable_good", "env", p=c.p(e.renewable_energy_percent))
    if c.band("employee_turnover_percent", s.employee_turnover_percent) in _GOOD:
        add("retention_good", "social", to=c.p(s.employee_turnover_percent))
    if c.band("training_hours_per_employee", s.training_hours_per_employee) in _GOOD:
        add("training_good", "social", h=c.hours(s.training_hours_per_employee))
    if s.female_employees_percent is not None and s.female_employees_percent >= MIXITE_EFFECTIF_REPERE:
        add("mix_good", "social", f=c.p(s.female_employees_percent))
    if c.band("independent_board_percent", g.independent_board_percent) in _GOOD:
        add("independence_good", "gov", p=c.p(g.independent_board_percent))
    counts = [g.ethics_violations, g.corruption_cases, g.data_breaches]
    if all(v is not None for v in counts) and not any(counts):
        add("integrity_clean", "gov")
    return out


# ── Liens entre piliers ───────────────────────────────────────────────────

def links(request, scores, found=None, sts=None) -> list[str]:
    c = _Ctx(request, scores)
    L = LINKS[c.lang]
    found = found if found is not None else issues(request, scores)
    sts = sts if sts is not None else strengths(request, scores)
    I = {i.key for i in found}
    S = {s.key for s in sts}
    g = c.gov
    out = []
    if "safety" in I and g.sustainability_committee is False:
        out.append(L["safety_steering"])
    if "safety" in I and "skills" in I:
        out.append(L["safety_skills"])
    if I & {"carbon_intensity", "renewable", "scope3"} and g.esg_audit_conducted is False:
        out.append(L["climate_audit"])
    if {"retention", "mix"} <= I:
        out.append(L["retention_mix"])
    if {"retention", "skills"} <= I:
        out.append(L["retention_skills"])
    if "steering_good" in S and found and found[0].severity >= 2:
        out.append(L["steering_ready"].format(name=found[0].name))
    if "intensity_good" in S and "scope3" in I:
        out.append(L["intensity_scope3"])
    capex = request.taxonomy.capex_aligned_percent if request.taxonomy else None
    if capex is not None and capex >= 20 and I & {"carbon_intensity", "renewable"}:
        out.append(L["capex_climate"].format(p=c.p(capex)))
    return out


# ── Sorties ───────────────────────────────────────────────────────────────

def _lower_first(s: str) -> str:
    """Titre repris en milieu de phrase : « Une sinistralité… » → « une… »."""
    return s[:1].lower() + s[1:] if s[1:2].islower() or s[1:2] == " " else s


def lead(text: str, min_len: int = 80) -> str:
    """Premières phrases d'un paragraphe, jusqu'à au moins `min_len` caractères."""
    out = ""
    for sentence in text.split(". "):
        out = f"{out}. {sentence}" if out else sentence
        if len(out) >= min_len:
            break
    return out.rstrip(".") + "."


def _elided(request, block: dict) -> dict:
    """« de Acme » → « d'Acme » dans toutes les chaînes (content_generator.elider)."""
    from content_generator import elider
    nom = request.company.name

    def fix(v):
        if isinstance(v, str):
            return elider(v, nom)
        if isinstance(v, list):
            return [fix(x) for x in v]
        return v
    return {k: fix(v) for k, v in block.items()}


def _count(forms, n, c):
    zero, one, many = forms
    return zero if n == 0 else one if n == 1 else many.format(n=c.n(n))


def _join(items, c):
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + (" and " if c.lang == "en" else " et ") + items[-1]


def overview(request, scores) -> dict:
    """{"title", "profile_title", "profile": [§], "issues_title", "issues_intro",
    "issues": [Issue], "links_title", "links": [§]}."""
    c = _Ctx(request, scores)
    t = T[c.lang]
    found, sts = issues(request, scores), strengths(request, scores)
    profile = [t["profile_counts"].format(name=request.company.name,
                                          ni=_count(t["n_issue"], len(found), c),
                                          ns=_count(t["n_strength"], len(sts), c))]
    if not found:
        profile[0] += " " + t["no_issue"]
    else:
        weight: dict[str, float] = {}
        for i in found:
            weight[i.pillar] = weight.get(i.pillar, 0) + i.severity
        main = max(weight, key=lambda p: weight[p])
        if weight[main] / sum(weight.values()) >= 0.6:
            names = [i.name for i in found if i.pillar == main]
            profile[0] += " " + t["concentrated"].format(p=t["pillars"][main],
                                                         names=_join(names, c))
        else:
            profile[0] += " " + t["spread"].format(names=_join([i.name for i in found[:4]], c))
    if sts:
        profile.append(t["strengths"].format(names=_join([s.name for s in sts[:4]], c)))
    filled, total = completeness(request)
    if filled / total < 0.5:
        profile.append(t["partial"].format(filled=filled, total=total))
    return _elided(request, {"title": t["overview"], "profile_title": t["profile_title"],
                             "profile": profile,
            "issues_title": t["issues_title"], "issues_intro": t["issues_intro"],
            "cause_label": t["cause_label"], "csq_label": t["csq_label"],
            "issues": found[:TOP], "links_title": t["links_title"],
            "links": links(request, scores, found, sts)})


def closing(request, scores) -> dict:
    """Conclusion propre au dossier : ce que nous retenons, si rien ne change,
    les 90 premiers jours."""
    c = _Ctx(request, scores)
    t = T[c.lang]
    found, sts = issues(request, scores), strengths(request, scores)
    lk = links(request, scores, found, sts)
    retain = []
    if sts:
        retain.append(t["retain_strength"].format(title=_lower_first(sts[0].title),
                                                  text=sts[0].text))
    if found:
        retain.append(t["retain_issue"].format(title=_lower_first(found[0].title),
                                               csq=lead(found[0].csq)))
    if lk:
        retain.append(t["retain_link"].format(text=lk[0]))
    ty = max(request.company.target_year, request.company.reporting_year + 1)
    horizon = ([t["horizon_intro"]] + [t["horizon_one"].format(name=i.name, text=i.horizon)
                                       for i in found[:TOP]]) if found else []
    return _elided(request, {"retain_title": t["retain_title"], "retain": retain,
            "horizon_title": t["horizon_title"].format(ty=ty), "horizon": horizon,
            "first_title": t["first_title"],
            "first_intro": t["first_intro"] if found else t["first_none"],
            "first": [i.action for i in found[:TOP]]})
