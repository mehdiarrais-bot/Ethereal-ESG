"""
Analyses ESG avancées, alignées sur les référentiels CSRD/ESRS, TCFD et SBTi.
Tout est dérivé localement des données saisies — aucune donnée externe.

- Double matérialité : positionnement des enjeux (impact vs. financier)
- Objectifs & trajectoire : cibles par pilier + trajectoire carbone type SBTi
- Taxonomie UE : synthèse CA / CapEx / OpEx alignés
"""
import hashlib
from models import ESGRequest, ESGScores


def _seed(name: str) -> float:
    """Petite variation déterministe par entreprise (0..1)."""
    return (int(hashlib.md5(name.encode()).hexdigest(), 16) % 1000) / 1000.0


def _clamp(v, lo=0.5, hi=9.5):
    return max(lo, min(hi, v))


def materiality_topics(request: ESGRequest, scores: ESGScores) -> list:
    """Retourne les enjeux ESG positionnés sur la matrice de double matérialité.

    Chaque enjeu : {label, impact, financial, pillar}
    - impact (0-10)   : importance de l'impact de l'entreprise sur la société/environnement
    - financial (0-10): importance financière de l'enjeu pour l'entreprise
    Un score faible sur le pilier => enjeu plus matériel (davantage à risque / à traiter).
    """
    env, soc, gov = request.environmental, request.social, request.governance
    jit = (_seed(request.company.name) - 0.5) * 1.2  # +/- 0.6 de décalage

    def inv(score):  # score bas -> matérialité haute
        return _clamp(9.5 - (score / 100.0) * 6.0 + jit)

    topics = []

    # ── Environnement ──────────────────────────────────────────────
    e = scores.environmental_score
    # Changement climatique (ESRS E1) : toujours financièrement très matériel
    climate_impact = 9.0 if (env.co2_emissions_tonnes or 0) > 0 else 7.5
    topics.append({"label": "Changement climatique", "impact": _clamp(climate_impact + jit),
                   "financial": _clamp(8.7 + jit * 0.5), "pillar": "env"})
    # Énergie
    topics.append({"label": "Énergie & renouvelables",
                   "impact": inv(env.renewable_energy_percent if env.renewable_energy_percent is not None else e),
                   "financial": _clamp(7.0 + jit), "pillar": "env"})
    # Eau & ressources / économie circulaire (ESRS E3/E5)
    topics.append({"label": "Eau & économie circulaire",
                   "impact": inv(env.waste_recycled_percent if env.waste_recycled_percent is not None else e),
                   "financial": _clamp(5.2 + jit), "pillar": "env"})
    # Biodiversité (ESRS E4)
    topics.append({"label": "Biodiversité", "impact": _clamp(5.5 + jit),
                   "financial": _clamp(4.0 + jit), "pillar": "env"})

    # ── Social ─────────────────────────────────────────────────────
    sc = scores.social_score
    topics.append({"label": "Capital humain & formation", "impact": inv(sc),
                   "financial": _clamp(7.2 + jit), "pillar": "social"})
    topics.append({"label": "Santé & sécurité",
                   "impact": inv(100 - min(100, (soc.accident_frequency_rate or 3) * 10)),
                   "financial": _clamp(6.4 + jit), "pillar": "social"})
    topics.append({"label": "Diversité & inclusion",
                   "impact": inv(soc.female_employees_percent if soc.female_employees_percent is not None else sc),
                   "financial": _clamp(5.0 + jit), "pillar": "social"})

    # ── Gouvernance ────────────────────────────────────────────────
    g = scores.governance_score
    topics.append({"label": "Éthique des affaires", "impact": inv(g),
                   "financial": _clamp(7.8 + jit), "pillar": "gov"})
    topics.append({"label": "Cybersécurité & données",
                   "impact": _clamp(6.0 + (gov.data_breaches or 0) * 1.5 + jit),
                   "financial": _clamp(7.5 + jit), "pillar": "gov"})
    return topics


def esg_targets(request: ESGRequest, scores: ESGScores) -> dict:
    """Objectifs par pilier + trajectoire carbone (type SBTi 1,5°C : -42% à 2030)."""
    base_year = request.company.reporting_year
    target_year = max(request.company.target_year, base_year + 1)

    def uplift(cur):
        gap = 100 - cur
        return round(min(100, cur + gap * 0.45 + 5), 0)

    pillars = [
        {"label": "Environnement", "current": scores.environmental_score,
         "target": uplift(scores.environmental_score), "color": "env"},
        {"label": "Social", "current": scores.social_score,
         "target": uplift(scores.social_score), "color": "social"},
        {"label": "Gouvernance", "current": scores.governance_score,
         "target": uplift(scores.governance_score), "color": "gov"},
        {"label": "Score global", "current": scores.total_esg_score,
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
