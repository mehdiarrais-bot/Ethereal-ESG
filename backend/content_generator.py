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
    """Dispatche vers le générateur FR ou EN selon request.language."""
    if getattr(request, "language", "fr") == "en":
        return _generate_en(request, scores)
    return _generate_fr(request, scores)


def _generate_fr(request: ESGRequest, scores: ESGScores) -> dict:
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

    # ── Double matérialité (CSRD/ESRS) ─────────────────────────────────────
    materiality = (
        f"Conformément aux exigences de la directive CSRD et des normes ESRS, {name} a conduit "
        f"une analyse de double matérialité. Celle-ci évalue chaque enjeu ESG sous deux angles : "
        f"la matérialité d'impact (effets de l'organisation sur la société et l'environnement) et "
        f"la matérialité financière (effets des enjeux de durabilité sur la performance et la "
        f"situation de {name}). Les enjeux situés dans le quadrant supérieur droit — combinant "
        f"impact et importance financière élevés — constituent les priorités stratégiques du "
        f"reporting extra-financier et concentrent les efforts de pilotage."
    )

    # ── Objectifs & trajectoire (SBTi) ─────────────────────────────────────
    ty = max(company.target_year, year + 1)
    targets_intro = [
        f"{name} inscrit sa démarche ESG dans une trajectoire de progrès chiffrée à horizon {ty}.",
        f"La feuille de route de durabilité de {name} fixe des cibles mesurables à l'échéance {ty}.",
        f"Des objectifs ESG quantifiés structurent l'ambition de {name} d'ici {ty}.",
    ]
    targets_txt = _pick(s, 6, targets_intro)
    if env.co2_emissions_tonnes and env.co2_emissions_tonnes > 0:
        targets_txt += (
            f" Sur le plan climatique, l'entreprise vise une réduction de 42% de ses émissions "
            f"de gaz à effet de serre d'ici 2030 par rapport à l'année de référence {year}, "
            f"en cohérence avec une trajectoire alignée sur l'objectif 1,5°C de l'Accord de Paris "
            f"(méthodologie Science Based Targets initiative). "
        )
    else:
        targets_txt += (
            " La définition d'une trajectoire carbone chiffrée, alignée sur l'initiative "
            "Science Based Targets, constitue une priorité de la feuille de route. "
        )
    targets_txt += (
        f"Chaque pilier fait l'objet d'une cible de progression, avec un suivi annuel des "
        f"indicateurs clés et une revue par la gouvernance ESG."
    )

    # ── Taxonomie UE ───────────────────────────────────────────────────────
    taxonomy = None
    tx = request.taxonomy
    if tx and any(v is not None for v in
                  (tx.turnover_aligned_percent, tx.capex_aligned_percent, tx.opex_aligned_percent)):
        parts = []
        if tx.turnover_aligned_percent is not None:
            parts.append(f"{tx.turnover_aligned_percent:.0f}% du chiffre d'affaires")
        if tx.capex_aligned_percent is not None:
            parts.append(f"{tx.capex_aligned_percent:.0f}% des CapEx")
        if tx.opex_aligned_percent is not None:
            parts.append(f"{tx.opex_aligned_percent:.0f}% des OpEx")
        taxonomy = (
            f"Au titre du règlement Taxonomie de l'Union européenne, {name} déclare la part de ses "
            f"activités durables sur le plan environnemental : " + ", ".join(parts) + " alignés. "
            f"Ces indicateurs traduisent la contribution substantielle des activités à au moins un "
            f"objectif environnemental, dans le respect du principe DNSH (« ne pas causer de "
            f"préjudice important ») et des garanties minimales sociales. Le CapEx aligné, "
            f"prospectif, reflète la trajectoire d'investissement de l'entreprise vers une "
            f"économie bas-carbone."
        )

    # ── Risques climatiques (TCFD) ─────────────────────────────────────────
    climate_risk = (
        f"En ligne avec les recommandations de la TCFD, {name} identifie deux catégories de "
        f"risques climatiques. Les risques physiques (aigus et chroniques) recouvrent l'exposition "
        f"des actifs et de la chaîne d'approvisionnement aux événements climatiques extrêmes et à "
        f"l'évolution des conditions environnementales. Les risques de transition — réglementaires, "
        f"technologiques, de marché et de réputation — découlent du passage à une économie "
        f"bas-carbone, notamment via la tarification du carbone et l'évolution des attentes des "
        f"parties prenantes. Ces risques, ainsi que les opportunités associées (efficacité "
        f"énergétique, nouveaux marchés durables), sont intégrés à la stratégie et au dispositif "
        f"de gestion des risques de l'organisation."
    )

    return {
        "executive_summary": executive_summary,
        "environmental": environmental,
        "social": social,
        "governance": governance,
        "materiality": materiality,
        "targets": targets_txt,
        "taxonomy": taxonomy,
        "climate_risk": climate_risk,
        "conclusion": conclusion,
    }


# ══════════════════════════════════════════════════════════════════════════
# ENGLISH CONTENT GENERATOR
# ══════════════════════════════════════════════════════════════════════════

SECTOR_CTX_EN = {
    "Énergie": ("the energy sector, exposed to low-carbon transition challenges", "decarbonising its assets"),
    "Energy": ("the energy sector, exposed to low-carbon transition challenges", "decarbonising its assets"),
    "Finance": ("the financial sector, a driver of sustainable finance", "embedding ESG into its investment criteria"),
    "Industrie": ("manufacturing industry, at the heart of carbon-efficiency challenges", "optimising its industrial footprint"),
    "Industry": ("manufacturing industry, at the heart of carbon-efficiency challenges", "optimising its industrial footprint"),
    "BTP": ("the construction sector, committed to sustainable building", "eco-design and waste reduction"),
    "Construction": ("the construction sector, committed to sustainable building", "eco-design and waste reduction"),
    "Agroalimentaire": ("the agri-food sector, exposed to biodiversity and water risks", "the traceability of its supply chains"),
    "Numérique": ("the technology sector, with a growing carbon footprint", "the energy efficiency of its data centres"),
    "Tech": ("the technology sector, with a growing carbon footprint", "the energy efficiency of its data centres"),
    "Logistique": ("logistics, a carbon-intensive sector", "decarbonising its fleet and flows"),
    "Transport": ("logistics, a carbon-intensive sector", "decarbonising its fleet and flows"),
    "Pharmaceutique": ("the pharmaceutical sector, with high governance standards", "the responsible management of its substances"),
    "Commerce": ("retail, under pressure across its supply chains", "the sustainability of its upstream value chain"),
    "Chimie": ("the chemical industry, facing major regulatory challenges", "reducing its pollutant emissions"),
    "Chemical": ("the chemical industry, facing major regulatory challenges", "reducing its pollutant emissions"),
}


def _ctx_en(sector):
    for k, v in SECTOR_CTX_EN.items():
        if k.lower() in sector.lower():
            return v
    return ("its industry", "the continuous improvement of its ESG practices")


PERF_DESC_EN = {
    "AAA": "leading performance, on par with global ESG leaders",
    "AA": "strong performance, exceeding recognised sector standards",
    "A": "good performance, well above the sector average",
    "BBB": "satisfactory performance with identified room for improvement",
    "BB": "developing performance — a structured action plan is under way",
    "B": "limited performance — deep transformation is needed across all pillars",
    "CCC": "insufficient performance — urgent mobilisation is required",
}

EXEC_OPENINGS_EN = [
    "{n} presents its {y} ESG report, asserting its position within {ctx}.",
    "As part of its extra-financial commitment, {n} publishes its {y} ESG review for {ctx}.",
    "{n} consolidates its {y} sustainability reporting, rooted in the realities of {ctx}.",
    "The {y} fiscal year marks a structuring step in the ESG trajectory of {n}, a player in {ctx}.",
    "This {y} ESG report reflects the sustainability strategy of {n} within {ctx}.",
    "As a player in {ctx}, {n} reports on its {y} extra-financial commitments.",
    "The CSR approach of {n} reaches a documented level of maturity in {y} ({ctx}).",
]
EXEC_SCORE_EN = [
    "The extra-financial assessment results in an overall score of {sc}/100, rating {r} — {p}.",
    "The multi-pillar analysis positions {n} at {sc}/100 ({r}), reflecting {p}.",
    "The consolidated ESG rating stands at {sc}/100 ({r}), a mark of {p}.",
    "With {sc}/100 and a {r} rating, {n} shows {p} across the full extra-financial scope.",
    "The composite score of {sc}/100 ({r}) confirms {p} on the E, S and G criteria.",
    "The ESG assessment places {n} at {sc}/100 (rating {r}), i.e. {p}.",
    "The {sc}/100 level ({r}) reflects {p}, confirmed by the analysis of the three pillars.",
]
EXEC_PILLAR_EN = [
    "The {bn} pillar ({bs}/100) is the cornerstone; the {wn} pillar ({ws}/100) remains the main lever for progress.",
    "Relative strength concentrates on {bn} ({bs}/100); {wn} ({ws}/100) calls for priority efforts.",
    "{bn} stands out as a strength ({bs}/100); {wn} ({ws}/100) is identified as a transformation area.",
    "The breakdown highlights the robustness of {bn} ({bs}/100) and the need to strengthen {wn} ({ws}/100).",
    "{bn} leads the ESG profile ({bs}/100) while {wn} ({ws}/100) is the priority area for improvement.",
    "The analysis reveals an edge on {bn} ({bs}/100) and a gap to close on {wn} ({ws}/100).",
    "In terms of balance, {bn} leads ({bs}/100) and {wn} ({ws}/100) requires priority attention.",
]
ENV_INTROS_EN = [
    "On the environmental front, {n} scores {sc}/100.",
    "The climate and environmental performance of {n} reaches {sc}/100.",
    "{n} achieves {sc}/100 on the environmental dimension of its reporting.",
    "The ecological footprint of {n} is assessed at {sc}/100.",
    "On environment and climate, {n} stands at {sc}/100.",
    "The environmental review of {n} results in a score of {sc}/100.",
    "{sc}/100 — that is the environmental performance measured for {n} this year.",
]
ENV_LIAISONS_EN = [
    "The reported indicators cover: ", "The reporting scope includes: ",
    "The key environmental data are: ", "The environmental inventory comprises: ",
    "The disclosed metrics include: ", "The environmental review documents: ",
    "The main environmental indicators are: ",
]
ENV_OUTLOOK_EN = [
    "The decarbonisation pathway centres on {p} for the coming years.",
    "The priority area for progress is {p}, in line with sector expectations.",
    "Upcoming efforts focus on {p}, an improvement lever set out in the roadmap.",
    "The environmental plan prioritises {p}, in line with sustainability commitments.",
    "The environmental roadmap targets {p} as an operational priority.",
    "{p} is the environmental priority embedded in the multi-year strategy.",
    "The multi-year environmental programme places {p} at the top of its 3-year objectives.",
]
SOC_INTROS_EN = [
    "The social dimension of {n} stands at {sc}/100.",
    "The social and human performance of {n} reaches {sc}/100.",
    "{n} scores {sc}/100 on the social axis of its extra-financial reporting.",
    "The social indicators of {n} reflect a score of {sc}/100.",
    "On the Social pillar, {n} achieves {sc}/100.",
    "The social review of {n} is assessed at {sc}/100 for the year.",
    "{sc}/100: that is the social rating of {n}, {trend}.",
]
SOC_LIAISONS_EN = [
    "The key social indicators are: ", "Social reporting covers: ",
    "The disclosed human and social data include: ", "The social review shows: ",
    "The reported HR and social indicators include: ", "Social performance translates into: ",
    "The documented social metrics encompass: ",
]
SOC_STRATEGIES_EN = [
    "HR policy targets talent attractiveness, gender balance and occupational risk prevention.",
    "The social ambition combines skills development, equity and quality of working life.",
    "The people strategy rests on retention, diversity promotion and lower accident rates.",
    "The social model prioritises training investment, professional equality and community engagement.",
    "The social approach blends upskilling, strengthened social dialogue and lasting inclusion.",
    "The social vision integrates employee fulfilment, safety and regional contribution.",
    "The organisation places social performance at the heart of its employer brand and local roots.",
]
GOV_INTROS_EN = [
    "The Governance pillar of {n} stands at {sc}/100.",
    "The governance quality of {n} is assessed at {sc}/100.",
    "{n} positions its Governance axis at {sc}/100.",
    "On governance criteria, {n} achieves {sc}/100.",
    "The governance structure of {n} generates a score of {sc}/100.",
    "The governance assessment of {n} results in {sc}/100.",
    "The extra-financial governance of {n} is rated {sc}/100.",
]
GOV_LIAISONS_EN = [
    "The governance structure rests on: ", "The governance framework relies on: ",
    "Governance foundations include: ", "The governance architecture comprises: ",
    "The governance framework is built around: ", "ESG governance is organised around: ",
    "The documented governance pillars are: ",
]
GOV_AUDITS_EN = [
    "An independent ESG audit reinforces the credibility and transparency of extra-financial reporting.",
    "External assurance of ESG data ensures the reliability and comparability of reporting.",
    "The independent audit conducted guarantees the integrity of the data published in this report.",
    "External certification of ESG indicators demonstrates the rigour of the reporting process.",
    "An independent third party has verified the consistency and accuracy of the extra-financial data.",
    "Third-party assurance of ESG data strengthens the confidence of investors and stakeholders.",
    "External assurance of ESG reporting is a mark of quality and transparency for all stakeholders.",
]
GOV_NO_AUDIT_EN = [
    "An independent ESG audit is recommended to strengthen the credibility of reporting.",
    "Introducing external assurance is identified as a priority for the next reporting cycle.",
    "Engaging a third-party auditor to validate extra-financial data is planned.",
    "External assurance of ESG data would strengthen stakeholder confidence.",
    "Rolling out external ESG certification is a short-term area for progress.",
    "Independent verification of ESG reporting is a commitment set out in the roadmap.",
    "Engaging an independent third party will strengthen the robustness of the reporting process.",
]
GOV_COMMITTEES_EN = [
    "A sustainability committee operating at Board level ensures strategic oversight of ESG issues.",
    "ESG governance benefits from a dedicated committee, guaranteeing sustainability integration at the highest level.",
    "The Board's CSR committee steers the sustainability strategy and monitors its execution.",
    "A specialised governance body oversees the ESG trajectory and the achievement of objectives.",
    "The ESG dimension is driven by an active sustainability committee anchored in the governance structure.",
    "ESG oversight is provided by a dedicated committee reporting directly to the Board.",
    "The Board has a permanent sustainability committee ensuring the consistency of the ESG strategy.",
]
GOV_NO_COMMITTEE_EN = [
    "Creating a sustainability committee at Board level is strongly recommended.",
    "Establishing a dedicated ESG governance body is a priority improvement lever.",
    "Strengthening ESG oversight through a dedicated body is identified as a structuring action.",
    "Setting up a CSR committee within the Board is a priority recommendation.",
    "Strengthened ESG governance requires creating a sustainability committee at executive level.",
    "The absence of a dedicated committee is a documented area for progress in the governance roadmap.",
    "Establishing a sustainability committee is planned to strengthen the strategic anchoring of ESG.",
]
CONCLUSION_HIGH_EN = [
    ("demonstrates a mature and structured ESG approach", "Building on these achievements,", "intends to consolidate its progress while accelerating on its improvement areas"),
    ("confirms its commitment to an ambitious sustainability strategy", "On this solid foundation,", "is equipped to take a further step in its extra-financial performance"),
    ("illustrates the growing maturity of its sustainability approach", "Capitalising on these results,", "commits to amplifying its efforts on the identified priority areas"),
    ("positions {n} among the responsible players in its sector", "In this positive momentum,", "continues to embed sustainability across all its strategic decisions"),
    ("validates the relevance of the ESG strategy pursued in recent years", "Strengthened by these results,", "accelerates the delivery of its long-term roadmap"),
]
CONCLUSION_MID_EN = [
    ("has resolutely engaged in transforming its ESG practices", "From this foundation,", "accelerates the delivery of its sustainability roadmap"),
    ("is building positive momentum across all ESG pillars", "Driven by these early results,", "is structuring a path of progress for the coming years"),
    ("shows measured, steady progress on its key indicators", "In this continuity,", "intensifies its efforts to reach its 3-year objectives"),
]
CONCLUSION_LOW_EN = [
    ("has initiated a structured ESG reflection that now calls for action", "Aware of this room for progress,", "is committing to an ambitious transformation approach"),
    ("stands at a pivotal moment in its ESG trajectory", "Faced with these challenges,", "mobilises its resources to accelerate its sustainable transformation"),
    ("acknowledges the significant areas for progress identified in this report", "With determination,", "commits to structuring a concrete, measurable ESG action plan"),
]
CONCLUSION_REFS_EN = [
    "in alignment with the GRI Standards, TCFD, CSRD and the UN Sustainable Development Goals.",
    "in line with the GRI, ESRS (CSRD), TCFD frameworks and the 17 Sustainable Development Goals.",
    "consistent with the GRI standards, CSRD requirements, the TCFD framework and the 2030 Agenda SDGs.",
    "compliant with the international GRI frameworks, the ESRS requirements of the CSRD directive and the SDGs.",
    "grounded in recognised reporting frameworks: GRI Standards, TCFD, CSRD/ESRS and UN SDGs.",
    "in response to the expectations of the GRI, ESRS, TCFD frameworks and the 2030 Agenda SDGs.",
    "through the lens of the CSRD/ESRS, GRI Standards, TCFD and UN SDG frameworks.",
]


def _generate_en(request: ESGRequest, scores: ESGScores) -> dict:
    company = request.company
    env, soc, gov = request.environmental, request.social, request.governance
    year, name = company.reporting_year, company.name
    s = _seed(name)
    sector_long, sector_priority = _ctx_en(company.sector)
    perf = PERF_DESC_EN.get(scores.rating, "measured performance")

    labels = {"Environnemental": "Environmental", "Social": "Social", "Gouvernance": "Governance"}
    best = max(("Environmental", scores.environmental_score), ("Social", scores.social_score),
               ("Governance", scores.governance_score), key=lambda x: x[1])
    worst = min(("Environmental", scores.environmental_score), ("Social", scores.social_score),
                ("Governance", scores.governance_score), key=lambda x: x[1])

    opening = _pick(s, 0, EXEC_OPENINGS_EN).format(n=name, y=year, ctx=sector_long)
    score_ph = _pick(s, 1, EXEC_SCORE_EN).format(n=name, sc=f"{scores.total_esg_score:.1f}", r=scores.rating, p=perf)
    pillar_ph = _pick(s, 2, EXEC_PILLAR_EN).format(bn=best[0], bs=f"{best[1]:.0f}", wn=worst[0], ws=f"{worst[1]:.0f}")
    sector_note = f" Within {sector_long}, the strategic priority focuses on {sector_priority}."
    executive_summary = f"{opening} {score_ph} {pillar_ph}{sector_note}"

    # Environment
    env_intro = _pick(s, 3, ENV_INTROS_EN).format(n=name, sc=f"{scores.environmental_score:.0f}")
    items = []
    if env.co2_emissions_tonnes:
        inten = ""
        if company.revenue_eur and company.revenue_eur > 0:
            inten = f" (intensity: {env.co2_emissions_tonnes / company.revenue_eur * 1e6:.1f} t/€M revenue)"
        items.append(f"{env.co2_emissions_tonnes:,.0f} t CO₂e total{inten}")
    if env.scope1_emissions and env.scope2_emissions and env.scope3_emissions:
        items.append(f"full Scope 1/2/3 carbon footprint ({env.scope1_emissions:,.0f} / {env.scope2_emissions:,.0f} / {env.scope3_emissions:,.0f} t CO₂e)")
    if env.renewable_energy_percent is not None:
        rc = ("exemplary" if env.renewable_energy_percent >= 75 else "50% target met" if env.renewable_energy_percent >= 50
              else "progress under way" if env.renewable_energy_percent >= 30 else "acceleration required")
        items.append(f"{env.renewable_energy_percent:.0f}% renewable energy ({rc})")
    if env.energy_consumption_mwh:
        items.append(f"{env.energy_consumption_mwh:,.0f} MWh consumed")
    if env.water_consumption_m3:
        items.append(f"{env.water_consumption_m3:,.0f} m³ withdrawn")
    if env.waste_recycled_percent is not None:
        wl = "excellent" if env.waste_recycled_percent >= 70 else "satisfactory" if env.waste_recycled_percent >= 40 else "to improve"
        items.append(f"{env.waste_recycled_percent:.0f}% recycling ({wl})")
    if env.biodiversity_initiatives:
        items.append(f"{env.biodiversity_initiatives} biodiversity initiative(s)")
    env_detail = (_pick(s, 5, ENV_LIAISONS_EN) + "; ".join(items) + ".") if items else "The environmental scope is being structured."
    environmental = f"{env_intro} {env_detail} {_pick(s, 6, ENV_OUTLOOK_EN).format(p=sector_priority)}"

    # Social
    trend = "improving" if scores.social_score >= 60 else "with priority areas to strengthen"
    soc_intro = _pick(s, 7, SOC_INTROS_EN).format(n=name, sc=f"{scores.social_score:.0f}", trend=trend)
    items = []
    if soc.total_employees:
        items.append(f"{soc.total_employees:,} employees ({company.country})")
    if soc.female_employees_percent is not None:
        gap = 40 - soc.female_employees_percent
        fn = "legal 40% target met" if gap <= 0 else f"{gap:.0f} pt(s) from the 40% target" if gap <= 5 else f"{gap:.0f} pts below the 40% target"
        items.append(f"{soc.female_employees_percent:.0f}% women ({fn})")
    if soc.training_hours_per_employee is not None:
        lvl = "excellent" if soc.training_hours_per_employee >= 40 else "satisfactory" if soc.training_hours_per_employee >= 20 else "to strengthen"
        items.append(f"{soc.training_hours_per_employee:.0f} h/year training per employee ({lvl})")
    if soc.accident_frequency_rate is not None:
        sf = "excellent" if soc.accident_frequency_rate < 2 else "satisfactory" if soc.accident_frequency_rate < 5 else "a priority to improve"
        items.append(f"accident frequency rate {soc.accident_frequency_rate:.1f} ({sf})")
    if soc.employee_turnover_percent is not None:
        items.append(f"{soc.employee_turnover_percent:.0f}% turnover")
    if soc.customer_satisfaction_score:
        items.append(f"customer satisfaction {soc.customer_satisfaction_score:.1f}/10")
    if soc.disabled_employees_percent is not None:
        items.append(f"{soc.disabled_employees_percent:.1f}% employees with disabilities")
    soc_detail = (_pick(s, 8, SOC_LIAISONS_EN) + "; ".join(items) + ".") if items else "Social indicators are being formalised."
    social = f"{soc_intro} {soc_detail} {_pick(s, 9, SOC_STRATEGIES_EN)}"

    # Governance
    gov_intro = _pick(s, 0, GOV_INTROS_EN).format(n=name, sc=f"{scores.governance_score:.0f}")
    items = []
    if gov.board_members:
        items.append(f"{gov.board_members}-member Board")
    if gov.female_board_percent is not None:
        rx = "compliant with the 40% quota" if gov.female_board_percent >= 40 else f"{40 - gov.female_board_percent:.0f} pt(s) below the 40% quota"
        items.append(f"{gov.female_board_percent:.0f}% women on the Board ({rx})")
    if gov.independent_board_percent is not None:
        ind = "≥50% independence met" if gov.independent_board_percent >= 50 else "below the 50% independence threshold"
        items.append(f"{gov.independent_board_percent:.0f}% independent directors ({ind})")
    if gov.csr_budget_eur:
        items.append(f"CSR budget €{gov.csr_budget_eur:,.0f}")
    if gov.ethics_violations is not None:
        items.append(f"{gov.ethics_violations} ethics breach(es)")
    if gov.data_breaches is not None and gov.data_breaches > 0:
        items.append(f"{gov.data_breaches} cybersecurity incident(s) reported")
    if gov.corruption_cases is not None and gov.corruption_cases == 0:
        items.append("zero corruption cases recorded")
    gov_detail = (_pick(s, 1, GOV_LIAISONS_EN) + "; ".join(items) + ".") if items else "The governance structure is being documented."
    audit_sent = _pick(s, 2, GOV_AUDITS_EN if gov.esg_audit_conducted else GOV_NO_AUDIT_EN)
    committee_sent = _pick(s, 3, GOV_COMMITTEES_EN if gov.sustainability_committee else GOV_NO_COMMITTEE_EN)
    governance = f"{gov_intro} {gov_detail} {audit_sent} {committee_sent}"

    # CSRD sections
    materiality = (
        f"In line with the CSRD directive and the ESRS standards, {name} has conducted a double "
        f"materiality assessment. It evaluates each ESG topic from two angles: impact materiality "
        f"(the organisation's effects on society and the environment) and financial materiality "
        f"(the effects of sustainability matters on the performance and position of {name}). Topics "
        f"in the upper-right quadrant — combining high impact and high financial importance — are the "
        f"strategic priorities of extra-financial reporting and concentrate management efforts."
    )
    ty = max(company.target_year, year + 1)
    targets_txt = f"{name} embeds its ESG approach in a quantified path of progress towards {ty}."
    if env.co2_emissions_tonnes and env.co2_emissions_tonnes > 0:
        targets_txt += (
            f" On climate, the company targets a 42% reduction in greenhouse gas emissions by 2030 "
            f"versus the {year} baseline, consistent with a 1.5°C pathway under the Paris Agreement "
            f"(Science Based Targets initiative methodology). ")
    else:
        targets_txt += (" Defining a quantified carbon trajectory aligned with the Science Based "
                        "Targets initiative is a roadmap priority. ")
    targets_txt += "Each pillar is assigned a progression target, with annual monitoring of key indicators reviewed by ESG governance."

    taxonomy = None
    tx = request.taxonomy
    if tx and any(v is not None for v in (tx.turnover_aligned_percent, tx.capex_aligned_percent, tx.opex_aligned_percent)):
        parts = []
        if tx.turnover_aligned_percent is not None:
            parts.append(f"{tx.turnover_aligned_percent:.0f}% of turnover")
        if tx.capex_aligned_percent is not None:
            parts.append(f"{tx.capex_aligned_percent:.0f}% of CapEx")
        if tx.opex_aligned_percent is not None:
            parts.append(f"{tx.opex_aligned_percent:.0f}% of OpEx")
        taxonomy = (
            f"Under the EU Taxonomy Regulation, {name} discloses the share of its environmentally "
            f"sustainable activities: " + ", ".join(parts) + " aligned. These indicators reflect a "
            f"substantial contribution to at least one environmental objective, in compliance with the "
            f"DNSH principle (‘do no significant harm’) and minimum social safeguards. Aligned "
            f"CapEx, forward-looking, reflects the company's investment path towards a low-carbon economy."
        )

    climate_risk = (
        f"In line with TCFD recommendations, {name} identifies two categories of climate risk. "
        f"Physical risks (acute and chronic) cover the exposure of assets and the supply chain to "
        f"extreme weather events and changing environmental conditions. Transition risks — "
        f"regulatory, technological, market and reputational — stem from the shift to a low-carbon "
        f"economy, notably through carbon pricing and evolving stakeholder expectations. These risks, "
        f"together with the associated opportunities (energy efficiency, new sustainable markets), are "
        f"integrated into the organisation's strategy and risk-management framework."
    )

    n_r = len(scores.recommendations)
    if scores.total_esg_score >= 70:
        traj_list = CONCLUSION_HIGH_EN
    elif scores.total_esg_score >= 50:
        traj_list = CONCLUSION_MID_EN
    else:
        traj_list = CONCLUSION_LOW_EN
    trajectory, bridge, forward = _pick(s, 4, traj_list)
    trajectory = trajectory.replace("{n}", name)
    ref = _pick(s, 5, CONCLUSION_REFS_EN)
    s_txt = f"{len(scores.strengths)} consolidated strength(s)" if scores.strengths else "emerging strengths"
    w_txt = f"{len(scores.weaknesses)} priority area(s) for improvement" if scores.weaknesses else "identified areas for progress"
    conclusion = (
        f"With an ESG score of {scores.total_esg_score:.1f}/100 ({scores.rating}), {name} {trajectory}. "
        f"The analysis highlights {s_txt} and {w_txt}. {bridge} {name} {forward}, drawing on the "
        f"{n_r} recommendations set out as an operational roadmap. The organisation reaffirms its "
        f"commitment to transparent, rigorous reporting, {ref}"
    )

    return {
        "executive_summary": executive_summary, "environmental": environmental,
        "social": social, "governance": governance, "materiality": materiality,
        "targets": targets_txt, "taxonomy": taxonomy, "climate_risk": climate_risk,
        "conclusion": conclusion,
    }


# ══════════════════════════════════════════════════════════════════════════
# RECOMMANDATIONS ENRICHIES (titre + bénéfice + pilier + horizon)
# ══════════════════════════════════════════════════════════════════════════

_REC_META = {
    # clé : (pillar, horizon_fr, horizon_en, detail_fr, detail_en)
    "renewable": ("env", "2027", "2027",
        "Réduit les émissions Scope 2 et l'exposition aux prix de l'énergie ; contribue directement à la trajectoire SBTi.",
        "Cuts Scope 2 emissions and energy-price exposure; directly supports the SBTi pathway."),
    "scope3": ("env", "Court terme", "Short term",
        "Comble le principal angle mort du bilan carbone ; exigé par l'ESRS E1 de la CSRD pour les émissions de la chaîne de valeur.",
        "Closes the main carbon blind spot; required under CSRD's ESRS E1 for value-chain emissions."),
    "parity": ("social", "2026", "2026",
        "Renforce la diversité et la conformité (loi Rixain, transparence salariale UE) ; améliore l'attractivité employeur.",
        "Strengthens diversity and compliance (EU pay transparency); improves employer attractiveness."),
    "training": ("social", "Continu", "Ongoing",
        "Développe les compétences et la fidélisation ; réduit le turnover et sécurise la transformation.",
        "Builds skills and retention; lowers turnover and de-risks transformation."),
    "audit": ("gov", "Annuel", "Annual",
        "Apporte l'assurance d'un tiers désormais requise par la CSRD ; renforce la confiance des investisseurs.",
        "Provides third-party assurance now required by CSRD; strengthens investor confidence."),
    "committee": ("gov", "Court terme", "Short term",
        "Ancre la supervision ESG au plus haut niveau de gouvernance et fiabilise le pilotage des objectifs.",
        "Embeds ESG oversight at the highest governance level and secures target steering."),
    "recycling": ("env", "2027", "2027",
        "Fait progresser l'économie circulaire (ESRS E5) et réduit les coûts de traitement des déchets.",
        "Advances the circular economy (ESRS E5) and cuts waste-disposal costs."),
    "frameworks": ("gov", "Continu", "Ongoing",
        "Renforce l'alignement sur les cadres de référence (ODD, TCFD) et la comparabilité du reporting.",
        "Strengthens alignment with reference frameworks (SDGs, TCFD) and reporting comparability."),
}

_REC_TITLES = {
    "renewable": ("Augmenter la part d'énergie renouvelable à 50%", "Raise the renewable-energy share to 50%"),
    "scope3": ("Mesurer et reporter les émissions Scope 3", "Measure and report Scope 3 emissions"),
    "parity": ("Définir des objectifs chiffrés de parité femme-homme", "Set quantified gender-balance targets"),
    "training": ("Porter la formation à 20h/employé/an minimum", "Raise training to at least 20h/employee/year"),
    "audit": ("Commander un audit ESG indépendant annuel", "Commission an annual independent ESG audit"),
    "committee": ("Créer un comité de durabilité au conseil", "Create a Board-level sustainability committee"),
    "recycling": ("Viser 60% de taux de recyclage des déchets", "Target a 60% waste-recycling rate"),
    "frameworks": ("Aligner la stratégie ESG sur les ODD & la TCFD", "Align the ESG strategy with the SDGs & TCFD"),
}


def enriched_recommendations(request: ESGRequest, scores: ESGScores) -> list:
    """Recommandations avec titre, bénéfice, pilier et horizon (FR/EN)."""
    en = getattr(request, "language", "fr") == "en"
    env, soc, gov = request.environmental, request.social, request.governance
    keys = []
    if env.renewable_energy_percent is None or env.renewable_energy_percent < 50: keys.append("renewable")
    if env.scope3_emissions is None: keys.append("scope3")
    if soc.female_employees_percent is None or soc.female_employees_percent < 40: keys.append("parity")
    if soc.training_hours_per_employee is None or soc.training_hours_per_employee < 20: keys.append("training")
    if not gov.esg_audit_conducted: keys.append("audit")
    if not gov.sustainability_committee: keys.append("committee")
    if env.waste_recycled_percent is None or env.waste_recycled_percent < 60: keys.append("recycling")
    keys.append("frameworks")

    out = []
    for k in keys[:6]:
        pillar, hfr, hen, dfr, den = _REC_META[k]
        tfr, ten = _REC_TITLES[k]
        out.append({
            "title": ten if en else tfr,
            "detail": den if en else dfr,
            "pillar": pillar,
            "horizon": hen if en else hfr,
        })
    return out


# ══════════════════════════════════════════════════════════════════════════
# INSIGHTS MÉTIER — message principal de chaque slide (lisible en < 5 s)
# ══════════════════════════════════════════════════════════════════════════

def _band(score):
    if score >= 75: return "high"
    if score >= 60: return "good"
    if score >= 45: return "mid"
    return "low"


_PILLAR_INSIGHT = {
    "fr": {
        "env": {
            "high": "Performance environnementale de premier plan : la maîtrise du carbone et de l'énergie constitue un actif différenciant.",
            "good": "Performance environnementale solide, au-dessus de la moyenne sectorielle ; l'intensité carbone reste le principal levier de création de valeur durable.",
            "mid": "Trajectoire environnementale engagée mais inégale : la décarbonation et la mesure Scope 3 conditionnent la conformité CSRD.",
            "low": "Performance environnementale en retrait : la transition bas-carbone doit devenir une priorité stratégique à court terme.",
        },
        "social": {
            "high": "Capital humain valorisé et sécurisé : un atout de marque employeur et de résilience opérationnelle.",
            "good": "Socle social solide ; la diversité et la formation sont les leviers pour transformer la conformité en avantage compétitif.",
            "mid": "Performance sociale en construction : parité et sécurité au travail appellent des objectifs chiffrés pour fidéliser les talents.",
            "low": "Performance sociale à renforcer : le risque de rétention et de conformité justifie un plan d'action RH immédiat.",
        },
        "gov": {
            "high": "Gouvernance exemplaire : indépendance, audit et supervision ESG inspirent confiance aux investisseurs.",
            "good": "Gouvernance robuste ; l'assurance externe et le comité de durabilité consolident la crédibilité du reporting.",
            "mid": "Gouvernance à structurer : l'audit indépendant et un comité dédié sont attendus par les marchés financiers.",
            "low": "Gouvernance insuffisante : l'absence de contrôle ESG expose l'entreprise à un risque réputationnel et réglementaire.",
        },
    },
    "en": {
        "env": {
            "high": "Leading environmental performance: carbon and energy control is a differentiating asset.",
            "good": "Solid environmental performance, above the sector average; carbon intensity remains the main lever for sustainable value creation.",
            "mid": "Environmental trajectory engaged but uneven: decarbonisation and Scope 3 measurement drive CSRD compliance.",
            "low": "Lagging environmental performance: the low-carbon transition must become a near-term strategic priority.",
        },
        "social": {
            "high": "Human capital valued and protected: an asset for employer brand and operational resilience.",
            "good": "Solid social foundation; diversity and training are the levers to turn compliance into a competitive edge.",
            "mid": "Social performance under construction: gender balance and workplace safety call for quantified targets to retain talent.",
            "low": "Social performance to strengthen: retention and compliance risk warrants an immediate HR action plan.",
        },
        "gov": {
            "high": "Exemplary governance: independence, audit and ESG oversight inspire investor confidence.",
            "good": "Robust governance; external assurance and a sustainability committee reinforce reporting credibility.",
            "mid": "Governance to structure: independent audit and a dedicated committee are expected by financial markets.",
            "low": "Insufficient governance: the lack of ESG control exposes the company to reputational and regulatory risk.",
        },
    },
}


def pillar_insights(request: ESGRequest, scores: ESGScores) -> dict:
    lang = "en" if getattr(request, "language", "fr") == "en" else "fr"
    P = _PILLAR_INSIGHT[lang]
    return {
        "env": P["env"][_band(scores.environmental_score)],
        "social": P["social"][_band(scores.social_score)],
        "gov": P["gov"][_band(scores.governance_score)],
    }


def score_verdict(request: ESGRequest, scores: ESGScores) -> str:
    """Message d'ouverture du tableau de bord — l'idée principale en une phrase."""
    en = getattr(request, "language", "fr") == "en"
    name = request.company.name
    pillars = [("env", scores.environmental_score), ("social", scores.social_score),
               ("gov", scores.governance_score)]
    labels = {"fr": {"env": "l'environnement", "social": "le social", "gov": "la gouvernance"},
              "en": {"env": "environment", "social": "social", "gov": "governance"}}
    lab = labels["en" if en else "fr"]
    best = max(pillars, key=lambda x: x[1]); worst = min(pillars, key=lambda x: x[1])
    band = _band(scores.total_esg_score)
    if en:
        qual = {"high": "a leading", "good": "a solid", "mid": "a developing", "low": "an early-stage"}[band]
        return (f"{name} shows {qual} ESG profile ({scores.total_esg_score:.0f}/100, {scores.rating}), "
                f"anchored by {lab[best[0]]} ({best[1]:.0f}/100); "
                f"{lab[worst[0]]} ({worst[1]:.0f}/100) concentrates the improvement potential.")
    qual = {"high": "un profil ESG de premier plan", "good": "un profil ESG solide",
            "mid": "un profil ESG en développement", "low": "un profil ESG en structuration"}[band]
    return (f"{name} affiche {qual} ({scores.total_esg_score:.0f}/100, {scores.rating}), "
            f"porté par {lab[best[0]]} ({best[1]:.0f}/100) ; "
            f"{lab[worst[0]]} ({worst[1]:.0f}/100) concentre le potentiel de progression.")


# ══════════════════════════════════════════════════════════════════════════
# HEADLINES « INFORMATION SCENT » — le titre porte déjà la conclusion
# ══════════════════════════════════════════════════════════════════════════

def pillar_headline(request: ESGRequest, scores: ESGScores) -> dict:
    """Sous-titre-conclusion par pilier (rang + niveau), FR/EN."""
    en = getattr(request, "language", "fr") == "en"
    pil = [("env", scores.environmental_score), ("social", scores.social_score),
           ("gov", scores.governance_score)]
    best = max(pil, key=lambda x: x[1])[0]
    worst = min(pil, key=lambda x: x[1])[0]
    same = len({p[1] for p in pil}) == 1

    def phrase(key, sc):
        if not same and key == best:
            return "The cornerstone of the ESG profile" if en else "Le point fort du profil ESG"
        if not same and key == worst:
            return "The main lever for ESG progress" if en else "Le principal levier de progression ESG"
        if sc >= 75:
            return "A leading performance" if en else "Une performance de premier plan"
        if sc >= 60:
            return "A solid performance" if en else "Une performance solide"
        if sc >= 45:
            return "A trajectory to consolidate" if en else "Une trajectoire à consolider"
        return "A priority area for action" if en else "Un chantier prioritaire"

    return {k: phrase(k, sc) for k, sc in pil}


# ══════════════════════════════════════════════════════════════════════════
# TITRES-CONCLUSION DE SECTION (une slide = une idée forte)
# ══════════════════════════════════════════════════════════════════════════

def section_headlines(request: ESGRequest, scores: ESGScores) -> dict:
    """Titres qui portent déjà la conclusion, par slide. FR/EN."""
    en = getattr(request, "language", "fr") == "en"
    from esg_advanced import materiality_topics
    env = request.environmental
    tx = request.taxonomy
    ty = max(request.company.target_year, request.company.reporting_year + 1)

    # Matérialité : enjeu le plus prioritaire (impact + financier)
    topics = materiality_topics(request, scores, "en" if en else "fr")
    top_topic = max(topics, key=lambda t: t["impact"] + t["financial"])["label"]

    # Taxonomie : métrique la mieux alignée
    tax_items = []
    if tx:
        if tx.turnover_aligned_percent is not None:
            tax_items.append((tx.turnover_aligned_percent, "du chiffre d'affaires" if not en else "of turnover"))
        if tx.capex_aligned_percent is not None:
            tax_items.append((tx.capex_aligned_percent, "des investissements (CapEx)" if not en else "of CapEx"))
        if tx.opex_aligned_percent is not None:
            tax_items.append((tx.opex_aligned_percent, "des dépenses (OpEx)" if not en else "of OpEx"))
    tax_top = max(tax_items, key=lambda x: x[0]) if tax_items else None

    ns, nw = len(scores.strengths), len(scores.weaknesses)

    if en:
        materiality = f"{top_topic} is the top-priority ESG issue"
        objectives = ("A -42% emissions pathway by 2030" if env.co2_emissions_tonnes
                      else f"Quantified ESG objectives by {ty}")
        taxonomy = (f"{tax_top[0]:.0f}% {tax_top[1]} already EU Taxonomy-aligned"
                    if tax_top else "EU Taxonomy alignment under way")
        strategic = f"{ns} established strengths, {nw} levers for progress"
        odd = "An ESG strategy anchored in the UN SDGs"
    else:
        materiality = f"Le {top_topic.lower()} concentre les enjeux ESG prioritaires"
        objectives = ("Une trajectoire de -42 % des émissions d'ici 2030" if env.co2_emissions_tonnes
                      else f"Des objectifs ESG chiffrés à horizon {ty}")
        taxonomy = (f"{tax_top[0]:.0f} % {tax_top[1]} déjà alignés à la Taxonomie UE"
                    if tax_top else "Alignement Taxonomie UE en cours")
        strategic = f"{ns} forces établies, {nw} leviers de progression"
        odd = "Une stratégie ESG ancrée dans les ODD de l'ONU"

    return {"materiality": materiality, "objectives": objectives,
            "taxonomy": taxonomy, "strategic": strategic, "odd": odd}


# ══════════════════════════════════════════════════════════════════════════
# VERDICT BENCHMARK & MATURITÉ (diagnostic personnalisé)
# ══════════════════════════════════════════════════════════════════════════

def benchmark_verdict(request: ESGRequest, scores: ESGScores) -> dict:
    """Titre-conclusion + lecture du positionnement vs. secteur."""
    from esg_advanced import sector_benchmark
    en = getattr(request, "language", "fr") == "en"
    bm = sector_benchmark(request, scores)
    gd = bm["deltas"]["global"]
    name, sector = request.company.name, request.company.sector
    d = bm["deltas"]
    labels = {"fr": {"env": "l'environnement", "social": "le social", "gov": "la gouvernance"},
              "en": {"env": "environment", "social": "social", "gov": "governance"}}[("en" if en else "fr")]
    lead = max(("env", "social", "gov"), key=lambda k: d[k])
    lag = min(("env", "social", "gov"), key=lambda k: d[k])
    agd = abs(gd)
    if en:
        title = (f"{name} outperforms its sector by {gd:.0f} points" if gd >= 8 else
                 f"{name} is above its sector average (+{gd:.0f} pts)" if gd >= 2 else
                 f"{name} is in line with its sector average" if gd >= -2 else
                 f"{name} is {agd:.0f} pts below its sector average")
        insight = (f"Your edge is on {labels[lead]} (+{d[lead]:.0f} pts vs sector); "
                   f"{labels[lag]} ({d[lag]:+.0f} pts) is where the gap must be closed.")
    else:
        title = (f"{name} surperforme son secteur de {gd:.0f} points" if gd >= 8 else
                 f"{name} devance la moyenne de son secteur (+{gd:.0f} pts)" if gd >= 2 else
                 f"{name} est aligné sur la moyenne de son secteur" if gd >= -2 else
                 f"{name} se situe {agd:.0f} pts sous la moyenne de son secteur")
        insight = (f"Votre avance se joue sur {labels[lead]} (+{d[lead]:.0f} pts vs secteur) ; "
                   f"{labels[lag]} ({d[lag]:+.0f} pts) est l'écart à combler en priorité.")
    return {"title": title, "insight": insight, "bm": bm}


def maturity_text(request: ESGRequest, scores: ESGScores) -> dict:
    """Stade de maturité + ce qui fait passer le cap suivant."""
    from esg_advanced import esg_maturity
    en = getattr(request, "language", "fr") == "en"
    m = esg_maturity(request, scores)
    gap_txt = {"fr": {"scope3": "mesurer le Scope 3", "audit": "faire auditer le reporting",
                      "committee": "créer un comité de durabilité"},
               "en": {"scope3": "measure Scope 3", "audit": "get the reporting audited",
                      "committee": "set up a sustainability committee"}}[("en" if en else "fr")]
    levers = [gap_txt[g] for g in m["gaps"][:2]]
    if m["next"] and levers:
        joiner = " and " if en else " et "
        nxt = (f"To reach the next level: {joiner.join(levers)}." if en
               else f"Pour franchir le cap suivant : {joiner.join(levers)}.")
    elif m["next"]:
        nxt = "Consolidate the current level to progress." if en else "Consolider le niveau actuel pour progresser."
    else:
        nxt = "Highest maturity level reached." if en else "Niveau de maturité maximal atteint."
    return {"stage": m["stage"], "key": m["key"], "next_hint": nxt}
