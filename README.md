# Plateforme ESG / RSE — Cabinet de conseil en une application

Application web **100 % locale** pour piloter une activité de conseil ESG/RSE de bout en bout :
pré-diagnostic scoré, lettre de mission, livrables niveau cabinet (PowerPoint, PDF, Word,
synthèse une page), dossiers clients avec historique pluriannuel et mini-CRM.

**Aucune API externe. Aucun abonnement. Aucune donnée ne quitte votre machine.**

---

## Démarrage rapide

### Windows
1. Installer [Python 3.10+](https://www.python.org/downloads/) *(cocher « Add Python to PATH »)*
2. Installer [Node.js 18+](https://nodejs.org/)
3. **Double-cliquer sur `start.bat`**

### Mac / Linux
```bash
chmod +x start.sh   # une seule fois
./start.sh
```

L'application s'ouvre sur **http://localhost:8000**.
Le script installe les dépendances à la première exécution.

---

## Le cycle d'une mission

| Étape | Dans l'application |
|---|---|
| **Prospection** | Saisie rapide (ou import CSV) → score instantané → **🖋 Lettre de mission** générée depuis le pré-diagnostic réel (écarts, maturité, phases) |
| **Collecte** | Formulaire guidé 5 étapes, modèle CSV téléchargeable, import CSV/Excel |
| **Dossier client** | **💾 Enregistrer** / **📁 Dossiers** : sauvegarde locale, statut CRM (prospect · signé · livré · archivé), rechargement en un clic |
| **Restitution** | **📦 Pack complet** : PPTX + PDF + Word + synthèse 1 page + lettre de mission en un zip |
| **Renouvellement** | Chaque exercice sauvegardé alimente l'historique : les livrables affichent l'**évolution N-1** et la **trajectoire pluriannuelle** |
| **Sécurité** | **⬇ Sauvegarde / ⬆ Restaurer** : zip de tous les dossiers |

---

## Livrables générés

| Livrable | Contenu |
|---|---|
| **PowerPoint** (21-23 slides) | Sommaire, mot de la direction, tableau de bord hero, benchmark sectoriel + maturité, trajectoire, analyse des écarts, chiffre-choc, piliers E/S/G, matérialité, objectifs, taxonomie, risques cotés P1-P3, matrice de priorisation, recommandations, feuille de route 12 mois, ODD, conclusion |
| **Rapport PDF** (~16 p.) | Structure cabinet en 3 actes (Situation · Diagnostic · Plan d'action) : synthèse une page avec digest décisionnel, piliers avec pastilles de statut KPI, analyse des écarts réglementaires (conforme/partiel/non conforme), registre des risques (impact × probabilité → priorité), plan d'action (objectif · responsable · échéance), note méthodologique |
| **Word** | Même contenu, éditable |
| **Synthèse 1 page** | Score hero + évolution, piliers vs secteur, forces/risques/opportunités, top-3 actions |
| **Lettre de mission** | Contexte + écarts constatés, objectifs, déroulé (issu de la feuille de route), livrables, prérequis, conditions à compléter |

Tous bilingues **FR/EN**, en **7 thèmes**, déclinables aux **couleurs du client**
(sélecteurs primaire/accent ou palette déterministe « 🎲 depuis le nom »).

### Contenu analytique (sans aucune donnée inventée)
- Double matérialité CSRD/ESRS : méthodologie IRO 4 étapes, enjeux réels cotés impact/financier
- Risques climatiques TCFD/ESRS E1-9 : sectorisés, 3 horizons, exposition au prix du carbone calculée
- Benchmark : référence sectorielle **interne** (étiquetée comme telle), marché PME/ETI
- Gap analysis ESRS : points de données manquants explicitement listés (« Non renseigné »)
- Notation lettrée **indicative** (échelle interne AAA-CCC, documentée dans la note méthodologique)
- Champs d'authenticité : initiatives internes réelles et mot du dirigeant tissés dans les textes

---

## Calcul des scores

| Pilier | Poids | Indicateurs |
|---|---|---|
| **Environnement** | 40 % | CO₂ (grille d'intensité **différenciée par famille sectorielle**), renouvelable, eau, déchets, Scopes 1/2/3 |
| **Social** | 35 % | Parité, formation, sécurité, turnover, satisfaction |
| **Gouvernance** | 25 % | Conseil, indépendance, éthique, cybersécurité, audit, comité |

Notation indicative : AAA · AA · A · BBB · BB · B · CCC — moyenne pondérée des piliers.

---

## Architecture

```
ici/
├── start.sh / start.bat        Lancement
├── backend/
│   ├── main.py                 API FastAPI (génération, dossiers clients, backup)
│   ├── models.py               Modèles pydantic (validation stricte)
│   ├── esg_calculator.py       Scores + grilles carbone sectorielles
│   ├── esg_advanced.py         Matérialité, benchmark, maturité, objectifs
│   ├── content_generator.py    Textes niveau CSRD (IRO, écarts, risques, plan d'action)
│   ├── chart_generator.py      Graphiques matplotlib (benchmark, matrices, trajectoire…)
│   ├── ppt_generator.py        PowerPoint
│   ├── report_generator.py     Rapport PDF
│   ├── docx_generator.py       Word
│   ├── onepager_generator.py   Synthèse 1 page
│   ├── proposal_generator.py   Lettre de mission
│   ├── branding.py             Déclinaison aux couleurs du client
│   ├── client_store.py         Dossiers clients (JSON local, écriture atomique)
│   ├── import_data.py          Import CSV/Excel
│   └── tests/                  Suite pytest
└── frontend/src/               Interface React (Vite)
```

### Données locales
Les dossiers clients sont stockés dans `backend/data/clients/` (hors git).
Pensez à la **sauvegarde zip** régulière depuis le panneau Dossiers.

---

## Tests

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest tests/ -q
```

---

## Prérequis

- **Python 3.10+**, **Node.js 18+**
- Dépendances : `fastapi`, `uvicorn`, `python-pptx`, `reportlab`, `python-docx`,
  `matplotlib`, `pillow`, `pydantic`, `openpyxl` (installées automatiquement)
