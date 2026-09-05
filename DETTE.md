# Dette d'exactitude réglementaire / métier

Constats trouvés en cours de travail, volontairement NON corrigés au moment
où ils ont été trouvés (hors périmètre du chantier en cours à ce moment-là),
consignés ici pour ne pas être perdus. À traiter en bloc, après le socle de
clauses (`backend/bands.py`, `backend/composer.py`, `backend/clauses/`) et
la rédaction des clauses elles-mêmes.

## 0. ÉVOLUTION PRIORITAIRE — donner un contenu propre à la section Positionnement

- **Contexte** : la comparaison à une référence sectorielle inventée a été
  retirée (chantier du 2026-09-02). La section « Positionnement » affiche
  désormais un classement **interne** des trois piliers — vrai, mais proche
  d'un doublon du tableau de bord de la page 2.
- **La vraie valeur d'un outil de suivi pluriannuel** : comparer l'entreprise
  **à elle-même**, exercice après exercice. La donnée existe déjà
  (`score_history` sur `ESGRequest`, déjà utilisée par la page trajectoire).
- **À faire** : reconstruire la section sur cette comparaison temporelle
  (évolution par pilier, écart au précédent exercice, tendance). Sourcé,
  vrai, et sans doublon. Limite connue : rien à afficher au premier
  exercice — prévoir le repli sur le classement interne actuel.

## 0bis. ÉTAPE B — collecter les objectifs et engagements du client

Le chantier du 2026-09-03 (étape A) a **retiré** tous les engagements que
l'outil fabriquait : trajectoire « -42 % à 2030 (SBTi) », cibles par pilier
calculées par `uplift()`, conformité ESRS E1-4 déduite de cet objectif,
respect du DNSH et des garanties minimales, alignement SFDR / ISO / six ODD.
Le rapport dit désormais que ces objectifs **restent à définir**.

**Étape B — les rendre saisissables.** Tant qu'elle n'est pas faite, le
rapport ne peut rien affirmer sur les engagements du client.

Périmètre chiffré au diagnostic :

| Emplacement | Volume actuel | Ajout estimé |
|---|---|---|
| `backend/models.py` | 51 champs | +5 à 7 (cible % / année de base / année cible / périmètre scopes / cadre revendiqué / certifications ISO / ODD retenus) + validateurs |
| Wizard React (`frontend/src/components/steps/`) | 5 steps | un **6ᵉ step « Objectifs & engagements »** plutôt que gonfler `StepEnvironmental` (77 l.) |
| `frontend/src/demoData.js` | — | valeurs de démonstration |
| `backend/questionnaire_generator.py` | 45 champs | +5 à 7 entrées |
| `backend/import_data.py` | 40 mappings CSV | +5 à 7 mappings + alias |
| Les 5 livrables | — | lecture conditionnelle : cible saisie → citée comme engagement du client ; absente → texte « à définir » |
| Tests | 127 | cas « avec cible » / « sans cible » sur chaque livrable |

**Coût caché identifié** : les certifications et les ODD sont des listes
**multi-sélection**, ce que le wizard ne sait pas faire aujourd'hui (il n'a
que des champs numériques et des booléens). C'est le vrai poste de travail
de l'étape B, pas les champs eux-mêmes.

**Ordre impératif** : A avant B. Faire B d'abord aurait laissé les
affirmations fausses en production le temps du chantier de saisie.

## 0ter. Mapping ODD dérivé des indicateurs réellement collectés

Les six ODD affichés (7, 8, 10, 12, 13, 16) étaient identiques pour tout
dossier et ont été retirés. Une version défendable reste possible : dériver
les ODD **des indicateurs effectivement collectés** — par exemple ODD 13 si
un bilan GES existe, ODD 7 si la part d'énergie renouvelable est renseignée,
ODD 5 si la mixité l'est. Le lien serait alors traçable jusqu'à la donnée,
et le rapport dirait « thèmes couverts par les indicateurs collectés »
plutôt que « l'organisation contribue aux ODD ».

À traiter avec l'étape B, ou séparément — cela ne demande aucun nouveau
champ, seulement une table de correspondance indicateur → ODD et une
formulation qui n'affirme pas une contribution.

## 0quater. Patron « liste noire sur un mot nu » — trois faux positifs, chantier dédié

- **Constat** : les tests de gel bannissent une chaîne dans le texte
  généré. Quand la chaîne bannie est une **formulation fautive**
  (« a conduit une analyse de double matérialité »), le test vise juste.
  Quand c'est un **mot nu ou une sous-chaîne générique**, il interdit
  aussi les emplois légitimes — y compris ceux qui **nient**
  l'affirmation, c'est-à-dire exactement la correction recherchée.
- **Trois occurrences déjà déclenchées** :
  1. « double matérialité » — l'expression reste légitime pour s'en
     démarquer ; d'où la scission `MARQUEURS_METHODO_INVENTEE` /
     `AFFIRMATIONS_INTERDITES`.
  2. « sector reference » — la note méthodologique EN l'emploie pour
     nier la comparaison ; d'où le NB en tête de
     `MARQUEURS_BENCHMARK_INVENTE` et le retrait du marqueur nu.
  3. « déclarée » — figure légitimement dans la note méthodologique
     (« parts déclarées comme alignées à la Taxonomie UE ») ; le test
     bannit désormais « déclarée engagée » / « déclarées engagées ».
- **Ce n'est plus un accident** : trois fois le même patron, corrigé
  trois fois après coup, chaque fois au moment où le test a cassé sur du
  texte juste. **À traiter comme un chantier dédié**, pas au cas par cas :
  passer en revue toutes les listes noires, remplacer chaque marqueur
  générique par la formulation qu'il visait, et poser la règle
  (« bannir une affirmation, jamais un mot »).
- **Inventaire des marqueurs encore exposés** : établi le 2026-09-05, non
  corrigé — voir la section « Marqueurs génériques restants » ci-dessous.

### Périmètre exact (corrigé le 2026-09-05)

Le premier chiffrage annonçait « 5 listes, 65 marqueurs ». **C'est faux :
il y a 6 listes et 75 marqueurs.**

| Liste | Marqueurs | Test bout-en-bout |
|---|---|---|
| `ENGAGEMENTS_FABRIQUES` | 23 | `test_aucun_engagement_fabrique_dans_les_livrables` |
| `MARQUEURS_BENCHMARK_INVENTE` | 24 | `test_aucune_comparaison_sectorielle_dans_les_livrables` |
| `ATTRIBUTIONS_LEGALES_FAUSSES` (`:557`) | 10 | `test_aucune_attribution_legale_fausse_dans_les_livrables` |
| `MARQUEURS_METHODO_INVENTEE` | 8 | `test_materialite_absente_des_livrables_generes` |
| `MARQUEURS_COUVERTURE_ESRS` | 6 | (partagé avec le test benchmark) |
| `AFFIRMATIONS_INTERDITES` | 4 | (partagé avec le test matérialité) |
| **Total** | **75** | **4 tests bout-en-bout** |

`ATTRIBUTIONS_LEGALES_FAUSSES` et son test avaient été **omis** de
l'inventaire initial : 65 était la somme des cinq autres listes.

À quoi s'ajoutent ~19 chaînes bannies en **assertions isolées**, hors
liste (`preuve`, `proof`, `42`, `module`, `optionnel`, `EAU`, `VSME/`,
`(s)`, `http://`, `automatiq`, `de EcoGroup`…).

**Doublon** : `"Rixain"` est banni **deux fois** — dans
`ATTRIBUTIONS_LEGALES_FAUSSES` (`:558`) et en assertion isolée (`:629`).

**Le patron d'assertion positive existe déjà** et n'est pas à inventer :
`REMPLACEMENTS_ATTENDUS` (`:462`, exige que le texte de remplacement soit
présent après un retrait) et `DIVULGATION_GRILLE_INTERNE` (exige que la
nature interne de la grille reste divulguée). Toute réécriture de
marqueur doit reprendre ce patron plutôt qu'en créer un autre.

### Classification en trois familles (validée le 2026-09-05)

La forme du garde-fou dépend de ce qui sépare la faute de l'énoncé
légitime :

- **forme** — la chaîne visée est un **artefact**, pas du vocabulaire
  (`(s)` de publipostage, `http://`, `automatiq`, `de EcoGroup`,
  `VSME/`, `EAU`). ~8 chaînes, toutes en assertions isolées : **aucune
  des six listes ne relève de cette famille**. Rien à changer sur le
  principe.
- **formulation** — la faute et l'énoncé légitime **diffèrent par la
  phrase**. Le patron validé s'applique : bannir la formulation fautive,
  avec une assertion positive quand un remplacement doit rester présent.
  - **27 bien écrits** : `AFFIRMATIONS_INTERDITES` (4),
    `MARQUEURS_COUVERTURE_ESRS` (6), les 11 tournures comparatives de
    `BENCHMARK`, 4 de `METHODO`, « ancrée dans les ODD » / « anchored in
    the UN SDGs ». Rien à faire.
  - **23 mal écrits** : 13 fragments génériques de `BENCHMARK`
    (`de son secteur`, `référence sectorielle`, `standards sectoriels`,
    `mid-market`, `leaders mondiaux`, `reference base for`…), 4 de
    `METHODO` (`IRO-1`, `SBM-3`, `irrémédiab`, `irremediab`), et les 6 de
    `LEGALES` — liste explicite, pour lever toute ambiguïté : `Rixain`,
    `objectif légal 40`, `legal 40% target`,
    `40 % de femmes dans les effectifs`, `40% women in the workforce`,
    `transparence salariale UE`. **Les quatre marqueurs `objectif 40%` /
    `target 40%` / `cible 40 %` / `40% target` n'en font PAS partie** :
    ils sont comptés en provenance ci-dessous.
- **provenance** — la faute et l'énoncé légitime sont **identiques au mot
  près** et ne se distinguent que par **l'existence de la donnée en
  amont**. Aucun test textuel ne peut trancher. **25 marqueurs** :

| Marqueurs | Nb | Donnée amont qui les rendrait légitimes |
|---|---|---|
| `SBTi`, `Science Based Targets`, `trajectoire SBTi`, `SBTi pathway` | 4 | Cadre revendiqué (étape B) |
| `-42 %`, `-42%`, `réduction de 42`, `42% reduction` | 4 | Cible % + année de base + année cible (étape B) |
| `SFDR`, `ISO 14001`, `ISO 26000` | 3 | Certifications ISO / cadre revendiqué (étape B) |
| `ODD 7`, `ODD 8`, `SDG 7`, `SDG 8` | 4 | ODD retenus (étape B) ou dérivation depuis les indicateurs (§ 0ter) |
| `dans le respect du principe DNSH`, `in compliance with the DNSH principle` | 2 | Cadre revendiqué (étape B) |
| `Cadres de Référence & Alignement ODD`, `Reporting Frameworks & SDG Alignment` | 2 | Titres de section, légitimes dès que la section a une donnée à afficher |
| `Chaque pilier fait l'objet d'une cible`, `Each pillar is assigned a progression target` | 2 | Cibles par pilier (étape B) |
| `objectif 40%`, `target 40%`, `cible 40 %`, `40% target` | 4 | Objectif de parité **déclaré par le client** (étape B) : c'est un fait, et c'est même ce que la recommandation « Définir des objectifs chiffrés de parité » demande au client de produire. Venaient de `ATTRIBUTIONS_LEGALES_FAUSSES` ; reclassement **déjà appliqué** au commit `1dec462` — les totaux 25 / 23 le reflètent déjà, ne pas le compter une seconde fois. Sortis de cette liste en passe 2 vers `PROVENANCE_SANS_DONNEE_COLLECTEE`, toujours assertés en attendant le différentiel. |

### Règle d'admission : 1 garde-fou prouvé sur 76

**Aucun des 75 marqueurs n'a jamais échoué sur la faute qu'il vise.** Ils
ont tous été écrits **après** la suppression de la faute : ils sont nés
verts et n'ont jamais rien discriminé. Le seul garde-fou du dépôt prouvé
par mutation est `test_sommaire_numerotation_et_pagination` (§ 0sexies,
commit `7eaeda4`), muté volontairement au moment de son écriture.

**Score honnête : 1 sur 76.**

Règle posée pour la suite : *un garde-fou n'est acquis qu'après avoir
échoué au moins une fois sur la faute qu'il vise.* Régime d'application
retenu, par famille — **non appliqué à ce jour** :

- **provenance** : auto-prouvant, la moitié « avec la donnée » du test
  différentiel *est* la mutation. Coût permanent nul.
- **formulation** : méta-test paramétré passant chaque marqueur dans un
  texte de synthèse qui le contient, pour vérifier que l'assertion casse.
  Ne génère aucun livrable. Limite connue : prouve que l'assertion se
  déclenche, pas que le générateur pourrait produire la chaîne.
- **forme** : mutation manuelle une fois, SHA d'échec tracé en
  commentaire.


### Passe 2 (2026-09-05) — 19 marqueurs de formulation réécrits

Chaque fragment générique a été remplacé par la **formulation réellement
fautive**, retrouvée dans les lignes supprimées du dépôt
(`git log -p -S` sur `26b3c75`, `33fae44`, `d9a079a`, `1b03075`).

- `MARQUEURS_BENCHMARK_INVENTE` — les 13 fragments (`de son secteur`,
  `référence sectorielle`, `standards sectoriels`, `mid-market`,
  `marché PME/ETI`, `leaders mondiaux`, `reference base for`…) sont
  devenus des comparatifs explicites (`dépasse la référence sectorielle`,
  `en tête de son secteur`, `exceeding recognised sector standards`…).
- `MARQUEURS_METHODO_INVENTEE` — `IRO-1` / `SBM-3` / `irrémédiab` visent
  désormais la revendication (`(IRO-1, SBM-3)`,
  `aux normes ESRS 1/ESRS 2`, `× irrémédiabilité`). **Citer un code ESRS
  réel est redevenu possible**, y compris pour dire qu'on ne couvre pas
  la norme.
- `ATTRIBUTIONS_LEGALES_FAUSSES` — `Rixain` nu est remplacé par
  `conforme loi Rixain` / `objectif Rixain` : la loi, qui est **réelle**,
  peut de nouveau être citée correctement. Le doublon `:558` / `:629` est
  résorbé, l'assertion isolée ayant disparu avec la réécriture.
- **`"preuve"`** — le ban du mot nu sur 16 pages est remplacé par
  `FORMULATIONS_DE_VERIFICATION` (`preuve à l'appui`, `action prouvée`,
  `sur justificatifs`, `vérifié par le cabinet`, équivalents EN),
  **restreintes au texte de l'encart**, avec l'assertion positive
  conservée. Régime FR et EN désormais identique — l'un balayait 16 pages,
  l'autre une seule chaîne.

**Le faux positif du § 4bis est levé** : `marché PME/ETI` ayant été
réécrit, l'exclusion de la lettre de mission n'avait plus d'objet. Elle a
été retirée et le livrable est désormais couvert par les tests de gel.

**Deux marqueurs NON réécrits, et c'est signalé** :
`40 % de femmes dans les effectifs` et `40% women in the workforce`. La
faute visée n'est pas une phrase mais une **ligne du tableau d'écarts
réglementaires** (la parité de l'effectif présentée comme une exigence).
Aucune reformulation textuelle ne distingue ce libellé d'un objectif que
le client déclarerait lui-même — et la faute structurelle est déjà
couverte par le test qui interdit cette ligne dans les écarts. Laissés en
l'état.

**Règle d'admission appliquée** : les 29 marqueurs réécrits passent par
`test_chaque_marqueur_reecrit_casse_sur_sa_faute`, qui les confronte à la
phrase historique qu'ils visent, doublé de
`test_aucun_marqueur_reecrit_ne_mord_le_texte_produit` (FR/EN). Aucun
marqueur mort, aucun qui morde le texte vivant. Coût : 0,30 s.
Le score du § « règle d'admission » passe donc de **1 sur 76 à 30 sur 76**.

### Marqueurs génériques restants (inventaire du 2026-09-05, NON corrigés)

| Marqueur | Où | Portée | Pourquoi il est exposé |
|---|---|---|---|
| `"preuve"` / `"proof"` | `test_suite.py:204,216,246` | **PDF entier** | Mot nu, et sous-chaîne d'« épreuve ». **Mord le vocabulaire de mise en garde que le projet emploie partout ailleurs** : la ligne de conduite constante depuis le 2026-09-01 est que l'outil *reporte une déclaration et ne prouve rien* — mais toute phrase qui le dit (« le cabinet n'a pas collecté d'éléments de preuve », « aucune preuve n'a été demandée ») casse le test. Le marqueur interdit donc exactement l'énoncé qu'il défend. Le plus exposé de la liste. |
| `"de son secteur"` | `MARQUEURS_BENCHMARK_INVENTE` | texte + 4 livrables | Fragment générique : « les obligations réglementaires de son secteur » est vrai et non comparatif. |
| `"référence sectorielle"` | idem | idem | Banni nu en FR alors que son équivalent EN « sector reference » est explicitement épargné pour pouvoir **nier** la comparaison. Asymétrie FR/EN non justifiée. |
| `"standards sectoriels"` / `"sector standards"` | idem | idem | Les normes sectorielles ESRS sont un objet réglementaire réel ; le marqueur interdit de les citer. |
| `"mid-market"` / `"marché PME/ETI"` / `"SME/mid-cap market"` | idem | idem | Faux positif **déjà connu et documenté** (§ 4bis) : contenu en restreignant la portée du test à cinq livrables plutôt qu'en corrigeant le marqueur. |
| `"leaders mondiaux"` / `"pratiques du secteur"` / `"reference base for"` | idem | idem | Fragments génériques, aucune affirmation comparative en propre. |
| `"IRO-1"` / `"SBM-3"` | `MARQUEURS_METHODO_INVENTEE` | texte materiality + 3 livrables | Codes ESRS réels : interdit de citer la norme même pour dire qu'on ne la couvre pas. |
| `"irrémédiab"` / `"irremediab"` | idem | idem | Radicaux tronqués : bloqueraient « le caractère irrémédiable n'a pas été coté ». |
| `"Rixain"` | `test_suite.py:629` | texte gouvernance | Loi **réelle**, avec des quotas réels sur les cadres dirigeants. Le marqueur interdit de la citer correctement — il visait une mauvaise attribution, pas la loi. |
| `"42"` | `test_suite.py:504` | `str(lignes[0])` | Bannit une paire de chiffres : casse sur toute valeur contenant 42, et ne voit pas la cible « -42 % » si elle réapparaît sur une autre ligne. Faux positif **et** faux négatif. |
| `"module"` / `"optionnel"` | `test_suite.py:321-322` | note d'audit | VSME est structuré en modules (Basic / Comprehensive) : le marqueur interdit de décrire correctement le référentiel. |
| `"EAU"` | `test_bands.py:413` | section composée | Sous-chaîne de NIVEAU, BUREAU, RÉSEAU, TABLEAU. Contenu aujourd'hui par des clauses de test maîtrisées, structurellement fragile. |
| `"VSME/"` | `test_suite.py:292` | `row["ref"]` | Bannit une forme de référence ; à confirmer contre les refs VSME réelles (B1-B11, C1-C9). |
| `"SBTi"` / `"Science Based Targets"` / `"trajectoire SBTi"` | `ENGAGEMENTS_FABRIQUES` | 4 livrables | Nom nu d'une initiative réelle. Interdit l'énoncé honnête « l'entreprise n'a pas d'objectif validé SBTi ». **Collision programmée — voir ci-dessous.** |
| `"SFDR"` / `"ISO 14001"` / `"ISO 26000"` | idem | idem | Acronymes nus de référentiels réels : interdit de les citer, y compris pour dire qu'ils ne sont pas revendiqués. **Collision programmée.** |
| `"ODD 7"` / `"ODD 8"` / `"SDG 7"` / `"SDG 8"` | idem | idem | Références nues à des ODD réels. **Collision programmée.** |

**Deux collisions programmées avec des chantiers déjà inscrits ici.** Ce
ne sont pas des risques théoriques : les marqueurs casseront le jour où
ces chantiers démarreront, et c'est le test qui aura tort.

1. **`"SBTi"` / `"Science Based Targets"` × étape B (§ 0bis).** L'étape A
   a retiré la trajectoire « -42 % à 2030 (SBTi) » que l'outil
   fabriquait, et a banni le terme avec l'affirmation. Mais l'étape B
   rendra une cible **saisissable par le client** : dès qu'un consultant
   renseignera un objectif validé SBTi, le livrable devra le citer comme
   engagement du client — et le test de gel le refusera. Le marqueur
   visait un objectif *inventé par l'outil*, pas un objectif *déclaré par
   l'entreprise* ; il ne sait pas faire la différence.
2. **`"ISO 14001"` / `"ISO 26000"` / `"ODD n"` × étape B et § 0ter.**
   L'étape B prévoit explicitement de collecter les **certifications
   ISO** et les **ODD retenus** (champs multi-sélection, cf. le tableau
   du § 0bis). Le § 0ter prévoit, lui, de **dériver les ODD des
   indicateurs réellement collectés** — un mapping défendable imprimerait
   « ODD 7 » dès qu'une part d'énergie renouvelable est renseignée. Les
   trois marqueurs interdisent ces deux sorties, qui sont pourtant la
   forme *corrigée* de ce que l'étape A a retiré.

**Conséquence pour l'ordonnancement** : le chantier « listes noires »
n'est pas seulement du nettoyage, il est **bloquant pour l'étape B**. Le
faire après l'étape B garantit de découvrir les collisions sous forme de
tests rouges au milieu d'un chantier de saisie.

**Contrôlés et jugés SAINS** (à ne pas ré-inventorier) : `"CSRD"` et
`"Taxonomie européenne"` (`:942-943`) et `"Vérification du reporting par un
tiers"` (`:330`) portent sur une **liste/ensemble de termes exacts**, pas sur
une sous-chaîne de prose. `"(s)"`, `"http://"`, `"automatiq"` visent une
forme, pas un mot de vocabulaire.

## 0quinquies. Tests de gel : portée réelle ≠ portée annoncée

Constaté le 2026-09-05 en vérifiant le contrôle de propagation de
l'étape A. **Non corrigé** — la correction suppose d'abord de trancher
l'inventaire du § 0quater.

| Test | Ce que le nom / la docstring annonce | Ce que le test vérifie |
|---|---|---|
| `test_aucun_engagement_fabrique_dans_les_livrables` | « Bout en bout sur les **cinq** livrables. » | **4** générateurs : `generate_pdf_report`, `generate_onepager_pdf`, `generate_pptx`, `generate_word_report`. **FR seul.** |
| `test_aucune_comparaison_sectorielle_dans_les_livrables` | « Bout en bout sur les **cinq** livrables : PDF, PPTX, Word, one-pager. » | Les **4** mêmes. La docstring **se contredit elle-même** : elle annonce cinq et en énumère quatre. **FR seul.** |
| `test_materialite_absente_des_livrables_generes` | « les **trois** formats (PDF, PPTX, Word) » | **3** générateurs — docstring exacte. **FR seul.** |

**Écart exact, en trois points :**

1. **Le livrable manquant est le questionnaire de collecte**
   (`generate_questionnaire_html`), absent des trois tests. La lettre de
   mission (`generate_proposal_docx`) est, elle, exclue **sciemment**
   (§ 4bis : elle déclencherait le faux positif « marché PME/ETI ») —
   c'est une exclusion assumée, pas un oubli. Les « cinq livrables
   analytiques » du § 4bis sont donc : PDF, PPTX, Word, one-pager,
   questionnaire — et le quatrième seul est couvert quatre fois sur cinq.
2. **Aucun des trois n'est paramétré en langue** : tous appellent
   `make_request()` sans argument, donc **FR uniquement**. L'anglais
   n'est gelé qu'au niveau du *texte* (`generate_esg_content`, tests
   `@parametrize("lang", ["fr","en"])`), **jamais au niveau du livrable
   rendu**. Or c'est précisément là que le trou s'est déjà produit : le
   commentaire de `MARQUEURS_BENCHMARK_INVENTE` note que « la note
   méthodologique EN est restée périmée un chantier entier parce que la
   liste calquait le libellé FR exact du moment ».
3. **Le nom porte l'affirmation la plus large** : `..._dans_les_livrables`
   se lit comme « dans tous les livrables ». Un lecteur qui cherche où
   est gelée une affirmation supprimée conclura, à tort, que les six
   documents sont couverts.

**Coût de la correction** : porter les trois tests à 5 livrables × FR/EN
multiplie leur temps d'exécution par ~3 (ils génèrent déjà des PDF/PPTX
réels) et fera remonter immédiatement les marqueurs génériques du
§ 0quater sur les livrables nouvellement couverts. À faire **après**
l'arbitrage sur l'inventaire, pas avant.

## 0sexies. Limite du test d'intégrité du sommaire

`test_sommaire_numerotation_et_pagination` (ajouté le 2026-09-05) vérifie
que chaque entrée du sommaire correspond à une section rendue, que la
numérotation va de 1 à 8 sans saut et que la pagination est continue,
en FR et en EN.

- **Découvert par mutation** : `_toc_parts` est une **variable locale**
  de `generate_pdf_report`, donc non importable. Le test **recopie** la
  liste des dix libellés à partir des clés i18n au lieu de la lire à la
  source.
- **Conséquence, vérifiée** : renommer le titre rendu d'une section
  (mutation sur `TR["pdf_concl"]`) fait bien échouer le test — c'est le
  cas réel visé, une section retirée dont l'entrée survit au sommaire.
  Mais **ajouter une entrée fantôme directement dans `_toc_parts`
  passerait inaperçu**, puisque le test n'interroge jamais `_toc_parts`.
- **Deuxième enseignement de la mutation** : un premier contrôle
  comparant les **index de page** déclarait orphelines les deux
  premières entrées, parce que le sommaire et les deux premiers titres
  tombent sur la même page. Le test final compte les **occurrences**
  (≥ 2 : une au sommaire, une en titre). À ne pas « simplifier » vers un
  contrôle par page.
- **À faire** : rendre `_toc_parts` extractible (constante de module ou
  fonction) pour supprimer la duplication et couvrir l'entrée fantôme.

## 0septies. Génération non déterministe — `examples/` indistinguable d'un état périmé

- **Constat (2026-09-05)** : régénérer les livrables d'exemple **sans le
  moindre changement de code** produit six binaires modifiés aux yeux de
  Git, pour un **contenu textuel strictement identique**. Vérifié par
  extraction du texte des six livrables avant et après régénération :
  `diff` vide, md5 tous différents.
- **Cause** : les générateurs PDF / PPTX / DOCX écrivent des
  **métadonnées variables** — horodatage de création, identifiants
  d'objets internes, ordre d'entrées dans les archives ZIP pour les
  formats OOXML.
- **Ce que ça coûte** : `git status` **ne permet pas de savoir si
  `examples/` est à jour**. Un dossier propre ne prouve pas que les
  exemples reflètent le code, et un dossier modifié ne prouve pas
  l'inverse. Le seul contrôle fiable aujourd'hui est de comparer le
  **texte extrait**, pas les fichiers.
- **Ça a déjà coûté un commit** : `7f4a5c9` a régénéré les exemples en
  affirmant qu'ils étaient périmés depuis les deux purges — alors que
  `33fae44` et `f5c616a` les avaient régénérés. Le commit ne changeait
  aucun contenu. Annulé par `git revert` (commit `56a7eab`).
- **Piste, non traitée** : figer ces métadonnées à la génération —
  horodatage fixe (ou dérivé de l'exercice du dossier plutôt que de
  l'heure courante), identifiants déterministes, écriture ZIP à ordre et
  dates constants. La génération deviendrait reproductible et
  `git status` redeviendrait un contrôle valable. À évaluer : ReportLab,
  python-pptx et python-docx n'exposent pas tous le même niveau de
  contrôle sur ces champs.

## 1. `accident_frequency_rate` — barème non recalibré

- **Où** : `backend/esg_calculator.py:132-135` (score), recopié tel quel
  dans `backend/bands.py` (`SEUILS["accident_frequency_rate"]`).
- **Constat** : le barème de score (1 / 3 / 5 / 8 / 15) n'a jamais été
  recalibré vers des valeurs réalistes. La moyenne nationale CNAM tourne
  autour de 20 (ordre de grandeur cité en session, à vérifier contre la
  source CNAM réelle avant correction — ne pas la recopier telle quelle sans
  vérification).
- **Décision pour ce chantier** : `bands.py` s'aligne sciemment sur le
  barème existant, même faux, pour ne pas introduire une divergence
  score/texte le jour où on corrige. La correction devra toucher les DEUX
  endroits **dans le même commit** : `esg_calculator.py` et `bands.py`.

## 1bis. `SECTOR_CARBON_THRESHOLDS` — grille sectorielle non sourcée

- **Où** : `backend/esg_calculator.py:21-40` — 15 familles sectorielles ×
  5 seuils d'intensité carbone (t CO₂e / M€ CA), écrits à la main. Seul
  « sourçage » : le commentaire « une industrie lourde n'est pas jugée sur
  la grille des services ».
- **DISTINCTION IMPORTANTE avec le benchmark ESG supprimé le 2026-09-02** :
  la variation sectorielle de l'intensité carbone est un **vrai fait
  métier**, contrairement à une « moyenne ESG par secteur » qui, elle,
  n'avait aucun fondement. Cette grille ne rend donc pas le rapport faux,
  seulement **imprécis**.
- **Ce qui rend le sujet sérieux malgré tout** : (i) les valeurs ne sont
  adossées à aucune source publiée ; (ii) cette grille pilote le **SCORE**,
  pas seulement le texte — elle influence la note lettrée du livrable ;
  (iii) depuis le chantier clauses, une clause affirme « L'intensité
  carbone est conforme à ce qu'on observe dans son secteur », ce qui
  transforme la grille en affirmation de comparaison sectorielle.
- **À faire** : adosser les seuils à une source réelle et citable (ADEME /
  Base Carbone, intensités sectorielles publiées, ou équivalent), et citer
  cette source dans la note méthodologique. **Même niveau de priorité que
  le TF1 (point 1)** : à traiter dans le chantier « exactitude du scoring »,
  avec le barème accidents et `corruption_cases`.

## 2. `corruption_cases` — absent du score

- **Où** : `backend/esg_calculator.py`, fonction `calculate_governance_score`
  (lignes 155-200). Le champ `corruption_cases` n'y apparaît jamais.
- **Constat** : un cas de corruption déclaré ne fait bouger ni le score de
  gouvernance, ni la note globale. Seul le texte (`content_generator.py:
  790-791`) le mentionne, et uniquement dans le cas `== 0` ("zéro cas de
  corruption enregistré") — rien n'est dit si `> 0`.
- **Anormal pour un indicateur ESG** : à corriger (formule de pénalité à
  ajouter au score, et libellé à écrire pour le cas `> 0`), sujet distinct
  du socle de clauses.

## 3. Régime du conseil d'administration : renforcement non traité

- **Traité le 2026-09-03** : l'attribution du quota de 40 % au conseil
  d'administration à la loi Rixain était fausse ; elle relève de la loi
  Copé-Zimmermann (n° 2011-103 du 27 janvier 2011). Corrigé, avec test.
- **CE QUI RESTE** : le régime du CA ne se résume plus à Copé-Zimmermann.
  L'**ordonnance n° 2024-934 du 15 octobre 2024**, transposant la
  **directive (UE) 2022/2381**, l'a renforcé — notamment en intégrant les
  administrateurs représentant les salariés dans le calcul, avec des
  objectifs à atteindre au 30 juin 2026 — et le **décret n° 2025-744 du
  30 juillet 2025** en précise l'application. Le livrable ne mentionne que
  Copé-Zimmermann : juste sur l'origine, incomplet sur le droit applicable.
- **À faire** : décider si le livrable doit citer ce régime consolidé, et
  sous quelle forme.

## 3bis. Seuils de Copé-Zimmermann non vérifiés sur texte primaire

- **Constat** : les résumés officiels consultés donnent des seuils
  d'application divergents (**500 salariés / 50 M€** dans l'un,
  **250 salariés / 50 M€** dans l'autre), vraisemblablement parce que le
  seuil a évolué — mais cela n'a **pas pu être vérifié**.
- **Pourquoi** : `legifrance.gouv.fr`, `vie-publique.fr` et
  `travail-emploi.gouv.fr` sont **bloqués par le proxy réseau** de
  l'environnement de développement. La vérification du 2026-09-02 s'est
  donc appuyée sur les résumés de recherche de ces pages officielles, pas
  sur les textes primaires.
- **Mesure prise en attendant** : le livrable ne cite **aucun seuil
  chiffré**, et emploie « pour les sociétés concernées » plutôt que
  d'affirmer que l'obligation s'applique au client.
- **À faire** : revérifier les seuils sur Légifrance dès que l'accès est
  possible, et décider si le livrable doit les mentionner.

## 4. Mixité de l'effectif : aucun quota légal — traité

- **Traité le 2026-09-03** : « objectif légal 40 % » sur l'effectif total
  supprimé partout (constat brut désormais), ligne « Mixité des effectifs
  (cible 40 %) » retirée du tableau d'écarts réglementaires, référence
  « loi Rixain » retirée de la recommandation parité, mention « objectif
  40 % » retirée des axes d'amélioration. Vérifié : aucun quota légal ne
  porte sur la mixité de l'effectif total, et l'Index de l'égalité
  professionnelle n'en fonde pas non plus (ses 5 indicateurs portent sur
  les rémunérations, augmentations, promotions et la parité parmi les
  10 plus hautes rémunérations).
- **RESTE À ARBITRER** : le seuil de 40 % subsiste comme **déclencheur
  interne** (`esg_calculator.py` : axe d'amélioration si < 40 %, point fort
  si ≥ 40 % ; `content_generator.py` : recommandation parité si < 40 %).
  Il ne s'affiche plus, mais il continue de piloter le jugement porté sur
  le client, en reprenant un chiffre emprunté aux quotas légaux. À
  reconsidérer dans le chantier « exactitude du scoring ».

## 4bis. Résidus du chantier « comparaison sectorielle » — points laissés ouverts

Chantier du 2026-09-03 : les phrases qui affirmaient une comparaison
sectorielle ont été réécrites (18 emplacements, FR et EN). Quatre points
identifiés au passage et **volontairement non traités** :

- **`carbon_grid_sector_specific` (`esg_calculator.py:80`)** : booléen
  stocké dans `details`, aucun consommateur trouvé. Donnée morte, à
  confirmer puis supprimer.
- **`donnees["co2_emissions_tonnes"]` (`content_generator.py`)** : la clé
  porte le nom du champ mais contient une **intensité** (t CO₂e/M€ de CA),
  pas la tonne brute. Nommage trompeur, source d'erreur pour qui reprend
  le code. À renommer (`co2_intensity`) avec les clés correspondantes dans
  `bands.py` et `clauses/fr.py`.
- **`onepager_generator.py:5` et `:92`** : docstring et commentaire disent
  encore « barres par pilier vs secteur ». Vérifié : le **rendu** ne
  comporte plus de repère sectoriel (retiré au chantier 2+4), seuls les
  commentaires sont périmés.
- **`questionnaire_generator.py:59`** : le questionnaire de collecte
  annonce « Seuil légal de référence : 40 % » pour `female_board_percent`.
  Formulation à revoir à la lumière du chantier Rixain — le quota relève
  de Copé-Zimmermann et ne s'applique qu'aux sociétés concernées.

**Faux positif connu du test de gel** : le marqueur « marché PME/ETI » /
« SME/mid-cap market » vise un **vocabulaire**, pas une affirmation.
`proposal_generator.py:72` et `:78` l'emploient légitimement pour décrire un
**périmètre réglementaire** (« les exigences CSRD/VSME applicables au marché
PME/ETI »), pas une comparaison. La couverture du test a donc été
volontairement **limitée aux cinq livrables analytiques**, lettre de mission
exclue. Étendre le test au document contractuel déclencherait ce faux
positif : il faudrait alors distinguer les deux usages.

## 5. Séparateur de milliers anglais dans un texte français

- **Où** : `backend/content_generator.py` (ancien générateur, format `,`
  — ex. ligne 708 : `f"{env.energy_consumption_mwh:,.0f} MWh consommés"`)
  et, par alignement volontaire, `backend/composer.py._formater_valeur()`.
- **Constat** : les nombres sortent en `12,000` (séparateur anglais) dans
  un texte français, où l'usage est `12 000`.
- **Décision pour ce chantier** : le composer **reproduit sciemment** le
  format de l'ancien générateur. Corriger seulement le composer ferait
  cohabiter `12 000` (sections déjà migrées) et `12,000` (sections encore
  sur l'ancien générateur) dans un même rapport, ce qui se verrait.
- **À faire** : passer tout le système en `12 000` **d'un seul coup**,
  ancien générateur + composer, avec un test de non-régression sur le
  rendu. Ne pas le faire section par section.

## 6. `include_benchmarks` : drapeau défini mais jamais lu

- **Où** : `backend/models.py:245` définit `include_benchmarks: bool = True`.
- **Constat** : aucun générateur ne teste ce drapeau (`grep` : 2 occurrences
  en tout, le modèle et un test). La section correspondante s'affiche donc
  toujours, même si le consultant la désactive dans le formulaire.
- **Décision** : non traité pendant le chantier « référence sectorielle »
  — le drapeau perd en partie son objet maintenant que la comparaison
  externe a disparu. À réévaluer : soit le câbler sur la section
  Positionnement, soit le retirer du modèle et du formulaire.

---

*Ce fichier est un registre, pas un plan d'action daté. Le retirer d'une
ligne seulement quand la vérification a été faite ET la correction
appliquée aux deux endroits concernés (score + bands le cas échéant).*
