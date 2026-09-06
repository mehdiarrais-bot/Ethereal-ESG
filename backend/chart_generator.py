from i18n import L
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import math
from models import ESGScores, AestheticTheme

THEME_COLORS = {
    AestheticTheme.CORPORATE_BLUE: {
        "primary": "#1B3A6B",
        "secondary": "#2E86C1",
        "accent": "#F39C12",
        "env": "#27AE60",
        "social": "#2E86C1",
        "gov": "#8E44AD",
        "bg": "#FFFFFF",
        "text": "#2C3E50",
    },
    AestheticTheme.GREEN_NATURE: {
        "primary": "#1A5C38",
        "secondary": "#27AE60",
        "accent": "#F1C40F",
        "env": "#2ECC71",
        "social": "#3498DB",
        "gov": "#E67E22",
        "bg": "#F8FFF8",
        "text": "#1A3325",
    },
    AestheticTheme.DARK_PREMIUM: {
        "primary": "#0D1117",
        "secondary": "#21262D",
        "accent": "#F7C948",
        "env": "#3FB950",
        "social": "#58A6FF",
        "gov": "#BC8CFF",
        "bg": "#161B22",
        "text": "#E6EDF3",
    },
    AestheticTheme.MINIMAL_WHITE: {
        "primary": "#212121",
        "secondary": "#616161",
        "accent": "#FF6F00",
        "env": "#43A047",
        "social": "#1E88E5",
        "gov": "#8E24AA",
        "bg": "#FAFAFA",
        "text": "#212121",
    },
    AestheticTheme.SUNSET_TERRACOTTA: {
        "primary": "#9A3412",
        "secondary": "#E76F51",
        "accent": "#F4A261",
        "env": "#2A9D8F",
        "social": "#E76F51",
        "gov": "#6D597A",
        "bg": "#FDF6F0",
        "text": "#4A2C22",
    },
    AestheticTheme.OCEAN_DEEP: {
        "primary": "#0F4C5C",
        "secondary": "#277DA1",
        "accent": "#00BFA6",
        "env": "#43AA8B",
        "social": "#277DA1",
        "gov": "#577590",
        "bg": "#F4FBFC",
        "text": "#123B44",
    },
    AestheticTheme.ROYAL_PURPLE: {
        "primary": "#2B1055",
        "secondary": "#B9A6E0",
        "accent": "#FFD54F",
        "env": "#2E9E62",
        "social": "#7E9BF5",
        "gov": "#C08CF5",
        "bg": "#241047",
        "text": "#F2EDFB",
    },
}


DARK_THEMES = {AestheticTheme.DARK_PREMIUM, AestheticTheme.ROYAL_PURPLE}


def get_colors(theme: AestheticTheme, light_bg: bool = False, brand: dict = None) -> dict:
    c = dict(THEME_COLORS.get(theme, THEME_COLORS[AestheticTheme.CORPORATE_BLUE]))
    if light_bg and theme in DARK_THEMES:
        # Variante pour insertion sur page blanche (PDF)
        c["bg"] = "#FFFFFF"
        c["text"] = "#2C3E50"
        c["secondary"] = "#5A6B7C"
    if brand:
        # Couleurs de marque du client : accent + primaire ; piliers inchangés
        from branding import brand_chart_colors
        c = brand_chart_colors(c, brand)
    return c


def radar_chart(scores: ESGScores, theme: AestheticTheme, light_bg: bool = False, lang: str = 'fr', brand: dict = None) -> bytes:
    colors = get_colors(theme, light_bg, brand)
    LB = L(lang)
    bg = colors["bg"]

    categories = [LB['chart_env'], LB['chart_soc'], LB['chart_gov']]
    values = [scores.environmental_score, scores.social_score, scores.governance_score]
    values_plot = values + [values[0]]

    angles = [n / float(3) * 2 * math.pi for n in range(3)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True),
                           facecolor=bg)
    ax.set_facecolor(bg)

    ax.plot(angles, values_plot, 'o-', linewidth=2.5, color=colors["secondary"])
    ax.fill(angles, values_plot, alpha=0.25, color=colors["secondary"])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=12, color=colors["text"], fontweight='bold')
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], size=8, color=colors["secondary"])
    ax.grid(color=colors["secondary"], alpha=0.3)
    ax.spines['polar'].set_color(colors["secondary"])

    for i, (angle, value, cat) in enumerate(zip(angles[:-1], values, categories)):
        c = [colors["env"], colors["social"], colors["gov"]][i]
        ax.plot(angle, value, 'o', color=c, markersize=10, zorder=5)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor=bg, edgecolor='none')
    plt.close()
    buf.seek(0)
    return buf.read()


def score_bars_chart(scores: ESGScores, theme: AestheticTheme, light_bg: bool = False, lang: str = 'fr', brand: dict = None) -> bytes:
    colors = get_colors(theme, light_bg, brand)
    LB = L(lang)
    bg = colors["bg"]

    fig, ax = plt.subplots(figsize=(8, 4), facecolor=bg)
    ax.set_facecolor(bg)

    categories = [LB['chart_env'], LB['chart_soc'], LB['chart_gov'], LB['chart_global']]
    values = [scores.environmental_score, scores.social_score,
              scores.governance_score, scores.total_esg_score]
    bar_colors = [colors["env"], colors["social"], colors["gov"], colors["accent"]]

    bars = ax.barh(categories, values, color=bar_colors, height=0.5, alpha=0.9)

    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                f'{val:.1f}', va='center', ha='left',
                color=colors["text"], fontweight='bold', fontsize=11)

    ax.set_xlim(0, 110)
    ax.set_ylim(-0.6, len(categories) - 0.4)
    # Zones de performance (storytelling : faible / excellence)
    ax.axvspan(0, 50, color="#E74C3C", alpha=0.05, zorder=0)
    ax.axvspan(75, 110, color=colors["env"], alpha=0.07, zorder=0)
    ax.set_xlabel(LB['chart_score_axis'], color=colors["text"], fontsize=10)
    ax.tick_params(colors=colors["text"])
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.spines['bottom'].set_color(colors["secondary"])
    ax.set_facecolor(bg)
    for label in ax.get_yticklabels():
        label.set_color(colors["text"])
        label.set_fontsize(11)

    # Seuils annotés (preuve sociale : moyenne / excellence)
    ytop = len(categories) - 0.35
    ax.axvline(x=50, color=colors["secondary"], linestyle='--', alpha=0.55, linewidth=1)
    ax.text(50, ytop, LB["chart_avg"], color=colors["secondary"], fontsize=8,
            ha="center", va="bottom", fontweight="bold")
    ax.axvline(x=75, color=colors["env"], linestyle='--', alpha=0.6, linewidth=1)
    ax.text(75, ytop, LB["chart_leaders"], color=colors["env"], fontsize=8,
            ha="center", va="bottom", fontweight="bold")

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor=bg, edgecolor='none')
    plt.close()
    buf.seek(0)
    return buf.read()


def emissions_breakdown_chart(scope1, scope2, scope3, theme: AestheticTheme, light_bg: bool = False, lang: str = 'fr', brand: dict = None) -> bytes:
    colors = get_colors(theme, light_bg, brand)
    LB = L(lang)
    bg = colors["bg"]

    data = {}
    if scope1 is not None:
        data[LB['pie_s1']] = scope1
    if scope2 is not None:
        data[LB['pie_s2']] = scope2
    if scope3 is not None:
        data[LB['pie_s3']] = scope3

    if not data:
        return None

    fig, ax = plt.subplots(figsize=(6, 5), facecolor=bg)
    ax.set_facecolor(bg)

    palette = [colors["env"], colors["social"], colors["gov"]]
    wedges, texts, autotexts = ax.pie(
        list(data.values()),
        labels=list(data.keys()),
        autopct='%1.1f%%',
        colors=palette[:len(data)],
        startangle=90,
        wedgeprops={'edgecolor': bg, 'linewidth': 2}
    )
    for text in texts:
        text.set_color(colors["text"])
        text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')

    ax.set_title(LB['pie_title'], color=colors["text"],
                 fontsize=12, fontweight='bold', pad=15)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor=bg, edgecolor='none')
    plt.close()
    buf.seek(0)
    return buf.read()


def _pillar_hex(colors, pillar):
    return colors.get(pillar, colors["secondary"])


def materiality_matrix(topics: list, theme: AestheticTheme, light_bg: bool = False, lang: str = 'fr', brand: dict = None) -> bytes:
    """Cartographie de priorisation des enjeux — points numérotés + légende
    latérale. Axes : exposition estimée / sensibilité économique estimée.
    Ce n'est pas une matrice de double matérialité au sens de l'ESRS 1 (voir
    esg_advanced.materiality_topics).

    Chaque enjeu porte un numéro dans sa bulle et est repris dans une légende
    groupée par pilier : plus aucun chevauchement de labels, lisible pour un
    comité de direction.
    """
    colors = get_colors(theme, light_bg, brand)
    LB = L(lang)
    bg = colors["bg"]
    grid = colors["secondary"]

    fig = plt.figure(figsize=(10.4, 6), facecolor=bg)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.55, 1], wspace=0.06)
    ax = fig.add_subplot(gs[0]); ax.set_facecolor(bg)
    lax = fig.add_subplot(gs[1]); lax.set_facecolor(bg); lax.axis("off")

    # Zone prioritaire (haut-droite) + médianes
    ax.axhspan(5, 10, xmin=0.5, xmax=1.0, color=colors["accent"], alpha=0.10, zorder=0)
    ax.axhline(5, color=grid, alpha=0.3, linewidth=1, linestyle='--')
    ax.axvline(5, color=grid, alpha=0.3, linewidth=1, linestyle='--')
    ax.text(5.2, 9.5, LB["mat_priority"], ha="left", fontsize=9,
            color=colors["accent"], fontweight="bold")

    pillar_order = ["env", "social", "gov"]
    for i, t in enumerate(topics, 1):
        c = _pillar_hex(colors, t["pillar"])
        ax.scatter(t["financial"], t["impact"], s=560, color=c, alpha=0.9,
                   edgecolors=bg, linewidths=2, zorder=3)
        ax.text(t["financial"], t["impact"], str(i), ha="center", va="center",
                fontsize=10, fontweight="bold", color="white", zorder=4)

    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    ax.set_xticks([0, 2, 4, 6, 8, 10]); ax.set_yticks([0, 2, 4, 6, 8, 10])
    ax.set_xlabel(LB["mat_x"], color=colors["text"], fontsize=11, fontweight="bold")
    ax.set_ylabel(LB["mat_y"], color=colors["text"], fontsize=11, fontweight="bold")
    ax.tick_params(colors=grid, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(grid); spine.set_alpha(0.4)

    # ── Légende groupée par pilier ─────────────────────────────────
    pillar_names = {"env": (LB["chart_env"], colors["env"]),
                    "social": (LB["chart_soc"], colors["social"]),
                    "gov": (LB["chart_gov"], colors["gov"])}
    y = 0.97
    lax.set_xlim(0, 1); lax.set_ylim(0, 1)
    for pil in pillar_order:
        pil_topics = [(i, t) for i, t in enumerate(topics, 1) if t["pillar"] == pil]
        if not pil_topics:
            continue
        pname, pcol = pillar_names[pil]
        lax.add_patch(plt.Rectangle((0.0, y - 0.028), 0.045, 0.045, color=pcol, transform=lax.transAxes, clip_on=False))
        lax.text(0.07, y, pname.upper(), fontsize=10.5, fontweight="bold",
                 color=colors["text"], va="center", transform=lax.transAxes)
        y -= 0.075
        for i, t in pil_topics:
            lax.scatter(0.03, y, s=250, color=pcol, transform=lax.transAxes, clip_on=False, zorder=3)
            lax.text(0.03, y, str(i), ha="center", va="center", fontsize=8.5,
                     fontweight="bold", color="white", transform=lax.transAxes, zorder=4)
            lax.text(0.09, y, t["label"], fontsize=9.5, color=colors["text"],
                     va="center", transform=lax.transAxes)
            y -= 0.066
        y -= 0.025

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=bg, edgecolor='none')
    plt.close()
    buf.seek(0)
    return buf.read()


def score_trend_chart(history: list, theme: AestheticTheme, light_bg: bool = False,
                      lang: str = 'fr', brand: dict = None) -> bytes:
    """Trajectoire pluriannuelle du score (global + piliers).

    `history` : [{year, env, social, gov, total}, ...] trié, ≥ 2 points —
    l'exercice courant inclus. Global en trait épais accent, piliers fins.
    """
    colors = get_colors(theme, light_bg, brand)
    LB = L(lang)
    bg = colors["bg"]

    years = [h["year"] for h in history]
    fig, ax = plt.subplots(figsize=(9, 4.6), facecolor=bg)
    ax.set_facecolor(bg)

    series = [
        ("total", LB["chart_global"], colors["accent"], 3.2, 1.0),
        ("env", LB["chart_env"], colors["env"], 1.6, 0.75),
        ("social", LB["chart_soc"], colors["social"], 1.6, 0.75),
        ("gov", LB["chart_gov"], colors["gov"], 1.6, 0.75),
    ]
    for key, label, col, lw, alpha in series:
        vals = [h[key] for h in history]
        ax.plot(years, vals, "o-", color=col, linewidth=lw, alpha=alpha,
                markersize=7 if key == "total" else 5, label=label,
                zorder=4 if key == "total" else 3)
        # étiquette de la dernière valeur (lecture directe)
        ax.annotate(f"{vals[-1]:.0f}", (years[-1], vals[-1]),
                    textcoords="offset points", xytext=(10, -3),
                    fontsize=10 if key == "total" else 8.5, fontweight="bold", color=col)

    ax.set_xticks(years)
    ax.set_xticklabels([str(y) for y in years], fontsize=10, color=colors["text"])
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.tick_params(colors=colors["secondary"], labelsize=8.5)
    ax.grid(axis="y", color=colors["secondary"], alpha=0.2, linewidth=0.8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(colors["secondary"]); ax.spines[spine].set_alpha(0.4)
    leg = ax.legend(loc="lower right", fontsize=8.5, frameon=False, ncol=4)
    for t in leg.get_texts():
        t.set_color(colors["text"])

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=bg, edgecolor='none')
    plt.close()
    buf.seek(0)
    return buf.read()


def priority_matrix_chart(recs: list, theme: AestheticTheme, light_bg: bool = False, lang: str = 'fr', brand: dict = None) -> bytes:
    """Matrice de priorisation effort/impact des recommandations (2×2 conseil).

    Chaque action porte le numéro qu'elle a dans la liste des recommandations,
    colorée par pilier ; quadrants nommés (quick wins en évidence).
    """
    colors = get_colors(theme, light_bg, brand)
    LB = L(lang)
    bg = colors["bg"]
    grid = colors["secondary"]

    fig = plt.figure(figsize=(10.4, 6), facecolor=bg)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.55, 1], wspace=0.06)
    ax = fig.add_subplot(gs[0]); ax.set_facecolor(bg)
    lax = fig.add_subplot(gs[1]); lax.set_facecolor(bg); lax.axis("off")

    # Quadrant quick wins (haut-gauche : fort impact, faible effort)
    ax.axhspan(5, 10, xmin=0.0, xmax=0.5, color=colors["accent"], alpha=0.10, zorder=0)
    ax.axhline(5, color=grid, alpha=0.3, linewidth=1, linestyle='--')
    ax.axvline(5, color=grid, alpha=0.3, linewidth=1, linestyle='--')
    qstyle = dict(fontsize=8.5, fontweight="bold", ha="left", zorder=1)
    ax.text(0.3, 9.55, LB["quad_qw"], color=colors["accent"], **qstyle)
    ax.text(5.3, 9.55, LB["quad_strat"], color=colors["text"], alpha=0.75, **qstyle)
    ax.text(0.3, 0.45, LB["quad_fill"], color=colors["text"], alpha=0.55, **qstyle)
    ax.text(5.3, 0.45, LB["quad_avoid"], color=colors["text"], alpha=0.55, **qstyle)

    # Décalage anti-chevauchement pour les points superposés
    seen = {}
    for i, r in enumerate(recs, 1):
        key = (r["effort"], r["impact"])
        dx = seen.get(key, 0)
        seen[key] = dx + 1
        c = _pillar_hex(colors, r["pillar"])
        x = r["effort"] + dx * 0.75
        ax.scatter(x, r["impact"], s=560, color=c, alpha=0.9,
                   edgecolors=bg, linewidths=2, zorder=3)
        ax.text(x, r["impact"], str(i), ha="center", va="center",
                fontsize=10, fontweight="bold", color="white", zorder=4)

    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    ax.set_xticks([0, 2, 4, 6, 8, 10]); ax.set_yticks([0, 2, 4, 6, 8, 10])
    ax.set_xlabel(LB["prio_x"], color=colors["text"], fontsize=11, fontweight="bold")
    ax.set_ylabel(LB["prio_y"], color=colors["text"], fontsize=11, fontweight="bold")
    ax.tick_params(colors=grid, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(grid); spine.set_alpha(0.4)

    # Légende latérale : numéro + intitulé de chaque action
    lax.set_xlim(0, 1); lax.set_ylim(0, 1)
    y = 0.95
    for i, r in enumerate(recs, 1):
        c = _pillar_hex(colors, r["pillar"])
        lax.scatter(0.035, y, s=250, color=c, transform=lax.transAxes, clip_on=False, zorder=3)
        lax.text(0.035, y, str(i), ha="center", va="center", fontsize=8.5,
                 fontweight="bold", color="white", transform=lax.transAxes, zorder=4)
        label = r["title"] if len(r["title"]) <= 46 else r["title"][:44] + "…"
        lax.text(0.10, y, label, fontsize=9, color=colors["text"],
                 va="center", transform=lax.transAxes)
        y -= 0.115

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=bg, edgecolor='none')
    plt.close()
    buf.seek(0)
    return buf.read()


# targets_chart() et carbon_trajectory_chart() supprimees le 2026-09-03 :
# elles tracaient des cibles par pilier et une trajectoire carbone -42 %
# fabriquees par l'outil, presentees comme les engagements du client.
# Voir la note dans esg_advanced.py.


def taxonomy_chart(vals: dict, theme: AestheticTheme, light_bg: bool = False, lang: str = 'fr', brand: dict = None) -> bytes:
    """Barres d'alignement Taxonomie UE (CA / CapEx / OpEx)."""
    colors = get_colors(theme, light_bg, brand)
    LB = L(lang)
    bg = colors["bg"]

    labels_map = {"turnover": LB["tax_turnover"], "capex": LB["tax_capex"], "opex": LB["tax_opex"]}
    items = [(labels_map[k], v) for k, v in vals.items() if v is not None]

    fig, ax = plt.subplots(figsize=(7.5, 3.4), facecolor=bg)
    ax.set_facecolor(bg)

    labels = [i[0] for i in items]
    aligned = [i[1] for i in items]
    ypos = list(range(len(labels)))

    ax.barh(ypos, [100] * len(labels), height=0.5, color=colors["secondary"], alpha=0.15)
    bars = ax.barh(ypos, aligned, height=0.5, color=colors["env"], alpha=0.92)
    for y, v in zip(ypos, aligned):
        ax.text(v + 2, y, LB["tax_aligned"].format(v=v), va="center", fontsize=9.5,
                color=colors["text"], fontweight="bold")

    ax.set_yticks(ypos)
    ax.set_yticklabels(labels, color=colors["text"], fontsize=10, fontweight="bold")
    ax.set_xlim(0, 100)
    ax.set_xlabel(LB["tax_x"], color=colors["text"], fontsize=9)
    ax.tick_params(colors=colors["text"])
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.spines['bottom'].set_color(colors["secondary"])

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=bg, edgecolor='none')
    plt.close()
    buf.seek(0)
    return buf.read()


def gauge_chart(score: float, label: str, theme: AestheticTheme) -> bytes:
    colors = get_colors(theme)
    bg = colors["bg"]

    fig, ax = plt.subplots(figsize=(5, 3.5), facecolor=bg)
    ax.set_facecolor(bg)
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-0.2, 1.3)
    ax.axis('off')

    # Background arc
    theta = [math.pi + (0 - math.pi) * i / 99 for i in range(100)]
    ax.plot([math.cos(t) for t in theta], [math.sin(t) for t in theta],
            linewidth=20, color='#E0E0E0', solid_capstyle='butt')

    # Score arc
    score_angle = math.pi * (1 - score / 100)
    theta_score = [math.pi + (score_angle - math.pi) * i / 99 for i in range(100)]
    if score >= 75:
        color = colors["env"]
    elif score >= 50:
        color = colors["accent"]
    else:
        color = "#E74C3C"

    ax.plot([math.cos(t) for t in theta_score], [math.sin(t) for t in theta_score],
            linewidth=20, color=color, solid_capstyle='butt')

    ax.text(0, 0.3, f'{score:.0f}', ha='center', va='center',
            fontsize=36, fontweight='bold', color=colors["text"])
    ax.text(0, 0.05, '/100', ha='center', va='center',
            fontsize=14, color=colors["secondary"])
    ax.text(0, -0.1, label, ha='center', va='center',
            fontsize=12, fontweight='bold', color=colors["text"])

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor=bg, edgecolor='none')
    plt.close()
    buf.seek(0)
    return buf.read()


def benchmark_chart(comp: dict, theme: AestheticTheme, light_bg: bool = False, lang: str = 'fr', brand: dict = None) -> bytes:
    """Barres des trois piliers + score global, série unique.

    La série « Secteur » a été retirée : elle s'appuyait sur une table de
    moyennes sectorielles inventée (cf. note dans esg_advanced.py). Ce qui
    reste est vrai sans référence externe — les scores de l'entreprise, et
    l'écart de chaque pilier au meilleur des trois.
    """
    colors = get_colors(theme, light_bg, brand)
    LB = L(lang)
    bg = colors["bg"]
    fig, ax = plt.subplots(figsize=(7.4, 4.6), facecolor=bg)
    ax.set_facecolor(bg)

    cats = [LB["chart_env"], LB["chart_soc"], LB["chart_gov"], LB["chart_global"]]
    keys = ["env", "social", "gov", "global"]
    vals = [comp[k] for k in keys]
    ypos = list(range(len(cats)))
    bar_cols = [colors["env"], colors["social"], colors["gov"], colors["accent"]]

    ax.barh(ypos, vals, height=0.5, color=bar_cols, zorder=3)
    meilleur = max(vals[:3])          # meilleur des trois piliers, hors global
    for y, v in enumerate(vals):
        ax.text(v + 1.5, y, f"{v:.0f}", va="center", fontsize=11,
                fontweight="bold", color=colors["text"])
        if y < 3:                     # écart interne : sur les piliers seulement
            d = v - meilleur
            ax.text(107, y, LB["bench_best"] if d == 0 else f"{d:.0f} pts",
                    va="center", ha="right", fontsize=9.5,
                    fontweight="bold" if d == 0 else "normal",
                    color=colors["env"] if d == 0 else colors["secondary"])

    ax.set_yticks(ypos); ax.set_yticklabels(cats, color=colors["text"], fontsize=11)
    ax.set_xlim(0, 112); ax.set_ylim(-0.6, len(cats) - 0.4)
    ax.set_xlabel(LB["chart_score_axis"], color=colors["text"], fontsize=10)
    ax.tick_params(colors=colors["text"])
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(colors["secondary"])
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=bg, edgecolor="none")
    plt.close()
    buf.seek(0)
    return buf.read()
