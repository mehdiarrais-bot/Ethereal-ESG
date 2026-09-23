"""Texte analytique du rapport PDF, composé à partir des données saisies.

Complète la rédaction de content_generator (synthèse, piliers, analyses) par
le texte qui manquait aux pages du rapport : présentation de l'entreprise et
du périmètre, lecture indicateur par indicateur, lecture de l'empreinte
carbone, introductions des chapitres, des tableaux et du plan d'action.

Les phrases vivent dans narrative_texts.py ; les tranches de lecture viennent
de bands.py (la grille même du score) ; ce module ne fait que sélectionner,
calculer des ratios et remplir. Aucune donnée absente n'est commentée comme
présente : un indicateur manquant est listé comme tel.
"""
from bands import classer
from narrative_texts import T, READINGS, LABELS, TRANCHES, COUNTS

# Indicateurs suivis par pilier (champs du modèle ESGRequest)
FIELDS = {
    "env": ["co2_emissions_tonnes", "scope1_emissions", "scope2_emissions", "scope3_emissions",
            "energy_consumption_mwh", "renewable_energy_percent", "water_consumption_m3",
            "waste_generated_tonnes", "waste_recycled_percent", "biodiversity_initiatives"],
    "social": ["total_employees", "female_employees_percent", "employee_turnover_percent",
               "training_hours_per_employee", "work_accidents", "accident_frequency_rate",
               "community_investment_eur", "local_suppliers_percent", "customer_satisfaction_score",
               "disabled_employees_percent"],
    "gov": ["board_members", "female_board_percent", "independent_board_percent",
            "ethics_violations", "corruption_cases", "data_breaches", "csr_budget_eur",
            "esg_audit_conducted", "sustainability_committee"],
}
# Indicateurs classés par bands.py, dans l'ordre de lecture
_GRADED = {
    "env": ["co2_emissions_tonnes", "renewable_energy_percent", "waste_recycled_percent",
            "biodiversity_initiatives"],
    "social": ["female_employees_percent", "training_hours_per_employee", "accident_frequency_rate",
               "employee_turnover_percent", "customer_satisfaction_score"],
    "gov": ["independent_board_percent", "female_board_percent", "csr_budget_eur"],
}
_PERCENT = {"renewable_energy_percent", "waste_recycled_percent", "female_employees_percent",
            "employee_turnover_percent", "female_board_percent", "independent_board_percent",
            "disabled_employees_percent", "local_suppliers_percent"}


# ── Mise en forme ─────────────────────────────────────────────────────────

def num(v: float, lang: str, decimals: int = 0) -> str:
    s = f"{v:,.{decimals}f}"
    return s if lang == "en" else s.replace(",", " ").replace(".", ",")


def pct(v: float, lang: str) -> str:
    return f"{num(v, lang)}%" if lang == "en" else f"{num(v, lang)} %"


def count(lang: str, key: str, n: int) -> str:
    zero, one, many = COUNTS[lang][key]
    return (zero if n == 0 else one if n == 1 else many).format(n=n)


def _join(items: list[str], lang: str) -> str:
    if len(items) <= 1:
        return "".join(items)
    last = " and " if lang == "en" else " et "
    return ", ".join(items[:-1]) + last + items[-1]


def _sector(sector: str) -> str:
    """Minuscule initiale pour un libellé cité en milieu de phrase
    (« Industrie manufacturière » -> « industrie manufacturière ») ; sigles
    et noms propres (deuxième lettre majuscule, chiffre…) laissés tels quels."""
    s = (sector or "").strip()
    return s[:1].lower() + s[1:] if len(s) > 1 and s[1:2].islower() else s


def _data(request) -> dict:
    d = {}
    for part in (request.environmental, request.social, request.governance):
        d.update(part.model_dump())
    return d


# ── Présentation et périmètre ─────────────────────────────────────────────

def completeness(request) -> tuple[int, int]:
    d = _data(request)
    fields = [f for fs in FIELDS.values() for f in fs]
    return sum(1 for f in fields if d.get(f) is not None), len(fields)


def company_paragraphs(request, ref: str) -> list[str]:
    lang, t, c = request.language, T[request.language], request.company
    staff = request.social.total_employees
    parts = {
        "staff": t["intro_staff"].format(v=num(staff, lang)) if staff else "",
        "revenue": "",
    }
    if c.revenue_eur:
        parts["revenue"] = t["intro_revenue"].format(
            sep=t["sep_and"] if staff else t["sep_none"],
            v=num(c.revenue_eur / 1e6, lang, 1 if c.revenue_eur < 1e7 else 0))
    if not staff and not c.revenue_eur:
        parts["staff"] = t["intro_none"]
    intro = t["intro"].format(n=c.name, an=c.reporting_year, sector=_sector(c.sector),
                              country=c.country, **parts)
    filled, total = completeness(request)
    ratio = filled / total
    reading = t["coverage_high"] if ratio >= 0.75 else (t["coverage_mid"] if ratio >= 0.45
                                                         else t["coverage_low"])
    coverage = t["coverage"].format(total=total, filled=filled, pct=pct(ratio * 100, lang),
                                    completeness_reading=reading)
    ty = max(c.target_year, c.reporting_year + 1)
    return [intro, coverage, t["structure"].format(ref=ref) + " " + t["horizon"].format(ty=ty)]


# ── Lecture des piliers ───────────────────────────────────────────────────

def _graded_value(key, d, request):
    if key == "co2_emissions_tonnes":
        rev = request.company.revenue_eur
        return round(d[key] / rev * 1e6) if d.get(key) and rev else None
    return d.get(key)


def _fmt(key, v, lang):
    if key in _PERCENT:
        return pct(v, lang)
    if key == "training_hours_per_employee":
        return f"{num(v, lang)} h"
    if key == "accident_frequency_rate":
        return num(v, lang, 1)
    if key == "customer_satisfaction_score":
        return num(v, lang, 1)
    return num(v, lang)


def indicator_readings(request, pillar: str) -> list[str]:
    """Une phrase par indicateur renseigné et classé par la grille du score."""
    lang, d = request.language, _data(request)
    out = []
    for key in _GRADED[pillar]:
        v = _graded_value(key, d, request)
        band = classer(key, v, request.company.sector) if v is not None else None
        if band is None:
            continue
        out.append(READINGS[lang][key].format(
            v=_fmt(key, v, lang), t=TRANCHES[lang][band],
            tf=TRANCHES["fr_f" if lang == "fr" else lang][band],
            ta=TRANCHES["en_a"][band]))
    return out


def score_position(request, scores, pillar: str) -> str:
    t = T[request.language]
    s = {"env": scores.environmental_score, "social": scores.social_score,
         "gov": scores.governance_score}[pillar]
    diff = round(s - scores.total_esg_score)
    name = t["pillar_names"][pillar]
    if diff == 0:
        return t["score_eq"].format(s=f"{s:.0f}", p=name)
    return t["score_pos"].format(s=f"{s:.0f}", p=name, d=abs(diff),
                                 dir=t["above"] if diff > 0 else t["below"],
                                 t=f"{scores.total_esg_score:.0f}")


def missing_sentence(request, pillar: str) -> str:
    lang, d = request.language, _data(request)
    missing = [LABELS[lang][f] for f in FIELDS[pillar] if d.get(f) is None]
    if not missing:
        return T[lang]["all_filled"]
    return T[lang]["missing"].format(items=_join(missing, lang))


def _facts_env(request) -> list[str]:
    lang, t, env = request.language, T[request.language], request.environmental
    staff = request.social.total_employees
    out = []
    if env.energy_consumption_mwh is not None and staff:
        out.append(t["energy_per_employee"].format(
            v=num(env.energy_consumption_mwh, lang),
            r=num(env.energy_consumption_mwh / staff, lang, 1)))
    if env.water_consumption_m3 is not None:
        out.append(t["water"].format(v=num(env.water_consumption_m3, lang)))
    return out


def _facts_social(request) -> list[str]:
    lang, t, soc = request.language, T[request.language], request.social
    out = []
    if soc.total_employees:
        out.append(t["staff"].format(v=num(soc.total_employees, lang)))
    if soc.work_accidents is not None:
        out.append(t["accidents_zero"] if soc.work_accidents == 0
                   else t["accidents_count"].format(v=num(soc.work_accidents, lang)))
    if soc.disabled_employees_percent is not None:
        out.append(t["disabled"].format(v=pct(soc.disabled_employees_percent, lang)))
    if soc.local_suppliers_percent is not None:
        out.append(t["local"].format(v=pct(soc.local_suppliers_percent, lang)))
    if soc.community_investment_eur is not None:
        out.append(t["community"].format(v=num(soc.community_investment_eur, lang)))
    return out


def _counter(t, key, n, lang):
    if n == 0:
        return t["counter_zero"][key]
    if n == 1:
        return t["counter_one"][key]
    return t["counter_many"][key].format(v=num(n, lang))


def _facts_gov(request) -> list[str]:
    lang, t, gov = request.language, T[request.language], request.governance
    out = []
    if gov.board_members:
        out.append(t["board"].format(v=gov.board_members))
    if gov.sustainability_committee is not None:
        out.append(t["committee_yes" if gov.sustainability_committee else "committee_no"])
    if gov.esg_audit_conducted is not None:
        out.append(t["audit_yes" if gov.esg_audit_conducted else "audit_no"])
    for key in ("ethics_violations", "corruption_cases", "data_breaches"):
        n = getattr(gov, key, None)
        if n is not None:
            out.append(_counter(t, key, n, lang))
    return out


_FACTS = {"env": _facts_env, "social": _facts_social, "gov": _facts_gov}


def pillar_paragraphs(request, scores, pillar: str) -> list[str]:
    """Deux paragraphes : lecture chiffrée, puis faits et données manquantes."""
    first = " ".join([score_position(request, scores, pillar)]
                     + indicator_readings(request, pillar))
    second = " ".join(_FACTS[pillar](request) + [missing_sentence(request, pillar)])
    return [first, second]


def levers_sentence(request, recs, pillar: str) -> str:
    """Renvoi du pilier vers les recommandations du plan d'action qui le visent."""
    t = T[request.language]
    mine = [r for r in recs if r.get("pillar") == pillar]
    if not mine:
        return t["levers_none"]
    items = [t["lever_item"].format(title=_sector(r["title"]),
                                    objective=_sector(r.get("objective") or "—"),
                                    horizon=_sector(r.get("horizon") or "—")) for r in mine]
    key = "levers_one" if len(items) == 1 else "levers_many"
    return t[key].format(n=len(items), items="; ".join(items))


def ghg_paragraph(request) -> str | None:
    lang, t, env = request.language, T[request.language], request.environmental
    scopes = [("Scope 1", env.scope1_emissions), ("Scope 2", env.scope2_emissions),
              ("Scope 3", env.scope3_emissions)]
    known = [(n, v) for n, v in scopes if v is not None]
    if not known:
        return None
    total = sum(v for _, v in known)
    out = [t["ghg_total"].format(v=num(total, lang))]
    if total and len(known) > 1:
        name, v = max(known, key=lambda x: x[1])
        out.append(t["ghg_dominant"].format(scope=name, p=pct(v / total * 100, lang)))
    if env.scope3_emissions is None:
        out.append(t["ghg_scope3_missing"])
    staff = request.social.total_employees
    if staff and total:
        out.append(t["ghg_per_employee"].format(v=num(total / staff, lang, 1)))
    return " ".join(out)


# ── Chapitres, tableaux, plan d'action ────────────────────────────────────

def _gap_counts(gaps):
    ok = sum(1 for g in gaps if g["status"] == "ok")
    open_ = sum(1 for g in gaps if g["status"] in ("no", "partial"))
    return ok, open_


def act1_intro(request, scores, gaps, risks) -> str:
    lang = request.language
    _, open_ = _gap_counts(gaps)
    p1 = sum(1 for r in risks if r.get("priority") == "P1")
    return T[lang]["act1_intro"].format(
        ns=count(lang, "strength", len(scores.strengths)),
        nw=count(lang, "weak", len(scores.weaknesses)),
        ng=count(lang, "req", len(gaps)), nopen=count(lang, "req_open", open_),
        nr=count(lang, "risk", len(risks)), np1=count(lang, "p1", p1))


def act2_intro(request, recs, roadmap) -> str:
    lang, c = request.language, request.company
    nq = sum(1 for ph in roadmap for a in ph["actions"] if a["quick_win"])
    return T[lang]["act2_intro"].format(
        nrec=count(lang, "rec", len(recs)), nq=count(lang, "quick", nq),
        ty=max(c.target_year, c.reporting_year + 1))


def act1_figures(request, scores, gaps, risks) -> list[tuple[str, str]]:
    f = T[request.language]["act_figures"]
    _, open_ = _gap_counts(gaps)
    return [(str(len(scores.strengths)), f["strengths"]), (str(len(scores.weaknesses)), f["weak"]),
            (str(open_), f["gaps"]), (str(len(risks)), f["risks"])]


def act2_figures(request, recs, roadmap) -> list[tuple[str, str]]:
    f = T[request.language]["act_figures"]
    c = request.company
    nq = sum(1 for ph in roadmap for a in ph["actions"] if a["quick_win"])
    return [(str(len(recs)), f["recs"]), (str(nq), f["quick"]), ("3", f["phases"]),
            (str(max(c.target_year, c.reporting_year + 1)), f["horizon"])]


def gaps_intro(request, gaps, ref: str) -> str:
    lang = request.language
    ok, open_ = _gap_counts(gaps)
    return T[lang]["gaps_intro"].format(ng=count(lang, "req", len(gaps)), ref=ref,
                                        nok=count(lang, "req_ok", ok),
                                        nopen=count(lang, "req_open_long", open_))


def risks_intro(request, risks) -> str:
    lang = request.language
    p1 = sum(1 for r in risks if r.get("priority") == "P1")
    return T[lang]["risks_intro"].format(nr=count(lang, "risk", len(risks)),
                                         np1=count(lang, "p1_long", p1))


def bench_intro(request) -> str:
    return T[request.language]["bench_intro"]


def recs_intro(request, recs) -> str:
    by = {p: sum(1 for r in recs if r["pillar"] == p) for p in ("env", "social", "gov")}
    return T[request.language]["recs_intro"].format(ne=by["env"], nso=by["social"], ngv=by["gov"])


def roadmap_intro(request, roadmap) -> str:
    t = T[request.language]
    phases = [t["roadmap_phase"].format(label=ph["label"],
                                        n=count(request.language, "action", len(ph["actions"])))
              for ph in roadmap if ph["actions"]]
    sentence = t["roadmap_intro"].format(phases=_join(phases, request.language) + ".")
    if any(a["quick_win"] for ph in roadmap for a in ph["actions"]):
        sentence += " " + t["roadmap_quick"]
    return sentence
