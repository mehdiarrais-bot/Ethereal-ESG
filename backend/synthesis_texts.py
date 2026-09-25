"""Phrases du diagnostic d'ensemble et de la conclusion (synthesis.py), FR/EN.

ISSUES : une fragilité repérée dans les données — titre chiffré, nom court,
cause, conséquence, horizon (« si rien ne change »), première action.
STRENGTHS : un point d'appui — titre chiffré, nom court, portée.
LINKS : liens entre piliers, déclenchés par des combinaisons d'enjeux.

Mêmes règles que analysis_texts : chiffres du dossier ou ratios calculés,
aucune affirmation réglementaire, causes formulées comme mécanismes connus
ou hypothèses à vérifier. Les fragments {…} viennent de synthesis.py ou du
contexte sectoriel (analysis_texts.SECTOR).
"""

ISSUES = {
    "fr": {
        "safety": {
            "title": "Une sinistralité {r} fois la moyenne nationale",
            "name": "la sécurité au travail",
            "cause": "Chez {label}, {safety}. Avec un taux de fréquence de {tf}, la prévention n'a "
                     "manifestement pas encore pris la mesure de cette exposition{turnover}.",
            "turnover": ", d'autant que la rotation du personnel ({to}) renouvelle sans cesse les "
                        "équipes à former",
            "csq": "Le premier coût est humain. Le deuxième est opérationnel — absences, "
                   "remplacements, équipes désorganisées. Le troisième est commercial : nombre de "
                   "donneurs d'ordres examinent la sinistralité de leurs prestataires avant de leur "
                   "confier un marché.",
            "horizon": "la sinistralité continuera de peser sur la continuité de l'activité et sur "
                       "la capacité à recruter, et chaque accident grave remettra en cause la "
                       "politique de prévention",
            "action": "Analyser un à un les accidents de l'exercice et désigner, pour chacun des "
                      "trois risques principaux, un responsable et une mesure de prévention datée.",
        },
        "retention": {
            "title": "Une rotation du personnel de {to}",
            "name": "la fidélisation des équipes",
            "cause": "{departures}Chez {label}, {talent}.{training}",
            "departures": "Environ {dep} salariés sont partis sur l'exercice. ",
            "training_low": " Avec {h} de formation par an, l'entreprise offre en outre peu de "
                            "perspectives visibles pour retenir ceux qui hésitent.",
            "training_high": " La formation ({h} par salarié) n'y suffit pas : les causes sont à "
                             "chercher du côté de la rémunération, des perspectives et du "
                             "management de proximité.",
            "csq": "Chaque départ coûte un recrutement, une période d'intégration et une part de "
                   "savoir-faire. À ce rythme, une partie de l'organisation est en permanence en "
                   "phase d'apprentissage, ce qui pèse sur la qualité de service et sur la charge "
                   "des équipes stables.",
            "horizon": "l'entreprise continuera de financer le renouvellement de ses équipes plutôt "
                       "que leur progression, et chaque départ deviendra plus coûteux à compenser",
            "action": "Conduire des entretiens de départ structurés et analyser la rotation par "
                      "métier, par site et par ancienneté pour localiser les causes.",
        },
        "skills": {
            "title": "{h} de formation par salarié et par an",
            "name": "le développement des compétences",
            "cause": "L'effort de formation reste faible au regard de la grille du diagnostic. Chez "
                     "{label}, {talent}.",
            "csq": "Des compétences qui ne sont pas entretenues deviennent un frein quand les "
                   "métiers changent — nouveaux équipements, outils numériques, exigences des "
                   "clients. La formation est aussi un levier de fidélisation dont l'entreprise se "
                   "prive.",
            "horizon": "l'écart de compétences se creusera au rythme de l'évolution des métiers, et "
                       "les transformations à venir manqueront de relais internes",
            "action": "Établir un plan de développement des compétences qui priorise les métiers "
                      "critiques et les compétences liées à la transition de l'activité.",
        },
        "mix": {
            "title": "{f} de femmes dans l'effectif",
            "name": "la mixité des équipes",
            "cause": "{context}",
            "generic": "Rien dans le profil du secteur ne rend ce déséquilibre inévitable : il "
                       "interroge les pratiques de recrutement et d'évolution.",
            "csq": "Au-delà de l'équité, c'est une question de vivier : l'entreprise recrute de fait "
                   "dans une partie seulement du marché du travail, au moment où les recrutements "
                   "se tendent. Ce repère est interne au diagnostic, non une obligation légale.",
            "horizon": "le déséquilibre se reproduira de lui-même, les candidates potentielles "
                       "lisant la composition des équipes avant de postuler",
            "action": "Mesurer la mixité par métier et par niveau, puis revoir les annonces, les "
                      "jurys de recrutement et les parcours des métiers les plus déséquilibrés.",
        },
        "carbon_intensity": {
            "title": "Une intensité carbone de {i} t CO2e par million d'euros",
            "name": "l'intensité carbone",
            "cause": "La grille sectorielle du diagnostic classe ce niveau comme {t} pour {label} : "
                     "l'écart ne tient donc pas seulement au métier, mais aux équipements, aux "
                     "procédés ou aux approvisionnements.{dominant}",
            "dominant": " L'essentiel des émissions mesurées relève du Scope {n} ({p}) : c'est là "
                        "que se joue la trajectoire.",
            "csq": "Cette intensité expose la marge aux hausses du coût de l'énergie et du carbone, "
                   "et fragilise la position de l'entreprise auprès des clients qui intègrent "
                   "l'empreinte de leurs fournisseurs dans leurs propres bilans.",
            "horizon": "l'écart avec les acteurs comparables qui auront engagé leur décarbonation se "
                       "creusera, et avec lui l'exposition commerciale et financière",
            "action": "Établir un plan de réduction chiffré sur les deux ou trois postes d'émissions "
                      "les plus lourds, avec pour chacun un responsable et un calendrier "
                      "d'investissement.",
        },
        "renewable": {
            "title": "{p} d'énergie renouvelable",
            "name": "l'approvisionnement énergétique",
            "cause": "L'énergie consommée reste très majoritairement d'origine fossile ou non "
                     "tracée.{scope}",
            "scope2": " Le Scope 2 représentant {p2} des émissions mesurées, l'origine de "
                      "l'électricité est ici un levier direct.",
            "scope1": " L'essentiel des émissions provenant toutefois des combustibles, ce levier "
                      "n'agira que sur une partie du bilan.",
            "csq": "L'entreprise reste exposée à la volatilité des prix de l'énergie et ne peut pas "
                   "faire valoir d'approvisionnement bas-carbone auprès de ses clients.",
            "horizon": "la part renouvelable resterait marginale et l'entreprise continuerait de "
                       "subir les variations de prix de l'énergie sans levier propre",
            "action": "Faire l'inventaire des contrats d'énergie et de leurs échéances, pour "
                      "préparer un approvisionnement renouvelable tracé au prochain renouvellement.",
        },
        "scope3": {
            "title": "Un bilan carbone sans Scope 3",
            "name": "la mesure de la chaîne de valeur",
            "cause": "{s3_missing}",
            "csq": "La stratégie climat repose donc sur une vision partielle : les priorités fixées "
                   "aujourd'hui pourraient se révéler mal ciblées une fois la chaîne de valeur "
                   "mesurée, et l'entreprise ne peut pas renseigner les clients qui lui demandent "
                   "sa part dans leur propre empreinte.",
            "horizon": "la trajectoire continuera d'être pilotée sur la partie la plus visible de "
                       "l'empreinte, avec le risque de concentrer l'effort sur des postes "
                       "secondaires",
            "action": "Chiffrer un premier Scope 3 sur les catégories les plus probables — {s3} —, "
                      "même par ratios monétaires, puis l'affiner avec les fournisseurs principaux.",
        },
        "carbon_unmeasured": {
            "title": "Aucun bilan d'émissions renseigné",
            "name": "la mesure des émissions",
            "cause": "Le dossier ne comporte ni total d'émissions ni répartition par scope.",
            "csq": "Sans cette base, aucune trajectoire ne peut être fixée ni suivie, et "
                   "l'entreprise ne peut pas répondre aux demandes de ses clients et de ses "
                   "financeurs sur son empreinte.",
            "horizon": "la question climatique restera sans réponse chiffrée, alors qu'elle figure "
                       "parmi les premières posées par les partenaires financiers et commerciaux",
            "action": "Établir un premier bilan des Scopes 1 et 2 à partir des factures d'énergie et "
                      "de carburant de l'exercice.",
        },
        "waste": {
            "title": "{p} des déchets valorisés",
            "name": "la valorisation des déchets",
            "cause": "Chez {label}, les gisements principaux sont en général {waste}. La majorité "
                     "part encore en élimination.",
            "csq": "C'est une dépense de traitement récurrente et une matière perdue, alors que des "
                   "filières de valorisation existent pour la plupart de ces flux.",
            "horizon": "les coûts d'élimination continueront de peser, sans contrepartie à faire "
                       "valoir auprès des clients attentifs à la circularité",
            "action": "Cartographier les flux de déchets par site et par filière, et renégocier les "
                      "contrats de collecte en intégrant le tri à la source.",
        },
        "steering": {
            "title_both": "Une démarche sans comité ni vérification externe",
            "title_committee": "Une démarche sans instance de pilotage",
            "title_audit": "Des données ESG non vérifiées",
            "name": "le pilotage de la démarche",
            "cause_both": "Ni comité de durabilité ni vérification externe : la démarche repose sur "
                          "quelques personnes plutôt que sur une organisation.",
            "cause_committee": "Aucun comité ne porte les arbitrages de durabilité : les sujets "
                               "remontent au fil de l'eau, sans lieu pour décider.",
            "cause_audit": "Les indicateurs publiés n'ont été contrôlés par aucun tiers.",
            "csq_both": "Les enjeux de ce diagnostic risquent de ne trouver aucune instance pour être "
                        "arbitrés, et les chiffres publiés restent exposés à la contestation des "
                        "banques, des investisseurs et des grands clients.",
            "csq_committee": "Les enjeux identifiés risquent de rester sans suite, faute d'instance "
                             "pour les arbitrer et en suivre la mise en œuvre.",
            "csq_audit": "Les chiffres publiés restent exposés à la contestation des partenaires "
                         "financiers et des grands clients, qui accordent davantage de crédit à une "
                         "information vérifiée.",
            "horizon": "la démarche restera dépendante de quelques personnes et difficile à rendre "
                       "crédible à l'extérieur",
            "action_committee": "Constituer un comité de durabilité, ou inscrire un point "
                                "trimestriel à l'ordre du jour du comité de direction.",
            "action_audit": "Faire revoir par un tiers deux ou trois indicateurs clés avant la "
                            "prochaine publication.",
        },
        "independence": {
            "title": "{p} d'administrateurs indépendants",
            "name": "l'indépendance du conseil",
            "cause": "Le conseil compte peu de membres extérieurs à la direction et à "
                     "l'actionnariat de référence.",
            "csq": "Il peut peiner à challenger les choix de la direction, en particulier sur les "
                   "arbitrages de long terme comme la durabilité, où un regard extérieur est le plus "
                   "utile.",
            "horizon": "les décisions structurantes continueront d'être prises sans contradiction "
                       "extérieure, ce que les partenaires financiers lisent comme un risque de "
                       "gouvernance",
            "action": "Définir le profil d'un ou deux administrateurs indépendants, en privilégiant "
                      "les compétences qui manquent aujourd'hui au conseil.",
        },
        "integrity": {
            "title": "Des incidents d'intégrité déclarés",
            "name": "l'intégrité et la sécurité de l'information",
            "cause": "{counts} sur l'exercice.",
            "csq_corruption": "Un cas de corruption engage la responsabilité de l'entreprise et de "
                              "ses dirigeants, et fragilise durablement l'accès aux financements et "
                              "à certains marchés.",
            "csq_breach": "Chaque violation de données entame la confiance des clients{core}.",
            "core": ", ce qui, pour {label}, touche directement le cœur de l'offre",
            "csq_ethics": "Chaque manquement éthique pose la question de la capacité du dispositif "
                          "de contrôle à prévenir la récidive.",
            "horizon": "chaque nouvel incident sera lu comme le signe d'un défaut de contrôle, avec "
                       "des conséquences croissantes sur la réputation et les relations d'affaires",
            "action": "Analyser les causes de chaque incident et vérifier que le dispositif "
                      "d'alerte, les contrôles internes et la sensibilisation couvrent les "
                      "situations rencontrées.",
        },
    },
    "en": {
        "safety": {
            "title": "An accident rate {r} times the national average",
            "name": "occupational safety",
            "cause": "For {label}, {safety}. With a frequency rate of {tf}, prevention has clearly "
                     "not yet caught up with this exposure{turnover}.",
            "turnover": ", all the more so as staff turnover ({to}) constantly renews the teams to "
                        "be trained",
            "csq": "The first cost is human. The second is operational — absences, replacements, "
                   "disrupted teams. The third is commercial: many buyers review their suppliers' "
                   "accident records before awarding a contract.",
            "horizon": "accidents will keep weighing on business continuity and on the ability to "
                       "recruit, and every serious accident will call the prevention policy into "
                       "question",
            "action": "Review each accident of the year and appoint, for each of the three main "
                      "risks, an owner and a dated prevention measure.",
        },
        "retention": {
            "title": "Staff turnover of {to}",
            "name": "staff retention",
            "cause": "{departures}For {label}, {talent}.{training}",
            "departures": "About {dep} employees left over the year. ",
            "training_low": " With {h} of training a year, the company also offers few visible "
                            "prospects to retain those who are hesitating.",
            "training_high": " Training ({h} per employee) is not enough: the causes lie in pay, "
                             "career prospects and front-line management.",
            "csq": "Every departure costs a recruitment, an onboarding period and a share of "
                   "know-how. At this pace, part of the organisation is permanently learning, which "
                   "weighs on service quality and on the workload of stable teams.",
            "horizon": "the company will keep paying to renew its teams rather than to develop "
                       "them, and every departure will become costlier to replace",
            "action": "Run structured exit interviews and analyse turnover by job, site and "
                      "seniority to pinpoint the causes.",
        },
        "skills": {
            "title": "{h} of training per employee per year",
            "name": "skills development",
            "cause": "The training effort remains low on the diagnostic's grid. For {label}, "
                     "{talent}.",
            "csq": "Skills that are not maintained become a brake when jobs change — new equipment, "
                   "digital tools, customer requirements. Training is also a retention lever the "
                   "company is forgoing.",
            "horizon": "the skills gap will widen as jobs evolve, and upcoming transformations will "
                       "lack internal champions",
            "action": "Draw up a skills development plan that prioritises critical jobs and the "
                      "skills tied to the business's transition.",
        },
        "mix": {
            "title": "{f} women in the workforce",
            "name": "workforce gender balance",
            "cause": "{context}",
            "generic": "Nothing in the sector's profile makes this imbalance inevitable: it raises "
                       "questions about recruitment and promotion practices.",
            "csq": "Beyond fairness, this is a talent-pool issue: the company in effect recruits "
                   "from only part of the labour market, just as hiring is getting harder. This "
                   "benchmark is internal to the diagnostic, not a legal requirement.",
            "horizon": "the imbalance will perpetuate itself, as potential candidates look at team "
                       "composition before applying",
            "action": "Measure gender balance by job and level, then review job ads, recruitment "
                      "panels and career paths in the most unbalanced jobs.",
        },
        "carbon_intensity": {
            "title": "A carbon intensity of {i} t CO2e per million euros",
            "name": "carbon intensity",
            "cause": "The diagnostic's sector grid rates this level as {t} for {label}: the gap is "
                     "therefore not only down to the trade, but to equipment, processes or "
                     "supplies.{dominant}",
            "dominant": " Most measured emissions fall under Scope {n} ({p}): this is where the "
                        "trajectory will be decided.",
            "csq": "This intensity exposes margins to rising energy and carbon costs, and weakens "
                   "the company's position with customers who include their suppliers' footprint "
                   "in their own inventories.",
            "horizon": "the gap with comparable players who have started decarbonising will widen, "
                       "and with it the commercial and financial exposure",
            "action": "Draw up a quantified reduction plan for the two or three heaviest emission "
                      "sources, each with an owner and an investment schedule.",
        },
        "renewable": {
            "title": "{p} renewable energy",
            "name": "energy supply",
            "cause": "The energy consumed remains overwhelmingly fossil-based or of untraced "
                     "origin.{scope}",
            "scope2": " With Scope 2 accounting for {p2} of measured emissions, the source of "
                      "electricity is a direct lever here.",
            "scope1": " Since most emissions come from fuels, however, this lever will only act on "
                      "part of the inventory.",
            "csq": "The company remains exposed to energy price volatility and cannot showcase a "
                   "low-carbon supply to its customers.",
            "horizon": "the renewable share would remain marginal and the company would keep "
                       "absorbing energy price swings without a lever of its own",
            "action": "Inventory energy contracts and their expiry dates, to prepare a traced "
                      "renewable supply at the next renewal.",
        },
        "scope3": {
            "title": "A carbon inventory without Scope 3",
            "name": "value-chain measurement",
            "cause": "{s3_missing}",
            "csq": "The climate strategy therefore rests on a partial view: today's priorities may "
                   "prove poorly targeted once the value chain is measured, and the company cannot "
                   "inform customers who ask for its share of their own footprint.",
            "horizon": "the trajectory will keep being steered on the most visible part of the "
                       "footprint, with the risk of focusing effort on secondary sources",
            "action": "Estimate a first Scope 3 on the most likely categories — {s3} —, even with "
                      "spend-based ratios, then refine it with the main suppliers.",
        },
        "carbon_unmeasured": {
            "title": "No emissions inventory reported",
            "name": "emissions measurement",
            "cause": "The file contains neither total emissions nor a breakdown by scope.",
            "csq": "Without this baseline, no trajectory can be set or tracked, and the company "
                   "cannot answer its customers' and financiers' questions about its footprint.",
            "horizon": "the climate question will remain without a quantified answer, although it "
                       "is among the first raised by financial and business partners",
            "action": "Produce a first Scope 1 and 2 inventory from the year's energy and fuel "
                      "invoices.",
        },
        "waste": {
            "title": "{p} of waste recovered",
            "name": "waste recovery",
            "cause": "For {label}, the main streams are usually {waste}. Most of it is still sent "
                     "for disposal.",
            "csq": "This is a recurring treatment expense and lost material, although recovery "
                   "channels exist for most of these streams.",
            "horizon": "disposal costs will keep weighing, with nothing to show customers who care "
                       "about circularity",
            "action": "Map waste streams by site and channel, and renegotiate collection contracts "
                      "to include sorting at source.",
        },
        "steering": {
            "title_both": "An approach with neither committee nor external assurance",
            "title_committee": "An approach without a steering body",
            "title_audit": "ESG data not externally assured",
            "name": "steering of the approach",
            "cause_both": "Neither a sustainability committee nor external assurance: the approach "
                          "rests on a few people rather than on an organisation.",
            "cause_committee": "No committee handles sustainability trade-offs: issues come up ad "
                               "hoc, with no forum to decide.",
            "cause_audit": "The published indicators have not been checked by any third party.",
            "csq_both": "The issues in this diagnostic may find no body to decide on them, and the "
                        "published figures remain open to challenge by banks, investors and large "
                        "customers.",
            "csq_committee": "The issues identified may go unaddressed, for lack of a body to "
                             "decide on them and monitor their implementation.",
            "csq_audit": "The published figures remain open to challenge by financial partners and "
                         "large customers, who give more credit to verified information.",
            "horizon": "the approach will remain dependent on a few people and hard to make "
                       "credible externally",
            "action_committee": "Set up a sustainability committee, or add a quarterly item to the "
                                "executive committee's agenda.",
            "action_audit": "Have a third party review two or three key indicators before the next "
                            "publication.",
        },
        "independence": {
            "title": "{p} independent directors",
            "name": "board independence",
            "cause": "The board has few members from outside management and the reference "
                     "shareholders.",
            "csq": "It may struggle to challenge management's choices, especially on long-term "
                   "trade-offs such as sustainability, where an outside view is most useful.",
            "horizon": "structural decisions will keep being taken without outside challenge, which "
                       "financial partners read as a governance risk",
            "action": "Define the profile of one or two independent directors, favouring the skills "
                      "the board currently lacks.",
        },
        "integrity": {
            "title": "Integrity incidents reported",
            "name": "integrity and information security",
            "cause": "{counts} over the year.",
            "csq_corruption": "A corruption case engages the liability of the company and its "
                              "executives, and durably weakens access to financing and to certain "
                              "markets.",
            "csq_breach": "Every data breach erodes customer trust{core}.",
            "core": ", which, for {label}, goes to the heart of the offer",
            "csq_ethics": "Every ethics breach raises the question of whether controls can prevent "
                          "a recurrence.",
            "horizon": "every new incident will be read as a sign of weak controls, with growing "
                       "consequences for reputation and business relationships",
            "action": "Analyse the causes of each incident and check that the whistleblowing "
                      "channel, internal controls and awareness training cover the situations "
                      "encountered.",
        },
    },
}

STRENGTHS = {
    "fr": {
        "safety_good": ("Un taux de fréquence de {tf}, bien en dessous de la moyenne nationale",
                        "la maîtrise des risques professionnels",
                        "Un acquis à protéger et à faire valoir auprès des clients et des "
                        "candidats."),
        "renewable_good": ("{p} d'énergie renouvelable", "un approvisionnement énergétique déjà "
                           "décarboné", "Un approvisionnement largement renouvelable, à sécuriser "
                           "par des contrats pluriannuels."),
        "intensity_good": ("Une intensité carbone {t} pour le secteur", "une intensité carbone "
                           "favorable", "Un argument auprès des clients qui mesurent l'empreinte "
                           "de leurs fournisseurs."),
        "mix_good": ("{f} de femmes dans l'effectif", "des équipes mixtes",
                     "Un vivier équilibré, dont il reste à vérifier la traduction dans "
                     "l'encadrement."),
        "training_good": ("{h} de formation par salarié", "l'investissement dans les compétences",
                          "Un effort réel, qui gagnerait à être relié aux parcours d'évolution."),
        "retention_good": ("Une rotation du personnel de {to}", "la stabilité des équipes",
                           "Des équipes stables, gage de qualité de service et de transmission "
                           "des savoir-faire."),
        "steering_good": ("Un comité de durabilité et des données vérifiées",
                          "un dispositif de pilotage complet",
                          "Un dispositif qui peut désormais porter des objectifs chiffrés."),
        "independence_good": ("{p} d'administrateurs indépendants", "un conseil indépendant",
                              "Un conseil en mesure de challenger la direction sur les "
                              "arbitrages de long terme."),
        "integrity_clean": ("Aucun incident d'intégrité déclaré", "l'absence d'incident "
                            "d'intégrité", "Un résultat à adosser à un dispositif d'alerte "
                            "connu pour qu'il soit probant."),
    },
    "en": {
        "safety_good": ("A frequency rate of {tf}, well below the national average",
                        "control of occupational risks",
                        "An asset to protect and to showcase to customers and candidates."),
        "renewable_good": ("{p} renewable energy", "an already decarbonised energy supply",
                           "A largely renewable supply, to be secured through multi-year "
                           "contracts."),
        "intensity_good": ("A {t} carbon intensity for the sector", "a favourable carbon "
                           "intensity", "An argument with customers who measure their "
                           "suppliers' footprint."),
        "mix_good": ("{f} women in the workforce", "gender-balanced teams",
                     "A balanced talent pool, whose reflection in management remains to be "
                     "checked."),
        "training_good": ("{h} of training per employee", "investment in skills",
                          "A real effort, which would benefit from being linked to career "
                          "paths."),
        "retention_good": ("Staff turnover of {to}", "team stability",
                           "Stable teams, a guarantee of service quality and know-how transfer."),
        "steering_good": ("A sustainability committee and assured data",
                          "a complete steering framework",
                          "A framework that can now carry quantified targets."),
        "independence_good": ("{p} independent directors", "an independent board",
                              "A board able to challenge management on long-term trade-offs."),
        "integrity_clean": ("No integrity incident reported", "the absence of integrity "
                            "incidents", "A result to be backed by a known whistleblowing "
                            "channel to be conclusive."),
    },
}

LINKS = {
    "fr": {
        "safety_steering": "La sinistralité et l'absence de comité de durabilité se répondent : "
                           "la sécurité au travail, premier enjeu social du dossier, n'a pas "
                           "d'instance de gouvernance où être suivie au bon niveau.",
        "climate_audit": "Les enjeux climatiques reposent sur des chiffres qu'aucun tiers n'a "
                         "vérifiés : avant d'y adosser une trajectoire, il faudra en fiabiliser la "
                         "mesure.",
        "retention_mix": "Rotation et déséquilibre de l'effectif se cumulent : l'entreprise puise "
                         "dans un vivier restreint des salariés qu'elle retient mal, ce qui rend "
                         "chaque départ plus difficile à remplacer.",
        "retention_skills": "Rotation élevée et formation limitée s'entretiennent l'une l'autre : "
                            "c'est un même chantier de ressources humaines, qui gagne à être "
                            "traité d'un seul tenant.",
        "steering_ready": "Le dispositif de pilotage existe déjà : l'enjeu est qu'il se saisisse "
                          "explicitement de {name}, premier sujet de ce diagnostic.",
        "intensity_scope3": "L'intensité carbone favorable ne porte que sur les scopes mesurés : "
                            "l'avantage reste à confirmer une fois la chaîne de valeur prise en "
                            "compte.",
        "capex_climate": "Les investissements déclarés alignés sur la Taxonomie ({p} des CapEx) "
                         "montrent qu'une partie de l'effort de transition est déjà engagée : le "
                         "plan de réduction peut s'y adosser.",
        "safety_skills": "Sinistralité et faible effort de formation vont souvent de pair : "
                         "l'accueil sécurité et les recyclages sont les premières heures de "
                         "formation à sanctuariser.",
    },
    "en": {
        "safety_steering": "Accident levels and the lack of a sustainability committee are "
                           "linked: occupational safety, the file's first social issue, has no "
                           "governance body to monitor it at the right level.",
        "climate_audit": "The climate issues rest on figures no third party has verified: before "
                         "building a trajectory on them, their measurement must be made reliable.",
        "retention_mix": "Turnover and workforce imbalance add up: the company draws from a narrow "
                         "talent pool employees it struggles to retain, making every departure "
                         "harder to replace.",
        "retention_skills": "High turnover and limited training feed each other: this is a single "
                            "HR workstream, best tackled as a whole.",
        "steering_ready": "The steering framework already exists: the challenge is for it to "
                          "explicitly take up {name}, the first issue of this diagnostic.",
        "intensity_scope3": "The favourable carbon intensity only covers the measured scopes: the "
                            "advantage remains to be confirmed once the value chain is included.",
        "capex_climate": "The investments reported as Taxonomy-aligned ({p} of CapEx) show that "
                         "part of the transition effort is already under way: the reduction plan "
                         "can build on them.",
        "safety_skills": "Accident levels and a low training effort often go together: safety "
                         "induction and refresher courses are the first training hours to "
                         "protect.",
    },
}

T = {
    "fr": {
        "overview": "Diagnostic d'ensemble",
        "cause_label": "Pourquoi",
        "csq_label": "Ce que cela entraîne",
        "profile_title": "Le profil qui se dégage",
        "issues_title": "Les enjeux structurants",
        "links_title": "Les liens entre piliers",
        "profile_counts": "Le dossier de {name} fait ressortir {ni} et {ns}.",
        "n_issue": ("aucun enjeu marqué", "un enjeu", "{n} enjeux"),
        "n_strength": ("aucun point d'appui marqué", "un point d'appui", "{n} points d'appui"),
        "concentrated": "Les fragilités se concentrent sur le pilier {p} : {names}. C'est là que "
                        "le plan d'action doit porter en premier.",
        "spread": "Les fragilités se répartissent entre plusieurs piliers — {names} —, ce qui "
                  "appelle un plan d'ensemble plutôt qu'un chantier unique.",
        "no_issue": "Aucune fragilité majeure ne ressort des indicateurs renseignés : l'enjeu est "
                    "désormais de consolider les acquis et de les documenter.",
        "strengths": "Les points d'appui sont {names} : ce sont eux qui donnent de la crédibilité "
                     "au plan d'action.",
        "partial": "La lecture reste partielle : {filled} des {total} indicateurs suivis sont "
                   "renseignés, et plusieurs conclusions devront être confirmées au prochain "
                   "exercice.",
        "issues_intro": "Les enjeux ci-dessous sont classés par gravité, telle que la mesurent les "
                        "écarts à la grille du diagnostic et aux références disponibles.",
        "retain_title": "Ce que nous retenons",
        "retain_strength": "À capitaliser : {title}. {text}",
        "retain_issue": "À traiter en priorité : {title}. {csq}",
        "retain_link": "À relier : {text}",
        "horizon_title": "Si rien ne change d'ici {ty}",
        "horizon_one": "Pour {name}, {text}.",
        "horizon_intro": "Sans action, les tendances observées cette année se prolongeront.",
        "first_title": "Les 90 premiers jours",
        "first_intro": "Ces décisions permettent d'engager le plan sans attendre les chantiers "
                       "structurants :",
        "first_none": "Aucun enjeu majeur n'imposant d'action immédiate, les 90 premiers jours "
                      "peuvent être consacrés à fiabiliser les données et à fixer des objectifs "
                      "chiffrés.",
        "pillars": {"env": "environnemental", "social": "social", "gov": "de gouvernance"},
    },
    "en": {
        "overview": "Overall diagnosis",
        "cause_label": "Why",
        "csq_label": "What it leads to",
        "profile_title": "The emerging profile",
        "issues_title": "The structural issues",
        "links_title": "Links between pillars",
        "profile_counts": "{name}'s file brings out {ni} and {ns}.",
        "n_issue": ("no marked issue", "one issue", "{n} issues"),
        "n_strength": ("no marked strength", "one strength", "{n} strengths"),
        "concentrated": "Weaknesses are concentrated in the {p} pillar: {names}. This is where the "
                        "action plan should focus first.",
        "spread": "Weaknesses are spread across several pillars — {names} —, which calls for an "
                  "overall plan rather than a single workstream.",
        "no_issue": "No major weakness emerges from the reported indicators: the challenge now is "
                    "to consolidate and document what has been achieved.",
        "strengths": "The strengths are {names}: they are what give the action plan credibility.",
        "partial": "The reading remains partial: {filled} of the {total} tracked indicators are "
                   "reported, and several conclusions will need confirming next year.",
        "issues_intro": "The issues below are ranked by severity, as measured by the gaps to the "
                        "diagnostic's grid and to the available references.",
        "retain_title": "Key takeaways",
        "retain_strength": "To build on: {title}. {text}",
        "retain_issue": "To address first: {title}. {csq}",
        "retain_link": "To connect: {text}",
        "horizon_title": "If nothing changes by {ty}",
        "horizon_one": "For {name}, {text}.",
        "horizon_intro": "Without action, this year's trends will continue.",
        "first_title": "The first 90 days",
        "first_intro": "These decisions get the plan started without waiting for the structural "
                       "workstreams:",
        "first_none": "With no major issue requiring immediate action, the first 90 days can be "
                      "used to make the data reliable and set quantified targets.",
        "pillars": {"env": "environmental", "social": "social", "gov": "governance"},
    },
}
