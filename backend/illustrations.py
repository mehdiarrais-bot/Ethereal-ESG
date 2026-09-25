"""Illustrations des piliers, dessinées à partir des données du dossier.

Aucune image décorative : chaque figure représente un chiffre du client
(position sur la grille, part sur 100, comparaison à la moyenne nationale,
sièges du conseil). Couleurs et police viennent du gabarit (chart_generator.
get_colors) ; libellés dans analysis_texts.ILLU.

ANCHORS dit où chaque figure s'insère dans l'analyse approfondie
(analysis.Section.key) : « _start » = en tête de l'analyse du pilier.
"""
import io
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                     # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle  # noqa: E402

from analysis_texts import ILLU                    # noqa: E402
from bands import SEUILS, PLUS_HAUT_MIEUX          # noqa: E402
from esg_calculator import TF_NATIONAL_2024, carbon_thresholds_for  # noqa: E402
from narrative import num, pct, _GRADED, _graded_value, _data       # noqa: E402
from narrative_texts import TRANCHES               # noqa: E402

DPI = 170
# Opacité de la couleur du pilier, de la tranche critique à l'exemplaire
_RAMP = [0.10, 0.22, 0.38, 0.58, 0.85]
_ORDER = ["critique", "fragile", "satisfaisant", "solide", "exemplaire"]

# (pilier, clé de section) -> figures ; la première section présente l'emporte
ANCHORS = {
    "env": [("_start", ["ill_ruler_env"]), (("energy", "waste"), ["ill_waffle_env"])],
    "social": [("_start", ["ill_ruler_social"]), (("safety",), ["ill_tf"]),
               (("talent", "mix"), ["ill_people"])],
    "gov": [("_start", ["ill_ruler_gov"]), (("board",), ["ill_board"])],
}


def placements(pillar: str, section_keys: list[str]) -> dict[str, list[str]]:
    """{clé de section ou "_start": [figures]} pour les sections présentes."""
    out: dict[str, list[str]] = {}
    for where, keys in ANCHORS[pillar]:
        if where == "_start":
            out.setdefault("_start", []).extend(keys)
            continue
        hit = next((k for k in where if k in section_keys), None)
        if hit:
            out.setdefault(hit, []).extend(keys)
    return out


def _png(fig, bg) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=DPI, bbox_inches="tight", facecolor=bg, edgecolor="none")
    plt.close(fig)
    return buf.getvalue()


def _lang(request) -> str:
    return "en" if request.language == "en" else "fr"


# ── Règle de positionnement sur la grille ─────────────────────────────────

def _segments(key, value, sector):
    """Bornes des cinq tranches, de la critique à l'exemplaire :
    [(nom, bas, haut)] dans le domaine des valeurs, et le sens."""
    entry = SEUILS[key]
    if key == "co2_emissions_tonnes":
        grid, _ = carbon_thresholds_for(sector)
        names = {100: "exemplaire", 80: "solide", 60: "satisfaisant", 40: "fragile", 20: "critique"}
        bornes = [(b, names[s]) for b, s in grid]
        higher = False
    else:
        bornes, higher = entry["bornes"], entry["sens"] == PLUS_HAUT_MIEUX
    segs = {}
    if higher:          # bornes décroissantes : (80, exemplaire), (60, solide)…
        top = max(value, bornes[0][0] * 1.25, 1)
        if key.endswith("_percent"):
            top = 100
        for i, (b, name) in enumerate(bornes):
            hi = top if i == 0 else bornes[i - 1][0]
            segs[name] = (b, hi)
    else:               # bornes croissantes : (4, exemplaire), (8, solide)…
        finite = [b for b, _ in bornes if b != float("inf")]
        top = max(value * 1.1, finite[-1] * 1.6)
        for i, (b, name) in enumerate(bornes):
            lo = 0 if i == 0 else bornes[i - 1][0]
            segs[name] = (lo, top if b == float("inf") else b)
    return segs, higher


def _position(value, segs, higher) -> float:
    """Abscisse 0..5 : index de tranche (critique = 0) + fraction."""
    for i, name in enumerate(_ORDER):
        lo, hi = segs[name]
        inside = lo <= value <= hi if higher else lo <= value <= hi
        if inside and hi > lo:
            frac = (value - lo) / (hi - lo)
            return i + (frac if higher else 1 - frac)
    return 5.0 if higher else 0.0


def _fmt(key, v, lang):
    if key.endswith("_percent"):
        return pct(v, lang)
    if key == "training_hours_per_employee":
        return f"{num(v, lang)} h"
    if key in ("accident_frequency_rate", "customer_satisfaction_score"):
        return num(v, lang, 1)
    return num(v, lang)


def ruler(request, pillar, colors) -> bytes | None:
    lang, d = _lang(request), _data(request)
    rows = []
    for key in _GRADED[pillar]:
        if key == "biodiversity_initiatives":
            continue
        v = _graded_value(key, d, request)
        if v is not None:
            rows.append((key, v))
    if len(rows) < 2:
        return None
    col, ink, muted, bg = colors[pillar], colors["text"], colors["secondary"], colors["bg"]
    L = ILLU[lang]
    fig, ax = plt.subplots(figsize=(7.6, 0.62 * len(rows) + 0.75), facecolor=bg)
    ax.set_facecolor(bg)
    for r, (key, v) in enumerate(rows):
        y = len(rows) - 1 - r
        segs, higher = _segments(key, v, request.company.sector)
        for i in range(5):
            ax.add_patch(Rectangle((i + 0.03, y - 0.16), 0.94, 0.32, color=col, alpha=_RAMP[i],
                                   lw=0))
        x = _position(v, segs, higher)
        ax.plot([x], [y + 0.28], marker="v", markersize=9, color=ink, zorder=5)
        ax.text(x, y + 0.42, _fmt(key, v, lang), ha="center", va="bottom", fontsize=8.5,
                color=ink, fontweight="bold")
        ax.text(-0.12, y, L["short"][key], ha="right", va="center", fontsize=8.5, color=ink)
    tr = TRANCHES["en" if lang == "en" else "fr"]
    for i, name in enumerate(_ORDER):
        ax.text(i + 0.5, -0.62, tr[name], ha="center", va="center", fontsize=7.5, color=muted)
    ax.set_xlim(-0.05, 5.05)
    ax.set_ylim(-0.85, len(rows) - 0.2)
    ax.axis("off")
    return _png(fig, bg)


# ── Grilles de 100 cases ──────────────────────────────────────────────────

def _waffle(ax, share, col, soft, label, ink):
    filled = round(share)
    for i in range(100):
        row, c = divmod(i, 10)
        ax.add_patch(FancyBboxPatch((c + 0.08, 9 - row + 0.08), 0.84, 0.84,
                                    boxstyle="round,pad=0,rounding_size=0.12",
                                    color=col if i < filled else soft, lw=0))
    ax.text(5, -0.9, label, ha="center", va="top", fontsize=9, color=ink, linespacing=1.3)
    ax.set_xlim(0, 10)
    ax.set_ylim(-2.6, 10)
    ax.set_aspect("equal")
    ax.axis("off")


def waffle_env(request, colors) -> bytes | None:
    env, lang = request.environmental, _lang(request)
    L = ILLU[lang]
    panels = [(v, L[k].format(p=pct(v, lang))) for v, k in
              ((env.renewable_energy_percent, "waffle_ren"),
               (env.waste_recycled_percent, "waffle_rec")) if v is not None]
    if not panels:
        return None
    bg = colors["bg"]
    fig, axes = plt.subplots(1, len(panels), figsize=(3.1 * len(panels), 3.5), facecolor=bg)
    axes = axes if len(panels) > 1 else [axes]
    for ax, (v, label) in zip(axes, panels):
        ax.set_facecolor(bg)
        _waffle(ax, v, colors["env"], colors["env_soft"], label, colors["text"])
    return _png(fig, bg)


# ── Silhouettes « sur 100 salariés » ─────────────────────────────────────

def _people(ax, n, col, soft, label, ink):
    for i in range(100):
        row, c = divmod(i, 20)
        x, y = c * 1.0 + 0.5, (4 - row) * 1.55
        color = col if i < n else soft
        ax.add_patch(Circle((x, y + 0.95), 0.2, color=color, lw=0))
        ax.add_patch(FancyBboxPatch((x - 0.26, y + 0.05), 0.52, 0.62,
                                    boxstyle="round,pad=0,rounding_size=0.2", color=color, lw=0))
    ax.text(10, -0.55, label, ha="center", va="top", fontsize=9.5, color=ink, linespacing=1.3)
    ax.set_xlim(0, 20)
    ax.set_ylim(-2.0, 7.6)
    ax.set_aspect("equal")
    ax.axis("off")


def people(request, colors) -> bytes | None:
    soc, lang = request.social, _lang(request)
    L = ILLU[lang]
    panels = [(round(v), L[k].format(n=num(round(v), lang))) for v, k in
              ((soc.female_employees_percent, "people_mix"),
               (soc.employee_turnover_percent, "people_turnover")) if v is not None]
    if not panels:
        return None
    bg = colors["bg"]
    fig, axes = plt.subplots(len(panels), 1, figsize=(7.2, 2.35 * len(panels)), facecolor=bg)
    axes = axes if len(panels) > 1 else [axes]
    for ax, (n, label) in zip(axes, panels):
        ax.set_facecolor(bg)
        _people(ax, n, colors["social"], colors["social_soft"], label, colors["text"])
    return _png(fig, bg)


# ── Taux de fréquence comparé à la moyenne nationale ─────────────────────

def tf_compare(request, colors) -> bytes | None:
    tf, lang = request.social.accident_frequency_rate, _lang(request)
    if tf is None:
        return None
    L = ILLU[lang]
    bg, ink, muted = colors["bg"], colors["text"], colors["secondary"]
    labels = [L["tf_company"].format(name=request.company.name), L["tf_national"]]
    values = [tf, TF_NATIONAL_2024]
    fig, ax = plt.subplots(figsize=(7.2, 1.9), facecolor=bg)
    ax.set_facecolor(bg)
    bars = ax.barh([1, 0], values, height=0.55, color=[colors["social"], colors["rule"]])
    top = max(values)
    for bar, v in zip(bars, values):
        ax.text(bar.get_width() + top * 0.015, bar.get_y() + bar.get_height() / 2,
                num(v, lang, 1), va="center", fontsize=10, color=ink, fontweight="bold")
    ratio = tf / TF_NATIONAL_2024
    ax.text(top * 1.2, 0.5, L["tf_ratio"].format(x=num(ratio, lang, 1)), ha="right", va="center",
            fontsize=10.5, color=colors["social"], fontweight="bold")
    ax.set_yticks([1, 0])
    ax.set_yticklabels(labels, fontsize=8.8, color=ink)
    ax.set_xlim(0, top * 1.22)
    ax.tick_params(axis="x", colors=muted, labelsize=7.5)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(colors["rule"])
    return _png(fig, bg)


# ── Hémicycle du conseil ──────────────────────────────────────────────────

def _hemicycle(ax, n, k, col, soft, label, ink):
    rows = 1 if n <= 7 else 2 if n <= 16 else 3
    per = [math.ceil(n * (r + 1) / sum(range(1, rows + 1))) for r in range(rows)]
    per[-1] = n - sum(per[:-1])
    seats = []
    for r, m in enumerate(per):
        radius = 1.0 + r * 0.42
        for j in range(m):
            a = math.pi * (1 - (j + 0.5) / m)
            seats.append((a, radius * math.cos(a), radius * math.sin(a)))
    seats.sort(key=lambda s: -s[0])          # de gauche à droite
    size = 0.22 if n <= 7 else 0.15      # sièges plus grands pour un petit conseil
    for i, (_, x, y) in enumerate(seats):
        ax.add_patch(Circle((x, y), size, color=col if i < k else soft, lw=0))
    ax.text(0, -0.35, label, ha="center", va="top", fontsize=9.5, color=ink)
    ax.set_xlim(-2.1, 2.1)
    ax.set_ylim(-0.8, 2.1)
    ax.set_aspect("equal")
    ax.axis("off")


def board(request, colors) -> bytes | None:
    g, lang = request.governance, _lang(request)
    n = g.board_members
    if not n:
        return None
    L = ILLU[lang]
    panels = [(round(n * v / 100), L[key].format(k=num(round(n * v / 100), lang), n=num(n, lang)))
              for v, key in ((g.independent_board_percent, "board_ind"),
                             (g.female_board_percent, "board_fem")) if v is not None]
    if not panels:
        return None
    bg = colors["bg"]
    fig, axes = plt.subplots(1, len(panels), figsize=(3.4 * len(panels), 2.3), facecolor=bg)
    axes = axes if len(panels) > 1 else [axes]
    for ax, (k, label) in zip(axes, panels):
        ax.set_facecolor(bg)
        _hemicycle(ax, n, k, colors["gov"], colors["gov_soft"], label, colors["text"])
    return _png(fig, bg)


# ── Assemblage ────────────────────────────────────────────────────────────

def _colors(request):
    from chart_generator import get_colors
    from report_designs import colors_of
    c = get_colors(request.aesthetic_theme, True, getattr(request, "custom_colors", None))
    soft = colors_of(request.aesthetic_theme)
    return {**c, "env_soft": soft["env_soft"], "social_soft": soft["social_soft"],
            "gov_soft": soft["gov_soft"]}


def build(request) -> dict[str, bytes]:
    """Toutes les illustrations disponibles pour ce dossier. Une figure qui
    échoue est omise : la génération du livrable ne s'interrompt jamais."""
    colors = _colors(request)
    makers = {
        "ill_ruler_env": lambda: ruler(request, "env", colors),
        "ill_ruler_social": lambda: ruler(request, "social", colors),
        "ill_ruler_gov": lambda: ruler(request, "gov", colors),
        "ill_waffle_env": lambda: waffle_env(request, colors),
        "ill_people": lambda: people(request, colors),
        "ill_tf": lambda: tf_compare(request, colors),
        "ill_board": lambda: board(request, colors),
    }
    out = {}
    for key, make in makers.items():
        try:
            img = make()
        except Exception as e:  # jamais bloquant ; visible dans le journal
            print(f"Illustration {key} error: {e}")
            img = None
        if img:
            out[key] = img
    return out


def caption(request, key: str) -> str:
    L = ILLU[_lang(request)]
    if key.startswith("ill_ruler_"):
        return L["cap_ruler"][key.rsplit("_", 1)[1]]
    return L[{"ill_waffle_env": "cap_waffle", "ill_people": "cap_people", "ill_tf": "cap_tf",
              "ill_board": "cap_board"}[key]]
