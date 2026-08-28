# Plateforme ESG / RSE — Directives permanentes

Application web 100 % locale pour cabinets de conseil ESG : pré-diagnostic scoré, génération de livrables (PDF/PPTX/Word), dossiers clients pluriannuels. Backend FastAPI (`backend/`), frontend React/Vite (`frontend/src/`).

## Design — deux surfaces distinctes

- **Interface (`frontend/src/`)** : système "Encre & Ambre" — fond blanc, accent ambre unique (≤ 10 %), plat par défaut (filets 1px, ombres légères). Aucun glow, aucun dégradé décoratif, aucun backdrop-filter. Voir `PRODUCT.md` et `DESIGN.md`.
- **Livrables PDF (`backend/report_generator.py`)** : système "Ethereal ESG" — mode hybride (couverture et pages de rupture en sombre #121314, corps en clair #F4F3F1), Playfair Display + Inter, accent sage dédoublé (#8FA391 aplats / #3F5A44 traits et textes). Les glows atmosphériques sont limités aux pages sombres du PDF, jamais à l'interface.
- L'ancien thème "Galaxy" est supprimé. Interdit sur les deux surfaces.
- `DESIGN.md` est régénéré automatiquement (`/impeccable document`) : ne pas l'éditer à la main. Ce fichier CLAUDE.md fait autorité.

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
