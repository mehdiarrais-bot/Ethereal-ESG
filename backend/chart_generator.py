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
}


def get_colors(theme: AestheticTheme) -> dict:
    return THEME_COLORS.get(theme, THEME_COLORS[AestheticTheme.CORPORATE_BLUE])


def radar_chart(scores: ESGScores, theme: AestheticTheme) -> bytes:
    colors = get_colors(theme)
    bg = colors["bg"]
    is_dark = theme == AestheticTheme.DARK_PREMIUM

    categories = ['Environnement', 'Social', 'Gouvernance']
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


def score_bars_chart(scores: ESGScores, theme: AestheticTheme) -> bytes:
    colors = get_colors(theme)
    bg = colors["bg"]

    fig, ax = plt.subplots(figsize=(8, 4), facecolor=bg)
    ax.set_facecolor(bg)

    categories = ['Environnement', 'Social', 'Gouvernance', 'Score Global']
    values = [scores.environmental_score, scores.social_score,
              scores.governance_score, scores.total_esg_score]
    bar_colors = [colors["env"], colors["social"], colors["gov"], colors["accent"]]

    bars = ax.barh(categories, values, color=bar_colors, height=0.5, alpha=0.9)

    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                f'{val:.1f}', va='center', ha='left',
                color=colors["text"], fontweight='bold', fontsize=11)

    ax.set_xlim(0, 110)
    ax.set_xlabel('Score / 100', color=colors["text"], fontsize=10)
    ax.tick_params(colors=colors["text"])
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.spines['bottom'].set_color(colors["secondary"])
    ax.set_facecolor(bg)
    for label in ax.get_yticklabels():
        label.set_color(colors["text"])
        label.set_fontsize(11)

    ax.axvline(x=50, color=colors["secondary"], linestyle='--', alpha=0.4, linewidth=1)
    ax.axvline(x=75, color=colors["accent"], linestyle='--', alpha=0.4, linewidth=1)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor=bg, edgecolor='none')
    plt.close()
    buf.seek(0)
    return buf.read()


def emissions_breakdown_chart(scope1, scope2, scope3, theme: AestheticTheme) -> bytes:
    colors = get_colors(theme)
    bg = colors["bg"]

    data = {}
    if scope1 is not None:
        data['Scope 1\n(Direct)'] = scope1
    if scope2 is not None:
        data['Scope 2\n(Énergie)'] = scope2
    if scope3 is not None:
        data['Scope 3\n(Indirect)'] = scope3

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

    ax.set_title('Répartition des émissions GES', color=colors["text"],
                 fontsize=12, fontweight='bold', pad=15)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor=bg, edgecolor='none')
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
