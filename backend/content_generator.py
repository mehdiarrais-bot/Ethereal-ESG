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

# ── Accords grammaticaux (aucun « (s) » ne doit apparaître dans les livrables)
_NUM_FR = ["zéro", "une", "deux", "trois", "quatre", "cinq", "six", "sept",
           "huit", "neuf", "dix", "onze", "douze"]
_NUM_FR_M = ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept",
             "huit", "neuf", "dix", "onze", "douze"]
_NUM_EN = ["zero", "one", "two", "three", "four", "five", "six", "seven",
           "eight", "nine", "ten", "eleven", "twelve"]

def _nb(n, en=False, fem=False):
    """Nombre en lettres jusqu'à douze, chiffres au-delà."""
    n = int(n)
    lst = _NUM_EN if en else (_NUM_FR if fem else _NUM_FR_M)
    return lst[n] if 0 <= n < len(lst) else str(n)

def _agree(n, sing, plur, en=False, fem=False):
    """« un point fort consolidé » / « deux points forts consolidés »."""
    return f"{_nb(n, en, fem)} {sing if int(n) == 1 else plur}"

def _pts(v):
    """« 1 pt » / « 13 pts » (valeur déjà arrondie à l'entier)."""
    n = abs(int(round(v)))
    return f"{n} pt" if n == 1 else f"{n} pts"

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
        content = _generate_en(request, scores)
    else:
        content = _generate_fr(request, scores)
    return deepen_content(request, scores, content)


# ══════════════════════════════════════════════════════════════════════════
# APPROFONDISSEMENT (niveau rapport CSRD : IRO, gap analysis, méthodologie)
# ══════════════════════════════════════════════════════════════════════════

# Risques climatiques physiques & de transition par famille sectorielle.
# (clé matching lower-case ; FR, EN)
_CLIMATE_SECTOR = {
    "industri": (
        ("la vulnérabilité des sites de production aux vagues de chaleur et au stress hydrique (refroidissement des procédés), ainsi que la perturbation des chaînes d'approvisionnement en matières premières",
         "le renchérissement du carbone (SEQE-UE, taxe carbone aux frontières CBAM) sur les intrants énergo-intensifs et l'exigence croissante d'écoconception de la part des donneurs d'ordre"),
        ("the vulnerability of production sites to heatwaves and water stress (process cooling), and the disruption of raw-material supply chains",
         "rising carbon costs (EU ETS, CBAM carbon border adjustment) on energy-intensive inputs and growing eco-design requirements from principals"),
    ),
    "agro": (
        ("l'exposition directe des rendements et des approvisionnements agricoles à la sécheresse, au gel tardif et aux régimes de précipitations erratiques",
         "l'évolution des attentes consommateurs vers des produits bas-carbone et la réglementation croissante sur la déforestation importée (règlement EUDR)"),
        ("the direct exposure of yields and agricultural sourcing to drought, late frost and erratic rainfall patterns",
         "shifting consumer expectations towards low-carbon products and growing regulation on imported deforestation (EUDR)"),
    ),
    "transport": (
        ("l'exposition des infrastructures et des flux aux événements extrêmes (inondations, tempêtes) et la congestion liée aux dérèglements",
         "la décarbonation imposée des flottes (normes CO₂, ZFE) et la volatilité des prix des carburants"),
        ("the exposure of infrastructure and flows to extreme events (floods, storms) and disruption-related congestion",
         "mandatory fleet decarbonisation (CO₂ standards, low-emission zones) and fuel-price volatility"),
    ),
    "logisti": (
        ("l'exposition des infrastructures et des flux aux événements extrêmes (inondations, tempêtes) et la congestion liée aux dérèglements",
         "la décarbonation imposée des flottes (normes CO₂, ZFE) et la volatilité des prix des carburants"),
        ("the exposure of infrastructure and flows to extreme events (floods, storms) and disruption-related congestion",
         "mandatory fleet decarbonisation (CO₂ standards, low-emission zones) and fuel-price volatility"),
    ),
    "btp": (
        ("la sinistralité accrue des chantiers en période de canicule et l'exposition du parc construit aux aléas climatiques",
         "le durcissement des normes de performance énergétique (RE2020, rénovation) et le renchérissement des matériaux carbonés (ciment, acier)"),
        ("higher site incident rates during heatwaves and the exposure of the built stock to climate hazards",
         "tightening energy-performance standards and the rising cost of carbon-intensive materials (cement, steel)"),
    ),
    "construction": (
        ("la sinistralité accrue des chantiers en période de canicule et l'exposition du parc construit aux aléas climatiques",
         "le durcissement des normes de performance énergétique (RE2020, rénovation) et le renchérissement des matériaux carbonés (ciment, acier)"),
        ("higher site incident rates during heatwaves and the exposure of the built stock to climate hazards",
         "tightening energy-performance standards and the rising cost of carbon-intensive materials (cement, steel)"),
    ),
    "numéri": (
        ("la dépendance des datacenters au refroidissement en période de canicule et la fragilité des infrastructures réseau face aux événements extrêmes",
         "la pression réglementaire et client sur l'efficacité énergétique du numérique et la sobriété des usages"),
        ("datacentre cooling dependence during heatwaves and the fragility of network infrastructure in extreme events",
         "regulatory and customer pressure on digital energy efficiency and usage sobriety"),
    ),
    "tech": (
        ("la dépendance des datacenters au refroidissement en période de canicule et la fragilité des infrastructures réseau face aux événements extrêmes",
         "la pression réglementaire et client sur l'efficacité énergétique du numérique et la sobriété des usages"),
        ("datacentre cooling dependence during heatwaves and the fragility of network infrastructure in extreme events",
         "regulatory and customer pressure on digital energy efficiency and usage sobriety"),
    ),
    "commerce": (
        ("la vulnérabilité des chaînes d'approvisionnement mondiales aux aléas climatiques et l'impact des canicules sur les points de vente",
         "l'exigence de transparence sur l'empreinte des produits (affichage environnemental) et le devoir de vigilance sur la chaîne amont"),
        ("the vulnerability of global supply chains to climate hazards and the impact of heatwaves on retail sites",
         "product-footprint transparency requirements (environmental labelling) and due-diligence duties on the upstream chain"),
    ),
    "énergie": (
        ("l'exposition des actifs de production et des réseaux aux événements extrêmes et à la disponibilité de la ressource en eau",
         "la recomposition rapide du mix énergétique, le risque d'actifs échoués et l'évolution des mécanismes de soutien"),
        ("the exposure of generation assets and grids to extreme events and water availability",
         "the rapid recomposition of the energy mix, stranded-asset risk and evolving support mechanisms"),
    ),
    "finance": (
        ("l'exposition indirecte des portefeuilles aux actifs physiquement vulnérables",
         "le risque de crédit et de marché lié aux actifs carbonés, et les obligations de reporting SFDR/Pilier 3 ESG"),
        ("indirect portfolio exposure to physically vulnerable assets",
         "credit and market risk on carbon-intensive assets, and SFDR/ESG Pillar 3 reporting duties"),
    ),
}

def _climate_sector_risks(sector: str, en: bool):
    s = (sector or "").lower()
    for key, (fr_pair, en_pair) in _CLIMATE_SECTOR.items():
        if key in s:
            return en_pair if en else fr_pair
    return (("l'exposition des actifs, des collaborateurs et de la chaîne d'approvisionnement aux événements climatiques extrêmes et chroniques",
             "le renchérissement du carbone et de l'énergie, ainsi que l'évolution des attentes réglementaires et commerciales")
            if not en else
            ("the exposure of assets, employees and the supply chain to acute and chronic climate events",
             "rising carbon and energy costs, together with evolving regulatory and commercial expectations"))


def _esrs_gaps(request: ESGRequest, en: bool) -> list:
    """Points de données ESRS structurants non renseignés (gap analysis)."""
    env, soc, gov = request.environmental, request.social, request.governance
    gaps = []
    if env.scope3_emissions is None:
        gaps.append(("les émissions de Scope 3 (ESRS E1-6), qui représentent en général la majorité de l'empreinte",
                     "Scope 3 emissions (ESRS E1-6), which typically account for most of the footprint"))
    if env.energy_consumption_mwh is None:
        gaps.append(("la consommation énergétique totale et sa décomposition (ESRS E1-5)",
                     "total energy consumption and its breakdown (ESRS E1-5)"))
    if env.water_consumption_m3 is None:
        gaps.append(("les prélèvements d'eau (ESRS E3)", "water withdrawals (ESRS E3)"))
    if soc.employee_turnover_percent is None:
        gaps.append(("le taux de rotation des effectifs (ESRS S1-6)", "employee turnover (ESRS S1-6)"))
    if soc.accident_frequency_rate is None:
        gaps.append(("les indicateurs de santé-sécurité (ESRS S1-14)", "health & safety indicators (ESRS S1-14)"))
    if gov.board_members is None:
        gaps.append(("la composition détaillée de l'organe d'administration (ESRS 2 GOV-1)",
                     "the detailed composition of the administrative body (ESRS 2 GOV-1)"))
    if not gov.esg_audit_conducted:
        gaps.append(("la vérification par un tiers indépendant, requise par la CSRD (assurance limitée)",
                     "independent third-party assurance, required by the CSRD (limited assurance)"))
    return [g[1] if en else g[0] for g in gaps]


def deepen_content(request: ESGRequest, scores: ESGScores, content: dict) -> dict:
    """Élève les textes au niveau d'un rapport de durabilité CSRD :
    matérialité citant les enjeux réels cotés, risques climat sectorisés par
    horizon, analyse ESRS par pilier, note méthodologique, synthèse décisionnelle."""
    en = getattr(request, "language", "fr") == "en"
    name = request.company.name
    env = request.environmental
    from esg_advanced import materiality_topics, sector_benchmark, esg_maturity
    bm = sector_benchmark(request, scores)
    mat = esg_maturity(request, scores)
    topics = sorted(materiality_topics(request, scores, "en" if en else "fr"),
                    key=lambda t: t["impact"] + t["financial"], reverse=True)
    top3 = topics[:3]

    def t3(fmt_fr, fmt_en):
        f = fmt_en if en else fmt_fr
        return " ; ".join(f.format(l=tp["label"], i=tp["impact"], fi=tp["financial"]) for tp in top3)

    # ── 1. Double matérialité : processus IRO + résultats réels ──────────
    if en:
        content["materiality"] = (
            f"In accordance with the CSRD and ESRS 1/ESRS 2 (IRO-1, SBM-3), {name} conducted a double "
            f"materiality assessment covering its own operations and its upstream and downstream value "
            f"chain. The process followed four steps: (i) mapping of impacts, risks and opportunities "
            f"(IROs) per ESRS topic, based on the reported indicators; (ii) rating of impact materiality "
            f"(severity × scope × irremediability, plus likelihood for potential impacts) and financial "
            f"materiality (magnitude × likelihood of effects on cash flows, cost of capital and access "
            f"to financing) on a 0-10 scale; (iii) consolidation into the materiality matrix; "
            f"(iv) internal validation by ESG governance. "
            f"The assessment identifies the following as the most material topics for {name}: "
            + t3("", "{l} (impact {i:.1f}/10, financial {fi:.1f}/10)") + ". "
            f"These topics determine the ESRS disclosure requirements applicable to the report and "
            f"concentrate the action plan resources; topics assessed as non-material are documented "
            f"and re-examined at each annual review."
        )
    else:
        content["materiality"] = (
            f"Conformément à la CSRD et aux normes ESRS 1/ESRS 2 (IRO-1, SBM-3), {name} a conduit une "
            f"analyse de double matérialité couvrant ses opérations propres ainsi que sa chaîne de "
            f"valeur amont et aval. Le processus a suivi quatre étapes : (i) cartographie des impacts, "
            f"risques et opportunités (IRO) par thématique ESRS, à partir des indicateurs déclarés ; "
            f"(ii) cotation de la matérialité d'impact (sévérité × étendue × irrémédiabilité, pondérée "
            f"par la probabilité pour les impacts potentiels) et de la matérialité financière "
            f"(ampleur × probabilité des effets sur les flux de trésorerie, le coût du capital et "
            f"l'accès au financement) sur une échelle de 0 à 10 ; (iii) consolidation dans la matrice "
            f"de matérialité ; (iv) validation interne par la gouvernance ESG. "
            f"L'analyse identifie comme enjeux les plus matériels pour {name} : "
            + t3("{l} (impact {i:.1f}/10, financier {fi:.1f}/10)", "") + ". "
            f"Ces enjeux déterminent les exigences de publication ESRS applicables au rapport et "
            f"concentrent les moyens du plan d'action ; les enjeux jugés non matériels sont documentés "
            f"et réexaminés à chaque revue annuelle."
        )

    # ── 2. Risques climatiques : sectorisés + horizons + résilience ──────
    phys, trans = _climate_sector_risks(request.company.sector, en)
    ci = (env.co2_emissions_tonnes / request.company.revenue_eur * 1e6
          if (env.co2_emissions_tonnes and request.company.revenue_eur) else None)
    if en:
        exposure = ""
        if ci is not None:
            lvl = ("high" if ci > 100 else "moderate" if ci > 30 else "contained")
            exposure = (f" With a carbon intensity of {ci:.0f} t CO₂e/€M revenue, the company's exposure "
                        f"to a carbon price of €100/t is assessed as {lvl}.")
        renew = (f" The renewable share of the energy mix ({env.renewable_energy_percent:.0f}%) partially "
                 f"mitigates energy-transition risk." if env.renewable_energy_percent is not None else "")
        content["climate_risk"] = (
            f"In line with TCFD recommendations and ESRS E1 (E1-9), {name} analyses its climate risks "
            f"over three horizons: short term (0-3 years, aligned with budget cycles), medium term "
            f"(3-10 years) and long term (beyond 10 years). Physical risks primarily concern {phys}. "
            f"Transition risks are driven by {trans}.{exposure}{renew} "
            f"The associated opportunities — energy efficiency, low-carbon offerings, access to "
            f"sustainability-linked financing — are assessed alongside the risks. The resilience of the "
            f"business model is reviewed against two reference scenarios (below 2°C and above 3°C), and "
            f"the findings feed the risk register and the strategic plan."
        )
    else:
        exposure = ""
        if ci is not None:
            lvl = ("élevée" if ci > 100 else "modérée" if ci > 30 else "contenue")
            exposure = (f" Avec une intensité carbone de {ci:.0f} t CO₂e/M€ de CA, l'exposition de "
                        f"l'entreprise à un prix du carbone de 100 €/t est jugée {lvl}.")
        renew = (f" La part renouvelable du mix énergétique ({env.renewable_energy_percent:.0f} %) atténue "
                 f"partiellement le risque de transition énergétique." if env.renewable_energy_percent is not None else "")
        content["climate_risk"] = (
            f"En ligne avec les recommandations de la TCFD et la norme ESRS E1 (E1-9), {name} analyse "
            f"ses risques climatiques sur trois horizons : court terme (0-3 ans, aligné sur les cycles "
            f"budgétaires), moyen terme (3-10 ans) et long terme (au-delà de 10 ans). Les risques "
            f"physiques concernent en premier lieu {phys}. Les risques de transition sont portés par "
            f"{trans}.{exposure}{renew} "
            f"Les opportunités associées — efficacité énergétique, offres bas-carbone, accès aux "
            f"financements à impact — sont évaluées en miroir des risques. La résilience du modèle "
            f"d'affaires est examinée au regard de deux scénarios de référence (inférieur à 2 °C et "
            f"supérieur à 3 °C), et les conclusions alimentent la cartographie des risques et le plan "
            f"stratégique."
        )

    # ── 3. Analyse ESRS + benchmark par pilier (phrase de clôture) ───────
    def bench_sentence(delta, en):
        if en:
            pos = "above" if delta >= 0 else "below"
            return f" The pillar stands {_pts(delta)} {pos} the internal sector reference"
        pos = "au-dessus de" if delta >= 0 else "en retrait de"
        return f" Le pilier se situe {_pts(delta)} {pos} la référence sectorielle interne"

    esrs_close = {
        "environmental": (" et couvre les principales exigences des normes ESRS E1 (climat) et E5 (économie circulaire).",
                          " and covers the main requirements of ESRS E1 (climate) and E5 (circular economy)."),
        "social": (" ; le reporting s'inscrit dans le périmètre de la norme ESRS S1 (effectifs propres).",
                   "; reporting falls within the scope of ESRS S1 (own workforce)."),
        "governance": (" ; le dispositif répond aux attendus des normes ESRS G1 (conduite des affaires) et ESRS 2 (gouvernance des enjeux de durabilité).",
                       "; the framework addresses ESRS G1 (business conduct) and ESRS 2 (sustainability governance)."),
    }
    for key, dkey in (("environmental", "env"), ("social", "social"), ("governance", "gov")):
        close_fr, close_en = esrs_close[key]
        content[key] = (content[key] + bench_sentence(bm["deltas"][dkey], en)
                        + (close_en if en else close_fr))

    # ── 4. Synthèse exécutive : ajout du « so what » décisionnel ─────────
    gaps = _esrs_gaps(request, en)
    gd = bm["deltas"]["global"]
    stage_fr = {"initiated": "initiée", "structuring": "en structuration", "structured": "structurée",
                "advanced": "avancée", "exemplary": "exemplaire"}
    stage_en = {"initiated": "initiated", "structuring": "structuring", "structured": "structured",
                "advanced": "advanced", "exemplary": "exemplary"}
    if en:
        pos = f"{_pts(gd)} {'above' if gd >= 0 else 'below'} the sector reference"
        content["executive_summary"] += (
            f" Overall, the profile stands {pos}, with an ESG maturity assessed as "
            f"{stage_en.get(mat.get('key', 'structured'), 'structured')} ({mat['stage']}/5). "
            + (f"Closing the priority reporting gaps — notably {gaps[0]} — is the fastest lever to "
               f"secure CSRD readiness and strengthen investor confidence." if gaps else
               f"Reporting coverage is complete on the structural CSRD datapoints, an asset for "
               f"assurance and investor dialogue.")
        )
    else:
        pos = f"{_pts(gd)} {'au-dessus' if gd >= 0 else 'en retrait'} de la référence sectorielle"
        content["executive_summary"] += (
            f" Au global, le profil se situe {pos}, avec une maturité ESG évaluée comme "
            f"{stage_fr.get(mat.get('key', 'structured'), 'structurée')} ({mat['stage']}/5). "
            + (f"Combler les lacunes de reporting prioritaires — au premier rang desquelles "
               f"{gaps[0]} — constitue le levier le plus rapide pour sécuriser la conformité CSRD "
               f"et renforcer la confiance des investisseurs." if gaps else
               f"La couverture du reporting est complète sur les points de données structurants de la "
               f"CSRD, un atout pour la vérification et le dialogue investisseurs.")
        )

    # ── 4bis. Initiatives internes : ancrage dans la réalité de l'entreprise ─
    ki_raw = getattr(request.company, "key_initiatives", None)
    if ki_raw:
        import re as _re
        items = [x.strip() for x in _re.split(r"[;,]", ki_raw) if x.strip()][:5]
        if items:
            if len(items) == 1:
                listed = items[0]
            elif en:
                listed = ", ".join(items[:-1]) + " and " + items[-1]
            else:
                listed = ", ".join(items[:-1]) + " et " + items[-1]
            if en:
                content["executive_summary"] += (
                    f" This approach builds on initiatives already under way, including {listed}.")
            else:
                content["executive_summary"] += (
                    f" Cette démarche s'appuie sur des initiatives déjà engagées, notamment {listed}.")

    # ── 5. Note méthodologique (périmètre, référentiels, limites) ────────
    year = request.company.reporting_year
    gap_txt = ""
    if gaps:
        listed = " ; ".join(gaps[:3]) if not en else "; ".join(gaps[:3])
        gap_txt = ((f" Les points de données suivants restent à consolider : {listed}.")
                   if not en else (f" The following datapoints remain to be consolidated: {listed}."))
    if en:
        content["methodology"] = (
            f"Reporting scope and methodology. The indicators cover the {year} financial year on an "
            f"operational-control basis. Greenhouse-gas emissions are computed according to the GHG "
            f"Protocol (Scopes 1, 2 and 3); social indicators follow ESRS S1 definitions; governance "
            f"indicators are documented from corporate records. Pillar scores (0-100) aggregate each "
            f"indicator against regulatory thresholds and recognised sector standards; the overall score "
            f"is the weighted average of the three pillars, and the letter rating (internal AAA-CCC "
            f"scale) is indicative — it does not constitute a rating-agency assessment. The sector "
            f"comparison uses an internal "
            f"reference base for the SME/mid-cap market and involves no external data transfer — the "
            f"entire report is produced locally. Limitations: some indicators rely on declarative data "
            f"and estimates; they are refined as measurement systems mature.{gap_txt}"
        )
    else:
        content["methodology"] = (
            f"Périmètre et méthodologie du reporting. Les indicateurs couvrent l'exercice {year} selon "
            f"l'approche du contrôle opérationnel. Les émissions de gaz à effet de serre sont calculées "
            f"selon le GHG Protocol (Scopes 1, 2 et 3) ; les indicateurs sociaux suivent les définitions "
            f"de la norme ESRS S1 ; les indicateurs de gouvernance sont documentés à partir des registres "
            f"de l'entreprise. Les scores par pilier (0-100) agrègent chaque indicateur au regard des "
            f"seuils réglementaires et des standards sectoriels reconnus ; le score global est la moyenne "
            f"pondérée des trois piliers, et la notation lettrée (échelle interne AAA-CCC) est indicative — "
            f"elle ne constitue pas une notation d'agence. La comparaison sectorielle s'appuie sur une base de référence "
            f"interne du marché PME/ETI et n'implique aucun transfert de données externe — l'ensemble du "
            f"rapport est produit localement. Limites : certains indicateurs reposent sur des données "
            f"déclaratives et des estimations ; ils sont affinés à mesure que les dispositifs de mesure "
            f"gagnent en maturité.{gap_txt}"
        )

    return content


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
    # Contexte sectoriel déjà dans l'ouverture, priorité déjà dans la section
    # environnement : pas de répétition dans la synthèse.
    sector_note = ""
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
        env_items.append(_agree(env.biodiversity_initiatives,
                                "initiative biodiversité", "initiatives biodiversité", fem=True))

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
        elif gap <= 5: fem_n = f"à {_pts(gap)} de l'objectif 40%"
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
        rixain = "conforme loi Rixain (≥40%)" if gov.female_board_percent >= 40 else f"{_pts(40 - gov.female_board_percent)} sous l'objectif Rixain 40%"
        gov_items.append(f"{gov.female_board_percent:.0f}% de femmes au CA ({rixain})")
    if gov.independent_board_percent is not None:
        afep = "conforme AFEP-MEDEF (≥50%)" if gov.independent_board_percent >= 50 else "sous le seuil AFEP-MEDEF 50%"
        gov_items.append(f"{gov.independent_board_percent:.0f}% d'administrateurs indépendants ({afep})")
    if gov.csr_budget_eur:
        gov_items.append(f"budget RSE {gov.csr_budget_eur:,.0f} €")
    if gov.ethics_violations is not None:
        gov_items.append("aucun manquement éthique enregistré" if gov.ethics_violations == 0
                         else _agree(gov.ethics_violations, "manquement éthique", "manquements éthiques"))
    if gov.data_breaches is not None and gov.data_breaches > 0:
        gov_items.append(_agree(gov.data_breaches, "incident cybersécurité déclaré",
                                "incidents cybersécurité déclarés"))
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

    s_txt = _agree(n_s, "point fort consolidé", "points forts consolidés") if n_s else "des points forts émergents"
    w_txt = _agree(n_w, "axe d'amélioration prioritaire", "axes d'amélioration prioritaires") if n_w else "des axes de progrès identifiés"

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
    # Sector context already in the opening and the priority in the environment
    # section: no repetition in the summary.
    sector_note = ""
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
        items.append(_agree(env.biodiversity_initiatives,
                            "biodiversity initiative", "biodiversity initiatives", en=True))
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
        fn = "legal 40% target met" if gap <= 0 else f"{_pts(gap)} from the 40% target" if gap <= 5 else f"{gap:.0f} pts below the 40% target"
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
        rx = "compliant with the 40% quota" if gov.female_board_percent >= 40 else f"{_pts(40 - gov.female_board_percent)} below the 40% quota"
        items.append(f"{gov.female_board_percent:.0f}% women on the Board ({rx})")
    if gov.independent_board_percent is not None:
        ind = "≥50% independence met" if gov.independent_board_percent >= 50 else "below the 50% independence threshold"
        items.append(f"{gov.independent_board_percent:.0f}% independent directors ({ind})")
    if gov.csr_budget_eur:
        items.append(f"CSR budget €{gov.csr_budget_eur:,.0f}")
    if gov.ethics_violations is not None:
        items.append("no ethics breach recorded" if gov.ethics_violations == 0
                     else _agree(gov.ethics_violations, "ethics breach", "ethics breaches", en=True))
    if gov.data_breaches is not None and gov.data_breaches > 0:
        items.append(_agree(gov.data_breaches, "cybersecurity incident reported",
                            "cybersecurity incidents reported", en=True))
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
    s_txt = _agree(len(scores.strengths), "consolidated strength", "consolidated strengths", en=True) if scores.strengths else "emerging strengths"
    w_txt = _agree(len(scores.weaknesses), "priority area for improvement", "priority areas for improvement", en=True) if scores.weaknesses else "identified areas for progress"
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

# Cotation de priorisation : (effort de mise en œuvre 1-10, impact ESG/valeur 1-10)
_REC_PRIORITY = {
    "renewable": (7, 8),   # investissement / PPA, mais gain carbone + coûts majeur
    "scope3": (6, 9),      # collecte lourde chaîne de valeur, critique CSRD
    "parity": (4, 6),
    "training": (3, 5),
    "audit": (3, 8),       # quick win crédibilité / conformité
    "committee": (2, 7),   # quick win gouvernance
    "recycling": (5, 5),
    "frameworks": (4, 6),
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
        effort, impact = _REC_PRIORITY.get(k, (5, 5))
        own_fr, own_en = _REC_OWNERS.get(k, ("Direction RSE", "CSR"))
        obj_fr, obj_en = _REC_OBJECTIVES.get(k, ("", ""))
        out.append({
            "key": k,
            "title": ten if en else tfr,
            "detail": den if en else dfr,
            "pillar": pillar,
            "horizon": hen if en else hfr,
            "effort": effort,
            "impact": impact,
            "owner": own_en if en else own_fr,
            "objective": obj_en if en else obj_fr,
        })
    return out


def priority_reading(request: ESGRequest, scores: ESGScores) -> str:
    """Lecture métier de la matrice effort/impact (quick wins nommés). FR/EN."""
    en = getattr(request, "language", "fr") == "en"
    recs = enriched_recommendations(request, scores)
    qw = [(i, r) for i, r in enumerate(recs, 1) if r["effort"] < 5 and r["impact"] >= 6]
    strat = [(i, r) for i, r in enumerate(recs, 1) if r["effort"] >= 5 and r["impact"] >= 7]

    def _join_nums(nums, conj):
        nums = [str(n) for n in nums]
        if len(nums) == 1:
            return nums[0]
        return ", ".join(nums[:-1]) + f" {conj} " + nums[-1]

    if en:
        if qw:
            ids = [i for i, _ in qw[:3]]
            if len(qw) == 1:
                txt = (f"One action combines high impact with limited effort — action {ids[0]} — and can "
                       f"be launched immediately with existing resources.")
            else:
                txt = (f"{_nb(len(qw), en=True).capitalize()} actions combine high impact with limited "
                       f"effort — actions {_join_nums(ids, 'and')} — and can be launched immediately "
                       f"with existing resources.")
        else:
            txt = "No immediate quick win stands out: sequencing should follow the 12-month roadmap."
        if strat:
            if len(strat) == 1:
                txt += (" The structural project in the top-right quadrant deserves a dedicated budget "
                        "and owner, as it carries most of the score upside.")
            else:
                txt += (f" The {_nb(len(strat), en=True)} structural projects (top right) deserve a "
                        f"dedicated budget and owner, as they carry most of the score upside.")
        return txt
    if qw:
        ids = [i for i, _ in qw[:3]]
        if len(qw) == 1:
            txt = (f"Une action combine fort impact et effort limité — l'action {ids[0]} — et peut être "
                   f"lancée immédiatement à moyens constants.")
        else:
            txt = (f"{_nb(len(qw), fem=True).capitalize()} actions combinent fort impact et effort limité "
                   f"— les actions {_join_nums(ids, 'et')} — et peuvent être lancées immédiatement à "
                   f"moyens constants.")
    else:
        txt = "Aucun quick win immédiat ne se détache : le séquencement suit la feuille de route 12 mois."
    if strat:
        if len(strat) == 1:
            txt += (" Le chantier structurant du quadrant haut-droit justifie un budget et un responsable "
                    "dédiés : il porte l'essentiel du potentiel de progression du score.")
        else:
            txt += (f" Les {_nb(len(strat))} chantiers structurants (quadrant haut-droit) justifient un "
                    f"budget et un responsable dédiés : ils portent l'essentiel du potentiel de "
                    f"progression du score.")
    return txt


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
    """Sous-titre-conclusion par pilier, ancré sur une donnée concrète. FR/EN."""
    en = getattr(request, "language", "fr") == "en"
    env, soc, gov = request.environmental, request.social, request.governance
    pil = [("env", scores.environmental_score), ("social", scores.social_score),
           ("gov", scores.governance_score)]
    best = max(pil, key=lambda x: x[1])[0]
    worst = min(pil, key=lambda x: x[1])[0]
    same = len({p[1] for p in pil}) == 1

    def num(v):  # entier sans décimale
        return f"{v:.0f}"

    def env_hook(sc):
        r = env.renewable_energy_percent
        w = env.waste_recycled_percent
        full = env.scope1_emissions is not None and env.scope2_emissions is not None and env.scope3_emissions is not None
        if r is not None and r >= 50:
            return (f"Renewable energy ({num(r)}%) drives environmental performance" if en
                    else f"L'énergie renouvelable ({num(r)} %) tire la performance environnementale")
        if full:
            return ("A full carbon footprint underpins the climate trajectory" if en
                    else "Un bilan carbone complet, socle de la trajectoire climat")
        if w is not None and w >= 60:
            return (f"Circular economy ({num(w)}% waste recycled) anchors the pillar" if en
                    else f"L'économie circulaire ({num(w)} % de déchets recyclés) porte le pilier")
        if env.scope3_emissions is None:
            return ("Measuring Scope 3 is the environmental priority" if en
                    else "Mesurer le Scope 3, priorité du pilier environnemental")
        if r is not None and r < 40:
            return (f"Energy mix ({num(r)}% renewable) is the lever to activate" if en
                    else f"Le mix énergétique ({num(r)} % renouvelable), levier à activer")
        return None

    def soc_hook(sc):
        g = soc.female_employees_percent
        tr = soc.training_hours_per_employee
        af = soc.accident_frequency_rate
        if g is not None and g >= 45:
            return (f"Near gender parity ({num(g)}% women) anchors the social pillar" if en
                    else f"Une quasi-parité femmes-hommes ({num(g)} %) ancre le pilier social")
        if tr is not None and tr >= 25:
            return (f"Training effort ({num(tr)}h/employee) sets the social pillar apart" if en
                    else f"L'effort de formation ({num(tr)} h/salarié) distingue le social")
        if af is not None and af > 5:
            return (f"Workplace safety (rate {af:.1f}) is the priority to address" if en
                    else f"La sécurité au travail (TF {af:.1f}), priorité à traiter")
        if g is not None and g < 40:
            return (f"Gender balance ({num(g)}% women) is the lever to activate" if en
                    else f"La parité femmes-hommes ({num(g)} %), levier à activer")
        return None

    def gov_hook(sc):
        bi = gov.independent_board_percent
        if gov.esg_audit_conducted and gov.sustainability_committee:
            return ("ESG audit and sustainability committee structure governance" if en
                    else "Audit ESG et comité de durabilité structurent la gouvernance")
        if bi is not None and bi >= 50:
            return (f"An independent board ({num(bi)}%) strengthens governance" if en
                    else f"Un conseil indépendant ({num(bi)} %) renforce la gouvernance")
        if not gov.esg_audit_conducted:
            return ("Independent ESG assurance is the governance priority" if en
                    else "L'assurance ESG indépendante, priorité de la gouvernance")
        if not gov.sustainability_committee:
            return ("A board-level sustainability committee is the missing link" if en
                    else "Un comité de durabilité au conseil, le maillon manquant")
        return None

    hooks = {"env": env_hook, "social": soc_hook, "gov": gov_hook}

    def phrase(key, sc):
        h = hooks[key](sc)
        if h:
            return h
        # Repli générique (rang + niveau) si aucune donnée saillante
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


def hero_stat(request: ESGRequest, scores: ESGScores) -> dict:
    """Chiffre-choc unique (ancrage visuel / focal point). FR/EN.
    Retourne {value, unit, label, statement}."""
    en = getattr(request, "language", "fr") == "en"
    env, tx = request.environmental, request.taxonomy
    from esg_advanced import sector_benchmark
    bm = sector_benchmark(request, scores)
    gd = bm["deltas"]["global"]

    # 1) Scope 3 dominant dans l'empreinte carbone
    scopes = [env.scope1_emissions, env.scope2_emissions, env.scope3_emissions]
    if all(v is not None for v in scopes) and sum(scopes) > 0 and env.scope3_emissions >= 0.5 * sum(scopes):
        share = env.scope3_emissions / sum(scopes) * 100
        return {"value": f"{share:.0f}", "unit": "%",
                "label": "des émissions relèvent du Scope 3" if not en else "of emissions come from Scope 3",
                "statement": ("La chaîne de valeur, principal terrain d'action climat." if not en
                              else "The value chain is the main climate battleground.")}

    # 2) Avance sectorielle nette
    if gd >= 4:
        return {"value": f"+{gd:.0f}", "unit": "pts",
                "label": "au-dessus de la moyenne de votre secteur" if not en else "above your sector average",
                "statement": ("Un positionnement ESG différenciant, à valoriser commercialement." if not en
                              else "A differentiating ESG position — worth leveraging commercially.")}

    # 3) Alignement Taxonomie fort
    tax_vals = [v for v in ((tx.turnover_aligned_percent, tx.capex_aligned_percent, tx.opex_aligned_percent)
                            if tx else ()) if v is not None]
    if tax_vals and max(tax_vals) >= 30:
        return {"value": f"{max(tax_vals):.0f}", "unit": "%",
                "label": "d'activités alignées à la Taxonomie UE" if not en else "of activities EU Taxonomy-aligned",
                "statement": ("Une éligibilité concrète aux financements verts." if not en
                              else "Concrete eligibility for green financing.")}

    # 4) Repli : mix renouvelable
    if env.renewable_energy_percent is not None:
        r = env.renewable_energy_percent
        return {"value": f"{r:.0f}", "unit": "%",
                "label": "d'énergie renouvelable dans le mix" if not en else "renewable energy in the mix",
                "statement": ("Un levier direct sur les coûts et l'empreinte carbone." if not en
                              else "A direct lever on costs and carbon footprint.")}

    # 5) Repli ultime : score global
    return {"value": f"{scores.total_esg_score:.0f}", "unit": "/100",
            "label": "score ESG global" if not en else "overall ESG score",
            "statement": ("Une base mesurée pour piloter la trajectoire durable." if not en
                          else "A measured baseline to steer the sustainability trajectory.")}


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


# ══════════════════════════════════════════════════════════════════════════
# FEUILLE DE ROUTE 12 MOIS (plan de marche actionnable)
# ══════════════════════════════════════════════════════════════════════════

_ROADMAP_PHASE = {
    "audit": (0, True), "committee": (0, True), "parity": (1, True),
    "scope3": (1, False), "frameworks": (1, False),
    "training": (2, False), "renewable": (2, False), "recycling": (2, False),
}


def roadmap_12m(request: ESGRequest, scores: ESGScores) -> list:
    """3 phases sur 12 mois, chaque action avec pilier + flag quick win."""
    en = getattr(request, "language", "fr") == "en"
    phase_labels = (["0-3 months", "3-6 months", "6-12 months"] if en
                    else ["0-3 mois", "3-6 mois", "6-12 mois"])
    phase_sub = (["Quick wins & foundations", "Structuring", "Deployment"] if en
                 else ["Quick wins & fondations", "Structuration", "Deploiement"])
    phases = [{"label": phase_labels[i], "sub": phase_sub[i], "actions": []} for i in range(3)]
    for rec in enriched_recommendations(request, scores):
        p, qw = _ROADMAP_PHASE.get(rec["key"], (2, False))
        phases[p]["actions"].append({"title": rec["title"], "pillar": rec["pillar"], "quick_win": qw})
    return phases


# ══════════════════════════════════════════════════════════════════════════
# RISQUES & OPPORTUNITÉS MAJEURS (dérivés du profil, pas génériques)
# ══════════════════════════════════════════════════════════════════════════

def risks_opportunities(request: ESGRequest, scores: ESGScores) -> dict:
    """Risques et opportunités ESG spécifiques à l'entreprise (FR/EN)."""
    en = getattr(request, "language", "fr") == "en"
    env, soc, gov = request.environmental, request.social, request.governance
    tx = request.taxonomy
    rev = request.company.revenue_eur
    from esg_advanced import sector_benchmark
    bm = sector_benchmark(request, scores)

    def T(fr, tag_fr, en_, tag_en, imp=None, lik=None):
        """imp/lik : 'H' (élevé/probable) ou 'M' (modéré/possible) → priorité P1-P3."""
        item = {"text": en_ if en else fr, "tag": tag_en if en else tag_fr}
        if imp is not None:
            item["impact"] = ("High" if en else "Élevé") if imp == "H" else ("Moderate" if en else "Modéré")
            item["likelihood"] = ("Likely" if en else "Probable") if lik == "H" else ("Possible" if en else "Possible")
            item["priority"] = "P1" if (imp == "H" and lik == "H") else ("P2" if "H" in (imp, lik) else "P3")
        return item

    risks = []
    if env.scope3_emissions is None:
        risks.append(T("Scope 3 non mesuré : non-conformité CSRD/ESRS E1 à venir", "Réglementaire",
                       "Scope 3 not measured: upcoming CSRD/ESRS E1 non-compliance", "Regulatory", "H", "H"))
    if not gov.esg_audit_conducted:
        risks.append(T("Reporting non audité : crédibilité limitée auprès des investisseurs", "Fiabilité",
                       "Unaudited reporting: limited credibility with investors", "Assurance", "H", "H"))
    ci = (env.co2_emissions_tonnes / rev * 1e6) if (env.co2_emissions_tonnes and rev) else None
    if ci is not None and ci > 100:
        risks.append(T("Intensité carbone élevée : marge exposée à la tarification du carbone", "Transition",
                       "High carbon intensity: margin exposed to carbon pricing", "Transition", "H", "M"))
    elif env.renewable_energy_percent is not None and env.renewable_energy_percent < 50:
        risks.append(T("Dépendance énergie fossile : exposition à la hausse des prix", "Transition",
                       "Fossil-energy dependence: exposure to rising prices", "Transition", "M", "H"))
    if soc.female_employees_percent is not None and soc.female_employees_percent < 40:
        risks.append(T("Parité sous la cible : risque réglementaire et d'attractivité", "Réglementaire",
                       "Gender balance below target: regulatory & attractiveness risk", "Regulatory", "M", "H"))
    if gov.data_breaches is not None and gov.data_breaches > 0:
        risks.append(T("Incident cyber déclaré : risque réputationnel et RGPD", "Réputation",
                       "Reported cyber incident: reputational & GDPR risk", "Reputation", "H", "M"))
    if soc.accident_frequency_rate is not None and soc.accident_frequency_rate > 5:
        risks.append(T("Sinistralité au-dessus des standards : risque humain et social", "Opérationnel",
                       "Accident rate above standards: human & social risk", "Operational", "H", "H"))
    if gov.ethics_violations is not None and gov.ethics_violations > 0:
        risks.append(T("Manquements éthiques enregistrés : risque juridique", "Éthique",
                       "Recorded ethics breaches: legal risk", "Ethics", "M", "M"))
    if len(risks) < 3:
        risks.append(T("Exigences CSRD croissantes : effort de reporting à anticiper", "Réglementaire",
                       "Rising CSRD requirements: reporting effort to anticipate", "Regulatory", "M", "H"))
    risks.sort(key=lambda r: r.get("priority", "P3"))

    opps = []
    if scores.governance_score >= 70 or (gov.esg_audit_conducted and gov.sustainability_committee):
        opps.append(T("Gouvernance solide : accès facilité aux financements ESG (green bonds, prêts indexés)", "Financement",
                      "Strong governance: easier access to ESG financing (green bonds, linked loans)", "Financing"))
    if tx and any(v is not None for v in (tx.turnover_aligned_percent, tx.capex_aligned_percent, tx.opex_aligned_percent)):
        opps.append(T("Activités alignées Taxonomie : éligibilité aux financements verts", "Financement",
                      "Taxonomy-aligned activities: eligible for green financing", "Financing"))
    if env.renewable_energy_percent is not None and env.renewable_energy_percent >= 40:
        opps.append(T("Mix renouvelable engagé : réduction des coûts énergétiques à terme", "Coûts",
                      "Renewable mix under way: lower energy costs over time", "Costs"))
    if soc.training_hours_per_employee and soc.training_hours_per_employee >= 20 or scores.social_score >= 65:
        opps.append(T("Politique sociale : marque employeur et rétention des talents renforcées", "Talents",
                      "Social policy: stronger employer brand and talent retention", "Talent"))
    if env.waste_recycled_percent is not None and env.waste_recycled_percent >= 60:
        opps.append(T("Économie circulaire : baisse des coûts matières et déchets", "Coûts",
                      "Circular economy: lower materials and waste costs", "Costs"))
    if bm["deltas"]["global"] >= 2:
        opps.append(T("Surperformance sectorielle : différenciation commerciale et appels d'offres", "Marché",
                      "Sector outperformance: commercial differentiation and tenders", "Market"))
    if env.scope1_emissions is not None and env.scope2_emissions is not None and env.scope3_emissions is not None:
        opps.append(T("Bilan carbone complet : avance sur la conformité CSRD", "Conformité",
                      "Full carbon footprint: ahead on CSRD compliance", "Compliance"))
    if len(opps) < 3:
        opps.append(T("Structuration ESG précoce : anticipation des exigences réglementaires", "Marché",
                      "Early ESG structuring: anticipating regulatory requirements", "Market"))

    return {"risks": risks[:4], "opportunities": opps[:4]}


def compliance_assessment(request: ESGRequest, scores: ESGScores) -> list:
    """Analyse des écarts vs exigences CSRD/réglementaires (données déclarées).
    Chaque ligne : {req, ref, status: 'ok'|'partial'|'no'|'na', note}. FR/EN."""
    en = getattr(request, "language", "fr") == "en"
    env, soc, gov = request.environmental, request.social, request.governance
    tx = request.taxonomy
    rows = []

    def R(req_fr, req_en, ref, status, note_fr, note_en):
        rows.append({"req": req_en if en else req_fr, "ref": ref, "status": status,
                     "note": note_en if en else note_fr})

    # Bilan GES Scopes 1 & 2
    s12 = env.scope1_emissions is not None and env.scope2_emissions is not None
    R("Bilan GES Scopes 1 & 2", "GHG inventory Scopes 1 & 2", "ESRS E1-6",
      "ok" if s12 else ("partial" if env.co2_emissions_tonnes else "no"),
      "Émissions mesurées et publiées" if s12 else
      ("Total publié, décomposition par scope à établir" if env.co2_emissions_tonnes else "Bilan GES à réaliser"),
      "Emissions measured and disclosed" if s12 else
      ("Total disclosed, scope breakdown to be established" if env.co2_emissions_tonnes else "GHG inventory to be produced"))

    # Scope 3
    R("Émissions de la chaîne de valeur (Scope 3)", "Value-chain emissions (Scope 3)", "ESRS E1-6",
      "ok" if env.scope3_emissions is not None else "no",
      "Scope 3 mesuré et publié" if env.scope3_emissions is not None else "Scope 3 non mesuré — priorité CSRD",
      "Scope 3 measured and disclosed" if env.scope3_emissions is not None else "Scope 3 not measured — CSRD priority")

    # Vérification tierce
    R("Vérification du reporting par un tiers", "Third-party assurance of reporting", "CSRD (assurance limitée)",
      "ok" if gov.esg_audit_conducted else "no",
      "Audit ESG indépendant réalisé" if gov.esg_audit_conducted else "Aucune assurance externe à date",
      "Independent ESG audit performed" if gov.esg_audit_conducted else "No external assurance to date")

    # Gouvernance durabilité
    R("Supervision de la durabilité par la gouvernance", "Sustainability oversight by governance", "ESRS 2 GOV-1",
      "ok" if gov.sustainability_committee else "no",
      "Comité de durabilité en place" if gov.sustainability_committee else "Pas de comité dédié",
      "Sustainability committee in place" if gov.sustainability_committee else "No dedicated committee")

    # Parité effectifs
    g = soc.female_employees_percent
    R("Mixité des effectifs (cible 40 %)", "Workforce gender balance (40% target)", "Index égalité / ESRS S1-9",
      "na" if g is None else ("ok" if g >= 40 else ("partial" if g >= 35 else "no")),
      "Donnée non renseignée" if g is None else f"{g:.0f} % de femmes",
      "Not reported" if g is None else f"{g:.0f}% women")

    # Indépendance du conseil
    bi = gov.independent_board_percent
    R("Indépendance du conseil (seuil 50 %)", "Board independence (50% threshold)", "AFEP-MEDEF",
      "na" if bi is None else ("ok" if bi >= 50 else ("partial" if bi >= 33 else "no")),
      "Donnée non renseignée" if bi is None else f"{bi:.0f} % d'administrateurs indépendants",
      "Not reported" if bi is None else f"{bi:.0f}% independent directors")

    # Taxonomie UE
    has_tx = tx and any(v is not None for v in
                        (tx.turnover_aligned_percent, tx.capex_aligned_percent, tx.opex_aligned_percent))
    R("Publication des indicateurs Taxonomie UE", "EU Taxonomy KPI disclosure", "Règlement (UE) 2020/852",
      "ok" if has_tx else "no",
      "Parts alignées publiées (CA/CapEx/OpEx)" if has_tx else "Éligibilité et alignement à évaluer",
      "Aligned shares disclosed (turnover/CapEx/OpEx)" if has_tx else "Eligibility and alignment to be assessed")

    # Trajectoire climat
    R("Objectifs climatiques chiffrés", "Quantified climate targets", "ESRS E1-4",
      "ok" if env.co2_emissions_tonnes else "partial",
      "Trajectoire -42 % à 2030 définie (réf. SBTi)" if env.co2_emissions_tonnes
      else "Trajectoire à définir une fois le bilan GES établi",
      "-42% by 2030 pathway defined (SBTi ref.)" if env.co2_emissions_tonnes
      else "Pathway to be set once the GHG inventory is established")

    return rows


# Responsable (fonction) et objectif chiffré par recommandation — plan d'action
_REC_OWNERS = {
    "renewable": ("Direction des opérations", "Operations"),
    "scope3": ("Direction RSE / Finance", "CSR / Finance"),
    "parity": ("Direction des ressources humaines", "Human Resources"),
    "training": ("Direction des ressources humaines", "Human Resources"),
    "audit": ("Direction générale", "Executive Management"),
    "committee": ("Conseil d'administration", "Board of Directors"),
    "recycling": ("Direction des opérations", "Operations"),
    "frameworks": ("Direction RSE", "CSR"),
}

_REC_OBJECTIVES = {
    "renewable": ("50 % d'énergie renouvelable dans le mix", "50% renewable energy in the mix"),
    "scope3": ("Scope 3 mesuré et publié au prochain exercice", "Scope 3 measured and disclosed next year"),
    "parity": ("40 % de femmes dans les effectifs", "40% women in the workforce"),
    "training": ("20 h de formation par salarié et par an", "20 training hours per employee per year"),
    "audit": ("Assurance limitée obtenue sur le reporting", "Limited assurance obtained on reporting"),
    "committee": ("Comité opérationnel dès le prochain trimestre", "Committee operational next quarter"),
    "recycling": ("60 % de déchets recyclés", "60% of waste recycled"),
    "frameworks": ("Alignement ODD / TCFD documenté", "SDG / TCFD alignment documented"),
}
