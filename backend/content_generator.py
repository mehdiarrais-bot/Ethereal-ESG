"""
Générateur de contenu ESG 100% local.
Produit des textes professionnels uniques par entreprise via variation
lexicale déterministe (seed basé sur le nom) + contexte sectoriel.
"""
import hashlib
from models import ESGRequest, ESGScores


def _seed(name: str) -> int:
    return int(hashlib.md5(name.encode()).hexdigest(), 16) % 10

def _pick(seed: int, offset: int, options: list):
    return options[(seed + offset) % len(options)]

def _fmt(v, suffix="", decimals=0):
    if v is None: return "—"
    return f"{v:,.{decimals}f}{suffix}"

SECTOR_CTX = {
    "Énergie": ("le secteur énergétique, exposé aux enjeux de transition bas-carbone", "la décarbonation de ses actifs"),
    "Finance": ("le secteur financier, vecteur du financement durable", "l'intégration ESG dans ses critères d'investissement"),
    "Industrie": ("l'industrie manufacturière, au cœur des défis d'efficacité carbone", "l'optimisation de son empreinte industrielle"),
    "BTP": ("le secteur du BTP, engagé dans la construction durable", "l'éco-conception et la réduction des déchets"),
    "Agroalimentaire": ("l'agroalimentaire, exposé aux risques biodiversité et eau", "la traçabilité de ses approvisionnements"),
    "Numérique": ("le secteur numérique, en croissance de son empreinte carbone", "l'efficacité énergétique de ses datacenters"),
    "Logistique": ("la logistique, secteur à forte intensité carbone", "la décarbonation de sa flotte et de ses flux"),
    "Pharmaceutique": ("le secteur pharmaceutique, aux standards élevés de gouvernance", "la gestion responsable de ses substances"),
    "Commerce": ("le commerce de détail, sous pression sur les chaînes d'approvisionnement", "la durabilité de sa chaîne de valeur amont"),
    "Chimie": ("l'industrie chimique, aux enjeux réglementaires majeurs", "la réduction de ses émissions polluantes"),
}

def _ctx(sector):
    for k, v in SECTOR_CTX.items():
        if k.lower() in sector.lower(): return v
    return ("son secteur d'activité", "l'amélioration continue de ses pratiques ESG")

EXEC_OPENINGS = [
    "{n} présente son rapport ESG {y}, affirmant sa position dans {ctx}.",
    "Dans le cadre de son engagement extra-financier, {n} publie son bilan ESG {y} pour {ctx}.",
    "{n} consolide pour l'exercice {y} son reporting de durabilité, ancré dans les réalités de {ctx}.",
    "L'exercice {y} marque une étape structurante dans la trajectoire ESG de {n}, acteur de {ctx}.",
    "Ce rapport ESG {y} reflète la stratégie de développement durable de {n} au sein de {ctx}.",
    "En qualité d'acteur de {ctx}, {n} rend compte pour {y} de ses engagements extra-financiers.",
    "La démarche RSE de {n} atteint en {y} un niveau de maturité documenté dans ce rapport ({ctx}).",
]

EXEC_SCORE_PHRASES = [
    "L'évaluation extra-financière aboutit à un score global de {sc}/100, note {r} — {p}.",
    "L'analyse multi-piliers positionne {n} à {sc}/100 ({r}), traduisant une {p}.",
    "La notation ESG consolidée s'établit à {sc}/100 ({r}), reflet d'une {p}.",
    "Avec {sc}/100 et une note {r}, {n} affiche une {p} sur l'ensemble du périmètre extra-financier.",
    "Le score composite {sc}/100 ({r}) valide pour {n} une {p} sur les critères E, S et G.",
    "L'audit ESG positionne {n} à {sc}/100 (notation {r}), soit une {p}.",
    "Le niveau {sc}/100 ({r}) reflète une {p}, confirmé par l'analyse des trois piliers.",
]

EXEC_PILLAR_PHRASES = [
    "Le pilier {bn} ({bs}/100) constitue le socle ; le pilier {wn} ({ws}/100) reste le principal levier de progression.",
    "L'excellence relative se concentre sur {bn} ({bs}/100) ; {wn} ({ws}/100) appelle des efforts prioritaires.",
    "{bn} s'impose comme point fort ({bs}/100) ; {wn} ({ws}/100) est identifié comme axe de transformation.",
    "La répartition souligne la robustesse de {bn} ({bs}/100) et la nécessité de renforcer {wn} ({ws}/100).",
    "{bn} domine le profil ESG ({bs}/100) tandis que {wn} ({ws}/100) constitue la marge d'amélioration prioritaire.",
    "L'analyse révèle une avance sur {bn} ({bs}/100) et un écart à combler sur {wn} ({ws}/100).",
    "En termes d'équilibre, {bn} devance ({bs}/100) et {wn} ({ws}/100) requiert l'attention prioritaire.",
]

ENV_INTROS = [
    "Sur le volet environnemental, {n} enregistre {sc}/100.",
    "La performance climatique et environnementale de {n} atteint {sc}/100.",
    "{n} obtient {sc}/100 sur la dimension environnementale de son reporting.",
    "L'empreinte écologique de {n} est évaluée à {sc}/100.",
    "En matière d'environnement et de climat, {n} se positionne à {sc}/100.",
    "Le bilan environnemental de {n} aboutit à un score de {sc}/100.",
    "{sc}/100 — telle est la performance environnementale mesurée pour {n} cet exercice.",
]

ENV_LIAISONS = [
    "Les indicateurs recensés couvrent : ",
    "Le périmètre de reporting intègre : ",
    "Les données environnementales clés sont : ",
    "L'inventaire environnemental comprend : ",
    "Les métriques déclarées incluent : ",
    "Le bilan environnemental documente : ",
    "Les principaux indicateurs environnementaux sont : ",
]

ENV_SCOPE_PHRASES = [
    "bilan carbone Scope 1/2/3 ({s1:,.0f} / {s2:,.0f} / {s3:,.0f} t CO₂e) couvrant l'intégralité de la chaîne de valeur",
    "décomposition carbone ({s1:,.0f} t directes, {s2:,.0f} t énergie, {s3:,.0f} t indirectes)",
    "émissions ventilées Scope 1 ({s1:,.0f} t) / Scope 2 ({s2:,.0f} t) / Scope 3 ({s3:,.0f} t CO₂e)",
    "reporting carbone complet : opérationnel {s1:,.0f} t, énergie {s2:,.0f} t, chaîne de valeur {s3:,.0f} t",
    "empreinte carbone totale ({s1:,.0f} + {s2:,.0f} + {s3:,.0f} t CO₂e) sur les trois périmètres",
]

ENV_OUTLOOK = [
    "La trajectoire de décarbonation s'articule autour de {p} pour les prochains exercices.",
    "L'axe de progrès prioritaire porte sur {p}, en cohérence avec les exigences sectorielles.",
    "Les efforts à venir se concentrent sur {p}, levier d'amélioration identifié dans la feuille de route.",
    "Le plan environnemental vise en priorité {p}, conformément aux engagements de durabilité.",
    "La feuille de route environnementale cible {p} comme priorité opérationnelle.",
    "{p} constitue la priorité environnementale inscrite dans la stratégie pluriannuelle.",
    "Le programme environnemental pluriannuel place {p} au premier rang des objectifs à horizon 3 ans.",
]

SOC_INTROS = [
    "Le volet social de {n} s'établit à {sc}/100.",
    "La performance sociale et humaine de {n} atteint {sc}/100.",
    "{n} enregistre {sc}/100 sur l'axe social de son reporting extra-financier.",
    "Les indicateurs sociaux de {n} reflètent un score de {sc}/100.",
    "Sur le pilier Social, {n} obtient {sc}/100.",
    "Le bilan social de {n} est évalué à {sc}/100 pour l'exercice.",
    "{sc}/100 : telle est la note sociale de {n}, {trend}.",
]

SOC_LIAISONS = [
    "Les indicateurs sociaux clés sont : ",
    "Le reporting social couvre : ",
    "Les données humaines et sociales déclarées comprennent : ",
    "Le bilan social présente : ",
    "Les indicateurs RH et sociaux reportés incluent : ",
    "La performance sociale se traduit par : ",
    "Les métriques sociales documentées englobent : ",
]

SOC_STRATEGIES = [
    "La politique RH cible l'attractivité des talents, la mixité et la prévention des risques professionnels.",
    "L'ambition sociale articule développement des compétences, équité et qualité de vie au travail.",
    "La stratégie humaine repose sur la fidélisation, la promotion de la diversité et la réduction de l'accidentologie.",
    "Le modèle social privilégie l'investissement formation, l'égalité professionnelle et l'engagement communautaire.",
    "La démarche sociale combine montée en compétences, dialogue social renforcé et inclusion durable.",
    "La vision sociale intègre l'épanouissement des collaborateurs, la sécurité et la contribution territoriale.",
    "L'organisation place la performance sociale au cœur de sa marque employeur et de son ancrage territorial.",
]

GOV_INTROS = [
    "Le pilier Gouvernance de {n} s'établit à {sc}/100.",
    "La qualité de gouvernance de {n} est évaluée à {sc}/100.",
    "{n} positionne son axe Gouvernance à {sc}/100.",
    "Sur les critères de gouvernance, {n} obtient {sc}/100.",
    "La structure de gouvernance de {n} génère un score de {sc}/100.",
    "L'évaluation gouvernance de {n} aboutit à {sc}/100.",
    "La gouvernance extra-financière de {n} est notée {sc}/100.",
]

GOV_LIAISONS = [
    "La structure de gouvernance repose sur : ",
    "Le dispositif de gouvernance s'appuie sur : ",
    "Les fondements de la gouvernance incluent : ",
    "L'architecture de gouvernance comprend : ",
    "Le cadre de gouvernance est structuré autour de : ",
    "La gouvernance ESG s'organise autour de : ",
    "Les piliers de la gouvernance documentée sont : ",
]

GOV_AUDITS = [
    "Un audit ESG indépendant renforce la crédibilité et la transparence du reporting extra-financier.",
    "La vérification externe des données ESG assure la fiabilité et la comparabilité du reporting.",
    "L'audit indépendant conduit garantit l'intégrité des données publiées dans ce rapport.",
    "La certification externe des indicateurs ESG témoigne de la rigueur du dispositif de reporting.",
    "Un tiers indépendant a vérifié la cohérence et l'exactitude des données extra-financières présentées.",
    "La vérification tierce des données ESG consolide la confiance des investisseurs et des parties prenantes.",
    "L'assurance externe du reporting ESG constitue un gage de qualité et de transparence pour l'ensemble des parties.",
]

GOV_NO_AUDIT = [
    "Le recours à un audit ESG indépendant est recommandé pour renforcer la crédibilité du reporting.",
    "La mise en place d'une vérification externe est identifiée comme priorité pour le prochain exercice.",
    "L'intégration d'un auditeur tiers pour valider les données extra-financières est planifiée.",
    "Une assurance externe sur les données ESG consoliderait la confiance des parties prenantes.",
    "Le déploiement d'une certification ESG externe constitue un axe de progrès à court terme.",
    "La vérification indépendante du reporting ESG est un engagement inscrit dans la feuille de route.",
    "Le recours à une tierce partie indépendante renforcera la robustesse du dispositif de reporting.",
]

GOV_COMMITTEES = [
    "Un comité de durabilité opérationnel au niveau du Conseil assure la supervision stratégique des enjeux ESG.",
    "La gouvernance ESG bénéficie d'un comité dédié, garant de l'intégration de la durabilité au plus haut niveau.",
    "Le comité RSE du Conseil d'Administration pilote la stratégie de durabilité et en suit l'exécution.",
    "Un organe de gouvernance spécialisé supervise la trajectoire ESG et l'atteinte des objectifs.",
    "La dimension ESG est portée par un comité de durabilité actif, ancré dans la structure de gouvernance.",
    "La supervision ESG est assurée par un comité dédié qui rend compte directement au Conseil.",
    "Le Conseil dispose d'un comité de durabilité permanent, garant de la cohérence de la stratégie ESG.",
]

GOV_NO_COMMITTEE = [
    "La création d'un comité de durabilité au niveau du Conseil est fortement recommandée.",
    "L'institution d'une instance de gouvernance ESG dédiée est un levier prioritaire d'amélioration.",
    "Le renforcement de la supervision ESG par un organe dédié est identifié comme action structurante.",
    "La mise en place d'un comité RSE au sein du Conseil constitue une recommandation prioritaire.",
    "Une gouvernance ESG renforcée passe par la création d'un comité de durabilité au niveau exécutif.",
    "L'absence de comité dédié est un axe de progrès documenté dans la feuille de route de gouvernance.",
    "La constitution d'un comité de durabilité est planifiée pour renforcer l'ancrage stratégique de l'ESG.",
]

CONCLUSION_HIGH = [
    ("témoigne d'une démarche ESG mature et structurée", "Fort de ces acquis,", "entend consolider ses avancées tout en accélérant sur ses axes d'amélioration"),
    ("confirme son engagement dans une stratégie de durabilité ambitieuse", "Sur cette base solide,", "se donne les moyens de franchir un cap supplémentaire dans sa performance extra-financière"),
    ("illustre la maturité croissante de sa démarche de développement durable", "Capitalisant sur ces résultats,", "s'engage à amplifier ses efforts sur les axes prioritaires identifiés"),
    ("positionne {n} parmi les acteurs responsables de son secteur", "Dans cette dynamique positive,", "poursuit l'intégration de la durabilité dans l'ensemble de ses décisions stratégiques"),
    ("valide la pertinence de la stratégie ESG engagée ces dernières années", "Renforcée par ces résultats,", "accélère la mise en œuvre de sa feuille de route long-terme"),
]

CONCLUSION_MID = [
    ("s'est engagée résolument dans la transformation de ses pratiques ESG", "À partir de ce socle,", "accélère la mise en œuvre de sa feuille de route de durabilité"),
    ("amorce une dynamique positive sur l'ensemble des piliers ESG", "Portée par ces premiers résultats,", "structure une trajectoire de progrès sur les prochains exercices"),
    ("démontre une progression mesurée et régulière sur ses indicateurs clés", "Dans cette continuité,", "intensifie ses efforts pour atteindre ses objectifs à horizon 3 ans"),
]

CONCLUSION_LOW = [
    ("a initié une réflexion ESG structurée qui appelle désormais à passer à l'acte", "Consciente de ces marges de progression,", "s'engage dans une démarche de transformation ambitieuse"),
    ("se trouve à un moment charnière de sa trajectoire ESG", "Face à ces enjeux,", "mobilise ses ressources pour accélérer sa transformation durable"),
    ("prend acte des axes de progrès significatifs identifiés dans ce rapport", "Avec détermination,", "s'engage à structurer un plan d'action ESG concret et mesurable"),
]

CONCLUSION_REFS = [
    "en alignement avec les référentiels GRI Standards, TCFD, CSRD et les ODD des Nations Unies.",
    "en cohérence avec les cadres GRI, ESRS (CSRD), TCFD et les 17 Objectifs de Développement Durable.",
    "en ligne avec les standards GRI, les exigences CSRD, le cadre TCFD et les ODD de l'Agenda 2030.",
    "conforme aux référentiels internationaux GRI, aux exigences ESRS de la directive CSRD et aux ODD.",
    "ancré dans les cadres de reporting reconnus : GRI Standards, TCFD, CSRD/ESRS et ODD Nations Unies.",
    "en réponse aux attentes des cadres GRI, ESRS, TCFD et des ODD de l'Agenda 2030.",
    "sous l'angle des référentiels CSRD/ESRS, GRI Standards, TCFD et ODD Nations Unies.",
]

PERF_DESC = {
    "AAA": "performance de premier plan, alignée avec les leaders mondiaux ESG",
    "AA":  "très bonne performance, dépassant les standards sectoriels reconnus",
    "A":   "bonne performance, nettement au-dessus de la moyenne sectorielle",
    "BBB": "performance satisfaisante avec des marges de progression identifiées",
    "BB":  "performance en développement — plan d'action structuré engagé",
    "B":   "performance limitée — transformation de fond nécessaire sur l'ensemble des piliers",
    "CCC": "performance insuffisante — mobilisation urgente requise",
}


def generate_esg_content(request: ESGRequest, scores: ESGScores) -> dict:
    company = request.company
    env = request.environmental
    soc = request.social
    gov = request.governance
    year = company.reporting_year
    name = company.name
    s = _seed(name)

    sector_long, sector_priority = _ctx(company.sector)
    perf = PERF_DESC.get(scores.rating, "performance mesurée")

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

    # ── Executive summary ──────────────────────────────────────────────────
    opening = _pick(s, 0, EXEC_OPENINGS).format(n=name, y=year, ctx=sector_long)
    score_ph = _pick(s, 1, EXEC_SCORE_PHRASES).format(
        n=name, sc=f"{scores.total_esg_score:.1f}", r=scores.rating, p=perf)
    pillar_ph = _pick(s, 2, EXEC_PILLAR_PHRASES).format(
        bn=best[0], bs=f"{best[1]:.0f}", wn=worst[0], ws=f"{worst[1]:.0f}")
    sector_note = f" Dans {sector_long}, la priorité stratégique porte sur {sector_priority}."
    executive_summary = f"{opening} {score_ph} {pillar_ph}{sector_note}"

    # ── Environnement ──────────────────────────────────────────────────────
    env_intro = _pick(s, 3, ENV_INTROS).format(n=name, sc=f"{scores.environmental_score:.0f}")
    env_items = []

    if env.co2_emissions_tonnes:
        intensity = ""
        if company.revenue_eur and company.revenue_eur > 0:
            intensity = f" (intensité : {env.co2_emissions_tonnes / company.revenue_eur * 1e6:.1f} t/M€ CA)"
        env_items.append(f"{env.co2_emissions_tonnes:,.0f} t CO₂e totales{intensity}")

    if env.scope1_emissions and env.scope2_emissions and env.scope3_emissions:
        env_items.append(_pick(s, 4, ENV_SCOPE_PHRASES).format(
            s1=env.scope1_emissions, s2=env.scope2_emissions, s3=env.scope3_emissions))
    elif env.scope3_emissions is None and (env.scope1_emissions or env.scope2_emissions):
        env_items.append("intégration du Scope 3 recommandée pour une vision carbone complète")

    if env.renewable_energy_percent is not None:
        if env.renewable_energy_percent >= 75: re_c = "performance exemplaire"
        elif env.renewable_energy_percent >= 50: re_c = "objectif 50% atteint"
        elif env.renewable_energy_percent >= 30: re_c = "progression engagée"
        else: re_c = "accélération requise"
        env_items.append(f"{env.renewable_energy_percent:.0f}% d'énergie renouvelable ({re_c})")

    if env.energy_consumption_mwh:
        env_items.append(f"{env.energy_consumption_mwh:,.0f} MWh consommés")
    if env.water_consumption_m3:
        env_items.append(f"{env.water_consumption_m3:,.0f} m³ prélevés")
    if env.waste_recycled_percent is not None:
        wl = "excellent" if env.waste_recycled_percent >= 70 else ("satisfaisant" if env.waste_recycled_percent >= 40 else "à améliorer")
        env_items.append(f"recyclage {env.waste_recycled_percent:.0f}% ({wl})")
    if env.biodiversity_initiatives:
        env_items.append(f"{env.biodiversity_initiatives} initiative(s) biodiversité")

    if env_items:
        env_detail = _pick(s, 5, ENV_LIAISONS) + " ; ".join(env_items) + "."
    else:
        no_data_opts = [
            "Le périmètre environnemental est en cours de structuration.",
            "La collecte des données environnementales est en déploiement progressif.",
            "Les indicateurs environnementaux sont en cours de formalisation.",
        ]
        env_detail = _pick(s, 5, no_data_opts)

    env_outlook = _pick(s, 6, ENV_OUTLOOK).format(p=sector_priority)
    environmental = f"{env_intro} {env_detail} {env_outlook}"

    # ── Social ─────────────────────────────────────────────────────────────
    trend = "en progression" if scores.social_score >= 60 else "avec des axes de renforcement prioritaires"
    soc_intro = _pick(s, 7, SOC_INTROS).format(n=name, sc=f"{scores.social_score:.0f}", trend=trend)
    soc_items = []

    if soc.total_employees:
        soc_items.append(f"{soc.total_employees:,} collaborateurs ({company.country})")
    if soc.female_employees_percent is not None:
        gap = 40 - soc.female_employees_percent
        if gap <= 0: fem_n = "objectif légal 40% atteint"
        elif gap <= 5: fem_n = f"à {gap:.0f} pt(s) de l'objectif 40%"
        else: fem_n = f"écart {gap:.0f} pts vs. objectif 40%"
        soc_items.append(f"{soc.female_employees_percent:.0f}% de femmes ({fem_n})")
    if soc.training_hours_per_employee is not None:
        lvl = "excellent" if soc.training_hours_per_employee >= 40 else ("satisfaisant" if soc.training_hours_per_employee >= 20 else "à renforcer")
        soc_items.append(f"{soc.training_hours_per_employee:.0f} h/an de formation par collaborateur ({lvl})")
    if soc.accident_frequency_rate is not None:
        sf = "excellent" if soc.accident_frequency_rate < 2 else ("satisfaisant" if soc.accident_frequency_rate < 5 else "à améliorer en priorité")
        soc_items.append(f"taux de fréquence accidents {soc.accident_frequency_rate:.1f} ({sf})")
    if soc.employee_turnover_percent is not None:
        soc_items.append(f"turnover {soc.employee_turnover_percent:.0f}%")
    if soc.community_investment_eur:
        soc_items.append(f"{soc.community_investment_eur:,.0f} € d'investissements communautaires")
    if soc.customer_satisfaction_score:
        soc_items.append(f"satisfaction client {soc.customer_satisfaction_score:.1f}/10")
    if soc.local_suppliers_percent is not None:
        soc_items.append(f"{soc.local_suppliers_percent:.0f}% fournisseurs locaux")
    if soc.disabled_employees_percent is not None:
        soc_items.append(f"{soc.disabled_employees_percent:.1f}% de collaborateurs en situation de handicap")

    if soc_items:
        soc_detail = _pick(s, 8, SOC_LIAISONS) + " ; ".join(soc_items) + "."
    else:
        soc_detail = "Les indicateurs sociaux sont en cours de formalisation."

    soc_strategy = _pick(s, 9, SOC_STRATEGIES)
    social = f"{soc_intro} {soc_detail} {soc_strategy}"

    # ── Gouvernance ────────────────────────────────────────────────────────
    gov_intro = _pick(s, 0, GOV_INTROS).format(n=name, sc=f"{scores.governance_score:.0f}")
    gov_items = []

    if gov.board_members:
        gov_items.append(f"CA de {gov.board_members} membres")
    if gov.female_board_percent is not None:
        rixain = "conforme loi Rixain (≥40%)" if gov.female_board_percent >= 40 else f"{40 - gov.female_board_percent:.0f} pt(s) sous l'objectif Rixain 40%"
        gov_items.append(f"{gov.female_board_percent:.0f}% de femmes au CA ({rixain})")
    if gov.independent_board_percent is not None:
        afep = "conforme AFEP-MEDEF (≥50%)" if gov.independent_board_percent >= 50 else "sous le seuil AFEP-MEDEF 50%"
        gov_items.append(f"{gov.independent_board_percent:.0f}% d'administrateurs indépendants ({afep})")
    if gov.csr_budget_eur:
        gov_items.append(f"budget RSE {gov.csr_budget_eur:,.0f} €")
    if gov.ethics_violations is not None:
        gov_items.append(f"{gov.ethics_violations} manquement(s) éthique")
    if gov.data_breaches is not None and gov.data_breaches > 0:
        gov_items.append(f"{gov.data_breaches} incident(s) cybersécurité déclaré(s)")
    if gov.corruption_cases is not None and gov.corruption_cases == 0:
        gov_items.append("zéro cas de corruption enregistré")

    if gov_items:
        gov_detail = _pick(s, 1, GOV_LIAISONS) + " ; ".join(gov_items) + "."
    else:
        gov_detail = "La structure de gouvernance est en cours de documentation."

    audit_sent = _pick(s, 2, GOV_AUDITS if gov.esg_audit_conducted else GOV_NO_AUDIT)
    committee_sent = _pick(s, 3, GOV_COMMITTEES if gov.sustainability_committee else GOV_NO_COMMITTEE)
    governance = f"{gov_intro} {gov_detail} {audit_sent} {committee_sent}"

    # ── Conclusion ─────────────────────────────────────────────────────────
    n_s = len(scores.strengths)
    n_w = len(scores.weaknesses)
    n_r = len(scores.recommendations)

    if scores.total_esg_score >= 70:
        traj_list = CONCLUSION_HIGH
    elif scores.total_esg_score >= 50:
        traj_list = CONCLUSION_MID
    else:
        traj_list = CONCLUSION_LOW

    trajectory, bridge, forward = _pick(s, 4, traj_list)
    trajectory = trajectory.replace("{n}", name)
    ref = _pick(s, 5, CONCLUSION_REFS)

    s_txt = f"{n_s} point(s) fort(s) consolidé(s)" if n_s else "des points forts émergents"
    w_txt = f"{n_w} axe(s) d'amélioration prioritaire(s)" if n_w else "des axes de progrès identifiés"

    conclusion = (
        f"Fort d'un score ESG de {scores.total_esg_score:.1f}/100 ({scores.rating}), "
        f"{name} {trajectory}. "
        f"L'analyse met en lumière {s_txt} et {w_txt}. "
        f"{bridge} {name} {forward}, "
        f"en s'appuyant sur les {n_r} recommandations formulées comme feuille de route opérationnelle. "
        f"L'organisation réaffirme son engagement envers un reporting transparent et rigoureux, {ref}"
    )

    return {
        "executive_summary": executive_summary,
        "environmental": environmental,
        "social": social,
        "governance": governance,
        "conclusion": conclusion,
    }
