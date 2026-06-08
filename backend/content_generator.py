"""
Générateur de contenu ESG 100% local — aucune API externe requise.
Produit des textes professionnels et contextualisés à partir des données saisies.
"""
from models import ESGRequest, ESGScores


def _fmt_num(v, suffix="", decimals=0):
    if v is None:
        return "—"
    fmt = f"{v:,.{decimals}f}"
    return f"{fmt}{suffix}"


def generate_esg_content(request: ESGRequest, scores: ESGScores) -> dict:
    company = request.company
    env = request.environmental
    soc = request.social
    gov = request.governance
    year = company.reporting_year

    # ── Descriptions des niveaux de performance ───────────────────────────
    perf_desc = {
        "AAA": "performance de premier plan, en ligne avec les leaders mondiaux ESG",
        "AA":  "très bonne performance, dépassant les standards sectoriels",
        "A":   "bonne performance, au-dessus de la moyenne du secteur",
        "BBB": "performance satisfaisante, avec des marges de progression identifiées",
        "BB":  "performance en développement — un plan d'action structuré est engagé",
        "B":   "performance limitée — une transformation de fond est nécessaire",
        "CCC": "performance insuffisante — mobilisation urgente requise sur tous les piliers",
    }
    perf = perf_desc.get(scores.rating, "performance mesurée")

    pillar_comment = ""
    best = max(
        ("Environnemental", scores.environmental_score),
        ("Social", scores.social_score),
        ("Gouvernance", scores.governance_score),
        key=lambda x: x[1]
    )
    worst = min(
        ("Environnemental", scores.environmental_score),
        ("Social", scores.social_score),
        ("Gouvernance", scores.governance_score),
        key=lambda x: x[1]
    )
    pillar_comment = (
        f"Le pilier {best[0]} ({best[1]:.0f}/100) constitue le principal atout, "
        f"tandis que le pilier {worst[0]} ({worst[1]:.0f}/100) "
        f"représente le principal levier de progression."
    )

    # ── Synthèse exécutive ────────────────────────────────────────────────
    executive_summary = (
        f"{company.name} publie son rapport ESG pour l'exercice {year} "
        f"(secteur : {company.sector}, {company.country}). "
        f"L'analyse extra-financière conduite sur les trois piliers aboutit à un score global de "
        f"{scores.total_esg_score:.1f}/100, correspondant à une notation {scores.rating} — "
        f"soit une {perf}. "
        f"{pillar_comment}"
    )

    # ── Environnement ────────────────────────────────────────────────────
    env_items = []
    if env.co2_emissions_tonnes:
        env_items.append(f"{env.co2_emissions_tonnes:,.0f} t CO₂e d'émissions totales")
    if env.scope1_emissions and env.scope2_emissions and env.scope3_emissions:
        total = env.scope1_emissions + env.scope2_emissions + env.scope3_emissions
        env_items.append(
            f"bilan carbone complet Scope 1/2/3 "
            f"({env.scope1_emissions:,.0f} / {env.scope2_emissions:,.0f} / {env.scope3_emissions:,.0f} t)"
        )
    if env.renewable_energy_percent is not None:
        trend = "en progression" if env.renewable_energy_percent >= 40 else "à accélérer"
        env_items.append(f"{env.renewable_energy_percent:.0f}% d'énergie renouvelable ({trend})")
    if env.energy_consumption_mwh:
        env_items.append(f"consommation énergétique de {env.energy_consumption_mwh:,.0f} MWh")
    if env.water_consumption_m3:
        env_items.append(f"prélèvement d'eau de {env.water_consumption_m3:,.0f} m³")
    if env.waste_recycled_percent is not None:
        env_items.append(f"taux de recyclage des déchets de {env.waste_recycled_percent:.0f}%")
    if env.biodiversity_initiatives:
        env_items.append(f"{env.biodiversity_initiatives} initiative(s) biodiversité engagée(s)")

    if env_items:
        env_detail = "Les principaux indicateurs recensés sont : " + ", ".join(env_items) + ". "
    else:
        env_detail = "Le périmètre de reporting environnemental est en cours de structuration. "

    env_outlook = ""
    if env.renewable_energy_percent is not None and env.renewable_energy_percent < 50:
        env_outlook = (
            f"L'augmentation du taux d'énergie renouvelable vers 50% constitue la priorité "
            f"environnementale pour les prochains exercices. "
        )
    if env.scope3_emissions is None:
        env_outlook += "L'intégration du Scope 3 dans le reporting carbone est recommandée pour disposer d'un bilan complet."

    environmental = (
        f"Sur le plan environnemental, {company.name} obtient un score de "
        f"{scores.environmental_score:.0f}/100. "
        + env_detail
        + env_outlook.strip()
    )

    # ── Social ─────────────────────────────────────────────────────────────
    soc_items = []
    if soc.total_employees:
        soc_items.append(f"{soc.total_employees:,} collaborateurs")
    if soc.female_employees_percent is not None:
        gap = 40 - soc.female_employees_percent
        mention = f"{'objectif 40% presque atteint' if gap <= 3 else f'écart de {gap:.0f}pts vs objectif 40%'}"
        soc_items.append(f"{soc.female_employees_percent:.0f}% de femmes dans les effectifs ({mention})")
    if soc.training_hours_per_employee is not None:
        soc_items.append(f"{soc.training_hours_per_employee:.0f} heures de formation par collaborateur et par an")
    if soc.accident_frequency_rate is not None:
        level = "excellent" if soc.accident_frequency_rate < 2 else ("satisfaisant" if soc.accident_frequency_rate < 5 else "à améliorer")
        soc_items.append(f"taux de fréquence des accidents de {soc.accident_frequency_rate:.1f} ({level})")
    if soc.employee_turnover_percent is not None:
        soc_items.append(f"turnover de {soc.employee_turnover_percent:.0f}%")
    if soc.community_investment_eur:
        soc_items.append(f"{soc.community_investment_eur:,.0f} € investis dans la communauté")
    if soc.customer_satisfaction_score:
        soc_items.append(f"satisfaction client de {soc.customer_satisfaction_score:.1f}/10")

    if soc_items:
        soc_detail = "Les indicateurs clés de la performance sociale couvrent : " + ", ".join(soc_items) + ". "
    else:
        soc_detail = "Les indicateurs sociaux sont en cours de formalisation. "

    social = (
        f"La performance sociale de {company.name} atteint {scores.social_score:.0f}/100. "
        + soc_detail
        + "La stratégie RH s'articule autour de l'attractivité des talents, "
        "la promotion de la diversité et de l'inclusion, et l'amélioration continue de la sécurité au travail."
    )

    # ── Gouvernance ────────────────────────────────────────────────────────
    gov_items = []
    if gov.board_members:
        gov_items.append(f"Conseil d'Administration de {gov.board_members} membres")
    if gov.female_board_percent is not None:
        law_status = "conforme loi Rixain (≥40%)" if gov.female_board_percent >= 40 else f"objectif légal 40% — {40 - gov.female_board_percent:.0f}pts à combler"
        gov_items.append(f"{gov.female_board_percent:.0f}% de femmes au CA ({law_status})")
    if gov.independent_board_percent is not None:
        afep = "conforme AFEP-MEDEF (≥50%)" if gov.independent_board_percent >= 50 else "en-dessous des recommandations AFEP-MEDEF"
        gov_items.append(f"{gov.independent_board_percent:.0f}% d'administrateurs indépendants ({afep})")
    if gov.csr_budget_eur:
        gov_items.append(f"budget RSE de {gov.csr_budget_eur:,.0f} €")
    if gov.ethics_violations is not None:
        gov_items.append(f"{gov.ethics_violations} violation(s) du code d'éthique")
    if gov.data_breaches is not None and gov.data_breaches > 0:
        gov_items.append(f"{gov.data_breaches} incident(s) de cybersécurité enregistré(s)")

    audit_sentence = (
        "Un audit ESG indépendant a été conduit, renforçant la crédibilité et la transparence du reporting extra-financier. "
        if gov.esg_audit_conducted else
        "La conduite d'un audit ESG indépendant est recommandée pour renforcer la crédibilité du reporting. "
    )
    committee_sentence = (
        "Un comité de durabilité opérationnel au niveau du Conseil assure la supervision stratégique des enjeux ESG."
        if gov.sustainability_committee else
        "La mise en place d'un comité de durabilité au niveau du Conseil est fortement recommandée."
    )

    if gov_items:
        gov_detail = "La structure de gouvernance s'appuie sur : " + ", ".join(gov_items) + ". "
    else:
        gov_detail = "La structure de gouvernance est en cours de documentation. "

    governance = (
        f"Le pilier Gouvernance enregistre un score de {scores.governance_score:.0f}/100. "
        + gov_detail
        + audit_sentence
        + committee_sentence
    )

    # ── Conclusion ─────────────────────────────────────────────────────────
    n_strengths = len(scores.strengths)
    n_weaknesses = len(scores.weaknesses)
    n_recs = len(scores.recommendations)

    trajectory = (
        "témoigne d'une démarche ESG mature et structurée"
        if scores.total_esg_score >= 70 else
        "s'est engagée dans une démarche de transformation durable"
        if scores.total_esg_score >= 50 else
        "a initié une réflexion ESG qui nécessite d'être amplifiée"
    )

    conclusion = (
        f"Fort d'un score ESG global de {scores.total_esg_score:.1f}/100 (note {scores.rating}), "
        f"{company.name} {trajectory}. "
        f"L'analyse a mis en évidence {n_strengths} point(s) fort(s) sur lesquels capitaliser "
        f"et {n_weaknesses} axe(s) d'amélioration à prioriser. "
        f"Les {n_recs} recommandations formulées constituent la feuille de route ESG pour les prochains exercices. "
        f"L'organisation réaffirme son engagement envers la transparence de son reporting extra-financier, "
        f"en alignement avec les référentiels GRI Standards, TCFD, CSRD et les ODD des Nations Unies."
    )

    return {
        "executive_summary": executive_summary,
        "environmental": environmental,
        "social": social,
        "governance": governance,
        "conclusion": conclusion,
    }
