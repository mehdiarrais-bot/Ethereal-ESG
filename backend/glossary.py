"""
Glossaire des termes du reporting extra-financier (FR / EN).

Rendu en annexe des livrables : un dirigeant ou un administrateur non
spécialiste doit pouvoir lire le rapport sans dictionnaire. Les entrées
sont filtrées selon ce que le rapport contient réellement — inutile de
définir la Taxonomie si l'entreprise ne publie aucun indicateur aligné.
"""

# (clé, terme FR, définition FR, terme EN, définition EN)
_TERMS = [
    ("csrd", "CSRD",
     "Directive européenne sur la publication d'informations en matière de durabilité. "
     "Impose un reporting extra-financier normalisé et vérifié aux entreprises entrant "
     "dans son périmètre.",
     "CSRD",
     "EU Corporate Sustainability Reporting Directive. Requires standardised, assured "
     "sustainability reporting from companies within its scope."),

    ("esrs", "ESRS",
     "Normes techniques d'application de la CSRD. Elles précisent, thème par thème "
     "(climat, effectifs, conduite des affaires), les informations à publier.",
     "ESRS",
     "The technical standards implementing the CSRD, specifying topic by topic "
     "(climate, workforce, business conduct) what must be disclosed."),

    ("vsme", "VSME",
     "Norme volontaire de l'EFRAG destinée aux PME hors périmètre CSRD. Allégée, elle "
     "sert notamment à répondre aux demandes des donneurs d'ordre et des banques.",
     "VSME",
     "EFRAG's voluntary standard for SMEs outside the CSRD scope. A lighter framework, "
     "mainly used to answer requests from clients and banks."),

    ("materiality", "Double matérialité",
     "Principe d'analyse retenant un enjeu s'il est significatif dans au moins un des "
     "deux sens : l'impact de l'entreprise sur son environnement, ou l'effet financier "
     "de cet enjeu sur l'entreprise.",
     "Double materiality",
     "Principle whereby a topic is material if significant in either direction: the "
     "company's impact on society and the environment, or the financial effect of that "
     "topic on the company."),

    ("scopes", "Scopes 1, 2 et 3",
     "Découpage des émissions de gaz à effet de serre : émissions directes (1), "
     "émissions liées à l'énergie achetée (2), et toutes les autres émissions de la "
     "chaîne de valeur, amont et aval (3).",
     "Scopes 1, 2 and 3",
     "Greenhouse-gas emissions split into direct emissions (1), emissions from purchased "
     "energy (2), and all other value-chain emissions, upstream and downstream (3)."),

    ("ghg", "GHG Protocol",
     "Référentiel international de comptabilisation des émissions de gaz à effet de "
     "serre, sur lequel repose le découpage en scopes.",
     "GHG Protocol",
     "The international greenhouse-gas accounting standard on which the scope breakdown "
     "is based."),

    ("intensity", "Intensité carbone",
     "Émissions rapportées à l'activité, ici en tonnes de CO₂ équivalent par million "
     "d'euros de chiffre d'affaires. Permet de comparer des entreprises de tailles "
     "différentes.",
     "Carbon intensity",
     "Emissions relative to activity — here tonnes of CO₂ equivalent per million euros of "
     "revenue — allowing comparison between companies of different sizes."),

    ("taxonomy", "Taxonomie européenne",
     "Classification des activités économiques durables. Une activité est « alignée » si "
     "elle contribue à un objectif environnemental sans nuire aux autres et respecte des "
     "garanties sociales minimales.",
     "EU Taxonomy",
     "Classification of environmentally sustainable economic activities. An activity is "
     "'aligned' if it contributes to an environmental objective without harming the "
     "others and meets minimum social safeguards."),

    ("dnsh", "DNSH",
     "« Do No Significant Harm ». Condition de la Taxonomie : contribuer à un objectif "
     "environnemental sans causer de préjudice important aux autres.",
     "DNSH",
     "'Do No Significant Harm' — the Taxonomy condition of contributing to one "
     "environmental objective without significantly harming the others."),

    ("tcfd", "TCFD",
     "Cadre de publication des risques financiers liés au climat, structuré autour de la "
     "gouvernance, de la stratégie, de la gestion des risques et des indicateurs.",
     "TCFD",
     "Framework for disclosing climate-related financial risks, structured around "
     "governance, strategy, risk management and metrics."),

    ("assurance", "Assurance limitée",
     "Niveau de vérification par un tiers indépendant requis par la CSRD : le vérificateur "
     "conclut qu'il n'a pas relevé d'anomalie significative, sans l'audit approfondi que "
     "suppose une assurance raisonnable.",
     "Limited assurance",
     "The level of independent third-party verification required by the CSRD: the verifier "
     "concludes that nothing material came to their attention, without the deeper testing "
     "of reasonable assurance."),

    ("gri", "GRI",
     "Global Reporting Initiative : référentiel international de reporting de durabilité, "
     "largement utilisé et compatible avec les ESRS.",
     "GRI",
     "Global Reporting Initiative — a widely used international sustainability reporting "
     "framework, interoperable with the ESRS."),
]


def glossary_entries(request, scores=None) -> list:
    """Entrées du glossaire pertinentes pour ce rapport précis.

    Retourne [{term, definition}] dans l'ordre de lecture. Les termes qui ne
    correspondent à rien dans le rapport sont écartés : le glossaire reste
    court, donc lu.
    """
    en = getattr(request, "language", "fr") == "en"
    vsme = getattr(request, "reporting_framework", "csrd") == "vsme"
    env = request.environmental
    tx = request.taxonomy

    has_scopes = any(v is not None for v in
                     (env.scope1_emissions, env.scope2_emissions, env.scope3_emissions))
    has_intensity = bool(env.co2_emissions_tonnes and request.company.revenue_eur)
    has_taxonomy = bool(tx and any(v is not None for v in (
        tx.turnover_aligned_percent, tx.capex_aligned_percent, tx.opex_aligned_percent)))
    has_carbon = env.co2_emissions_tonnes is not None

    skip = set()
    if not has_scopes:
        skip.add("scopes")
        skip.add("ghg")
    if not has_intensity:
        skip.add("intensity")
    if not has_taxonomy:
        skip |= {"taxonomy", "dnsh"}
    # Le référentiel non retenu n'a pas à être défini
    skip.add("vsme" if not vsme else "csrd")

    out = []
    for key, term_fr, def_fr, term_en, def_en in _TERMS:
        if key in skip:
            continue
        out.append({"term": term_en if en else term_fr,
                    "definition": def_en if en else def_fr})
    return out
