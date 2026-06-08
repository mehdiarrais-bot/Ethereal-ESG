import os
from anthropic import Anthropic
from models import ESGRequest, ESGScores

_client = None

def get_client():
    global _client
    if _client is None:
        _client = Anthropic()
    return _client


def _rich_fallback(request: ESGRequest, scores: ESGScores) -> dict:
    """Generate contextual content from data without AI."""
    company = request.company
    env = request.environmental
    soc = request.social
    gov = request.governance
    year = company.reporting_year

    # Build contextual sentences from actual data
    env_details = []
    if env.co2_emissions_tonnes:
        env_details.append(f"{env.co2_emissions_tonnes:,.0f} t CO₂e d'émissions totales")
    if env.renewable_energy_percent:
        env_details.append(f"{env.renewable_energy_percent:.0f}% d'énergie renouvelable")
    if env.waste_recycled_percent:
        env_details.append(f"{env.waste_recycled_percent:.0f}% de taux de recyclage")
    if env.scope1_emissions and env.scope2_emissions and env.scope3_emissions:
        total_scope = env.scope1_emissions + env.scope2_emissions + env.scope3_emissions
        env_details.append(f"bilan carbone complet (Scopes 1+2+3 : {total_scope:,.0f} t)")

    soc_details = []
    if soc.total_employees:
        soc_details.append(f"{soc.total_employees:,} collaborateurs")
    if soc.female_employees_percent:
        soc_details.append(f"{soc.female_employees_percent:.0f}% de femmes dans les effectifs")
    if soc.training_hours_per_employee:
        soc_details.append(f"{soc.training_hours_per_employee:.0f} heures de formation par an et par salarié")
    if soc.accident_frequency_rate is not None:
        soc_details.append(f"taux de fréquence des accidents de {soc.accident_frequency_rate:.1f}")

    gov_details = []
    if gov.female_board_percent:
        gov_details.append(f"{gov.female_board_percent:.0f}% de femmes au Conseil d'Administration")
    if gov.independent_board_percent:
        gov_details.append(f"{gov.independent_board_percent:.0f}% d'administrateurs indépendants")
    if gov.csr_budget_eur:
        gov_details.append(f"un budget RSE de {gov.csr_budget_eur:,.0f} €")

    env_str = (", ".join(env_details) + ".") if env_details else "les données environnementales disponibles."
    soc_str = (", ".join(soc_details) + ".") if soc_details else "les indicateurs sociaux disponibles."
    gov_str = (", ".join(gov_details) + ".") if gov_details else "les mécanismes de gouvernance en place."

    rating_desc = {
        "AAA": "performance ESG de premier plan, en ligne avec les meilleures pratiques mondiales",
        "AA": "très bonne performance ESG, dépassant les standards sectoriels",
        "A": "bonne performance ESG, au-dessus de la moyenne sectorielle",
        "BBB": "performance ESG satisfaisante, avec des marges de progression identifiées",
        "BB": "performance ESG en développement, des axes d'amélioration significatifs existent",
        "B": "performance ESG limitée, nécessitant un plan d'action structuré",
        "CCC": "performance ESG insuffisante, une transformation profonde est nécessaire",
    }.get(scores.rating, "performance ESG mesurée")

    return {
        "executive_summary": (
            f"{company.name} publie son rapport ESG pour l'exercice {year}, "
            f"secteur {company.sector}, {company.country}. "
            f"L'analyse extra-financière conduite sur les trois piliers ESG aboutit à un score global de "
            f"{scores.total_esg_score:.1f}/100, correspondant à une notation {scores.rating} — soit une "
            f"{rating_desc}. "
            f"Le pilier Gouvernance ({scores.governance_score:.0f}/100) constitue le principal point fort, "
            f"tandis que les piliers Environnemental ({scores.environmental_score:.0f}/100) et "
            f"Social ({scores.social_score:.0f}/100) offrent des leviers d'amélioration."
        ),
        "environmental": (
            f"Sur le plan environnemental, {company.name} affiche un score de "
            f"{scores.environmental_score:.0f}/100. "
            f"L'analyse couvre : {env_str} "
            f"L'organisation s'est engagée dans la mesure et la réduction de son empreinte carbone, "
            f"avec une attention particulière portée à la transition énergétique et à l'économie circulaire. "
            f"Le renforcement du taux d'énergie renouvelable et la mesure complète des émissions Scope 3 "
            "restent des priorités pour les prochains exercices."
        ),
        "social": (
            f"La performance sociale de {company.name} atteint {scores.social_score:.0f}/100. "
            f"Les indicateurs clés recensés incluent : {soc_str} "
            f"La stratégie RH s'articule autour de trois axes : l'attractivité et la rétention des talents, "
            f"la promotion de la diversité et de l'inclusion, et la sécurité au travail. "
            f"L'engagement communautaire et la relation avec les fournisseurs locaux complètent ce dispositif."
        ),
        "governance": (
            f"Le pilier Gouvernance enregistre le score le plus élevé à {scores.governance_score:.0f}/100. "
            f"La structure de gouvernance repose sur : {gov_str} "
            + ("Un audit ESG indépendant a été conduit, renforçant la crédibilité du reporting extra-financier. "
               if gov.esg_audit_conducted else
               "La mise en place d'un audit ESG indépendant constituerait un signal fort de transparence. ")
            + ("Un comité de durabilité opérationnel au niveau du Conseil assure la supervision des enjeux ESG."
               if gov.sustainability_committee else
               "La création d'un comité de durabilité est recommandée pour ancrer les enjeux ESG au plus haut niveau.")
        ),
        "conclusion": (
            f"Fort d'un score ESG global de {scores.total_esg_score:.1f}/100 (note {scores.rating}), "
            f"{company.name} témoigne d'une démarche de responsabilité sociétale structurée et engagée. "
            f"Les {len(scores.strengths)} points forts identifiés reflètent les progrès accomplis, "
            f"tandis que les {len(scores.weaknesses)} axes d'amélioration tracent la feuille de route "
            f"pour les prochains exercices. "
            f"L'organisation s'engage à maintenir la transparence de son reporting extra-financier, "
            f"en alignement avec les standards GRI, TCFD et la directive CSRD."
        ),
    }


def generate_esg_content(request: ESGRequest, scores: ESGScores) -> dict:
    """Generate AI narrative content for ESG reports."""
    # Try AI first
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return _rich_fallback(request, scores)

    company = request.company
    lang = "français" if request.language == "fr" else "English"
    env = request.environmental
    soc = request.social
    gov = request.governance

    env_facts = []
    if env.co2_emissions_tonnes:
        env_facts.append(f"CO₂ : {env.co2_emissions_tonnes:,.0f} t")
    if env.renewable_energy_percent:
        env_facts.append(f"renouvelable : {env.renewable_energy_percent}%")
    if env.scope1_emissions and env.scope2_emissions and env.scope3_emissions:
        env_facts.append(f"Scope 1/2/3 : {env.scope1_emissions}/{env.scope2_emissions}/{env.scope3_emissions} t")
    if env.waste_recycled_percent:
        env_facts.append(f"recyclage : {env.waste_recycled_percent}%")

    soc_facts = []
    if soc.total_employees:
        soc_facts.append(f"{soc.total_employees:,} employés")
    if soc.female_employees_percent:
        soc_facts.append(f"{soc.female_employees_percent}% femmes")
    if soc.training_hours_per_employee:
        soc_facts.append(f"{soc.training_hours_per_employee}h formation/an")
    if soc.accident_frequency_rate is not None:
        soc_facts.append(f"TF accidents : {soc.accident_frequency_rate}")

    gov_facts = []
    if gov.female_board_percent:
        gov_facts.append(f"{gov.female_board_percent}% femmes CA")
    if gov.esg_audit_conducted:
        gov_facts.append("audit ESG oui")
    if gov.sustainability_committee:
        gov_facts.append("comité durabilité oui")
    if gov.data_breaches is not None:
        gov_facts.append(f"{gov.data_breaches} violation(s) données")

    prompt = f"""Expert ESG, rédige un rapport en {lang} pour {company.name} ({company.sector}, {company.country}, {company.reporting_year}).

Scores : E={scores.environmental_score}/100, S={scores.social_score}/100, G={scores.governance_score}/100, Total={scores.total_esg_score}/100 (note {scores.rating})
Données env : {', '.join(env_facts) if env_facts else 'limitées'}
Données soc : {', '.join(soc_facts) if soc_facts else 'limitées'}
Données gouv : {', '.join(gov_facts) if gov_facts else 'limitées'}
Forces : {', '.join(scores.strengths[:3])}
Faiblesses : {', '.join(scores.weaknesses[:3])}

Rédige 5 sections factuelles et professionnelles (2-3 phrases chacune), en JSON :
{{"executive_summary":"...","environmental":"...","social":"...","governance":"...","conclusion":"..."}}"""

    try:
        message = get_client().messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        import json
        text = message.content[0].text.strip()
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
    except Exception as e:
        print(f"AI content generation error: {e}")

    return _rich_fallback(request, scores)
