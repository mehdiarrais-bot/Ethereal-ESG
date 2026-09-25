<div align="center">

<img src="docs/img/cover.png" alt="Ethereal ESG" width="100%">

# Ethereal ESG

**Plateforme de diagnostic et de reporting extra-financier — 100 % locale.**

Transforme les données ESG d'une PME/ETI en livrables de niveau cabinet de conseil :
rapport PDF, présentation de direction, rapport Word, synthèse une page, lettre de mission
et questionnaire de collecte.
Aucune API externe, aucun compte, aucune donnée qui sort de la machine.

`Python` · `FastAPI` · `React` · `python-pptx` · `ReportLab` · `python-docx` · `matplotlib`

</div>

![Interface de configuration des livrables](docs/img/02-livrables.png)

*L'interface : six gabarits éditoriaux, photos de l'entreprise, score calculé en direct.*

---

## Pourquoi 100 % local

Les données ESG d'une entreprise sont sensibles : émissions, effectifs, incidents éthiques,
manquements réglementaires. Les envoyer à un service SaaS ou à une API d'IA générative est un
frein commercial réel — et souvent un interdit chez le client.

Ethereal ESG fait le pari inverse : **tout est calculé et rédigé en local**.

- Pas d'appel réseau au moment de la génération. L'application fonctionne hors ligne.
- Les textes analytiques ne viennent pas d'un LLM mais d'un moteur de rédaction déterministe :
  variation lexicale indexée sur l'entreprise, contexte sectoriel, formulations conditionnées
  par les données réelles.
- Les dossiers clients sont des fichiers JSON sur le disque de l'utilisateur, avec écriture
  atomique et sauvegarde/restauration par archive.

C'est une contrainte d'architecture assumée, pas une limitation : elle devient l'argument
commercial du consultant qui l'utilise (« vos données ne quittent pas ma machine »).

---

## Ce que ça produit

Six livrables, générés en un clic à partir du même jeu de données, bilingues **FR/EN**
et déclinables en **6 gabarits éditoriaux** (Aurora, Annuel, Institutionnel, Portrait,
Terre, Galerie) — voir [les six rapports d'exemple](examples/gabarits/).

| Livrable | Contenu |
|---|---|
| **Rapport PDF** (~20 p.) | Couverture photo, sommaire paginé, l'entreprise en bref, ESG en un coup d'œil, puis trois actes : Situation · Diagnostic · Plan d'action |
| **Présentation** (21-23 slides) | Deck de comité de direction, titres porteurs de conclusion ; l'analyse détaillée du rapport en notes de l'orateur |
| **Rapport Word** | Même texte analytique que le PDF, éditable par le client |
| **Synthèse une page** | Le document que le dirigeant transfère à son conseil |
| **Lettre de mission** | Proposition commerciale bâtie sur le pré-diagnostic réel du prospect |
| **Questionnaire de collecte** | Fichier HTML autonome envoyé au client : il le remplit hors ligne, renvoie un CSV réimporté sans ressaisie |

📂 **[Voir les livrables générés →](examples/)** *(PDF, PPTX, DOCX réels, données fictives)*

<table>
<tr>
<td width="50%"><img src="docs/img/07-onepager.png" alt="Synthèse une page"></td>
<td width="50%"><img src="docs/img/05-rapport-diagnostic.png" alt="Page diagnostic du rapport PDF"></td>
</tr>
<tr>
<td align="center"><em>Synthèse une page : score, évolution sur un an, risques, top-3 actions</em></td>
<td align="center"><em>Diagnostic : trajectoire pluriannuelle, couverture des exigences de reporting</em></td>
</tr>
<tr>
<td width="50%"><img src="docs/img/04-rapport-synthese.png" alt="Synthèse exécutive du rapport"></td>
<td width="50%"><img src="docs/img/06-rapport-plan-action.png" alt="Plan d'action priorisé"></td>
</tr>
<tr>
<td align="center"><em>Synthèse exécutive : digest décisionnel et analyse du consultant</em></td>
<td align="center"><em>Plan d'action : objectif, responsable et échéance par action, feuille de route sur 12 mois</em></td>
</tr>
</table>

### Une identité visuelle par client

En option, le gabarit se décline aux couleurs du client : une palette est dérivée de son nom
(ou saisie à la main) et reprise dans les aplats, les chiffres clés et les graphiques.
Trois clients, trois rendus — sans toucher aux couleurs sémantiques des piliers E/S/G.

![Trois clients, trois identités visuelles](docs/img/08-branding.png)

---

## Le contenu analytique

L'enjeu n'est pas de remplir des pages, c'est de produire un diagnostic défendable devant
un directeur financier. Sans jamais inventer une donnée : ce qui n'est pas renseigné est
affiché comme tel.

- **Priorisation des enjeux** — cartographie dérivée des indicateurs déclarés et des scores par
  pilier, reprise nommément dans le texte. Le rapport indique explicitement qu'elle **ne constitue
  pas** une analyse de double matérialité au sens d'ESRS 1 : l'outil ne conduit ni consultation des
  parties prenantes, ni cotation des IRO.
- **Couverture des exigences de reporting** — sept exigences (ESRS E1-6, ESRS 2 GOV-1, AFEP-MEDEF,
  Taxonomie UE…) avec un statut qui dit ce qui est constaté et rien de plus : *publié / publié
  partiellement / non publié* pour les lignes de publication, *au-dessus / sous le seuil* pour les
  lignes de seuil, et *non renseigné* (donnée absente chez le client) distingué de *non couvert par
  ce reporting* (donnée que l'outil ne collecte pas).
- **Registre des risques** — chaque risque coté impact × probabilité, priorisé P1-P3.
- **Risques climatiques TCFD** — risques physiques et de transition **spécifiques au secteur**,
  sur trois horizons, avec exposition au prix du carbone calculée depuis l'intensité réelle.
- **Benchmark sectoriel** et **maturité ESG** en cinq stades.
- **Plan d'action** priorisé par matrice effort/impact, avec objectif chiffré, fonction
  responsable et échéance.
- **Trajectoire pluriannuelle** dès qu'un client a deux exercices d'historique.
- **Glossaire** en annexe, filtré sur ce que le rapport contient réellement — le lecteur
  non spécialiste n'a pas besoin d'un dictionnaire.

Le scoring différencie les **grilles d'intensité carbone par famille sectorielle** : une même
intensité vaut 40/100 dans les services, 60 dans l'industrie, 70 dans l'énergie. La notation
lettrée est explicitement présentée comme *indicative* et documentée dans une note
méthodologique qui déclare aussi les limites et les points de données manquants.

Un mode **VSME** (norme volontaire PME de l'EFRAG) requalifie les exigences optionnelles
au lieu de les compter comme non conformes.

---

## Le workflow d'une mission

L'application ne s'arrête pas à la génération : elle porte le cycle complet d'une activité
de conseil indépendante.

![Vue portefeuille](docs/img/03-portefeuille.png)

*La vue portefeuille : statut de mission, dernier score et trajectoire de chaque client.*

| Étape | Dans l'application |
|---|---|
| **Prospection** | Saisie rapide ou import CSV/Excel → score instantané → lettre de mission personnalisée |
| **Collecte** | Envoi du questionnaire HTML au client → il le remplit hors ligne → le CSV renvoyé s'importe directement |
| **Mission** | Dossier client sauvegardé, statut (prospect · signé · livré · archivé) |
| **Restitution** | Pack complet : les cinq documents de restitution dans une archive |
| **Suivi** | Les actions réalisées sont cochées et apparaissent comme acquis dans le rapport suivant |
| **Renouvellement** | Chaque exercice enrichit l'historique : évolution N-1 et trajectoire pluriannuelle |
| **Sécurité** | Export/import de tous les dossiers en une archive |

Les analyses libres du consultant sont injectées dans des encarts dédiés
« L'analyse du consultant » — ce qui distingue un diagnostic d'un rapport automatique.

![Saisie guidée des données](docs/img/01-saisie.png)

*Saisie guidée en cinq étapes, avec calcul du score en temps réel et import CSV/Excel.*

---

## Points techniques notables

- **Trois moteurs de rendu documentaire** exploités à un niveau inhabituel : ReportLab en
  *canvas* (couverture pleine page, synthèse une page dessinée au point près) **et** en
  *flowables* (rapport paginé), python-pptx avec ajustement automatique de la taille des
  titres, python-docx avec styles et ombrages XML.
- **Système de branding** avec garde-fous de luminance : la couleur primaire est assombrie
  si elle porte du texte blanc, l'accent éclairci s'il devient illisible ; les couleurs
  sémantiques des piliers sont préservées.
- **Typographie** : polices embarquées (SIL OFL), nombres à la française dans tous les
  livrables FR (« 21 500 MWh », « 6,2 », « 42 % »), pagination sans veuve, orpheline ni page
  presque vide.
- **Rédaction déterministe** : accords grammaticaux réels (« deux points forts consolidés »,
  jamais « 2 point(s) fort(s) »), déduplication des formules, aucun artefact de publipostage.
- **Persistance robuste** : écriture atomique (fichier temporaire + `os.replace`), validation
  Pydantic stricte de toutes les entrées, middleware ASGI de limitation de taille et
  d'en-têtes de sécurité, refus des requêtes venant d'un site web tiers (origine et nom
  d'hôte contrôlés), import de sauvegarde borné et validé.
- **Tests** : suite pytest (livrables × langues × six gabarits, sécurité, pagination,
  typographie, parité des livrables, garde-fous rédactionnels) et tests Node de la logique
  d'interface (`npm test`).

```
backend/
├── main.py                 API FastAPI — génération, dossiers clients, sauvegarde
├── models.py               Modèles Pydantic (validation stricte de toutes les entrées)
├── esg_calculator.py       Scoring + grilles carbone sectorielles
├── esg_advanced.py         Matérialité, benchmark, maturité, objectifs
├── content_generator.py    Moteur de rédaction (IRO, écarts, risques, plan d'action)
├── chart_generator.py      Graphiques matplotlib
├── ppt_generator.py        PowerPoint · report_generator.py  Rapport PDF
├── docx_generator.py       Word · onepager_generator.py  Synthèse 1 page
├── proposal_generator.py   Lettre de mission
├── questionnaire_generator.py  Questionnaire de collecte autonome
├── glossary.py             Glossaire CSRD/ESRS filtré selon le rapport
├── branding.py             Déclinaison aux couleurs du client
├── client_store.py         Dossiers clients (JSON local, écriture atomique)
└── tests/                  Suite pytest
frontend/src/               Interface React (Vite)
scripts/make_examples.py    Régénère les livrables d'exemple
```

---

## Démarrage

### Version exécutable Windows (sans Python ni Node)

Télécharger `EtherealESG-windows.zip` depuis l'onglet **Actions** du dépôt (workflow
*Build Windows exe*), le décompresser, puis double-cliquer sur `EtherealESG\EtherealESG.exe`.
L'application s'ouvre dans le navigateur ; la fenêtre console doit rester ouverte pendant
l'utilisation. Les dossiers clients sont stockés dans `%APPDATA%\EtherealESG\clients`,
donc conservés lors d'une mise à jour de l'exécutable.

Reprise des dossiers créés avec `start.bat` : ils se trouvent dans `backend\data\clients`
du dossier source. Les exporter depuis l'ancienne installation (sauvegarde des dossiers),
puis les importer dans l'exécutable ; ou copier les fichiers `.json` dans
`%APPDATA%\EtherealESG\clients`.

L'exécutable n'est pas signé : Windows SmartScreen affiche un avertissement au premier
lancement (« Informations complémentaires » puis « Exécuter quand même »).

Construction locale : `cd frontend && npm run build`, puis depuis la racine
`pyinstaller packaging/ethereal_esg.spec --noconfirm` et
`python packaging/smoke_test.py dist/EtherealESG/EtherealESG.exe`.

### Depuis les sources

```bash
# Windows : double-cliquer sur start.bat
# Mac / Linux :
chmod +x start.sh && ./start.sh
```

L'application s'ouvre sur **http://localhost:8000**. Les dépendances sont installées à la
première exécution. Prérequis : Python 3.12+ et Node.js 22+ (versions vérifiées par la CI).

```bash
# Tests (lancés aussi par la CI à chaque push : .github/workflows/tests.yml)
# depuis la racine du dépôt
pip install -r backend/requirements.txt -r backend/requirements-dev.txt
(cd backend && python -m pytest tests/ -q -n auto)   # suite backend, en parallèle
python -m pyright                                    # typage (mode standard)
(cd frontend && npm test)                            # logique d'interface
```

Les livrables d'exemple de `examples/` sont reproductibles — `python scripts/make_examples.py`.

Les dossiers clients sont stockés dans `backend/data/clients/` (jamais versionnés).

---

## Licence

Code publié à des fins de démonstration et d'évaluation. **Tous droits réservés** —
aucune autorisation de réutilisation, de redistribution ou d'exploitation commerciale
n'est accordée. Pour toute question : ouvrir une issue.
