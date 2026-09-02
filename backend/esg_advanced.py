"""
Analyses ESG avancées, alignées sur les référentiels CSRD/ESRS, TCFD et SBTi.
Tout est dérivé localement des données saisies — aucune donnée externe.

- Priorisation des enjeux : positionnement (exposition vs. sensibilité
  économique), dérivé des indicateurs déclarés — PAS une double matérialité
  au sens de l'ESRS 1 (ni consultation des parties prenantes, ni cotation
  dédiée des impacts, risques et opportunités)
- Objectifs & trajectoire : cibles par pilier + trajectoire carbone type SBTi
- Taxonomie UE : synthèse CA / CapEx / OpEx alignés
"""
from models import ESGRequest, ESGScores


def _clamp(v, lo=0.5, hi=9.5):
    return max(lo, min(hi, v))


_MAT_LABELS = {
    "fr": ["Changement climatique", "Énergie & renouvelables", "Eau & économie circulaire",
           "Biodiversité", "Capital humain & formation", "Santé & sécurité",
           "Diversité & inclusion", "Éthique des affaires", "Cybersécurité & données"],
    "en": ["Climate change", "Energy & renewables", "Water & circular economy",
           "Biodiversity", "Human capital & training", "Health & safety",
           "Diversity & inclusion", "Business ethics", "Cybersecurity & data"],
}
_PILLAR_LABELS = {
    "fr": ["Environnement", "Social", "Gouvernance", "Score global"],
    "en": ["Environmental", "Social", "Governance", "Overall score"],
}


def materiality_topics(request: ESGRequest, scores: ESGScores, lang: str = "fr") -> list:
    """Positionne les enjeux ESG sur la cartographie de PRIORISATION.

    Ce n'est PAS une analyse de double matérialité au sens de l'ESRS 1 :
    il n'y a ni consultation de parties prenantes, ni cotation dédiée des
    impacts/risques/opportunités. Les deux dimensions sont estimées à
    partir des indicateurs déclarés et des scores par pilier — le texte
    généré (content_generator.deepen_content) doit le dire explicitement.

    Chaque enjeu : {label, impact, financial, pillar}
    - impact (0-10)   : exposition estimée de l'entreprise sur l'enjeu
    - financial (0-10): sensibilité économique estimée de l'enjeu
    Un score faible sur le pilier => enjeu plus prioritaire (davantage à
    risque / à traiter).
    """
    env, soc, gov = request.environmental, request.social, request.governance
    ML = _MAT_LABELS.get(lang, _MAT_LABELS["fr"])

    def inv(score):  # score bas -> priorité haute
        return _clamp(9.5 - (score / 100.0) * 6.0)

    topics = []

    # ── Environnement ──────────────────────────────────────────────
    e = scores.environmental_score
    # Changement climatique (ESRS E1) : toujours financièrement très matériel
    climate_impact = 9.0 if (env.co2_emissions_tonnes or 0) > 0 else 7.5
    topics.append({"label": ML[0], "impact": _clamp(climate_impact),
                   "financial": _clamp(8.7), "pillar": "env"})
    # Énergie
    topics.append({"label": ML[1],
                   "impact": inv(env.renewable_energy_percent if env.renewable_energy_percent is not None else e),
                   "financial": _clamp(7.0), "pillar": "env"})
    # Eau & ressources / économie circulaire (ESRS E3/E5)
    topics.append({"label": ML[2],
                   "impact": inv(env.waste_recycled_percent if env.waste_recycled_percent is not None else e),
                   "financial": _clamp(5.2), "pillar": "env"})
    # Biodiversité (ESRS E4)
    topics.append({"label": ML[3], "impact": _clamp(5.5),
                   "financial": _clamp(4.0), "pillar": "env"})

    # ── Social ─────────────────────────────────────────────────────
    sc = scores.social_score
    topics.append({"label": ML[4], "impact": inv(sc),
                   "financial": _clamp(7.2), "pillar": "social"})
    topics.append({"label": ML[5],
                   "impact": inv(100 - min(100, (soc.accident_frequency_rate or 3) * 10)),
                   "financial": _clamp(6.4), "pillar": "social"})
    topics.append({"label": ML[6],
                   "impact": inv(soc.female_employees_percent if soc.female_employees_percent is not None else sc),
                   "financial": _clamp(5.0), "pillar": "social"})

    # ── Gouvernance ────────────────────────────────────────────────
    g = scores.governance_score
    topics.append({"label": ML[7], "impact": inv(g),
                   "financial": _clamp(7.8), "pillar": "gov"})
    topics.append({"label": ML[8],
                   "impact": _clamp(6.0 + (gov.data_breaches or 0) * 1.5),
                   "financial": _clamp(7.5), "pillar": "gov"})
    return topics


def esg_targets(request: ESGRequest, scores: ESGScores, lang: str = "fr") -> dict:
    """Objectifs par pilier + trajectoire carbone (type SBTi 1,5°C : -42% à 2030)."""
    base_year = request.company.reporting_year
    PL = _PILLAR_LABELS.get(lang, _PILLAR_LABELS["fr"])
    target_year = max(request.company.target_year, base_year + 1)

    def uplift(cur):
        gap = 100 - cur
        return round(min(100, cur + gap * 0.45 + 5), 0)

    pillars = [
        {"label": PL[0], "current": scores.environmental_score,
         "target": uplift(scores.environmental_score), "color": "env"},
        {"label": PL[1], "current": scores.social_score,
         "target": uplift(scores.social_score), "color": "social"},
        {"label": PL[2], "current": scores.governance_score,
         "target": uplift(scores.governance_score), "color": "gov"},
        {"label": PL[3], "current": scores.total_esg_score,
         "target": uplift(scores.total_esg_score), "color": "accent"},
    ]

    # Trajectoire carbone SBTi : réduction linéaire -42% entre base et 2030
    carbon = None
    co2 = request.environmental.co2_emissions_tonnes
    if co2 and co2 > 0:
        sbti_year = 2030
        reduction = 0.42
        end = base_year if target_year <= base_year else min(target_year, sbti_year)
        if end <= base_year:
            end = base_year + 5
        years = list(range(base_year, end + 1))
        # interpolation linéaire jusqu'à -42% en 2030
        span = max(1, sbti_year - base_year)
        pts = []
        for y in years:
            frac = min(1.0, (y - base_year) / span)
            pts.append(round(co2 * (1 - reduction * frac)))
        carbon = {"years": years, "values": pts, "base": round(co2),
                  "target": round(co2 * (1 - reduction)), "reduction_pct": int(reduction * 100),
                  "target_year": sbti_year}

    return {"base_year": base_year, "target_year": target_year,
            "pillars": pillars, "carbon": carbon}


def taxonomy_summary(request: ESGRequest):
    """Synthèse Taxonomie UE si au moins un KPI est renseigné, sinon None."""
    t = request.taxonomy
    if t is None:
        return None
    vals = {
        "turnover": t.turnover_aligned_percent,
        "capex": t.capex_aligned_percent,
        "opex": t.opex_aligned_percent,
    }
    if all(v is None for v in vals.values()):
        return None
    return vals


# ══════════════════════════════════════════════════════════════════════════
# MATURITÉ ESG (diagnostic stratégique)
#
# NOTE : il n'y a volontairement PLUS de benchmark sectoriel ici. Le code
# portait une table SECTOR_BENCHMARKS de 15 triplets (E, S, G) écrits à la
# main, sans échantillon, sans méthode, sans date, sans source — et le
# livrable en imprimait des écarts chiffrés ("+13 pts au-dessus de la
# référence sectorielle"). Un chiffre inventé assorti d'un avertissement
# reste un chiffre inventé : la comparaison externe a été retirée, pas
# requalifiée. Le positionnement affiché est désormais interne (comparaison
# des trois piliers entre eux), ce qui est vrai sans référence externe.
# Une comparaison sourcée reste possible à terme : l'entreprise à
# elle-même, exercice après exercice (score_history) — cf. DETTE.md.
# ══════════════════════════════════════════════════════════════════════════

_MATURITY = [
    (0, 45, "initiated"), (45, 58, "structuring"), (58, 70, "structured"),
    (70, 82, "advanced"), (82, 101, "exemplary"),
]


def esg_maturity(request: ESGRequest, scores: ESGScores) -> dict:
    """Niveau de maturité ESG (5 stades) + progression vers le suivant."""
    sc = scores.total_esg_score
    stage = 0
    for i, (lo, hi, key) in enumerate(_MATURITY):
        if lo <= sc < hi:
            stage = i
            break
    lo, hi, key = _MATURITY[stage]
    nxt = _MATURITY[stage + 1][2] if stage < 4 else None
    progress = (sc - lo) / max(1, hi - lo)
    # signaux structurants (ce qui fait passer un cap)
    gaps = []
    if request.environmental.scope3_emissions is None:
        gaps.append("scope3")
    if not request.governance.esg_audit_conducted:
        gaps.append("audit")
    if not request.governance.sustainability_committee:
        gaps.append("committee")
    return {"stage": stage, "key": key, "next": nxt,
            "progress": round(min(1.0, progress), 2), "gaps": gaps}
