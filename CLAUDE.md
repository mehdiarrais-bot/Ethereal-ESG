# Plateforme ESG / RSE — Directives permanentes

Application web 100 % locale pour cabinets de conseil ESG : pré-diagnostic scoré, génération de livrables (PDF/PPTX/Word), dossiers clients pluriannuels. Backend FastAPI (`backend/`), frontend React/Vite (`frontend/src/`).

## Design — état réel du dépôt

Ce bloc décrit ce que contient le code, pas une cible. Toute évolution du design se
décide explicitement et met ce bloc à jour.

- **Interface (`frontend/src/`)** : thème "Reporting", clair, en vigueur depuis le 2026-09-22 (remplace le thème "Galaxy" sombre violet/néon). 45 jetons nommés dans `index.css`, seule source de vérité : fond `#f4f7f5`, surfaces `#ffffff`, navigation vert profond `#0e2e24`, marque `#12805a`, piliers `--env` `#0f7a4d`, `--social` `#1c6ca8`, `--gov` `#6a46a6` avec leurs variantes `-soft` (fonds teintés) et `-on-nav` (lisibles sur la navigation sombre), états `ok`/`warn`/`danger`/`neutral`, rayons 8/10/14 px. **Aucun glow, aucun `backdrop-filter`, aucun dégradé décoratif** — ils ont tous été retirés. **Polices : pile système uniquement**, aucun webfont distant, l'application devant fonctionner 100 % hors ligne. **Aucune couleur en dur** dans les composants. Le sélecteur de gabarit (`DesignPicker.jsx`) et l'aperçu (`PreviewPanel.jsx`) lisent les couleurs des livrables via `GET /api/designs` (hook `useDesigns`) : ils annoncent le rendu du livrable et ne suivent donc PAS le thème de l'interface, mais n'embarquent plus aucune palette (l'ancienne duplication avec le backend est levée depuis le 2026-09-23). Vignettes réelles des gabarits : `frontend/public/designs/*.jpg`, produites par `scripts/make_design_thumbnails.py`.
- **Hiérarchie de l'information** : la complétude du reporting est l'information de pilotage ; le score global et la note lettrée sont affichés en **rang secondaire** (barre basse, en-tête, panneau de résultats, fiches de dossier), sans pastille colorée. Ils restent calculés par le backend et imprimés dans les livrables — le chantier « exactitude du scoring » garde donc tout son objet.
- **Gabarits des livrables (`backend/report_designs.py`, source unique)** : six gabarits éditoriaux tirés des maquettes validées le 2026-09-23 — `aurora` (défaut, vert forêt sur ivoire), `annuel`, `institutionnel`, `portrait`, `terre`, `galerie`. Chacun fixe ses jetons de couleur (papier, encre, primaire, accent, piliers et leurs fonds `-soft`), ses polices, sa mise en page (couverture, page « coup d'œil », en-tête, style des indicateurs) et ses photos par emplacement. PDF, PPTX, Word, synthèse une page, lettre de mission et graphiques **convertissent** ces jetons ; aucun ne redéfinit une palette (verrouillé par `tests/test_designs.py`). Les sept anciens thèmes (`corporate_blue`…) sont relus sous le gabarit le plus proche (`LEGACY_THEMES`), à la validation comme au chargement d'un dossier.
- **Rapport PDF** : `report_generator.py` (assemblage, composé en deux passes pour paginer le sommaire), `pdf_pages.py` (pages composées au canevas : 6 couvertures, 6 pages « ESG en un coup d'œil », sommaire, entreprise, mot de la direction, focus, chapitres, quatrième de couverture), `pdf_kit.py` (polices, photos recadrées, repère maquette 794 × 1123 px). Les pages composées n'affichent que des données du modèle : le radar ne trace que les trois piliers (N-1 en pointillés si l'historique existe). La « médiane sectorielle » et le radar à six dimensions des maquettes ont été **écartés** : données absentes, règle 9.
- **Polices PDF** : embarquées dans `backend/assets/fonts` (SIL OFL, figées en statiques et sous-ensemble latin par `scripts/build_fonts.py`) — Newsreader, Instrument Serif/Sans, Libre Caslon Text, Hanken Grotesk, Albert Sans, Source Sans 3. Plus de dépendance aux polices système ; repli base-14 seulement si le dossier manque (le test de fumée de l'exécutable le détecte). Les glyphes hors sous-ensemble (●, ■) ne s'affichent pas : utiliser « • ».
- **Photos** : l'entreprise peut fournir cinq photos (`report_photos` : cover, company, environment, social, governance ; PNG/JPEG ≤ 1,5 Mo, réduites dans le navigateur). À défaut, et pour les emplacements éditoriaux (focus, chapitres, quatrième de couverture), banque locale `backend/assets/photos` : 20 photos Wikimedia Commons **domaine public / CC0**, provenance dans `CREDITS.md`. Le rapport le signale dans la note méthodologique (elles ne représentent ni les sites ni les équipes du client).
- **PPTX et Word** : polices système sûres déclarées par gabarit (`office` : Georgia, Segoe UI, Calibri), couleurs converties du gabarit, bandeau de couverture = photo de couverture du gabarit. Toutes les diapositives sont claires.

## Hiérarchie des objectifs

En cas d'arbitrage, cet ordre tranche :
1. Exactitude métier (un chiffre, un seuil ou une affirmation réglementaire faux invalident le livrable)
2. Fiabilité (ne jamais casser une génération en cours)
3. Lisibilité et maintenabilité
4. Testabilité
5. Esthétique du rendu
6. Performance

Un barème ou une affirmation faux se corrigent même hors périmètre. Une optimisation ne se fait jamais au prix de la lisibilité.

## Règles de process (priment sur toute instruction ponctuelle qui les contredirait)

1. **Diagnostiquer avant de coder.** Sur toute tâche touchant plus d'un fichier ou une fonction partagée : cartographier l'existant, montrer le diagnostic, attendre validation. Ne jamais patcher un symptôme sans avoir identifié la cause.
2. **S'arrêter sur anomalie, ne jamais corriger silencieusement.** Si une modification révèle un problème hors périmètre (couleur ou variable qui change de sens, seuil incohérent, bug préexistant), s'arrêter et le montrer, ne pas le corriger en passant.
3. **Prouver, ne pas déclarer.** Ne jamais dire "c'est fait" sans preuve : capture du rendu, sortie de test, extrait généré, cat du fichier. Une modification non vérifiée n'est pas terminée.
4. **Ne jamais présenter un travail partiel comme complet.** Le dire explicitement en tête de réponse.
5. **Ne pas enchaîner plusieurs chantiers en auto-validation.** Après une reprise de session, ou face à une demande large ("fais tout"), traiter un chantier à la fois et rendre la main pour validation. Ne jamais annoncer une to-do "soldée" sans que chaque chantier ait été validé.
6. **Le code fait foi, pas la prose.** En cas de divergence entre documentation et implémentation, partir de l'implémentation et signaler l'écart.
7. **Commit avant tout changement transverse.** Point de retour obligatoire avant toute modification touchant l'architecture, le build, ou plus de cinq fichiers.
8. **Ne pas élargir le périmètre sans demander.** Signaler les chantiers adjacents, ne pas les engager.
9. **Aucune affirmation réglementaire écrite de mémoire.** Toute référence à une norme (ESRS, VSME, GRI, TCFD, seuils légaux, codes de datapoints) doit être vérifiable contre le texte réel. Ne jamais fabriquer un code de référence ni reclasser une exigence sans source. Un livrable qui cite une norme engage le cabinet et son client.

## Qualité de code

**Avant d'ajouter, simplifier :** identifier les duplications de la zone touchée, supprimer le code mort produit par la modification, signaler toute fonction de plus de 40 lignes ou à responsabilités multiples avant d'y ajouter quoi que ce soit.

**Structure :** une source de vérité par donnée (aucun seuil, palette ou libellé dupliqué entre fichiers). Données et logique séparées (seuils, clauses, libellés dans des modules de données que le code lit). Pas de valeur magique en dur (hexadécimal, seuil, taille) : tout passe par un token nommé. Pas d'abstraction spéculative (factoriser à partir du troisième cas identique).

**Écriture :** fonctions courtes à responsabilité unique, noms explicites, pas de booléen de configuration ambigu en paramètre, commentaires réservés au "pourquoi" non évident. Validation stricte de toute donnée entrante (import CSV, saisie wizard) et de tout chemin de fichier.

**Robustesse :** échouer bruyamment en développement (clé manquante, placeholder inconnu visibles), gracieusement en production (jamais interrompre la génération d'un livrable). Toute correction de bug s'accompagne d'un test qui l'aurait attrapé. Toute nouvelle fonctionnalité s'accompagne d'un test qui la couvre — pas de chantier livré sans filet.

## Tests

`python -m pytest tests/ -q` doit passer avant chaque modification et après. Un chantier n'est pas terminé tant qu'un test ne le couvre pas et que la suite n'est pas verte.

## Choix de modèle (indicatif)

Injection de contenu, correctifs ciblés, écriture de tests : modèle standard. Diagnostics d'architecture, corrections réglementaires sensibles, raisonnement transverse : modèle supérieur. Refactoring lourd multi-fichiers où une erreur en cours de route coûte cher : modèle le plus capable.
