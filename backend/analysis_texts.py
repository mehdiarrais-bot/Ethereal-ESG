"""Phrases de l'analyse approfondie des piliers (analysis.py), FR et EN.

Deux familles de textes :
  - SECTOR : le contexte propre à une famille de secteurs (d'où viennent les
    émissions, quels déchets, quels risques d'accident…). C'est ce qui fait
    qu'un transporteur et une société de conseil ne lisent pas le même
    rapport, à données comparables.
  - A : les raisonnements (constat, cause, conséquence, levier), choisis
    par analysis.py selon les tranches de la grille (bands.py) et les
    croisements entre indicateurs.

Règles de rédaction (CLAUDE.md) : aucune donnée inventée — les chiffres
cités sont ceux du dossier ou des ratios calculés à partir d'eux ; aucune
affirmation réglementaire (les rappels de droit vérifiés vivent dans
content_generator) ; les liens de cause à effet sont formulés comme des
mécanismes connus ou des hypothèses à vérifier, jamais comme des constats
que le dossier ne permet pas d'établir.
"""

# ── Contexte sectoriel ────────────────────────────────────────────────────
# Familles : voir analysis.family(). « general » sert de repli.
SECTOR = {
    "industrie": {
        "fr": {
            "label": "un industriel",
            "s1": "fours, chaudières, procédés thermiques et engins de manutention brûlent des "
                  "combustibles sur les sites",
            "s2": "l'électricité alimente les lignes de production, l'air comprimé, le froid et "
                  "l'éclairage des ateliers",
            "s3": "matières premières et composants achetés, transport amont et aval, et parfois "
                  "usage et fin de vie des produits vendus",
            "s3_missing": "Pour un industriel, les achats de matières et de composants pèsent souvent "
                          "plus lourd que les sites eux-mêmes : l'ordre des priorités pourrait s'en "
                          "trouver modifié.",
            "lever_s1": "Les leviers classiques sont la récupération de chaleur fatale, "
                        "l'électrification des procédés à basse et moyenne température et le réglage "
                        "fin des combustions ; ils se planifient au rythme des arrêts techniques et du "
                        "renouvellement des équipements.",
            "energy": "Dans l'industrie, les gisements d'efficacité se cachent souvent dans les "
                      "utilités — air comprimé, froid, vapeur — et dans les moteurs, où la variation "
                      "de vitesse et la chasse aux fuites produisent des gains rapides.",
            "waste": "les chutes de production, les emballages des matières premières, les déchets "
                     "dangereux (huiles, solvants) et les rebuts de qualité",
            "water": "le refroidissement, le lavage des pièces et certains procédés",
            "bio": "la gestion écologique des terrains des sites, la maîtrise des rejets et "
                   "l'attention portée aux milieux sensibles voisins",
            "safety": "la manutention, les machines, les chutes et les interventions de maintenance "
                      "concentrent traditionnellement l'essentiel des risques",
            "talent": "les métiers techniques de la production et de la maintenance sont en tension, "
                      "et la transmission des savoir-faire entre générations devient un sujet",
            "mix": "L'industrie reste un secteur historiquement très masculin, en particulier dans "
                   "les métiers de la production et de la maintenance. Le déséquilibre relève en "
                   "partie des filières de formation, mais il réduit d'autant le vivier accessible "
                   "pour des postes souvent difficiles à pourvoir.",
        },
        "en": {
            "label": "a manufacturer",
            "s1": "furnaces, boilers, thermal processes and handling equipment burn fuel on site",
            "s2": "electricity powers production lines, compressed air, refrigeration and workshop "
                  "lighting",
            "s3": "purchased raw materials and components, upstream and downstream transport, and "
                  "sometimes the use and end of life of the products sold",
            "s3_missing": "For a manufacturer, purchased materials and components often weigh more "
                          "than the sites themselves: the order of priorities could change.",
            "lever_s1": "The classic levers are waste-heat recovery, electrification of low- and "
                        "medium-temperature processes and fine-tuning of combustion; they are "
                        "planned around maintenance shutdowns and equipment renewal cycles.",
            "energy": "In manufacturing, efficiency gains often hide in the utilities — compressed "
                      "air, refrigeration, steam — and in motors, where variable-speed drives and "
                      "leak hunting deliver quick wins.",
            "waste": "production offcuts, raw-material packaging, hazardous waste (oils, solvents) "
                     "and quality rejects",
            "water": "cooling, parts washing and some processes",
            "bio": "ecological management of site land, control of discharges and attention to "
                   "nearby sensitive habitats",
            "safety": "handling, machinery, falls and maintenance work traditionally account for "
                      "most of the risk",
            "talent": "technical production and maintenance jobs are hard to fill, and passing "
                      "know-how from one generation to the next is becoming an issue",
            "mix": "Manufacturing remains a historically male-dominated sector, especially in "
                   "production and maintenance roles. The imbalance partly reflects training "
                   "pipelines, but it shrinks the candidate pool for positions that are often hard "
                   "to fill.",
        },
    },
    "transport": {
        "fr": {
            "label": "un transporteur",
            "s1": "le gazole des poids lourds et des utilitaires, auquel s'ajoutent les engins de "
                  "manutention et le chauffage des entrepôts",
            "s2": "l'électricité alimente les entrepôts, leur éclairage, les chambres froides et, le "
                  "cas échéant, la recharge des véhicules électriques",
            "s3": "la sous-traitance de transport, la fabrication des véhicules et la production "
                  "amont des carburants",
            "s3_missing": "Pour un transporteur, le Scope 3 recouvre notamment les trajets confiés à "
                          "des sous-traitants, la fabrication des véhicules et la production amont "
                          "des carburants : selon la part d'affrètement, il peut modifier sensiblement "
                          "la hiérarchie des postes.",
            "lever_s1": "Les leviers se situent à trois niveaux : l'exploitation (taux de remplissage, "
                        "optimisation des tournées, réduction des kilomètres à vide), la conduite "
                        "(formation à l'éco-conduite, suivi des consommations par conducteur) et la "
                        "flotte (motorisations alternatives, à arbitrer selon les usages et la "
                        "disponibilité des infrastructures d'avitaillement).",
            "energy": "Dans le transport, l'énergie est d'abord du carburant : la consommation aux "
                      "cent kilomètres et par tonne transportée est l'indicateur le plus parlant "
                      "pour les équipes d'exploitation.",
            "waste": "les films et emballages, les palettes, les pneumatiques, les huiles et les "
                     "pièces d'entretien de la flotte",
            "water": "le lavage des véhicules et les usages sanitaires des sites",
            "bio": "la gestion des emprises logistiques, souvent vastes et imperméabilisées, et "
                   "des abords des plateformes",
            "safety": "les risques routiers, la manutention, les chutes lors du chargement et la "
                      "circulation des engins sur les quais sont les causes d'accident les plus "
                      "fréquentes",
            "talent": "les métiers de la conduite et de l'entrepôt connaissent des tensions de "
                      "recrutement récurrentes",
            "mix": "Le transport et la logistique restent des métiers historiquement très masculins, "
                   "à la conduite comme en entrepôt. Le déséquilibre relève en partie du secteur, "
                   "mais il ferme une partie du vivier de recrutement dans des métiers déjà en "
                   "tension.",
        },
        "en": {
            "label": "a transport and logistics company",
            "s1": "diesel for trucks and vans, plus handling equipment and warehouse heating",
            "s2": "electricity powers warehouses, their lighting, cold rooms and, where relevant, "
                  "electric vehicle charging",
            "s3": "subcontracted transport, vehicle manufacturing and upstream fuel production",
            "s3_missing": "For a transport company, Scope 3 notably covers journeys subcontracted "
                          "to carriers, vehicle manufacturing and upstream fuel production: "
                          "depending on the share of chartering, it could significantly change "
                          "the ranking of emission sources.",
            "lever_s1": "The levers sit at three levels: operations (load factor, route "
                        "optimisation, fewer empty kilometres), driving (eco-driving training, "
                        "fuel monitoring per driver) and the fleet (alternative powertrains, to be "
                        "weighed against usage patterns and the availability of refuelling "
                        "infrastructure).",
            "energy": "In transport, energy primarily means fuel: consumption per hundred kilometres "
                      "and per tonne carried is the most meaningful indicator for operations teams.",
            "waste": "films and packaging, pallets, tyres, oils and fleet maintenance parts",
            "water": "vehicle washing and sanitary use on site",
            "bio": "the management of logistics land, often large and sealed, and of the "
                   "surroundings of the platforms",
            "safety": "road risks, handling, falls during loading and vehicle traffic on the docks "
                      "are the most frequent causes of accidents",
            "talent": "driving and warehouse jobs face recurring recruitment shortages",
            "mix": "Transport and logistics remain historically male-dominated trades, both at "
                   "the wheel and in the warehouse. The imbalance is partly structural, but it "
                   "closes off part of the candidate pool for jobs that are already hard to fill.",
        },
    },
    "construction": {
        "fr": {
            "label": "une entreprise du bâtiment et des travaux publics",
            "s1": "le carburant des engins de chantier et des véhicules, ainsi que le chauffage des "
                  "bases vie et des dépôts",
            "s2": "l'électricité des dépôts, des ateliers et des installations de chantier "
                  "raccordées au réseau",
            "s3": "les matériaux achetés — ciment, acier, enrobés —, leur transport et l'usage des "
                  "ouvrages livrés",
            "s3_missing": "Dans la construction, les matériaux achetés — béton, acier, enrobés — "
                          "représentent souvent la plus grande part de l'empreinte : leur absence du "
                          "bilan en change la lecture.",
            "lever_s1": "Les leviers portent sur le parc d'engins (entretien, renouvellement, "
                        "motorisations moins émettrices), la logistique des chantiers et le "
                        "raccordement anticipé au réseau électrique pour se passer des groupes "
                        "électrogènes.",
            "energy": "Sur les chantiers, la consommation dépend largement de l'organisation : "
                      "raccordement électrique anticipé, arrêt des moteurs au ralenti, mutualisation "
                      "des engins entre chantiers.",
            "waste": "les déblais, les gravats inertes, les emballages et les chutes de matériaux",
            "water": "la fabrication des bétons, le nettoyage des engins et l'arrosage "
                     "anti-poussière",
            "bio": "la préparation des chantiers — inventaires écologiques, calendrier des travaux, "
                   "remise en état des emprises",
            "safety": "les chutes de hauteur, les engins et la manutention de charges lourdes sont "
                      "les principales sources de risque sur les chantiers",
            "talent": "les métiers qualifiés du chantier sont difficiles à recruter, et l'intérim "
                      "y tient souvent une place importante",
            "mix": "Le BTP reste un secteur historiquement très masculin, surtout sur les chantiers. "
                   "Le déséquilibre relève en grande partie du vivier, mais il limite l'accès à des "
                   "candidats dont le secteur a besoin.",
        },
        "en": {
            "label": "a construction company",
            "s1": "fuel for site machinery and vehicles, plus heating of site facilities and depots",
            "s2": "electricity for depots, workshops and grid-connected site installations",
            "s3": "purchased materials — cement, steel, asphalt —, their transport and the use of "
                  "the structures delivered",
            "s3_missing": "In construction, purchased materials — concrete, steel, asphalt — often "
                          "make up the largest share of the footprint: leaving them out changes "
                          "the picture.",
            "lever_s1": "The levers concern the machinery fleet (maintenance, renewal, lower-emission "
                        "engines), site logistics and early grid connection to avoid diesel "
                        "generators.",
            "energy": "On construction sites, consumption depends largely on organisation: early "
                      "grid connection, no idling engines, sharing machinery between sites.",
            "waste": "excavated earth, inert rubble, packaging and material offcuts",
            "water": "concrete production, machinery cleaning and dust suppression",
            "bio": "site preparation — ecological surveys, works scheduling, restoration of land",
            "safety": "falls from height, machinery and heavy lifting are the main sources of risk "
                      "on construction sites",
            "talent": "skilled site trades are hard to recruit for, and temporary work often plays "
                      "a large role",
            "mix": "Construction remains a historically male-dominated sector, especially on site. "
                   "The imbalance largely reflects the talent pool, but it limits access to "
                   "candidates the sector needs.",
        },
    },
    "agro": {
        "fr": {
            "label": "un acteur agroalimentaire",
            "s1": "la production de chaleur et de vapeur (cuisson, séchage, pasteurisation), les "
                  "fuites de fluides frigorigènes et la flotte de véhicules",
            "s2": "l'électricité alimente la production de froid, le conditionnement et les lignes "
                  "de transformation",
            "s3": "les matières premières agricoles, les emballages et la logistique",
            "s3_missing": "Dans l'agroalimentaire, les matières premières agricoles et les emballages "
                          "pèsent souvent plus lourd que les usines : sans Scope 3, une grande part de "
                          "l'empreinte reste probablement hors champ.",
            "lever_s1": "Les leviers portent sur la récupération de chaleur, la maîtrise des fuites de "
                        "fluides frigorigènes et la substitution progressive des combustibles "
                        "fossiles dans la production de chaleur.",
            "energy": "Le froid et la chaleur de procédé concentrent l'essentiel des consommations : "
                      "récupération de chaleur sur les groupes froid, isolation et régulation sont "
                      "souvent rentables à court terme.",
            "waste": "les coproduits et déchets organiques, les emballages et les invendus",
            "water": "le nettoyage des installations, les procédés de transformation et le "
                     "refroidissement",
            "bio": "les pratiques agricoles des fournisseurs de matières premières, principal point "
                   "de contact entre l'activité et la biodiversité",
            "safety": "la manutention, les gestes répétitifs, les sols glissants et le travail au "
                      "froid sont des sources de risque fréquentes",
            "talent": "les postes de production, souvent en horaires décalés, sont difficiles à "
                      "pourvoir durablement",
            "mix": None,
        },
        "en": {
            "label": "an agri-food company",
            "s1": "heat and steam production (cooking, drying, pasteurisation), refrigerant leaks "
                  "and the vehicle fleet",
            "s2": "electricity powers refrigeration, packaging and processing lines",
            "s3": "agricultural raw materials, packaging and logistics",
            "s3_missing": "In agri-food, agricultural raw materials and packaging often weigh more "
                          "than the plants: without Scope 3, a large part of the footprint is "
                          "probably out of view.",
            "lever_s1": "The levers concern heat recovery, control of refrigerant leaks and the "
                        "gradual replacement of fossil fuels in heat production.",
            "energy": "Refrigeration and process heat account for most of the consumption: heat "
                      "recovery on chillers, insulation and controls are often profitable in the "
                      "short term.",
            "waste": "by-products and organic waste, packaging and unsold goods",
            "water": "cleaning of installations, processing and cooling",
            "bio": "the farming practices of raw-material suppliers, the main point of contact "
                   "between the business and biodiversity",
            "safety": "handling, repetitive movements, slippery floors and work in cold "
                      "environments are frequent sources of risk",
            "talent": "production jobs, often on staggered hours, are hard to fill durably",
            "mix": None,
        },
    },
    "energie": {
        "fr": {
            "label": "un acteur de l'énergie",
            "s1": "la combustion sur les installations de production ou de transformation d'énergie "
                  "et les éventuelles émissions fugitives",
            "s2": "l'électricité consommée par les installations et les sites tertiaires",
            "s3": "l'amont des combustibles et l'usage de l'énergie vendue aux clients",
            "s3_missing": "Pour un acteur de l'énergie, l'usage de l'énergie vendue peut constituer "
                          "l'essentiel de l'empreinte : sans Scope 3, le bilan n'en donne qu'une "
                          "image très partielle.",
            "lever_s1": "Les leviers relèvent de la composition du parc de production, de la détection "
                        "et de la réduction des émissions fugitives, et du rendement des "
                        "installations.",
            "energy": "La performance énergétique des installations elles-mêmes (pertes, "
                      "autoconsommation) reste un gisement souvent sous-estimé face aux enjeux du "
                      "parc de production.",
            "waste": "les déchets d'exploitation et de maintenance, dont une partie est dangereuse",
            "water": "le refroidissement et les procédés",
            "bio": "l'implantation et l'exploitation des installations, en particulier en milieu "
                   "naturel",
            "safety": "les interventions sur des installations sous tension ou sous pression et les "
                      "travaux en hauteur sont les risques caractéristiques du secteur",
            "talent": "les compétences techniques de la transition énergétique sont très recherchées",
            "mix": "Les métiers techniques de l'énergie restent historiquement très masculins. Le "
                   "déséquilibre relève en partie des filières de formation, mais il réduit le "
                   "vivier au moment où les besoins de compétences augmentent.",
        },
        "en": {
            "label": "an energy company",
            "s1": "combustion in energy production or conversion facilities and any fugitive "
                  "emissions",
            "s2": "electricity consumed by the facilities and office sites",
            "s3": "upstream fuel production and the use of the energy sold to customers",
            "s3_missing": "For an energy company, the use of the energy sold can make up most of "
                          "the footprint: without Scope 3, the inventory gives only a very partial "
                          "picture.",
            "lever_s1": "The levers lie in the composition of the generation portfolio, the "
                        "detection and reduction of fugitive emissions, and plant efficiency.",
            "energy": "The energy performance of the facilities themselves (losses, own "
                      "consumption) is often underestimated next to portfolio issues.",
            "waste": "operating and maintenance waste, part of which is hazardous",
            "water": "cooling and processes",
            "bio": "the siting and operation of facilities, particularly in natural environments",
            "safety": "work on live or pressurised installations and work at height are the "
                      "sector's characteristic risks",
            "talent": "the technical skills of the energy transition are in high demand",
            "mix": "Technical energy jobs remain historically male-dominated. The imbalance partly "
                   "reflects training pipelines, but it narrows the talent pool just as skill "
                   "needs are rising.",
        },
    },
    "commerce": {
        "fr": {
            "label": "une entreprise de commerce et de distribution",
            "s1": "le chauffage des magasins et des entrepôts, les fuites de fluides frigorigènes "
                  "des équipements de froid et la flotte de livraison",
            "s2": "l'électricité alimente l'éclairage des surfaces de vente, le froid commercial et "
                  "la climatisation",
            "s3": "les produits achetés pour être revendus, leur transport et, pour certains, leur "
                  "usage par les clients",
            "s3_missing": "Pour un distributeur, les marchandises achetées pour être revendues "
                          "représentent souvent l'essentiel de l'empreinte : le bilan présenté n'en "
                          "couvre ici qu'une petite partie.",
            "lever_s1": "Les leviers portent sur la maîtrise des fuites et le passage à des fluides "
                        "frigorigènes à faible pouvoir de réchauffement, sur le chauffage des "
                        "surfaces et sur l'organisation des livraisons.",
            "energy": "Dans le commerce, l'éclairage, le froid alimentaire et la climatisation sont "
                      "les premiers postes : fermeture des meubles froids, pilotage horaire et "
                      "éclairage performant produisent des gains rapides et visibles des clients.",
            "waste": "les cartons et films d'emballage, les invendus et, le cas échéant, les déchets "
                     "alimentaires",
            "water": "les usages sanitaires et l'entretien des surfaces",
            "bio": "les critères d'achat des produits vendus et l'aménagement des parkings et des "
                   "abords des magasins",
            "safety": "la manutention, le port de charges, les chutes et les situations de tension "
                      "avec la clientèle sont les risques caractéristiques de l'activité",
            "talent": "le temps partiel, les horaires étendus et la saisonnalité rendent la "
                      "fidélisation difficile",
            "mix": None,
        },
        "en": {
            "label": "a retail and distribution company",
            "s1": "heating of stores and warehouses, refrigerant leaks from cooling equipment and "
                  "the delivery fleet",
            "s2": "electricity powers sales-floor lighting, commercial refrigeration and air "
                  "conditioning",
            "s3": "goods purchased for resale, their transport and, for some, their use by "
                  "customers",
            "s3_missing": "For a retailer, goods purchased for resale often make up most of the "
                          "footprint: the inventory presented covers only a small part of it.",
            "lever_s1": "The levers concern leak control and a switch to low-warming-potential "
                        "refrigerants, heating of sales areas and the organisation of deliveries.",
            "energy": "In retail, lighting, food refrigeration and air conditioning are the main "
                      "items: closing refrigerated cabinets, time-based controls and efficient "
                      "lighting deliver quick gains that customers can see.",
            "waste": "cardboard and packaging film, unsold goods and, where relevant, food waste",
            "water": "sanitary use and cleaning",
            "bio": "purchasing criteria for the products sold and the landscaping of car parks and "
                   "store surroundings",
            "safety": "handling, carrying loads, falls and tense situations with customers are the "
                      "characteristic risks of the business",
            "talent": "part-time work, long opening hours and seasonality make retention difficult",
            "mix": None,
        },
    },
    "services": {
        "fr": {
            "label": "une société de services",
            "s1": "le chauffage des bureaux au gaz ou au fioul et, le cas échéant, les véhicules de "
                  "fonction ou de service",
            "s2": "l'électricité des bureaux — éclairage, climatisation, informatique — et, le cas "
                  "échéant, le chauffage urbain",
            "s3": "les déplacements professionnels, les trajets domicile-travail, les achats de "
                  "prestations et de matériel informatique",
            "s3_missing": "Pour une société de services, les déplacements, les trajets "
                          "domicile-travail et les achats constituent souvent l'essentiel de "
                          "l'empreinte : le bilan présenté n'en montre qu'une faible part.",
            "lever_s1": "Les leviers portent sur le mode de chauffage des locaux et sur la politique "
                        "de véhicules, deux décisions qui relèvent autant de la gestion immobilière "
                        "que de la politique de ressources humaines.",
            "energy": "Dans les services, la consommation dépend surtout des bâtiments : performance "
                      "des locaux, réglage du chauffage et de la climatisation, taux d'occupation "
                      "des surfaces.",
            "waste": "le papier, les équipements informatiques en fin de vie et les déchets de "
                     "restauration",
            "water": "les usages sanitaires",
            "bio": "le choix des implantations, la gestion des espaces extérieurs et les critères "
                   "d'achat",
            "safety": "les risques routiers lors des déplacements, les troubles musculosquelettiques "
                      "liés au travail sur écran et les risques psychosociaux dominent",
            "talent": "la concurrence pour attirer et retenir les profils qualifiés est forte",
            "mix": "Dans les services, où les viviers de diplômés sont largement mixtes, un "
                   "déséquilibre marqué s'explique mal par le marché du travail : il interroge les "
                   "pratiques de recrutement et d'évolution.",
        },
        "en": {
            "label": "a services company",
            "s1": "gas or oil heating of offices and, where relevant, company or service vehicles",
            "s2": "office electricity — lighting, air conditioning, IT — and, where relevant, "
                  "district heating",
            "s3": "business travel, commuting, purchased services and IT equipment",
            "s3_missing": "For a services company, travel, commuting and purchases often make up "
                          "most of the footprint: the inventory presented shows only a small part "
                          "of it.",
            "lever_s1": "The levers concern how offices are heated and the vehicle policy — two "
                        "decisions that belong as much to property management as to HR policy.",
            "energy": "In services, consumption depends mainly on buildings: the performance of the "
                      "premises, heating and cooling settings, and space occupancy.",
            "waste": "paper, end-of-life IT equipment and catering waste",
            "water": "sanitary use",
            "bio": "the choice of locations, management of outdoor spaces and purchasing criteria",
            "safety": "road risks during travel, musculoskeletal disorders linked to screen work and "
                      "psychosocial risks dominate",
            "talent": "competition to attract and retain qualified profiles is intense",
            "mix": "In services, where graduate pools are broadly balanced, a marked imbalance is "
                   "hard to explain by the labour market: it raises questions about recruitment "
                   "and promotion practices.",
        },
    },
    "numerique": {
        "fr": {
            "label": "une entreprise du numérique",
            "s1": "le chauffage des locaux et, le cas échéant, les groupes électrogènes de secours "
                  "des salles informatiques",
            "s2": "l'électricité des bureaux et surtout des infrastructures informatiques hébergées "
                  "en propre",
            "s3": "la fabrication des équipements, les services d'hébergement achetés, les "
                  "déplacements et l'usage des services par les clients",
            "s3_missing": "Dans le numérique, la fabrication des équipements et les services "
                          "d'hébergement achetés pèsent souvent davantage que les bureaux : leur "
                          "absence du bilan en change la lecture.",
            "lever_s1": "Le Scope 1 d'une entreprise du numérique reste en général modeste ; son "
                        "traitement relève du mode de chauffage des locaux et de l'entretien des "
                        "groupes de secours.",
            "energy": "Le taux d'utilisation des serveurs, le refroidissement et l'allongement de la "
                      "durée de vie des équipements sont les leviers les plus puissants du secteur.",
            "waste": "les équipements électriques et électroniques en fin de vie, pour lesquels les "
                     "filières de reconditionnement sont bien structurées",
            "water": "les usages sanitaires et, le cas échéant, le refroidissement des salles "
                     "informatiques",
            "bio": "les critères d'achat des équipements et des services d'hébergement",
            "safety": "les troubles musculosquelettiques liés au travail sur écran et les risques "
                      "psychosociaux — charge de travail, connexion permanente — sont les "
                      "principaux risques",
            "talent": "les profils techniques sont très recherchés et la mobilité entre employeurs "
                      "est forte",
            "mix": "Le numérique peine historiquement à féminiser ses métiers techniques. Le "
                   "déséquilibre reflète en partie les filières de formation, mais il prive "
                   "l'entreprise d'une partie des talents dont elle a besoin.",
        },
        "en": {
            "label": "a digital and technology company",
            "s1": "heating of premises and, where relevant, backup generators for server rooms",
            "s2": "electricity for offices and above all for self-hosted IT infrastructure",
            "s3": "equipment manufacturing, purchased hosting services, travel and customers' use "
                  "of the services",
            "s3_missing": "In the digital sector, equipment manufacturing and purchased hosting "
                          "often weigh more than the offices: leaving them out changes the picture.",
            "lever_s1": "Scope 1 is usually modest for a digital company; it comes down to how "
                        "premises are heated and how backup generators are maintained.",
            "energy": "Server utilisation, cooling and extending equipment lifetimes are the "
                      "sector's most powerful levers.",
            "waste": "end-of-life electrical and electronic equipment, for which refurbishment "
                     "channels are well established",
            "water": "sanitary use and, where relevant, cooling of server rooms",
            "bio": "purchasing criteria for equipment and hosting services",
            "safety": "musculoskeletal disorders linked to screen work and psychosocial risks — "
                      "workload, always-on culture — are the main risks",
            "talent": "technical profiles are in high demand and job mobility is high",
            "mix": "The digital sector has historically struggled to attract women into technical "
                   "roles. The imbalance partly reflects training pipelines, but it deprives the "
                   "company of part of the talent it needs.",
        },
    },
    "tourisme": {
        "fr": {
            "label": "un acteur du tourisme et de l'hôtellerie",
            "s1": "le chauffage des établissements, la production d'eau chaude, la cuisson et les "
                  "fuites de fluides frigorigènes",
            "s2": "l'électricité de l'éclairage, de la climatisation, des cuisines et des "
                  "blanchisseries",
            "s3": "les déplacements des clients, les achats alimentaires et les services "
                  "sous-traités",
            "s3_missing": "Dans le tourisme, les déplacements des clients et les achats alimentaires "
                          "pèsent souvent davantage que les établissements eux-mêmes.",
            "lever_s1": "Les leviers portent sur la production de chaleur et d'eau chaude (pompes à "
                        "chaleur, récupération de chaleur), l'entretien des équipements de froid et "
                        "le suivi des consommations par chambre occupée.",
            "energy": "La consommation rapportée à la nuitée ou au couvert servi est l'indicateur le "
                      "plus parlant pour les équipes d'exploitation.",
            "waste": "les biodéchets de restauration, les emballages et les produits d'accueil à "
                     "usage unique",
            "water": "les chambres, la blanchisserie, la restauration et, le cas échéant, les "
                     "piscines et espaces verts",
            "bio": "l'aménagement des sites et la pression exercée sur des milieux naturels souvent "
                   "fragiles",
            "safety": "la manutention, les brûlures et coupures en cuisine, les chutes et les "
                      "horaires décalés sont les risques caractéristiques de l'activité",
            "talent": "la saisonnalité et les horaires atypiques rendent le recrutement et la "
                      "fidélisation difficiles",
            "mix": None,
        },
        "en": {
            "label": "a tourism and hospitality company",
            "s1": "heating of establishments, hot water production, cooking and refrigerant leaks",
            "s2": "electricity for lighting, air conditioning, kitchens and laundries",
            "s3": "guests' travel, food purchases and subcontracted services",
            "s3_missing": "In tourism, guests' travel and food purchases often weigh more than the "
                          "establishments themselves.",
            "lever_s1": "The levers concern heat and hot-water production (heat pumps, heat "
                        "recovery), maintenance of cooling equipment and tracking consumption per "
                        "occupied room.",
            "energy": "Consumption per night or per cover served is the most meaningful indicator "
                      "for operations teams.",
            "waste": "catering bio-waste, packaging and single-use guest amenities",
            "water": "rooms, laundry, catering and, where relevant, pools and green spaces",
            "bio": "site development and pressure on often fragile natural environments",
            "safety": "handling, burns and cuts in kitchens, falls and staggered hours are the "
                      "characteristic risks of the business",
            "talent": "seasonality and atypical hours make recruitment and retention difficult",
            "mix": None,
        },
    },
    "general": {
        "fr": {
            "label": "une entreprise de ce profil",
            "s1": "les combustibles consommés sur les sites (chauffage, procédés) et les véhicules "
                  "détenus ou exploités",
            "s2": "l'électricité et, le cas échéant, la chaleur ou le froid achetés pour les sites",
            "s3": "les biens et services achetés, le transport, les déplacements et l'usage des "
                  "produits ou services vendus",
            "s3_missing": "Dans la plupart des activités, les achats de biens et de services et le "
                          "transport pèsent lourd dans l'empreinte : sans Scope 3, la hiérarchie des "
                          "postes reste provisoire.",
            "lever_s1": "Les leviers portent sur la performance des équipements de chauffage et de "
                        "procédé et sur la composition de la flotte de véhicules.",
            "energy": "Un audit énergétique des principaux sites permet en général d'identifier des "
                      "gains rapides dans la régulation, l'éclairage et les équipements les plus "
                      "anciens.",
            "waste": "les emballages, les déchets d'activité et les équipements en fin de vie",
            "water": "les usages sanitaires et, le cas échéant, les procédés",
            "bio": "l'aménagement des sites et les critères d'achat",
            "safety": "la manutention, les chutes et les déplacements figurent parmi les causes "
                      "d'accident les plus fréquentes",
            "talent": "le marché du travail reste tendu sur de nombreux métiers",
            "mix": None,
        },
        "en": {
            "label": "a company with this profile",
            "s1": "fuel burned on site (heating, processes) and owned or operated vehicles",
            "s2": "electricity and, where relevant, purchased heat or cooling for the sites",
            "s3": "purchased goods and services, transport, travel and the use of the products or "
                  "services sold",
            "s3_missing": "In most activities, purchased goods and services and transport weigh "
                          "heavily in the footprint: without Scope 3, the ranking of emission "
                          "sources remains provisional.",
            "lever_s1": "The levers concern the performance of heating and process equipment and "
                        "the make-up of the vehicle fleet.",
            "energy": "An energy audit of the main sites usually identifies quick wins in controls, "
                      "lighting and the oldest equipment.",
            "waste": "packaging, operating waste and end-of-life equipment",
            "water": "sanitary use and, where relevant, processes",
            "bio": "site development and purchasing criteria",
            "safety": "handling, falls and travel are among the most frequent causes of workplace "
                      "accidents",
            "talent": "the labour market remains tight for many jobs",
            "mix": None,
        },
    },
}


# ── Raisonnements ─────────────────────────────────────────────────────────
A = {
    "fr": {
        "title": {"env": "Analyse approfondie : ce que disent les chiffres environnementaux",
                  "social": "Analyse approfondie : ce que disent les chiffres sociaux",
                  "gov": "Analyse approfondie : ce que disent les chiffres de gouvernance"},
        # Structure de l'empreinte
        "t_ghg": "Où se forme l'empreinte carbone",
        "ghg_split": "Sur les {tot} t CO2e mesurées sur les scopes renseignés, {parts}.",
        "ghg_part": "le Scope {n} en représente {p}",
        "ghg_part_next": "le Scope {n}, {p}",
        "s1_dom": "L'essentiel des émissions naît donc sur place, dans des équipements que "
                  "l'entreprise possède ou exploite : chez {label}, {s1}.",
        "s1_csq": "C'est à la fois une force et une contrainte. Une force, parce que ces émissions "
                  "sont entièrement entre les mains de la direction : aucun fournisseur à convaincre, "
                  "aucune donnée à attendre. Une contrainte, parce qu'elles sont adossées à des actifs "
                  "à longue durée de vie : chaque équipement renouvelé sans critère carbone engage "
                  "l'empreinte pour de longues années.",
        "s2_dom": "L'empreinte mesurée est d'abord celle de l'énergie achetée : chez {label}, {s2}.",
        "s2_csq": "Ce profil rend le bilan très sensible à des paramètres que l'entreprise ne "
                  "maîtrise qu'en partie, comme le contenu carbone du réseau électrique du pays "
                  "d'implantation. Il offre en contrepartie des leviers rapides : sobriété des "
                  "usages, efficacité des équipements, puis choix de l'origine de l'électricité.",
        "s3_dom": "La majeure partie de l'empreinte se situe hors des murs, dans la chaîne de "
                  "valeur : chez {label}, elle recouvre {s3}.",
        "s3_csq": "L'entreprise ne peut la réduire seule : elle dépend des choix de ses fournisseurs, "
                  "de la conception de ses offres et de l'usage qu'en font ses clients. Elle en porte "
                  "pourtant le risque, car une hausse du coût du carbone chez les fournisseurs finit "
                  "par se retrouver dans les prix d'achat. Le chantier commence par les données : "
                  "identifier les fournisseurs et les catégories d'achat qui pèsent le plus, obtenir "
                  "leurs propres bilans, puis intégrer un critère carbone aux consultations.",
        "s3_missing_intro": "Faute de Scope 3, cette lecture ne porte que sur la partie la plus "
                            "visible de l'empreinte.",
        # Intensité
        "t_int": "Intensité carbone : ce que dit le ratio",
        "int_fact": "Rapportées à l'activité, les {co2} t CO2e déclarées représentent {i} t par "
                    "million d'euros de chiffre d'affaires",
        "int_staff": ", soit {e} t par salarié",
        "int_grid_sector": "Pour {label}, la grille sectorielle du diagnostic classe ce niveau "
                           "comme {t}.",
        "int_grid_generic": "Faute de famille sectorielle reconnue, le diagnostic le lit sur sa "
                            "grille générique, qui le classe comme {t}.",
        "int_good": "Chaque euro de chiffre d'affaires est produit avec relativement peu de carbone. "
                    "Cet acquis a une valeur commerciale : de nombreux donneurs d'ordres intègrent "
                    "désormais l'empreinte de leurs fournisseurs dans leur propre bilan, et un ratio "
                    "favorable devient un argument dans les consultations. Le risque est de s'en "
                    "contenter : un bon ratio peut masquer des émissions absolues qui augmentent avec "
                    "la croissance de l'activité.",
        "int_mid": "L'entreprise n'est ni en avance ni en retard sur les acteurs comparables. C'est "
                   "pourtant une position exposée à moyen terme : les attentes se déplacent, et ce "
                   "qui est dans la moyenne aujourd'hui deviendra un retard dès que les concurrents "
                   "auront engagé leur propre décarbonation.",
        "int_bad": "La grille tient pourtant déjà compte de la nature de l'activité : l'écart ne "
                   "s'explique donc pas seulement par le métier. Il signale des équipements, des "
                   "procédés ou des approvisionnements plus carbonés que ceux des acteurs "
                   "comparables. La conséquence est double : une exposition plus forte aux hausses "
                   "du prix de l'énergie et du carbone, qui pèseront davantage sur la marge que chez "
                   "les concurrents, et une fragilité commerciale auprès des clients qui choisissent "
                   "leurs fournisseurs sur ce critère.",
        # Énergie
        "t_energy": "Énergie : sobriété, efficacité, origine",
        "en_fact": "L'entreprise a consommé {mwh} MWh sur l'exercice",
        "en_staff": ", soit {r} MWh par salarié",
        "en_rev": " et {x} MWh par million d'euros de chiffre d'affaires",
        "en_ren": "{p} de l'énergie consommée est d'origine renouvelable, un niveau {t} selon la "
                  "grille du diagnostic.",
        "en_ren_s1": "L'effort sur l'approvisionnement électrique a donc porté ses fruits ; mais "
                     "comme l'essentiel des émissions vient des combustibles (Scope 1), ce levier "
                     "arrive en bout de course. La suite passe par l'électrification des usages "
                     "thermiques ou par des combustibles moins carbonés, des décisions plus lourdes "
                     "et plus longues à mettre en œuvre.",
        "en_low_s2": "Or le Scope 2 pèse {p} des émissions mesurées : l'origine de l'électricité "
                     "est ici un levier de premier ordre, activable rapidement par un changement de "
                     "contrat d'approvisionnement, sans investissement lourd.",
        "en_low": "La marge de progression est réelle ; son effet sur le bilan carbone dépendra "
                  "toutefois de la place de l'électricité dans le mix énergétique, donnée qui "
                  "permettra de hiérarchiser les actions.",
        "en_ok": "Le niveau atteint montre qu'une politique d'achat existe ; il reste à la "
                 "sécuriser dans la durée, par des contrats pluriannuels et une traçabilité de "
                 "l'origine de l'énergie.",
        "en_order": "Dans une démarche bien ordonnée, la sobriété précède l'efficacité, qui précède "
                    "le verdissement : chaque mégawattheure évité est un gain à la fois économique et "
                    "climatique, alors qu'un mégawattheure verdi reste une dépense.",
        # Déchets
        "t_waste": "Déchets et ressources",
        "w_fact": "{wt} t de déchets ont été produites sur l'exercice",
        "w_staff": ", soit {r} t par salarié",
        "w_rec": "{p} des déchets sont valorisés, un taux {t} selon la grille du diagnostic.",
        "w_streams": "Chez {label}, les gisements principaux sont en général {w}.",
        "w_good": "Le tri et les filières sont en place. L'enjeu suivant est la réduction à la "
                  "source, car un déchet bien recyclé reste une matière achetée puis perdue.",
        "w_mid": "Une part significative part encore en élimination : c'est un coût de collecte et "
                 "de traitement, et une matière perdue. Des filières de valorisation existent pour "
                 "la plupart des flux ; le frein est souvent organisationnel — tri à la source, "
                 "contrats de collecte séparée, suivi par site.",
        "w_bad": "La majorité des déchets est éliminée sans valorisation. Au-delà de l'impact "
                 "environnemental, c'est une dépense récurrente et un signal négatif pour les clients "
                 "qui évaluent la circularité de leurs fournisseurs.",
        # Eau
        "t_water": "Eau",
        "water_fact": "{w} m³ d'eau ont été consommés sur l'exercice",
        "water_staff": ", soit {r} m³ par salarié",
        "water_use": "Chez {label}, l'eau sert principalement à {u}.",
        "water_read": "Le diagnostic ne classe pas ce volume, faute de grille sectorielle "
                      "défendable. Il invite en revanche à le suivre site par site : un même volume "
                      "n'a pas le même enjeu dans un bassin en tension hydrique et dans un bassin "
                      "excédentaire, et c'est cette géographie qui détermine le risque "
                      "d'approvisionnement.",
        # Biodiversité
        "t_bio": "Biodiversité",
        "bio_zero": "Aucune initiative en faveur de la biodiversité n'est déclarée. Pour {label}, "
                    "l'enjeu passe d'abord par {b}.",
        "bio_some": "{c}, un niveau {t} selon la grille du diagnostic. Pour {label}, "
                    "l'enjeu principal passe par {b}. La portée de ces actions reste à qualifier : "
                    "surfaces concernées, suivi écologique dans le temps, pérennité des "
                    "financements.",
        # Données manquantes
        "t_gaps": "Ce que les données ne disent pas encore",
        "gaps_intro": "Plusieurs indicateurs manquent au dossier, et chacun prive l'analyse d'un "
                      "éclairage précis.",
        "gap": {
            "energy_consumption_mwh": "Sans la consommation d'énergie, l'efficacité énergétique ne "
                                      "peut pas être mesurée, ni la part renouvelable traduite en "
                                      "volume.",
            "scope1_emissions": "Sans le Scope 1, le poids des combustibles et des véhicules reste "
                                "inconnu.",
            "scope2_emissions": "Sans le Scope 2, l'effet des achats d'électricité sur le bilan ne "
                                "peut pas être évalué.",
            "waste_generated_tonnes": "Sans le volume de déchets, le taux de valorisation ne dit rien "
                                      "des quantités en jeu.",
            "water_consumption_m3": "Sans la consommation d'eau, l'exposition au risque hydrique "
                                    "reste hors champ.",
            "renewable_energy_percent": "Sans la part d'énergie renouvelable, la stratégie "
                                        "d'approvisionnement ne peut pas être appréciée.",
            "co2_emissions_tonnes": "Sans total d'émissions, aucune intensité carbone ne peut être "
                                    "calculée.",
            "employee_turnover_percent": "Sans le taux de rotation, la capacité à fidéliser les "
                                         "équipes ne peut pas être appréciée.",
            "training_hours_per_employee": "Sans les heures de formation, l'investissement dans les "
                                           "compétences reste invisible.",
            "accident_frequency_rate": "Sans le taux de fréquence, la sinistralité ne peut pas être "
                                       "comparée aux références nationales.",
            "female_employees_percent": "Sans la part de femmes, la mixité des équipes ne peut pas "
                                        "être lue.",
            "total_employees": "Sans l'effectif, aucun ratio par salarié ne peut être calculé.",
            "independent_board_percent": "Sans la part d'administrateurs indépendants, la capacité "
                                         "du conseil à challenger la direction reste inconnue.",
            "female_board_percent": "Sans la part de femmes au conseil, la diversité de l'instance "
                                    "ne peut pas être appréciée.",
            "esg_audit_conducted": "Sans information sur la vérification externe, la fiabilité des "
                                   "chiffres publiés ne peut pas être qualifiée.",
            "sustainability_committee": "Sans information sur un comité dédié, le pilotage de la "
                                        "démarche reste à décrire.",
        },
        "gaps_close": "Ces lacunes ne pèsent pas sur le score — un indicateur absent n'est jamais "
                      "noté — mais elles limitent la portée des conclusions. Les combler au prochain "
                      "exercice est souvent le progrès le moins coûteux du plan.",
        # Santé-sécurité
        "t_safety": "Santé et sécurité au travail",
        "tf_fact": "Le taux de fréquence des accidents s'établit à {tf}, {cmp} la moyenne nationale "
                   "publiée par l'Assurance Maladie pour 2024 ({nat}).",
        "tf_cmp_half": "moins de la moitié de",
        "tf_cmp_below": "en dessous de",
        "tf_cmp_equal": "au niveau de",
        "tf_cmp_times": "soit {x} fois",
        "acc_count": "{n} accidents du travail ont été déclarés sur l'exercice.",
        "acc_one": "Un accident du travail a été déclaré sur l'exercice.",
        "acc_zero": "Aucun accident du travail n'a été déclaré sur l'exercice.",
        "acc_no_tf": "Sans le nombre d'heures travaillées, ce chiffre ne peut être comparé ni d'une "
                     "année sur l'autre ni aux références nationales : c'est pourquoi le taux de "
                     "fréquence est l'indicateur à suivre.",
        "safety_ctx": "Chez {label}, {s}.",
        "tf_high": "Au-delà du coût humain, qui prime, une sinistralité de ce niveau désorganise "
                   "l'activité — absences, remplacements, équipes en sous-effectif — et pèse sur "
                   "l'attractivité de l'employeur. Les démarches qui produisent des résultats "
                   "rapides combinent l'analyse systématique de chaque accident et presque-accident, "
                   "l'implication de l'encadrement de proximité et un plan d'action suivi en comité "
                   "de direction.",
        "tf_mid": "L'entreprise se situe sous la moyenne nationale sans être exemplaire. Le passage "
                  "au niveau supérieur demande en général de sortir de la seule conformité : "
                  "remontée des presque-accidents, visites de sécurité managériales, analyse des "
                  "causes profondes plutôt que des seules circonstances.",
        "tf_low": "Ce résultat témoigne d'une prévention installée. Il doit être protégé : un bon "
                  "taux de fréquence peut coexister avec des risques graves mais rares, ou avec des "
                  "troubles musculosquelettiques qui ne se traduisent pas immédiatement en arrêts. "
                  "Le suivi de la gravité et des presque-accidents complète utilement l'indicateur.",
        "tf_turnover": "La rotation du personnel ({to}) complique probablement la prévention : "
                       "chaque nouvel arrivant doit apprendre les risques de son poste, et une "
                       "équipe qui se renouvelle vite transmet mal les bons réflexes.",
        "tf_training": "Avec {h} de formation par salarié et par an, le temps disponible pour "
                       "l'accueil sécurité et les recyclages paraît court au regard de l'enjeu.",
        # Fidélisation et compétences
        "t_talent": "Fidélisation et compétences",
        "to_fact": "Avec un taux de rotation de {to}, l'entreprise a vu partir l'équivalent "
                   "d'environ {dep} salariés sur l'exercice.",
        "to_fact_nostaff": "Le taux de rotation du personnel atteint {to}.",
        "tr_fact": "Chaque salarié a suivi en moyenne {h} de formation",
        "tr_total": ", soit de l'ordre de {tot} heures au total",
        "talent_ctx": "Le contexte n'aide pas : chez {label}, {t}.",
        "q_bad_bad": "Les deux indicateurs se renforcent l'un l'autre, dans le mauvais sens. Un "
                     "salarié peu formé voit moins de perspectives et part plus facilement ; une "
                     "entreprise qui voit partir ses salariés hésite à investir dans leur formation. "
                     "Ce cercle se paie en coûts de recrutement, en temps d'intégration et en perte "
                     "de savoir-faire, et finit par peser sur la qualité de service.",
        "q_bad_good": "Le paradoxe est notable : l'entreprise forme, mais ne retient pas. Une partie "
                      "de l'investissement de formation profite donc à d'autres employeurs. Les "
                      "causes sont à chercher ailleurs que dans les compétences — rémunération, "
                      "perspectives d'évolution, conditions de travail, qualité du management de "
                      "proximité — et des entretiens de départ structurés permettraient de les "
                      "objectiver.",
        "q_good_bad": "La stabilité des équipes est un atout, mais le faible effort de formation "
                      "expose à un vieillissement des compétences. Dans un contexte où les métiers se "
                      "transforment, une équipe stable et peu formée peut devenir une équipe "
                      "dépassée.",
        "q_good_good": "La combinaison est vertueuse : les salariés restent et progressent. C'est un "
                       "capital difficile à imiter pour les concurrents, qui mérite d'être mis en "
                       "avant dans la marque employeur.",
        "q_mid": "Aucun des deux indicateurs n'appelle d'alerte, sans que l'un ou l'autre constitue "
                 "un avantage distinctif. Les suivre par métier et par site permettrait de repérer "
                 "les poches de fragilité que la moyenne masque.",
        "to_only_bad": "À ce niveau, la rotation représente un coût caché important : recrutement, "
                       "intégration, perte de productivité pendant la montée en compétence.",
        "to_only_good": "La stabilité des équipes est un atout pour la qualité de service et la "
                        "transmission des savoir-faire.",
        "tr_only_bad": "C'est peu pour entretenir les compétences dans la durée, a fortiori dans des "
                       "métiers qui évoluent.",
        "tr_only_good": "L'investissement dans les compétences est réel ; il gagnerait à être relié "
                        "aux parcours d'évolution pour produire aussi de la fidélisation.",
        # Mixité
        "t_mix": "Mixité des équipes",
        "mix_fact": "Les femmes représentent {f} de l'effectif",
        "mix_count": ", soit environ {n} salariées",
        "mix_below": "C'est en deçà du repère interne de {rep} % retenu par ce diagnostic — un "
                     "repère d'analyse, non une obligation légale.",
        "mix_above": "C'est au-dessus du repère interne de {rep} % retenu par ce diagnostic. La "
                     "question se déplace alors vers la répartition : les femmes accèdent-elles dans "
                     "les mêmes proportions aux postes d'encadrement et de direction ?",
        "mix_generic": "Rien dans le profil du secteur ne rend ce déséquilibre inévitable : il "
                       "invite à examiner les pratiques de recrutement, l'intitulé et les conditions "
                       "des postes proposés, et les parcours d'évolution.",
        "mix_csq": "Un effectif déséquilibré se prive d'une partie des candidats, et donc de "
                   "compétences, au moment où les recrutements se tendent.",
        "mix_board_up": "Fait notable, le conseil ({b} de femmes) est plus féminisé que "
                        "l'effectif : la gouvernance donne un signal que l'organisation ne suit pas "
                        "encore.",
        "mix_board_down": "Le conseil ({b} de femmes) est en revanche moins féminisé que "
                          "l'effectif : le déséquilibre se concentre au sommet de l'organisation.",
        # Ancrage territorial
        "t_stake": "Ancrage territorial et parties prenantes",
        "local_fact": "{p} des achats sont réalisés auprès de fournisseurs locaux.",
        "local_high": "Cet ancrage réduit la dépendance aux chaînes d'approvisionnement longues et "
                      "soutient l'économie du territoire, ce qui compte dans les relations avec les "
                      "collectivités et les clients publics.",
        "local_low": "Une part plus élevée d'achats de proximité raccourcirait les chaînes "
                     "d'approvisionnement ; l'arbitrage avec le prix et la disponibilité gagnerait à "
                     "être documenté par catégorie d'achat.",
        "comm_fact": "{v} € ont été consacrés à des actions en faveur des communautés locales",
        "comm_staff": ", soit {r} € par salarié",
        "comm_read": "Pour en mesurer la portée, il faudra relier ces montants à des résultats : "
                     "bénéficiaires, projets soutenus, durée de l'engagement.",
        "sat_fact": "La satisfaction client atteint {v}/10, un niveau {t} selon la grille du "
                    "diagnostic.",
        "sat_read": "C'est l'indicateur qui relie le plus directement la politique sociale au modèle "
                    "économique : des équipes stables et formées contribuent à un service plus "
                    "régulier.",
        "dis_fact": "Les personnes en situation de handicap déclarée représentent {p} de l'effectif.",
        "dis_read": "L'indicateur mesure autant la politique d'inclusion que la confiance des "
                    "salariés, qui ne déclarent leur situation que s'ils n'en redoutent pas les "
                    "conséquences.",
        # Pilotage
        "t_steer": "Pilotage de la démarche de durabilité",
        "st_both": "L'entreprise dispose à la fois d'un comité de durabilité et d'une vérification "
                   "externe de ses données ESG : le dispositif de pilotage est complet dans sa "
                   "forme. La question devient celle de son influence réelle — fréquence des "
                   "réunions, sujets inscrits à l'ordre du jour du conseil, lien avec les décisions "
                   "d'investissement et, le cas échéant, avec la rémunération des dirigeants.",
        "st_comm_only": "Un comité de durabilité existe, mais les données ESG ne font pas l'objet "
                        "d'une vérification externe. Le pilotage repose donc sur des chiffres que "
                        "personne d'extérieur n'a contrôlés : c'est une fragilité face aux banques, "
                        "aux investisseurs et aux grands clients, qui accordent plus de crédit à une "
                        "information vérifiée. Une revue externe ciblée sur quelques indicateurs "
                        "clés constitue une première étape proportionnée.",
        "st_audit_only": "Les données ESG sont vérifiées par un tiers, mais aucune instance dédiée ne "
                         "pilote la démarche. Le risque est que les constats de la vérification "
                         "restent sans suite, faute de lieu où les arbitrer. Confier ce rôle à un "
                         "comité, ou à un point régulier de l'ordre du jour du conseil, donnerait un "
                         "débouché aux recommandations.",
        "st_none": "Ni comité de durabilité ni vérification externe : la démarche repose "
                   "aujourd'hui sur des initiatives individuelles plus que sur une organisation. "
                   "C'est fréquent au début d'une démarche, mais cela la rend dépendante de "
                   "quelques personnes et difficile à rendre crédible à l'extérieur. Désigner un "
                   "responsable, fixer un rendez-vous régulier en comité de direction et documenter "
                   "les méthodes de calcul sont les premiers pas.",
        "st_comm_only_partial": "Un comité de durabilité existe ; le dossier ne précise pas si les "
                                "données ESG font l'objet d'une vérification externe.",
        "st_no_comm_partial": "Aucun comité de durabilité n'est déclaré : le pilotage de la démarche "
                              "reste à organiser.",
        "st_audit_partial": "Les données ESG font l'objet d'une vérification externe ; le dossier ne "
                            "précise pas quelle instance en pilote les suites.",
        "st_no_audit_partial": "Les données ESG ne font pas l'objet d'une vérification externe, ce "
                               "qui limite leur crédibilité auprès des partenaires financiers.",
        # Conseil
        "t_board": "Le conseil d'administration",
        "board_fact": "Le conseil compte {n} membres",
        "board_ind": ("aucun indépendant", "{a}un indépendant ({p})", "{a}{k} indépendants ({p})"),
        "board_fem": ("aucune femme", "{a}une femme ({p})", "{a}{k} femmes ({p})"),
        "about": "environ ",
        "board_small": "Un conseil resserré décide vite, mais concentre l'expertise sur peu de "
                       "personnes : les sujets climat, social ou numérique risquent de ne trouver "
                       "aucun administrateur pour les porter.",
        "board_mid": "Cette taille permet de réunir des compétences variées sans alourdir les "
                     "délibérations.",
        "board_large": "Un conseil de cette taille assure une large représentation, au prix de "
                       "débats plus difficiles à conduire : le travail en comités spécialisés "
                       "devient alors indispensable.",
        "ind_low": "Avec peu d'administrateurs indépendants, le conseil peut peiner à challenger la "
                   "direction ou l'actionnaire de référence. C'est précisément sur les arbitrages de "
                   "long terme, comme la durabilité, que ce regard extérieur est le plus utile.",
        "ind_high": "La proportion d'indépendants permet un contrôle effectif de la direction et "
                    "rassure les partenaires financiers sur la qualité des décisions.",
        # Intégrité
        "t_integrity": "Éthique, intégrité et sécurité de l'information",
        "int_all_zero": "Aucun manquement éthique, cas de corruption ou violation de données n'est "
                        "déclaré sur l'exercice. Ce résultat n'a de valeur que s'il repose sur des "
                        "dispositifs capables de détecter les incidents : un canal d'alerte connu "
                        "et utilisé, des contrôles internes, une surveillance des systèmes "
                        "d'information. Sans eux, « zéro » peut signifier « rien n'a été vu » "
                        "plutôt que « rien n'est arrivé ».",
        "eth_some": "{c}. Au-delà du nombre, c'est le traitement qui compte : chaque cas "
                    "a-t-il donné lieu à une enquête, à une réponse proportionnée et à la correction "
                    "du processus en cause ?",
        "cor_some": "{c} : c'est le sujet le plus grave du pilier. Au-delà des "
                    "conséquences juridiques, un tel cas fragilise l'accès aux financements et à "
                    "certains marchés, et durablement la réputation. La réponse attendue combine "
                    "une cartographie des risques de corruption, des contrôles renforcés sur les "
                    "tiers et une formation ciblée des fonctions exposées.",
        "brc_some": "{c}. Chaque incident expose l'entreprise à des coûts de remédiation, "
                    "à une perte de confiance des clients et, le cas échéant, à des obligations de "
                    "notification. L'analyse des causes — erreur humaine, faille technique, "
                    "prestataire — doit orienter le plan : sensibilisation, correctifs, exigences "
                    "contractuelles envers les sous-traitants.",
        # Moyens
        "t_budget": "Moyens consacrés à la durabilité",
        "bud_fact": "Le budget consacré à la RSE s'élève à {v} €",
        "bud_staff": ", soit {r} € par salarié",
        "bud_rev": " et {p} du chiffre d'affaires",
        "bud_read": "Un budget n'est pas une performance : sa pertinence se juge à ce qu'il finance.",
        "bud_focus": "La lecture croisée avec les scores suggère de le concentrer sur le pilier "
                     "{p}, le moins bien noté.",
    },
    "en": {
        "title": {"env": "In-depth analysis: what the environmental figures say",
                  "social": "In-depth analysis: what the social figures say",
                  "gov": "In-depth analysis: what the governance figures say"},
        "t_ghg": "Where the carbon footprint comes from",
        "ghg_split": "Of the {tot} t CO2e measured across the reported scopes, {parts}.",
        "ghg_part": "Scope {n} accounts for {p}",
        "ghg_part_next": "Scope {n}, {p}",
        "s1_dom": "Most emissions therefore arise on site, from equipment the company owns or "
                  "operates: for {label}, {s1}.",
        "s1_csq": "This is both a strength and a constraint. A strength, because these emissions "
                  "are entirely in management's hands: no supplier to persuade, no data to wait for. "
                  "A constraint, because they are tied to long-lived assets: every piece of "
                  "equipment renewed without a carbon criterion locks in the footprint for years.",
        "s2_dom": "The measured footprint is first and foremost that of purchased energy: for "
                  "{label}, {s2}.",
        "s2_csq": "This profile makes the inventory highly sensitive to parameters the company only "
                  "partly controls, such as the carbon content of the national grid. In return, it "
                  "offers quick levers: energy sufficiency, efficient equipment, then the choice of "
                  "electricity source.",
        "s3_dom": "Most of the footprint lies outside the company's walls, in the value chain: for "
                  "{label}, it covers {s3}.",
        "s3_csq": "The company cannot reduce it alone: it depends on suppliers' choices, on how its "
                  "offer is designed and on how customers use it. Yet the company bears the risk, "
                  "since a rising carbon cost at suppliers eventually shows up in purchase prices. "
                  "The work starts with data: identify the suppliers and purchase categories that "
                  "weigh most, obtain their own inventories, then add a carbon criterion to "
                  "tenders.",
        "s3_missing_intro": "Without Scope 3, this reading covers only the most visible part of "
                            "the footprint.",
        "t_int": "Carbon intensity: what the ratio says",
        "int_fact": "Relative to activity, the {co2} t CO2e reported represent {i} t per million "
                    "euros of revenue",
        "int_staff": ", or {e} t per employee",
        "int_grid_sector": "For {label}, the diagnostic's sector grid rates this level as {t}.",
        "int_grid_generic": "With no recognised sector family, the diagnostic reads it on its "
                            "generic grid, which rates it as {t}.",
        "int_good": "Each euro of revenue is generated with relatively little carbon. This has "
                    "commercial value: many buyers now include their suppliers' footprint in their "
                    "own inventories, and a favourable ratio becomes an argument in tenders. The "
                    "risk is complacency: a good ratio can hide absolute emissions that rise with "
                    "business growth.",
        "int_mid": "The company is neither ahead nor behind comparable players. Yet this is an "
                   "exposed position in the medium term: expectations are shifting, and what is "
                   "average today will become a lag once competitors have started their own "
                   "decarbonisation.",
        "int_bad": "The grid already takes the nature of the business into account, so the gap is "
                   "not explained by the trade alone. It points to equipment, processes or supplies "
                   "that are more carbon-intensive than those of comparable players. The "
                   "consequence is twofold: greater exposure to rising energy and carbon prices, "
                   "which will weigh more heavily on margins than at competitors, and commercial "
                   "fragility with customers who select suppliers on this criterion.",
        "t_energy": "Energy: sufficiency, efficiency, source",
        "en_fact": "The company consumed {mwh} MWh over the year",
        "en_staff": ", or {r} MWh per employee",
        "en_rev": " and {x} MWh per million euros of revenue",
        "en_ren": "{p} of the energy consumed comes from renewable sources, rated {t} on the "
                  "diagnostic's grid.",
        "en_ren_s1": "The effort on electricity supply has therefore paid off; but since most "
                     "emissions come from fuels (Scope 1), this lever is reaching its limit. The "
                     "next step is to electrify thermal uses or switch to lower-carbon fuels — "
                     "heavier decisions that take longer to implement.",
        "en_low_s2": "Yet Scope 2 accounts for {p} of measured emissions: the source of electricity "
                     "is a first-order lever here, which can be activated quickly by changing the "
                     "supply contract, without heavy investment.",
        "en_low": "There is real room for progress; its effect on the carbon inventory will, "
                  "however, depend on the share of electricity in the energy mix, a figure that "
                  "will help rank the actions.",
        "en_ok": "The level reached shows that a purchasing policy exists; it now needs to be "
                 "secured over time through multi-year contracts and traceability of the energy's "
                 "origin.",
        "en_order": "In a well-ordered approach, sufficiency comes before efficiency, which comes "
                    "before greening: every megawatt-hour avoided is both an economic and a climate "
                    "gain, whereas a greened megawatt-hour is still an expense.",
        "t_waste": "Waste and resources",
        "w_fact": "{wt} t of waste were generated over the year",
        "w_staff": ", or {r} t per employee",
        "w_rec": "{p} of waste is recovered, a rate the diagnostic's grid rates as {t}.",
        "w_streams": "For {label}, the main streams are usually {w}.",
        "w_good": "Sorting and recovery channels are in place. The next step is reduction at "
                  "source, because even well-recycled waste is still material bought and then lost.",
        "w_mid": "A significant share is still sent for disposal: a collection and treatment cost, "
                 "and lost material. Recovery channels exist for most streams; the obstacle is "
                 "often organisational — sorting at source, separate collection contracts, "
                 "site-level monitoring.",
        "w_bad": "Most waste is disposed of without recovery. Beyond the environmental impact, this "
                 "is a recurring expense and a negative signal for customers who assess their "
                 "suppliers' circularity.",
        "t_water": "Water",
        "water_fact": "{w} m³ of water were consumed over the year",
        "water_staff": ", or {r} m³ per employee",
        "water_use": "For {label}, water is mainly used for {u}.",
        "water_read": "The diagnostic does not rate this volume, lacking a defensible sector grid. "
                      "It does recommend tracking it site by site: the same volume does not carry "
                      "the same stakes in a water-stressed basin as in a water-rich one, and it is "
                      "this geography that determines supply risk.",
        "t_bio": "Biodiversity",
        "bio_zero": "No biodiversity initiative is reported. For {label}, the issue lies first in "
                    "{b}.",
        "bio_some": "{c}, rated {t} on the diagnostic's grid. For {label}, the "
                    "main issue lies in {b}. The scope of these actions remains to be qualified: "
                    "areas covered, ecological monitoring over time, durability of funding.",
        "t_gaps": "What the data does not yet show",
        "gaps_intro": "Several indicators are missing from the file, and each deprives the analysis "
                      "of a specific insight.",
        "gap": {
            "energy_consumption_mwh": "Without energy consumption, energy efficiency cannot be "
                                      "measured, nor the renewable share translated into volume.",
            "scope1_emissions": "Without Scope 1, the weight of fuels and vehicles remains unknown.",
            "scope2_emissions": "Without Scope 2, the effect of electricity purchases on the "
                                "inventory cannot be assessed.",
            "waste_generated_tonnes": "Without the waste volume, the recovery rate says nothing "
                                      "about the quantities at stake.",
            "water_consumption_m3": "Without water consumption, exposure to water risk remains out "
                                    "of view.",
            "renewable_energy_percent": "Without the renewable share, the supply strategy cannot be "
                                        "assessed.",
            "co2_emissions_tonnes": "Without total emissions, no carbon intensity can be computed.",
            "employee_turnover_percent": "Without the turnover rate, the ability to retain staff "
                                         "cannot be assessed.",
            "training_hours_per_employee": "Without training hours, investment in skills remains "
                                           "invisible.",
            "accident_frequency_rate": "Without the frequency rate, accident levels cannot be "
                                       "compared with national references.",
            "female_employees_percent": "Without the share of women, workforce gender balance "
                                        "cannot be read.",
            "total_employees": "Without headcount, no per-employee ratio can be computed.",
            "independent_board_percent": "Without the share of independent directors, the board's "
                                         "ability to challenge management remains unknown.",
            "female_board_percent": "Without the share of women on the board, its diversity cannot "
                                    "be assessed.",
            "esg_audit_conducted": "Without information on external assurance, the reliability of "
                                   "published figures cannot be qualified.",
            "sustainability_committee": "Without information on a dedicated committee, the "
                                        "steering of the approach remains to be described.",
        },
        "gaps_close": "These gaps do not affect the score — a missing indicator is never rated — "
                      "but they limit the reach of the conclusions. Filling them next year is often "
                      "the cheapest progress in the plan.",
        "t_safety": "Occupational health and safety",
        "tf_fact": "The accident frequency rate stands at {tf}, {cmp} the national average "
                   "published by the French Health Insurance for 2024 ({nat}).",
        "tf_cmp_half": "less than half of",
        "tf_cmp_below": "below",
        "tf_cmp_equal": "in line with",
        "tf_cmp_times": "{x} times",
        "acc_count": "{n} workplace accidents were reported over the year.",
        "acc_one": "One workplace accident was reported over the year.",
        "acc_zero": "No workplace accident was reported over the year.",
        "acc_no_tf": "Without the number of hours worked, this figure cannot be compared from one "
                     "year to the next or with national references: this is why the frequency rate "
                     "is the indicator to track.",
        "safety_ctx": "For {label}, {s}.",
        "tf_high": "Beyond the human cost, which comes first, accident levels like these disrupt "
                   "operations — absences, replacements, understaffed teams — and weigh on the "
                   "company's appeal as an employer. The approaches that deliver quick results "
                   "combine systematic analysis of every accident and near miss, involvement of "
                   "front-line managers and an action plan monitored by the executive committee.",
        "tf_mid": "The company is below the national average without being exemplary. Reaching the "
                  "next level usually means going beyond compliance: reporting near misses, "
                  "management safety walks, analysing root causes rather than just circumstances.",
        "tf_low": "This result reflects an established prevention culture. It must be protected: a "
                  "good frequency rate can coexist with serious but rare risks, or with "
                  "musculoskeletal disorders that do not immediately lead to time off. Tracking "
                  "severity and near misses usefully complements the indicator.",
        "tf_turnover": "Staff turnover ({to}) probably complicates prevention: every newcomer has to "
                       "learn the risks of the job, and a team that renews itself quickly passes on "
                       "good habits poorly.",
        "tf_training": "With {h} of training per employee per year, the time available for safety "
                       "induction and refresher courses seems short given the stakes.",
        "t_talent": "Retention and skills",
        "to_fact": "With a turnover rate of {to}, the company lost the equivalent of about {dep} "
                   "employees over the year.",
        "to_fact_nostaff": "Staff turnover stands at {to}.",
        "tr_fact": "Each employee received on average {h} of training",
        "tr_total": ", some {tot} hours in total",
        "talent_ctx": "The context does not help: for {label}, {t}.",
        "q_bad_bad": "The two indicators reinforce each other, in the wrong direction. A poorly "
                     "trained employee sees fewer prospects and leaves more easily; a company that "
                     "sees its staff leave hesitates to invest in their training. This cycle is paid "
                     "for in recruitment costs, onboarding time and lost know-how, and eventually "
                     "weighs on service quality.",
        "q_bad_good": "The paradox is striking: the company trains but does not retain. Part of the "
                      "training investment therefore benefits other employers. The causes lie "
                      "elsewhere than in skills — pay, career prospects, working conditions, "
                      "quality of front-line management — and structured exit interviews would help "
                      "pin them down.",
        "q_good_bad": "Team stability is an asset, but the low training effort exposes the company "
                      "to ageing skills. As jobs change, a stable but under-trained team can become "
                      "an outdated one.",
        "q_good_good": "The combination is virtuous: employees stay and grow. This is an asset "
                       "competitors find hard to copy, and it deserves to be showcased in the "
                       "employer brand.",
        "q_mid": "Neither indicator calls for an alert, but neither is a distinctive advantage. "
                 "Tracking them by job and by site would reveal pockets of fragility that the "
                 "average hides.",
        "to_only_bad": "At this level, turnover is a significant hidden cost: recruitment, "
                       "onboarding, lost productivity while newcomers get up to speed.",
        "to_only_good": "Team stability is an asset for service quality and the transfer of "
                        "know-how.",
        "tr_only_bad": "This is little to maintain skills over time, especially in changing jobs.",
        "tr_only_good": "The investment in skills is real; linking it to career paths would also "
                        "make it a retention tool.",
        "t_mix": "Gender balance in the workforce",
        "mix_fact": "Women make up {f} of the workforce",
        "mix_count": ", or about {n} employees",
        "mix_below": "This is below the internal benchmark of {rep}% used in this diagnostic — an "
                     "analytical benchmark, not a legal requirement.",
        "mix_above": "This is above the internal benchmark of {rep}% used in this diagnostic. The "
                     "question then shifts to distribution: do women reach management and "
                     "leadership positions in the same proportions?",
        "mix_generic": "Nothing in the sector's profile makes this imbalance inevitable: it calls "
                       "for a review of recruitment practices, the wording and conditions of the "
                       "positions offered, and career paths.",
        "mix_csq": "An unbalanced workforce misses out on part of the candidate pool, and therefore "
                   "on skills, just as recruitment is getting harder.",
        "mix_board_up": "Notably, the board ({b} women) is more gender-balanced than the workforce: "
                        "governance is sending a signal the organisation has yet to follow.",
        "mix_board_down": "The board ({b} women), however, is less gender-balanced than the "
                          "workforce: the imbalance is concentrated at the top of the organisation.",
        "t_stake": "Local roots and stakeholders",
        "local_fact": "{p} of purchases are made from local suppliers.",
        "local_high": "This local footprint reduces dependence on long supply chains and supports "
                      "the local economy, which matters in relations with local authorities and "
                      "public customers.",
        "local_low": "A higher share of local purchasing would shorten supply chains; the trade-off "
                     "with price and availability would benefit from being documented by purchase "
                     "category.",
        "comm_fact": "€{v} were devoted to community initiatives",
        "comm_staff": ", or €{r} per employee",
        "comm_read": "To measure their reach, these amounts will need to be linked to outcomes: "
                     "beneficiaries, projects supported, length of commitment.",
        "sat_fact": "Customer satisfaction stands at {v}/10, rated {t} on the diagnostic's grid.",
        "sat_read": "This is the indicator that most directly links social policy to the business "
                    "model: stable, well-trained teams contribute to more consistent service.",
        "dis_fact": "Employees with a declared disability make up {p} of the workforce.",
        "dis_read": "The indicator measures inclusion policy as much as employees' trust: people "
                    "only declare their situation if they do not fear the consequences.",
        "t_steer": "Steering the sustainability approach",
        "st_both": "The company has both a sustainability committee and external assurance of its "
                   "ESG data: the steering framework is complete in form. The question becomes its "
                   "real influence — frequency of meetings, topics on the board's agenda, links "
                   "with investment decisions and, where relevant, with executive pay.",
        "st_comm_only": "A sustainability committee exists, but ESG data is not externally "
                        "assured. Steering therefore relies on figures no outsider has checked: a "
                        "weakness with banks, investors and large customers, who give more credit "
                        "to verified information. A targeted external review of a few key "
                        "indicators is a proportionate first step.",
        "st_audit_only": "ESG data is externally assured, but no dedicated body steers the approach. "
                         "The risk is that assurance findings go unaddressed for lack of a forum to "
                         "decide on them. Giving this role to a committee, or to a regular item on "
                         "the board's agenda, would give the recommendations an outlet.",
        "st_none": "Neither a sustainability committee nor external assurance: the approach "
                   "currently rests on individual initiatives rather than on an organisation. This "
                   "is common at the start, but it makes the approach dependent on a few people and "
                   "hard to make credible externally. Appointing a lead, setting a regular slot at "
                   "the executive committee and documenting calculation methods are the first "
                   "steps.",
        "st_comm_only_partial": "A sustainability committee exists; the file does not say whether "
                                "ESG data is externally assured.",
        "st_no_comm_partial": "No sustainability committee is reported: steering of the approach "
                              "remains to be organised.",
        "st_audit_partial": "ESG data is externally assured; the file does not say which body "
                            "follows up on it.",
        "st_no_audit_partial": "ESG data is not externally assured, which limits its credibility "
                               "with financial partners.",
        "t_board": "The board of directors",
        "board_fact": "The board has {n} members",
        "board_ind": ("no independent director", "{a}one independent director ({p})",
                      "{a}{k} independent directors ({p})"),
        "board_fem": ("no women", "{a}one woman ({p})", "{a}{k} women ({p})"),
        "about": "about ",
        "board_small": "A small board decides quickly but concentrates expertise in few people: "
                       "climate, social or digital issues may find no director to champion them.",
        "board_mid": "This size brings together varied skills without weighing down "
                     "deliberations.",
        "board_large": "A board of this size ensures broad representation, at the cost of harder "
                       "debates: work in specialised committees then becomes essential.",
        "ind_low": "With few independent directors, the board may struggle to challenge management "
                   "or the reference shareholder. It is precisely on long-term trade-offs, such as "
                   "sustainability, that this outside view is most useful.",
        "ind_high": "The proportion of independent directors allows effective oversight of "
                    "management and reassures financial partners about the quality of decisions.",
        "t_integrity": "Ethics, integrity and information security",
        "int_all_zero": "No ethics breach, corruption case or data breach is reported for the year. "
                        "This result is only meaningful if it rests on systems able to detect "
                        "incidents: a known and used whistleblowing channel, internal controls, "
                        "information-system monitoring. Without them, \"zero\" may mean \"nothing "
                        "was seen\" rather than \"nothing happened\".",
        "eth_some": "{c}. Beyond the number, what matters is how they were handled: did "
                    "each case lead to an investigation, a proportionate response and a fix to the "
                    "process at fault?",
        "cor_some": "{c}: this is the most serious issue in the pillar. Beyond the legal "
                    "consequences, such a case weakens access to financing and to certain markets, "
                    "and damages reputation for a long time. The expected response combines a "
                    "corruption risk map, tighter third-party checks and targeted training for "
                    "exposed functions.",
        "brc_some": "{c}. Each incident exposes the company to remediation costs, loss of "
                    "customer trust and, where applicable, notification obligations. Root-cause "
                    "analysis — human error, technical flaw, service provider — should shape the "
                    "plan: awareness, fixes, contractual requirements for subcontractors.",
        "t_budget": "Resources devoted to sustainability",
        "bud_fact": "The CSR budget amounts to €{v}",
        "bud_staff": ", or €{r} per employee",
        "bud_rev": " and {p} of revenue",
        "bud_read": "A budget is not performance: its relevance is judged by what it funds.",
        "bud_focus": "Cross-reading with the scores suggests focusing it on the {p} pillar, the "
                     "lowest rated.",
    },
}

# Compteurs accordés (0 / 1 / plusieurs) des phrases d'intégrité et de biodiversité
COUNTERS = {
    "fr": {
        "ethics_violations": ("", "Un manquement éthique a été déclaré", "{n} manquements éthiques ont été déclarés"),
        "corruption_cases": ("", "Un cas de corruption a été déclaré", "{n} cas de corruption ont été déclarés"),
        "data_breaches": ("", "Une violation de données a été déclarée", "{n} violations de données ont été déclarées"),
        "biodiversity_initiatives": ("", "Une initiative en faveur de la biodiversité a été déclarée",
                                     "{n} initiatives en faveur de la biodiversité ont été déclarées"),
    },
    "en": {
        "ethics_violations": ("", "One ethics breach was reported", "{n} ethics breaches were reported"),
        "corruption_cases": ("", "One corruption case was reported", "{n} corruption cases were reported"),
        "data_breaches": ("", "One data breach was reported", "{n} data breaches were reported"),
        "biodiversity_initiatives": ("", "One biodiversity initiative was reported",
                                     "{n} biodiversity initiatives were reported"),
    },
}


# Libellés des illustrations (illustrations.py)
ILLU = {
    "fr": {
        "short": {
            "co2_emissions_tonnes": "Intensité carbone (t CO2e / M€)",
            "renewable_energy_percent": "Énergie renouvelable",
            "waste_recycled_percent": "Déchets valorisés",
            "biodiversity_initiatives": "Initiatives biodiversité",
            "female_employees_percent": "Femmes dans l'effectif",
            "training_hours_per_employee": "Formation par salarié",
            "accident_frequency_rate": "Taux de fréquence des accidents",
            "employee_turnover_percent": "Rotation du personnel",
            "customer_satisfaction_score": "Satisfaction client (/10)",
            "independent_board_percent": "Administrateurs indépendants",
            "female_board_percent": "Femmes au conseil",
            "csr_budget_eur": "Budget RSE (€)",
        },
        "ruler_note": "Position de chaque indicateur sur la grille du diagnostic, de la tranche "
                      "critique (à gauche) à la tranche exemplaire (à droite).",
        "waffle_ren": "{p} de l'énergie\nd'origine renouvelable",
        "waffle_rec": "{p} des déchets\nvalorisés",
        "people_mix": "{n} femmes sur 100 salariés",
        "people_turnover": "{n} départs sur 100 salariés\ndans l'année",
        "tf_company": "{name}",
        "tf_national": "Moyenne nationale 2024\n(Assurance Maladie)",
        "tf_ratio": "{x} × la moyenne",
        "board_ind": "Indépendants : {k} sur {n}",
        "board_fem": "Femmes : {k} sur {n}",
        "cap_ruler": {"env": "Indicateurs environnementaux sur la grille du diagnostic",
                      "social": "Indicateurs sociaux sur la grille du diagnostic",
                      "gov": "Indicateurs de gouvernance sur la grille du diagnostic"},
        "cap_waffle": "Chaque carré représente 1 % : énergie et déchets rapportés à 100",
        "cap_people": "Chaque silhouette représente 1 % de l'effectif",
        "cap_tf": "Accidents avec arrêt par million d'heures travaillées",
        "cap_board": "Sièges du conseil : les deux lectures sont présentées séparément, les "
                     "données ne précisant pas qui cumule les deux qualités",
    },
    "en": {
        "short": {
            "co2_emissions_tonnes": "Carbon intensity (t CO2e / €M)",
            "renewable_energy_percent": "Renewable energy",
            "waste_recycled_percent": "Waste recovered",
            "biodiversity_initiatives": "Biodiversity initiatives",
            "female_employees_percent": "Women in the workforce",
            "training_hours_per_employee": "Training per employee",
            "accident_frequency_rate": "Accident frequency rate",
            "employee_turnover_percent": "Staff turnover",
            "customer_satisfaction_score": "Customer satisfaction (/10)",
            "independent_board_percent": "Independent directors",
            "female_board_percent": "Women on the board",
            "csr_budget_eur": "CSR budget (€)",
        },
        "ruler_note": "Position of each indicator on the diagnostic's grid, from the critical band "
                      "(left) to the exemplary band (right).",
        "waffle_ren": "{p} of energy\nfrom renewable sources",
        "waffle_rec": "{p} of waste\nrecovered",
        "people_mix": "{n} women per 100 employees",
        "people_turnover": "{n} departures per 100 employees\nover the year",
        "tf_company": "{name}",
        "tf_national": "National average 2024\n(French Health Insurance)",
        "tf_ratio": "{x} × the average",
        "board_ind": "Independent: {k} of {n}",
        "board_fem": "Women: {k} of {n}",
        "cap_ruler": {"env": "Environmental indicators on the diagnostic's grid",
                      "social": "Social indicators on the diagnostic's grid",
                      "gov": "Governance indicators on the diagnostic's grid"},
        "cap_waffle": "Each square represents 1%: energy and waste scaled to 100",
        "cap_people": "Each figure represents 1% of the workforce",
        "cap_tf": "Lost-time accidents per million hours worked",
        "cap_board": "Board seats: the two readings are shown separately, as the data does not "
                     "say who holds both qualities",
    },
}
