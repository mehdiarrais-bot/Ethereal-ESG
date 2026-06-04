from models import ESGRequest, ESGScores, EnvironmentalData, SocialData, GovernanceData
from typing import List, Tuple
import math


def score_metric(value: float, thresholds: List[Tuple[float, float]], higher_is_better: bool = True) -> float:
    """Normalize a metric to a 0-100 score."""
    if value is None:
        return 50.0
    for threshold, score in thresholds:
        if higher_is_better:
            if value >= threshold:
                return score
        else:
            if value <= threshold:
                return score
    return thresholds[-1][1]


def calculate_environmental_score(env: EnvironmentalData, revenue: float = None) -> Tuple[float, dict]:
    scores = {}
    details = {}

    # Renewable energy score (higher = better)
    if env.renewable_energy_percent is not None:
        scores["renewable"] = score_metric(env.renewable_energy_percent, [
            (80, 100), (60, 80), (40, 60), (20, 40), (0, 20)
        ])
        details["renewable_energy"] = env.renewable_energy_percent

    # Waste recycling score
    if env.waste_recycled_percent is not None:
        scores["recycling"] = score_metric(env.waste_recycled_percent, [
            (80, 100), (60, 80), (40, 60), (20, 40), (0, 20)
        ])
        details["waste_recycled"] = env.waste_recycled_percent

    # Carbon intensity (lower = better)
    carbon_intensity = None
    if env.co2_emissions_tonnes and revenue:
        carbon_intensity = (env.co2_emissions_tonnes / revenue) * 1_000_000
        scores["carbon"] = score_metric(carbon_intensity, [
            (10, 100), (50, 80), (100, 60), (500, 40), (1000, 20)
        ], higher_is_better=False)
        details["carbon_intensity"] = round(carbon_intensity, 2)

    # Scope completeness bonus
    if env.scope1_emissions is not None and env.scope2_emissions is not None and env.scope3_emissions is not None:
        scores["scope_reporting"] = 80
    elif env.co2_emissions_tonnes is not None:
        scores["scope_reporting"] = 60

    # Energy intensity
    energy_intensity = None
    if env.energy_consumption_mwh and revenue:
        energy_intensity = (env.energy_consumption_mwh / revenue) * 1_000_000
        details["energy_intensity"] = round(energy_intensity, 2)

    # Biodiversity
    if env.biodiversity_initiatives is not None:
        scores["biodiversity"] = min(100, env.biodiversity_initiatives * 20)

    if not scores:
        return 50.0, details

    env_score = sum(scores.values()) / len(scores)
    return round(env_score, 1), details


def calculate_social_score(social: SocialData) -> Tuple[float, dict]:
    scores = {}
    details = {}

    # Gender parity
    gender_parity = None
    if social.female_employees_percent is not None:
        gender_parity = social.female_employees_percent
        scores["gender"] = score_metric(social.female_employees_percent, [
            (45, 100), (35, 80), (25, 60), (15, 40), (0, 20)
        ])
        details["female_percent"] = social.female_employees_percent

    # Low turnover (lower = better)
    if social.employee_turnover_percent is not None:
        scores["turnover"] = score_metric(social.employee_turnover_percent, [
            (5, 100), (10, 80), (15, 60), (20, 40), (30, 20)
        ], higher_is_better=False)

    # Training investment
    if social.training_hours_per_employee is not None:
        scores["training"] = score_metric(social.training_hours_per_employee, [
            (40, 100), (30, 80), (20, 60), (10, 40), (0, 20)
        ])
        details["training_hours"] = social.training_hours_per_employee

    # Safety (lower accidents = better)
    if social.accident_frequency_rate is not None:
        scores["safety"] = score_metric(social.accident_frequency_rate, [
            (1, 100), (3, 80), (5, 60), (8, 40), (15, 20)
        ], higher_is_better=False)
        details["accident_rate"] = social.accident_frequency_rate

    # Customer satisfaction
    if social.customer_satisfaction_score is not None:
        scores["satisfaction"] = score_metric(social.customer_satisfaction_score, [
            (8.5, 100), (7.5, 80), (6.5, 60), (5.5, 40), (0, 20)
        ])

    # Community investment
    if social.community_investment_eur is not None and social.community_investment_eur > 0:
        scores["community"] = min(100, (social.community_investment_eur / 100000) * 20)

    if not scores:
        return 50.0, details

    social_score = sum(scores.values()) / len(scores)
    return round(social_score, 1), details


def calculate_governance_score(gov: GovernanceData) -> Tuple[float, dict]:
    scores = {}
    details = {}

    # Board gender diversity
    if gov.female_board_percent is not None:
        scores["board_gender"] = score_metric(gov.female_board_percent, [
            (40, 100), (30, 80), (20, 60), (10, 40), (0, 20)
        ])
        details["female_board"] = gov.female_board_percent

    # Board independence
    if gov.independent_board_percent is not None:
        scores["independence"] = score_metric(gov.independent_board_percent, [
            (60, 100), (50, 80), (40, 60), (30, 40), (0, 20)
        ])

    # Ethics violations (lower = better)
    if gov.ethics_violations is not None:
        scores["ethics"] = 100 if gov.ethics_violations == 0 else max(0, 100 - gov.ethics_violations * 20)

    # Data security
    if gov.data_breaches is not None:
        scores["security"] = 100 if gov.data_breaches == 0 else max(0, 100 - gov.data_breaches * 30)

    # ESG audit bonus
    if gov.esg_audit_conducted is True:
        scores["audit"] = 100
    elif gov.esg_audit_conducted is False:
        scores["audit"] = 20

    # Sustainability committee
    if gov.sustainability_committee is True:
        scores["committee"] = 100
    elif gov.sustainability_committee is False:
        scores["committee"] = 20

    # CSR budget
    if gov.csr_budget_eur is not None and gov.csr_budget_eur > 0:
        scores["csr_budget"] = min(100, (gov.csr_budget_eur / 500000) * 100)

    if not scores:
        return 50.0, details

    gov_score = sum(scores.values()) / len(scores)
    return round(gov_score, 1), details


def get_rating(score: float) -> str:
    if score >= 85:
        return "AAA"
    elif score >= 75:
        return "AA"
    elif score >= 65:
        return "A"
    elif score >= 55:
        return "BBB"
    elif score >= 45:
        return "BB"
    elif score >= 35:
        return "B"
    else:
        return "CCC"


def generate_strengths(env_score, social_score, gov_score, env: EnvironmentalData, social: SocialData, gov: GovernanceData) -> List[str]:
    strengths = []
    if env_score >= 70:
        strengths.append("Excellente performance environnementale")
    if env.renewable_energy_percent and env.renewable_energy_percent >= 50:
        strengths.append(f"Fort taux d'énergie renouvelable ({env.renewable_energy_percent}%)")
    if social.female_employees_percent and social.female_employees_percent >= 40:
        strengths.append("Bonne parité homme-femme dans les effectifs")
    if social.training_hours_per_employee and social.training_hours_per_employee >= 30:
        strengths.append("Investissement significatif dans la formation")
    if gov.esg_audit_conducted:
        strengths.append("Audit ESG conduit — transparence renforcée")
    if gov.sustainability_committee:
        strengths.append("Comité de durabilité opérationnel")
    if social_score >= 70:
        strengths.append("Politique sociale exemplaire")
    if gov_score >= 70:
        strengths.append("Gouvernance de haute qualité")
    if not strengths:
        strengths.append("Démarche ESG en cours de structuration")
    return strengths[:5]


def generate_weaknesses(env_score, social_score, gov_score, env: EnvironmentalData, social: SocialData, gov: GovernanceData) -> List[str]:
    weaknesses = []
    if env_score < 50:
        weaknesses.append("Performance environnementale à améliorer")
    if env.renewable_energy_percent and env.renewable_energy_percent < 30:
        weaknesses.append("Faible part d'énergie renouvelable")
    if env.scope3_emissions is None:
        weaknesses.append("Scope 3 non mesuré — angle mort carbone")
    if social.female_employees_percent and social.female_employees_percent < 30:
        weaknesses.append("Déséquilibre de genre dans les effectifs")
    if social.accident_frequency_rate and social.accident_frequency_rate > 5:
        weaknesses.append("Taux d'accidents supérieur aux standards sectoriels")
    if gov.ethics_violations and gov.ethics_violations > 0:
        weaknesses.append("Incidents éthiques à traiter")
    if not gov.esg_audit_conducted:
        weaknesses.append("Absence d'audit ESG indépendant")
    if gov_score < 50:
        weaknesses.append("Structure de gouvernance à renforcer")
    return weaknesses[:5]


def generate_recommendations(env: EnvironmentalData, social: SocialData, gov: GovernanceData) -> List[str]:
    recs = []
    if env.renewable_energy_percent is None or env.renewable_energy_percent < 50:
        recs.append("Augmenter la part d'énergie renouvelable à 50% d'ici 2027")
    if env.scope3_emissions is None:
        recs.append("Mettre en place la mesure et le reporting des émissions Scope 3")
    if social.female_employees_percent is None or social.female_employees_percent < 40:
        recs.append("Définir des objectifs chiffrés de parité femme-homme")
    if social.training_hours_per_employee is None or social.training_hours_per_employee < 20:
        recs.append("Porter les heures de formation à 20h/employé/an minimum")
    if not gov.esg_audit_conducted:
        recs.append("Commander un audit ESG indépendant annuel")
    if not gov.sustainability_committee:
        recs.append("Créer un comité de durabilité au niveau du conseil")
    if env.waste_recycled_percent is None or env.waste_recycled_percent < 60:
        recs.append("Viser 60% de taux de recyclage des déchets")
    recs.append("Aligner la stratégie ESG sur les ODD de l'ONU et les recommandations TCFD")
    return recs[:6]


def calculate_esg_scores(request: ESGRequest) -> ESGScores:
    revenue = request.company.revenue_eur

    env_score, env_details = calculate_environmental_score(request.environmental, revenue)
    social_score, social_details = calculate_social_score(request.social)
    gov_score, gov_details = calculate_governance_score(request.governance)

    total = round((env_score * 0.40 + social_score * 0.35 + gov_score * 0.25), 1)
    rating = get_rating(total)

    strengths = generate_strengths(env_score, social_score, gov_score, request.environmental, request.social, request.governance)
    weaknesses = generate_weaknesses(env_score, social_score, gov_score, request.environmental, request.social, request.governance)
    recommendations = generate_recommendations(request.environmental, request.social, request.governance)

    return ESGScores(
        environmental_score=env_score,
        social_score=social_score,
        governance_score=gov_score,
        total_esg_score=total,
        carbon_intensity=env_details.get("carbon_intensity"),
        energy_intensity=env_details.get("energy_intensity"),
        gender_parity_index=social_details.get("female_percent"),
        safety_index=social_details.get("accident_rate"),
        governance_quality=gov_score,
        rating=rating,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=recommendations,
    )
