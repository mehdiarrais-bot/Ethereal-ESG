import os
from anthropic import Anthropic
from models import ESGRequest, ESGScores

client = Anthropic()


def generate_esg_content(request: ESGRequest, scores: ESGScores) -> dict:
    """Generate AI narrative content for ESG reports."""
    company = request.company
    lang = "français" if request.language == "fr" else "English"

    env = request.environmental
    soc = request.social
    gov = request.governance

    env_facts = []
    if env.co2_emissions_tonnes:
        env_facts.append(f"émissions CO₂: {env.co2_emissions_tonnes:,.0f} t")
    if env.renewable_energy_percent:
        env_facts.append(f"énergie renouvelable: {env.renewable_energy_percent}%")
    if env.waste_recycled_percent:
        env_facts.append(f"recyclage: {env.waste_recycled_percent}%")

    soc_facts = []
    if soc.total_employees:
        soc_facts.append(f"{soc.total_employees:,} employés")
    if soc.female_employees_percent:
        soc_facts.append(f"{soc.female_employees_percent}% de femmes")
    if soc.training_hours_per_employee:
        soc_facts.append(f"{soc.training_hours_per_employee}h de formation/an")

    gov_facts = []
    if gov.female_board_percent:
        gov_facts.append(f"{gov.female_board_percent}% de femmes au CA")
    if gov.esg_audit_conducted:
        gov_facts.append("audit ESG conduit")
    if gov.sustainability_committee:
        gov_facts.append("comité durabilité en place")

    prompt = f"""Tu es un expert ESG/RSE rédigeant un rapport professionnel en {lang}.

Entreprise: {company.name}
Secteur: {company.sector}
Pays: {company.country}
Année: {company.reporting_year}

Scores ESG calculés:
- Environnement: {scores.environmental_score}/100
- Social: {scores.social_score}/100
- Gouvernance: {scores.governance_score}/100
- Score global: {scores.total_esg_score}/100 (Note: {scores.rating})

Données clés:
- Environnement: {', '.join(env_facts) if env_facts else 'données limitées'}
- Social: {', '.join(soc_facts) if soc_facts else 'données limitées'}
- Gouvernance: {', '.join(gov_facts) if gov_facts else 'données limitées'}

Points forts: {', '.join(scores.strengths[:3])}
Points faibles: {', '.join(scores.weaknesses[:3])}

Rédige en {lang} les sections suivantes pour un rapport ESG professionnel.
Chaque section doit être factuelle, professionnelle, concise (2-3 phrases max par section).
Réponds UNIQUEMENT en JSON avec ces clés:
{{
  "executive_summary": "...",
  "environmental": "...",
  "social": "...",
  "governance": "...",
  "conclusion": "..."
}}"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        text = message.content[0].text.strip()
        # Extract JSON from response
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
    except Exception as e:
        print(f"AI content generation error: {e}")

    # Fallback content
    return {
        "executive_summary": (
            f"{company.name} présente son rapport ESG {company.reporting_year} avec un score global de "
            f"{scores.total_esg_score}/100 (note {scores.rating}). Cette performance témoigne de l'engagement "
            "de l'entreprise en faveur du développement durable et de la responsabilité sociale."
        ),
        "environmental": (
            "L'analyse des données environnementales met en lumière les efforts déployés pour réduire "
            "l'empreinte écologique de l'organisation, notamment en matière d'émissions de GES et de consommation d'énergie."
        ),
        "social": (
            "La politique sociale de l'entreprise se traduit par des investissements dans le capital humain, "
            "la promotion de la diversité et l'amélioration des conditions de travail."
        ),
        "governance": (
            "La structure de gouvernance garantit la transparence et l'intégrité des pratiques d'affaires, "
            "avec des mécanismes de contrôle robustes et un engagement fort envers l'éthique."
        ),
        "conclusion": (
            f"{company.name} réaffirme son engagement vers un modèle d'affaires durable et responsable. "
            "Les axes d'amélioration identifiés feront l'objet de plans d'action concrets pour les prochains exercices."
        ),
    }
