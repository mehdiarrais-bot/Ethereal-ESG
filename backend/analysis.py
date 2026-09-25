"""Analyse approfondie des piliers : constat, cause, conséquence, levier.

Là où narrative.py décrit (« la part d'énergie renouvelable atteint 8 %,
un niveau critique »), ce module explique : d'où vient le chiffre, ce qu'il
coûte ou expose, comment les indicateurs se répondent. Trois sources de
différenciation d'un dossier à l'autre :
  1. les ratios calculés à partir des données (part de chaque scope,
     émissions et énergie par salarié, départs, heures de formation…) ;
  2. les croisements entre indicateurs (rotation × formation, part
     renouvelable × poids du Scope 2, comité × vérification externe…) ;
  3. le contexte de la famille de secteurs (analysis_texts.SECTOR).

Déterministe et local. Les tranches viennent de bands.py (la grille même
du score) ; un indicateur absent n'est jamais commenté comme présent ; un
booléen inconnu (None) n'est jamais lu comme « non » (DETTE § 17).

Sortie : liste de Section (clé, titre, paragraphes), partagée par le PDF, le Word et les
notes de l'orateur du PowerPoint.
"""
from typing import NamedTuple

from analysis_texts import A, SECTOR, COUNTERS
from bands import classer
from esg_calculator import (MIXITE_EFFECTIF_REPERE, TF_NATIONAL_2024, carbon_thresholds_for)
from narrative import num, pct

_GOOD = {"exemplaire", "solide"}
_BAD = {"fragile", "critique"}

# Familles de secteurs : premier radical trouvé dans le libellé saisi
_FAMILIES = [
    ("transport", ("transport", "logisti")),
    ("construction", ("btp", "construction", "bâtiment", "travaux publics")),
    ("agro", ("agro", "agri", "alimentaire")),
    ("energie", ("énergie", "energie", "energy")),
    ("numerique", ("numérique", "numerique", "tech", "logiciel", "informatique", "télécom",
                   "telecom", "digital", "software")),
    ("commerce", ("commerce", "distribution", "retail", "négoce")),
    ("tourisme", ("tourisme", "hôtel", "hotel", "restauration", "hospitality")),
    ("industrie", ("industri", "manufactur", "automobile", "chimie", "pharma", "métallurg",
                   "plasturg")),
    ("services", ("service", "conseil", "finance", "assurance", "banque", "immobilier",
                  "consulting", "insurance")),
]


def family(sector: str | None) -> str:
    s = (sector or "").lower()
    for fam, keys in _FAMILIES:
        if any(k in s for k in keys):
            return fam
    return "general"


class _Ctx:
    """Données et outils de rédaction d'un dossier."""

    def __init__(self, request, scores):
        self.r, self.s = request, scores
        self.lang = "en" if request.language == "en" else "fr"
        self.t = A[self.lang]
        self.fam = family(request.company.sector)
        self.sec = SECTOR[self.fam][self.lang]
        self.env, self.soc, self.gov = request.environmental, request.social, request.governance
        self.staff = request.social.total_employees or None
        self.rev = request.company.revenue_eur or None

    def n(self, v, d=0):
        return num(v, self.lang, d)

    def p(self, v):
        return pct(v, self.lang)

    def band(self, key, v):
        return classer(key, v, self.r.company.sector) if v is not None else None

    def tranche(self, band, feminine=False):
        from narrative_texts import TRANCHES
        if self.lang == "en":
            return TRANCHES["en"][band]
        return TRANCHES["fr_f" if feminine else "fr"][band]

    def counter(self, key, n):
        zero, one, many = COUNTERS[self.lang][key]
        return one if n == 1 else many.format(n=self.n(n))

    def hours(self, h):
        return f"{self.n(h)} h"

    def ratio_decimals(self, v):
        return 0 if v >= 100 else (1 if v >= 1 else 2)


def _para(*parts) -> str:
    return " ".join(p for p in parts if p)


class Section(NamedTuple):
    key: str                 # ancre des illustrations (illustrations.ANCHORS)
    title: str
    paragraphs: list[str]


def _section(c, key, *paragraphs) -> Section:
    """Section `key` (titre A[lang]["t_" + key]) ; chaque paragraphe est une
    chaîne ou une liste de phrases à joindre ; les vides sont retirés."""
    paras = [_para(*p) if isinstance(p, (list, tuple)) else p for p in paragraphs]
    return Section(key, c.t["t_" + key], [p for p in paras if p])


# ── Environnement ─────────────────────────────────────────────────────────

def _scopes(c):
    return [(k, v) for k, v in (("1", c.env.scope1_emissions), ("2", c.env.scope2_emissions),
                                ("3", c.env.scope3_emissions)) if v is not None]


def _ghg_structure(c):
    known = _scopes(c)
    total = sum(v for _, v in known)
    if len(known) < 2 or not total:
        return None
    t = c.t
    ranked = sorted(known, key=lambda kv: -kv[1])
    parts = [t["ghg_part" if i == 0 else "ghg_part_next"].format(n=k, p=c.p(v / total * 100))
             for i, (k, v) in enumerate(ranked)]
    sep = " and " if c.lang == "en" else " et "
    split = t["ghg_split"].format(tot=c.n(total), parts=", ".join(parts[:-1]) + sep + parts[-1])
    dom = ranked[0][0]
    if dom == "1":
        head = t["s1_dom"].format(label=c.sec["label"], s1=c.sec["s1"])
        reading = [t["s1_csq"], c.sec["lever_s1"]]
    elif dom == "2":
        head = t["s2_dom"].format(label=c.sec["label"], s2=c.sec["s2"])
        reading = [t["s2_csq"]]
    else:
        head = t["s3_dom"].format(label=c.sec["label"], s3=c.sec["s3"])
        reading = [t["s3_csq"]]
    missing = ([t["s3_missing_intro"], c.sec["s3_missing"]]
               if c.env.scope3_emissions is None else "")
    return _section(c, "ghg", [split, head], reading, missing)


def _intensity(c):
    co2 = c.env.co2_emissions_tonnes
    if not co2 or not c.rev:
        return None
    t = c.t
    i = co2 / c.rev * 1e6
    band = c.band("co2_emissions_tonnes", round(i))
    if band is None:
        return None
    fact = t["int_fact"].format(co2=c.n(co2), i=c.n(i, 0 if i >= 10 else 1))
    if c.staff:
        e = co2 / c.staff
        fact += t["int_staff"].format(e=c.n(e, c.ratio_decimals(e)))
    _, sectoral = carbon_thresholds_for(c.r.company.sector)
    grid = (t["int_grid_sector"] if sectoral else t["int_grid_generic"]).format(
        label=c.sec["label"], t=c.tranche(band))
    reading = t["int_good"] if band in _GOOD else t["int_bad"] if band in _BAD else t["int_mid"]
    return _section(c, "int", [fact + ".", grid], reading)


def _energy(c):
    mwh, ren = c.env.energy_consumption_mwh, c.env.renewable_energy_percent
    if mwh is None and ren is None:
        return None
    t = c.t
    out: list[str] = []
    if mwh is not None:
        fact = t["en_fact"].format(mwh=c.n(mwh))
        if c.staff:
            r = mwh / c.staff
            fact += t["en_staff"].format(r=c.n(r, c.ratio_decimals(r)))
        if c.rev:
            x = mwh / c.rev * 1e6
            fact += t["en_rev"].format(x=c.n(x, c.ratio_decimals(x)))
        out.append(fact + ".")
    if ren is not None:
        band = c.band("renewable_energy_percent", ren)
        out.append(t["en_ren"].format(p=c.p(ren), t=c.tranche(band)))
        known = _scopes(c)
        total = sum(v for _, v in known)
        shares = {k: v / total * 100 for k, v in known} if total else {}
        dom = max(known, key=lambda kv: kv[1])[0] if len(known) >= 2 else None
        if ren >= 60 and dom == "1":
            out.append(t["en_ren_s1"])
        elif ren < 40 and shares.get("2", 0) >= 30:
            out.append(t["en_low_s2"].format(p=c.p(shares["2"])))
        elif ren < 40:
            out.append(t["en_low"])
        else:
            out.append(t["en_ok"])
    # Le principe sobriété > efficacité > verdissement ne s'illustre qu'avec
    # une consommation déclarée ; sans elle, il resterait une généralité.
    return _section(c, "energy", out,
                    [c.sec["energy"], t["en_order"] if mwh is not None else ""])


def _waste(c):
    wt, rec = c.env.waste_generated_tonnes, c.env.waste_recycled_percent
    if wt is None and rec is None:
        return None
    t = c.t
    out = []
    if wt is not None:
        fact = t["w_fact"].format(wt=c.n(wt))
        if c.staff:
            r = wt / c.staff
            fact += t["w_staff"].format(r=c.n(r, c.ratio_decimals(r)))
        out.append(fact + ".")
    out.append(t["w_streams"].format(label=c.sec["label"], w=c.sec["waste"]))
    reading = ""
    if rec is not None:
        band = c.band("waste_recycled_percent", rec)
        out.append(t["w_rec"].format(p=c.p(rec), t=c.tranche(band)))
        reading = t["w_good"] if band in _GOOD else t["w_bad"] if band in _BAD else t["w_mid"]
    return _section(c, "waste", out, reading)


def _water(c):
    w = c.env.water_consumption_m3
    if w is None:
        return None
    t = c.t
    fact = t["water_fact"].format(w=c.n(w))
    if c.staff:
        r = w / c.staff
        fact += t["water_staff"].format(r=c.n(r, c.ratio_decimals(r)))
    return _section(c, "water",
                    [fact + ".", t["water_use"].format(label=c.sec["label"], u=c.sec["water"])],
                    t["water_read"])


def _biodiversity(c):
    n = c.env.biodiversity_initiatives
    if n is None:
        return None
    t = c.t
    if n == 0:
        return _section(c, "bio", t["bio_zero"].format(label=c.sec["label"], b=c.sec["bio"]))
    band = c.band("biodiversity_initiatives", n)
    return _section(c, "bio", t["bio_some"].format(c=c.counter("biodiversity_initiatives", n),
                                                     t=c.tranche(band), label=c.sec["label"],
                                                     b=c.sec["bio"]))


_GAP_KEYS = {
    "env": ["co2_emissions_tonnes", "scope1_emissions", "scope2_emissions",
            "energy_consumption_mwh", "renewable_energy_percent", "waste_generated_tonnes",
            "water_consumption_m3"],
    "social": ["total_employees", "accident_frequency_rate", "employee_turnover_percent",
               "training_hours_per_employee", "female_employees_percent"],
    "gov": ["independent_board_percent", "female_board_percent", "esg_audit_conducted",
            "sustainability_committee"],
}


def _gaps(c, pillar):
    """Conséquence analytique de chaque donnée clé manquante (au moins deux)."""
    data = {}
    for part in (c.env, c.soc, c.gov):
        data.update(part.model_dump())
    missing = [k for k in _GAP_KEYS[pillar] if data.get(k) is None]
    if len(missing) < 2:
        return None
    t = c.t
    return _section(c, "gaps", [t["gaps_intro"], *(t["gap"][k] for k in missing)],
                    t["gaps_close"])


# ── Social ────────────────────────────────────────────────────────────────

def _safety(c):
    tf, acc = c.soc.accident_frequency_rate, c.soc.work_accidents
    if tf is None and acc is None:
        return None
    t = c.t
    out = []
    if tf is not None:
        r = tf / TF_NATIONAL_2024
        if r < 0.5:
            cmp = t["tf_cmp_half"]
        elif r < 0.9:
            cmp = t["tf_cmp_below"]
        elif r <= 1.1:
            cmp = t["tf_cmp_equal"]
        else:
            cmp = t["tf_cmp_times"].format(x=c.n(r, 1))
        out.append(t["tf_fact"].format(tf=c.n(tf, 1), cmp=cmp, nat=c.n(TF_NATIONAL_2024, 1)))
    if acc is not None:
        out.append(t["acc_zero"] if acc == 0 else t["acc_one"] if acc == 1
                   else t["acc_count"].format(n=c.n(acc)))
        if tf is None:
            out.append(t["acc_no_tf"])
    out.append(t["safety_ctx"].format(label=c.sec["label"], s=c.sec["safety"]))
    reading, crossed = "", []
    if tf is not None:
        if tf > TF_NATIONAL_2024:
            reading = t["tf_high"]
            to, h = c.soc.employee_turnover_percent, c.soc.training_hours_per_employee
            if to is not None and c.band("employee_turnover_percent", to) in _BAD:
                crossed.append(t["tf_turnover"].format(to=c.p(to)))
            if h is not None and c.band("training_hours_per_employee", h) in _BAD:
                crossed.append(t["tf_training"].format(h=c.hours(h)))
        elif c.band("accident_frequency_rate", tf) in _GOOD:
            reading = t["tf_low"]
        else:
            reading = t["tf_mid"]
    return _section(c, "safety", out, reading, crossed)


def _talent(c):
    to, h = c.soc.employee_turnover_percent, c.soc.training_hours_per_employee
    if to is None and h is None:
        return None
    t = c.t
    out = []
    if to is not None:
        if c.staff:
            out.append(t["to_fact"].format(to=c.p(to), dep=c.n(round(to / 100 * c.staff))))
        else:
            out.append(t["to_fact_nostaff"].format(to=c.p(to)))
    if h is not None:
        fact = t["tr_fact"].format(h=c.hours(h))
        if c.staff:
            fact += t["tr_total"].format(tot=c.n(round(h * c.staff, -1) if h * c.staff >= 100
                                                 else h * c.staff))
        out.append(fact + ".")
    facts, out = out, []
    bt = c.band("employee_turnover_percent", to)
    bh = c.band("training_hours_per_employee", h)
    if bt and bh:
        hi_to, lo_to = bt in _BAD, bt in _GOOD
        lo_tr, hi_tr = bh in _BAD, bh in _GOOD
        if hi_to and lo_tr:
            out.append(t["q_bad_bad"])
        elif hi_to and hi_tr:
            out.append(t["q_bad_good"])
        elif lo_to and lo_tr:
            out.append(t["q_good_bad"])
        elif lo_to and hi_tr:
            out.append(t["q_good_good"])
        elif hi_to:
            out.append(t["to_only_bad"])
        elif lo_tr:
            out.append(t["tr_only_bad"])
        else:
            out.append(t["q_mid"])
    elif bt:
        out.append(t["to_only_bad"] if bt in _BAD else t["to_only_good"] if bt in _GOOD else "")
    elif bh:
        out.append(t["tr_only_bad"] if bh in _BAD else t["tr_only_good"] if bh in _GOOD else "")
    if (bt in _BAD) or (bh in _BAD):
        out.append(t["talent_ctx"].format(label=c.sec["label"], t=c.sec["talent"]))
    return _section(c, "talent", facts, out)


def _mix(c):
    f = c.soc.female_employees_percent
    if f is None:
        return None
    t = c.t
    fact = t["mix_fact"].format(f=c.p(f))
    if c.staff:
        fact += t["mix_count"].format(n=c.n(round(f / 100 * c.staff)))
    head, reading, board = [fact + "."], [], ""
    if f < MIXITE_EFFECTIF_REPERE:
        head.append(t["mix_below"].format(rep=MIXITE_EFFECTIF_REPERE))
        reading = [c.sec["mix"] or t["mix_generic"], t["mix_csq"]]
    else:
        head.append(t["mix_above"].format(rep=MIXITE_EFFECTIF_REPERE))
    b = c.gov.female_board_percent
    if b is not None:
        if b >= f + 10:
            board = t["mix_board_up"].format(b=c.p(b))
        elif b <= f - 10:
            board = t["mix_board_down"].format(b=c.p(b))
    return _section(c, "mix", head, reading, board)


def _stakeholders(c):
    t, s = c.t, c.soc
    out: list[list[str]] = []
    if s.local_suppliers_percent is not None:
        out.append([t["local_fact"].format(p=c.p(s.local_suppliers_percent)),
                    t["local_high"] if s.local_suppliers_percent >= 50 else t["local_low"]])
    if s.community_investment_eur is not None:
        fact = t["comm_fact"].format(v=c.n(s.community_investment_eur))
        if c.staff:
            fact += t["comm_staff"].format(r=c.n(s.community_investment_eur / c.staff))
        out.append([fact + ".", t["comm_read"]])
    if s.customer_satisfaction_score is not None:
        band = c.band("customer_satisfaction_score", s.customer_satisfaction_score)
        out.append([t["sat_fact"].format(v=c.n(s.customer_satisfaction_score, 1),
                                         t=c.tranche(band)), t["sat_read"]])
    if s.disabled_employees_percent is not None:
        out.append([t["dis_fact"].format(p=c.p(s.disabled_employees_percent)), t["dis_read"]])
    return _section(c, "stake", *out) if out else None


# ── Gouvernance ───────────────────────────────────────────────────────────

def _steering(c):
    com, aud = c.gov.sustainability_committee, c.gov.esg_audit_conducted
    t = c.t
    if com is None and aud is None:
        return None
    if com is True and aud is True:
        text = t["st_both"]
    elif com is True and aud is False:
        text = t["st_comm_only"]
    elif com is False and aud is True:
        text = t["st_audit_only"]
    elif com is False and aud is False:
        text = t["st_none"]
    elif com is not None:   # vérification inconnue
        text = t["st_comm_only_partial"] if com else t["st_no_comm_partial"]
    else:                   # comité inconnu
        text = t["st_audit_partial"] if aud else t["st_no_audit_partial"]
    return _section(c, "steer", text)


def _board(c):
    g, t = c.gov, c.t
    n = g.board_members
    if not n:
        return None
    parts = [_seats(c, t[key], n, share) for key, share in
             (("board_ind", g.independent_board_percent), ("board_fem", g.female_board_percent))
             if share is not None]
    joint = (" including " if c.lang == "en" else ", dont ")
    sep = " and " if c.lang == "en" else " et "
    fact = t["board_fact"].format(n=c.n(n)) + (joint + sep.join(parts) if parts else "") + "."
    size = t["board_small"] if n < 5 else t["board_large"] if n > 12 else t["board_mid"]
    bi = c.band("independent_board_percent", g.independent_board_percent)
    ind = t["ind_low"] if bi in _BAD else t["ind_high"] if bi in _GOOD else ""
    return _section(c, "board", [fact, size], ind)


def _seats(c, forms, n, share):
    """« environ 2 indépendants (33 %) » : sièges déduits de la part saisie,
    « environ » seulement si le produit n'est pas entier."""
    exact = n * share / 100
    k = round(exact)
    about = c.t["about"] if abs(exact - k) > 0.05 else ""
    zero, one, many = forms
    return (zero if k == 0 else one if k == 1 else many).format(a=about, k=c.n(k), p=c.p(share))


def _integrity(c):
    g, t = c.gov, c.t
    vals = {k: getattr(g, k) for k in ("ethics_violations", "corruption_cases", "data_breaches")}
    known = {k: v for k, v in vals.items() if v is not None}
    if not known:
        return None
    if len(known) == 3 and not any(known.values()):
        return _section(c, "integrity", t["int_all_zero"])
    out = []
    tmpl = {"corruption_cases": "cor_some", "ethics_violations": "eth_some",
            "data_breaches": "brc_some"}
    for k in ("corruption_cases", "ethics_violations", "data_breaches"):
        v = known.get(k)
        if v:
            out.append(t[tmpl[k]].format(c=c.counter(k, v)))
    if not out:
        return None
    return _section(c, "integrity", *out)


def _budget(c):
    b, t = c.gov.csr_budget_eur, c.t
    if b is None:
        return None
    fact = t["bud_fact"].format(v=c.n(b))
    if c.staff:
        fact += t["bud_staff"].format(r=c.n(b / c.staff))
    if c.rev:
        share = b / c.rev * 100
        fact += t["bud_rev"].format(p=(f"{c.n(share, 2)} %" if c.lang == "fr" else f"{c.n(share, 2)}%"))
    out = [fact + ".", t["bud_read"]]
    rated = {k: v for k, v in (("env", c.s.environmental_score), ("social", c.s.social_score),
                               ("gov", c.s.governance_score)) if v is not None}
    if len(rated) >= 2:
        from narrative_texts import T
        low = min(rated, key=lambda k: rated[k])
        out.append(t["bud_focus"].format(p=T[c.lang]["pillar_names"][low]))
    return _section(c, "budget", out)


_SECTIONS = {
    "env": [_ghg_structure, _intensity, _energy, _waste, _water, _biodiversity],
    "social": [_safety, _talent, _mix, _stakeholders],
    "gov": [_steering, _board, _integrity, _budget],
}


def pillar_analysis(request, scores, pillar: str) -> list[Section]:
    """Sections (clé, titre, paragraphes) de l'analyse approfondie d'un pilier.
    Liste vide si aucune donnée du pilier ne permet de raisonner."""
    c = _Ctx(request, scores)
    out = [sec for fn in _SECTIONS[pillar] if (sec := fn(c))]
    gaps = _gaps(c, pillar)
    if gaps and out:
        out.append(gaps)
    return out


def analysis_title(request, pillar: str) -> str:
    return A["en" if request.language == "en" else "fr"]["title"][pillar]
