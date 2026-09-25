"""Deuxième série d'illustrations (lot 4), dessinées depuis les données.

Mêmes règles que illustrations.py : chaque figure représente des chiffres
ou des constats du dossier, aux couleurs du gabarit ; aucune n'apparaît
sans la donnée qui la fonde ; aucune valeur inventée (un scope non mesuré
est signalé sans taille, les 90 premiers jours ne reçoivent pas de dates).
"""
import textwrap

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

from analysis_texts import ILLU
from bands import SEUILS
from esg_calculator import MIXITE_EFFECTIF_REPERE
from illustrations import _png, _lang
from narrative import num, pct, FIELDS, _data

_SOCIAL_BANDS = {k: SEUILS[k]["bornes"] for k in ("training_hours_per_employee",
                                                   "employee_turnover_percent")}


def _wrap(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(text, width))


def _box(ax, x, y, w, h, fill, edge=None, radius=0.08, lw: float = 0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                                facecolor=fill, edgecolor=edge or fill, linewidth=lw))


def _canvas(w, h, bg):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=bg)
    ax.set_facecolor(bg)
    ax.axis("off")
    return fig, ax


# ── Carte des enjeux et points d'appui ────────────────────────────────────

def issue_map(request, scores, colors) -> bytes | None:
    import synthesis as SY
    found, sts = SY.issues(request, scores), SY.strengths(request, scores)
    if not found and not sts:
        return None
    L = ILLU[_lang(request)]
    cols = {p: ([i.name for i in found if i.pillar == p], [s.name for s in sts if s.pillar == p])
            for p in ("env", "social", "gov")}
    rows = max(len(a) + len(b) for a, b in cols.values()) or 1
    bg = colors["bg"]
    fig, ax = _canvas(7.6, 0.72 * rows + 1.4, bg)
    for j, (p, (iss, stg)) in enumerate(cols.items()):
        x = j * 3.4
        ax.text(x + 1.55, rows + 0.55, L["pillar_names"][p].upper(), ha="center", va="center",
                fontsize=9, color=colors[p], fontweight="bold")
        items = [(n, False) for n in iss] + [(n, True) for n in stg]
        for r, (name, strong) in enumerate(items):
            y = rows - 1 - r
            fill = colors[p] if strong else colors[f"{p}_soft"]
            _box(ax, x, y + 0.08, 3.1, 0.78, fill, edge=colors[p], lw=0 if strong else 1.2)
            ax.text(x + 1.55, y + 0.47, _wrap(name[:1].upper() + name[1:], 30), ha="center",
                    va="center", fontsize=8, color=bg if strong else colors["text"])
        if not items:
            ax.text(x + 1.55, rows - 0.55, L["map_none"], ha="center", color=colors["secondary"])
    # légende
    _box(ax, 0, -0.75, 0.35, 0.3, colors["social_soft"], edge=colors["social"], lw=1.2)
    ax.text(0.45, -0.6, L["map_issue"], va="center", fontsize=8, color=colors["text"])
    _box(ax, 1.9, -0.75, 0.35, 0.3, colors["social"])
    ax.text(2.35, -0.6, L["map_strength"], va="center", fontsize=8, color=colors["text"])
    ax.set_xlim(-0.1, 10.1)
    ax.set_ylim(-0.95, rows + 0.9)
    return _png(fig, bg)


# ── Chaîne du premier enjeu ───────────────────────────────────────────────

def _first_sentence(text: str) -> str:
    return text.split(". ")[0].rstrip(".") + "."


def chain(request, scores, colors) -> bytes | None:
    import synthesis as SY
    found = SY.issues(request, scores)
    if not found:
        return None
    i, L = found[0], ILLU[_lang(request)]
    from synthesis import lead
    texts = [i.title, _first_sentence(i.cause), lead(i.csq, 90), _first_sentence(i.action)]
    wrapped = [_wrap(t, 27) for t in texts]
    lines = max(w.count("\n") + 1 for w in wrapped)
    h = 0.26 * lines + 0.9
    bg, col, soft = colors["bg"], colors[i.pillar], colors[f"{i.pillar}_soft"]
    fig, ax = _canvas(8.4, h + 0.4, bg)
    for k, (step, body) in enumerate(zip(L["chain_steps"], wrapped)):
        x = k * 2.55
        _box(ax, x, 0, 2.2, h, soft)
        ax.add_patch(Rectangle((x, h - 0.32), 2.2, 0.32, color=col, lw=0))
        ax.text(x + 1.1, h - 0.16, step.upper(), ha="center", va="center", fontsize=7.5,
                color=bg, fontweight="bold")
        ax.text(x + 0.12, h - 0.45, body, ha="left", va="top", fontsize=7.6, color=colors["text"],
                linespacing=1.25)
        if k < 3:
            ax.annotate("", xy=(x + 2.5, h / 2), xytext=(x + 2.24, h / 2),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=1.6))
    ax.set_xlim(-0.05, 10.3)
    ax.set_ylim(-0.05, h + 0.05)
    return _png(fig, bg)


# ── Ratios dérivés (l'entreprise en bref) ─────────────────────────────────

def ratios(request, colors) -> bytes | None:
    lang, L = _lang(request), ILLU[_lang(request)]
    e, s, g = request.environmental, request.social, request.governance
    staff, rev = s.total_employees or None, request.company.revenue_eur or None
    tiles = []
    if e.co2_emissions_tonnes and staff:
        tiles.append(("env", num(e.co2_emissions_tonnes / staff, lang, 1), L["ratios"]["co2_staff"]))
    if e.co2_emissions_tonnes and rev:
        tiles.append(("env", num(e.co2_emissions_tonnes / rev * 1e6, lang), L["ratios"]["co2_rev"]))
    if e.energy_consumption_mwh and staff:
        tiles.append(("env", num(e.energy_consumption_mwh / staff, lang, 1),
                      L["ratios"]["mwh_staff"]))
    if s.employee_turnover_percent is not None and staff:
        tiles.append(("social", num(round(s.employee_turnover_percent / 100 * staff), lang),
                      L["ratios"]["departures"]))
    if s.training_hours_per_employee is not None and staff:
        tiles.append(("social", num(round(s.training_hours_per_employee * staff, -1), lang),
                      L["ratios"]["training_total"]))
    if g.csr_budget_eur is not None and staff:
        tiles.append(("gov", num(g.csr_budget_eur / staff, lang), L["ratios"]["csr_staff"]))
    if len(tiles) < 2:
        return None
    tiles = tiles[:6]
    n = len(tiles)
    bg = colors["bg"]
    fig, ax = _canvas(7.6, 1.45, bg)
    w = 10 / n
    for k, (p, value, label) in enumerate(tiles):
        x = k * w
        ax.add_patch(Rectangle((x + 0.05, 1.18), w - 0.1, 0.05, color=colors[p], lw=0))
        ax.text(x + 0.12, 0.8, value, fontsize=17, color=colors[p], va="center")
        ax.text(x + 0.12, 0.22, _wrap(label, 18), fontsize=7.4, color=colors["secondary"],
                va="center", linespacing=1.2)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 1.3)
    return _png(fig, bg)


# ── Complétude des données par pilier ─────────────────────────────────────

def completeness(request, colors) -> bytes | None:
    L, d = ILLU[_lang(request)], _data(request)
    bg = colors["bg"]
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.4), facecolor=bg)
    for ax, p in zip(axes, ("env", "social", "gov")):
        total = len(FIELDS[p])
        filled = sum(1 for f in FIELDS[p] if d.get(f) is not None)
        ax.set_facecolor(bg)
        ax.pie([filled, total - filled] if filled < total else [1], startangle=90, counterclock=False,
               colors=[colors[p], colors[f"{p}_soft"]][:2 if filled < total else 1],
               wedgeprops=dict(width=0.28, linewidth=0))
        ax.text(0, 0.05, f"{filled}/{total}", ha="center", va="center", fontsize=15,
                color=colors[p])
        ax.set_title(L["pillar_names"][p], fontsize=9.5, color=colors["text"], pad=4)
        ax.set_aspect("equal")
    return _png(fig, bg)


# ── Couverture du bilan carbone ───────────────────────────────────────────

def scope_coverage(request, colors) -> bytes | None:
    lang, L, e = _lang(request), ILLU[_lang(request)], request.environmental
    scopes = [("1", e.scope1_emissions), ("2", e.scope2_emissions), ("3", e.scope3_emissions)]
    known = [(k, v) for k, v in scopes if v is not None]
    missing = [k for k, v in scopes if v is None]
    total = sum(v for _, v in known)
    if not known or not total or not missing:
        return None   # bilan complet : le camembert existant suffit
    bg = colors["bg"]
    fig, ax = _canvas(7.6, 1.55, bg)
    x, alphas = 0.0, {"1": 1.0, "2": 0.65, "3": 0.4}
    span = 7.0
    for k, v in known:
        w = span * v / total
        ax.add_patch(Rectangle((x, 0.55), w, 0.5, color=colors["env"], alpha=alphas[k], lw=0))
        if w > 0.9:
            ax.text(x + w / 2, 0.8, f"Scope {k}\n{pct(v / total * 100, lang)}", ha="center",
                    va="center", fontsize=7.8, color=bg, linespacing=1.15)
        x += w
    mx = span + 0.25
    for k in missing:
        ax.add_patch(Rectangle((mx, 0.55), 2.5, 0.5, fill=False, ec=colors["secondary"], lw=1.1,
                               ls=(0, (3, 2))))
        ax.text(mx + 1.25, 0.8, L["scope_missing"].format(n=k), ha="center", va="center",
                fontsize=7.6, color=colors["secondary"])
        mx += 2.7
    ax.text(0, 0.18, L["scope_note"], fontsize=7.2, color=colors["secondary"], style="italic")
    ax.set_xlim(-0.05, max(mx, span + 0.3))
    ax.set_ylim(0, 1.15)
    return _png(fig, bg)


# ── Grille du dispositif de gouvernance ───────────────────────────────────

def gov_checklist(request, colors) -> bytes | None:
    from bands import classer
    from narrative_texts import TRANCHES
    lang, L, g = _lang(request), ILLU[_lang(request)], request.governance
    tr = TRANCHES["en" if lang == "en" else "fr"]

    def flag(v):
        return (None, L["check_na"]) if v is None else (v, L["check_yes"] if v else L["check_no"])

    def band(key, v):
        if v is None:
            return None, L["check_na"]
        b = classer(key, v)
        if b is None:
            return None, pct(v, lang)
        return b in ("exemplaire", "solide"), f"{pct(v, lang)} — {tr[b]}"

    counts = [g.ethics_violations, g.corruption_cases, g.data_breaches]
    known = [c for c in counts if c is not None]
    integ = ((None, L["check_na"]) if not known else
             (True, L["check_none"]) if not any(known) else
             (False, L["check_incidents"].format(n=num(sum(known), lang))))
    rows = [("committee", flag(g.sustainability_committee)), ("audit", flag(g.esg_audit_conducted)),
            ("independence", band("independent_board_percent", g.independent_board_percent)),
            ("board_mix", band("female_board_percent", g.female_board_percent)),
            ("integrity", integ)]
    if sum(1 for _, (ok, _) in rows if ok is not None) < 3:
        return None
    bg, col = colors["bg"], colors["gov"]
    fig, ax = _canvas(7.2, 0.5 * len(rows) + 0.2, bg)
    for r, (key, (ok, label)) in enumerate(rows):
        y = len(rows) - 1 - r
        ax.add_patch(Circle((0.25, y + 0.25), 0.17, facecolor=col if ok else bg,
                            edgecolor=col if ok is not None else colors["secondary"], lw=1.4))
        mark = "✓" if ok else ("✕" if ok is False else "?")
        ax.text(0.25, y + 0.24, mark, ha="center", va="center", fontsize=9,
                color=bg if ok else colors["secondary"], fontweight="bold")
        ax.text(0.65, y + 0.25, L["check"][key], va="center", fontsize=9, color=colors["text"])
        ax.text(9.9, y + 0.25, label, va="center", ha="right", fontsize=8.6,
                color=col if ok else colors["secondary"])
        ax.plot([0.65, 9.9], [y - 0.02, y - 0.02], color=colors["rule"], lw=0.6)
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.1, len(rows))
    return _png(fig, bg)


# ── Ancrage territorial et parties prenantes ──────────────────────────────

def stakeholders(request, colors) -> bytes | None:
    lang, L, s = _lang(request), ILLU[_lang(request)], request.social
    rows = [(L["stake"]["local"], s.local_suppliers_percent, 100, pct),
            (L["stake"]["satisfaction"], s.customer_satisfaction_score, 10,
             lambda v, lg: f"{num(v, lg, 1)}/10"),
            (L["stake"]["disabled"], s.disabled_employees_percent, 100, pct)]
    rows = [r for r in rows if r[1] is not None]
    if len(rows) < 2:
        return None
    bg, col = colors["bg"], colors["social"]
    fig, ax = _canvas(7.2, 0.62 * len(rows) + 0.1, bg)
    for r, (label, v, top, fmt) in enumerate(rows):
        y = len(rows) - 1 - r
        ax.text(0, y + 0.3, label, va="center", fontsize=8.8, color=colors["text"])
        ax.add_patch(Rectangle((3.4, y + 0.18), 5.4, 0.24, color=colors["social_soft"], lw=0))
        ax.add_patch(Rectangle((3.4, y + 0.18), 5.4 * min(v, top) / top, 0.24, color=col, lw=0))
        ax.text(9.95, y + 0.3, fmt(v, lang), va="center", ha="right", fontsize=9, color=col,
                fontweight="bold")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(rows))
    return _png(fig, bg)


# ── Feuille de route 12 mois ──────────────────────────────────────────────

_PHASES = [(0, 3), (3, 6), (6, 12)]


def roadmap(request, scores, colors) -> bytes | None:
    from content_generator import roadmap_12m
    L = ILLU[_lang(request)]
    rm = roadmap_12m(request, scores)
    bars = [(a, _PHASES[i]) for i, ph in enumerate(rm[:3]) for a in ph["actions"][:4]]
    if not bars:
        return None
    bg = colors["bg"]
    fig, ax = _canvas(7.6, 0.42 * len(bars) + 0.8, bg)
    for r, (a, (start, end)) in enumerate(bars):
        y = len(bars) - 1 - r
        col = colors.get(a["pillar"], colors["accent"])
        ax.add_patch(FancyBboxPatch((start + 0.05, y + 0.1), end - start - 0.1, 0.3,
                                    boxstyle="round,pad=0,rounding_size=0.1", color=col, lw=0))
        label = a["title"] + (f"  ★ {L['quick_win']}" if a["quick_win"] else "")
        ax.text(12.3, y + 0.25, _wrap(label, 58), va="center", fontsize=7.6, color=colors["text"])
    for m in (0, 3, 6, 12):
        ax.plot([m, m], [-0.15, len(bars)], color=colors["rule"], lw=0.7, zorder=0)
        ax.text(m, -0.45, f"{m}", ha="center", fontsize=7.5, color=colors["secondary"])
    ax.text(6, -0.85, L["months"], ha="center", fontsize=7.5, color=colors["secondary"])
    ax.set_xlim(-0.3, 26)
    ax.set_ylim(-1.0, len(bars))
    return _png(fig, bg)


# ── Mixité : effectif et conseil ──────────────────────────────────────────

def mix_board(request, colors) -> bytes | None:
    lang, L = _lang(request), ILLU[_lang(request)]
    f, b = request.social.female_employees_percent, request.governance.female_board_percent
    if f is None or b is None:
        return None
    bg = colors["bg"]
    fig, ax = _canvas(7.2, 1.35, bg)
    for r, (label, v, p) in enumerate(((L["mixboard_staff"], f, "social"),
                                        (L["mixboard_board"], b, "gov"))):
        y = 1 - r
        ax.text(0, y + 0.3, label, va="center", fontsize=8.8, color=colors["text"])
        ax.add_patch(Rectangle((3.0, y + 0.16), 6.0, 0.28, color=colors[f"{p}_soft"], lw=0))
        ax.add_patch(Rectangle((3.0, y + 0.16), 6.0 * v / 100, 0.28, color=colors[p], lw=0))
        ax.text(9.95, y + 0.3, pct(v, lang), va="center", ha="right", fontsize=9, color=colors[p],
                fontweight="bold")
    xr = 3.0 + 6.0 * MIXITE_EFFECTIF_REPERE / 100
    ax.plot([xr, xr], [0.05, 1.55], color=colors["text"], lw=0.9, ls=(0, (2, 2)))
    ax.text(xr, 1.62, L["mixboard_ref"].format(rep=MIXITE_EFFECTIF_REPERE), ha="center",
            fontsize=7, color=colors["secondary"])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 1.8)
    return _png(fig, bg)


# ── Quadrant rotation × formation ─────────────────────────────────────────

def quadrant(request, colors) -> bytes | None:
    L = ILLU[_lang(request)]
    lang = _lang(request)
    h, to = request.social.training_hours_per_employee, request.social.employee_turnover_percent
    if h is None or to is None:
        return None
    # Frontières : bas de la tranche « satisfaisant » de chaque grille (bands.py)
    hx = dict((n, b) for b, n in _SOCIAL_BANDS["training_hours_per_employee"])["satisfaisant"]
    ty = dict((n, b) for b, n in _SOCIAL_BANDS["employee_turnover_percent"])["satisfaisant"]
    xmax, ymax = max(45, h * 1.15), max(35, to * 1.15)
    bg, col = colors["bg"], colors["social"]
    fig, ax = plt.subplots(figsize=(6.4, 3.4), facecolor=bg)
    ax.set_facecolor(bg)
    ax.axvline(hx, color=colors["rule"], lw=1)
    ax.axhline(ty, color=colors["rule"], lw=1)
    q = L["quad"]
    # Étiquettes dans les coins extérieurs : le point de l'entreprise, au
    # centre d'un quadrant le plus souvent, ne les recouvre pas.
    for (x, y, key, ha, va) in ((0.02 * xmax, 0.97 * ymax, "bad_bad", "left", "top"),
                                (0.98 * xmax, 0.97 * ymax, "bad_good", "right", "top"),
                                (0.02 * xmax, 0.03 * ymax, "good_bad", "left", "bottom"),
                                (0.98 * xmax, 0.03 * ymax, "good_good", "right", "bottom")):
        ax.text(x, y, q[key], ha=ha, va=va, fontsize=8.5, color=colors["secondary"],
                style="italic")
    ax.scatter([h], [to], s=160, color=col, zorder=5, edgecolor=bg, linewidth=1.5)
    ax.annotate(request.company.name, (h, to), xytext=(8, 8), textcoords="offset points",
                fontsize=8.5, color=col, fontweight="bold")
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.set_xlabel(L["quad_x"], fontsize=8, color=colors["secondary"])
    ax.set_ylabel(L["quad_y"], fontsize=8, color=colors["secondary"])
    ax.tick_params(colors=colors["secondary"], labelsize=7.5)
    from matplotlib.ticker import FuncFormatter
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: num(v, lang)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: num(v, lang)))
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(colors["rule"])
    return _png(fig, bg)


# ── Calendrier : exercice, prochain exercice, horizon ─────────────────────

def timeline(request, scores, colors) -> bytes | None:
    import synthesis as SY
    from narrative import completeness
    L, c = ILLU[_lang(request)], request.company
    y0, ty = c.reporting_year, max(c.target_year, c.reporting_year + 1)
    filled, total = completeness(request)
    n_issues = len(SY.issues(request, scores))
    bg, col = colors["bg"], colors["accent"]
    fig, ax = _canvas(7.6, 1.9, bg)
    span = max(ty - y0, 1)
    ax.plot([0, 10], [1, 1], color=colors["rule"], lw=2.2, solid_capstyle="round")
    points: list[tuple[float, str]] = [(0, L["tl_today"].format(y=y0))]
    if ty - y0 > 1:
        nxt = (L["tl_next"].format(y=y0 + 1, n=total - filled) if total > filled
               else L["tl_next_full"].format(y=y0 + 1))
        points.append((10 / span, nxt))
    points.append((10, L["tl_target"].format(y=ty)))
    for x, label in points:
        ax.add_patch(Circle((x, 1), 0.13, color=col, zorder=3))
        ax.text(x, 0.72, label, ha="center", va="top", fontsize=7.8, color=colors["text"],
                linespacing=1.25)
    if n_issues:
        ax.text(5 + 5 / span, 1.3, L["tl_issues"].format(n=n_issues), ha="center", fontsize=8.5,
                color=col, fontweight="bold")
    ax.set_xlim(-1.2, 11.2)
    ax.set_ylim(-0.25, 1.6)
    return _png(fig, bg)


# ── Les 90 premiers jours ─────────────────────────────────────────────────

def first_days(request, scores, colors) -> bytes | None:
    import synthesis as SY
    L = ILLU[_lang(request)]
    actions = SY.closing(request, scores)["first"]
    if not actions:
        return None
    bg, col = colors["bg"], colors["accent"]
    wrapped = [_wrap(a, 27) for a in actions]
    lines = max(w.count("\n") + 1 for w in wrapped)
    h = 0.24 * lines + 0.5
    fig, ax = _canvas(7.8, h + 0.9, bg)
    ax.annotate("", xy=(10.2, h + 0.35), xytext=(0, h + 0.35),
                arrowprops=dict(arrowstyle="-|>", color=colors["rule"], lw=2))
    ax.text(0, h + 0.55, L["first_start"], fontsize=8, color=colors["secondary"])
    ax.text(10.2, h + 0.55, L["first_end"], fontsize=8, color=colors["secondary"], ha="right")
    w = 10.2 / len(actions)
    for k, text in enumerate(wrapped):
        x = k * w
        _box(ax, x, 0, w - 0.2, h, colors["panel"] if "panel" in colors else colors["rule"])
        ax.add_patch(Circle((x + 0.3, h - 0.28), 0.2, color=col))
        ax.text(x + 0.3, h - 0.29, str(k + 1), ha="center", va="center", fontsize=9, color=bg,
                fontweight="bold")
        ax.text(x + 0.65, h - 0.12, text, va="top", fontsize=7.6, color=colors["text"],
                linespacing=1.25)
    ax.set_xlim(-0.05, 10.3)
    ax.set_ylim(-0.05, h + 0.8)
    return _png(fig, bg)
