# Plateforme ESG / RSE — Générateur Automatique de Livrables

Application web **100% locale** pour générer automatiquement des rapports ESG/RSE professionnels et des présentations PowerPoint à partir de vos données ESG.

**Aucune API externe. Aucun abonnement. Fonctionne hors-ligne.**

---

## Démarrage rapide

### Windows
1. Installer [Python 3.10+](https://www.python.org/downloads/) *(cocher "Add Python to PATH")*
2. Installer [Node.js 18+](https://nodejs.org/)
3. **Double-cliquer sur `start.bat`**

### Mac / Linux
```bash
# Rendre le script exécutable (une seule fois)
chmod +x start.sh

# Lancer l'application
./start.sh
```

L'application s'ouvre automatiquement sur **http://localhost:8000**

> Le script installe les dépendances automatiquement à la première exécution.

---

## Fonctionnalités

| Fonctionnalité | Détail |
|---|---|
| **Saisie guidée** | Formulaire 5 étapes : Entreprise → E → S → G → Livrables |
| **Score temps réel** | Calcul automatique pendant la saisie |
| **PowerPoint** | 9 slides professionnelles, 4 thèmes, 5 types |
| **PDF** | Rapport complet, Livre Blanc, Synthèse exécutive |
| **Word (.docx)** | Même contenu, format Word éditable |
| **Données exemple** | Bouton pour pré-remplir avec EcoGroup Industries |
| **Zéro API** | 100% local, fonctionne sans internet |

---

## Thèmes disponibles

| Thème | Style |
|---|---|
| **Corporate Blue** | Finance & industrie, sobre et professionnel |
| **Green Nature** | RSE impact, tons verts |
| **Dark Premium** | Haut de gamme, pour les investisseurs |
| **Minimal White** | Épuré, focus sur les données |

---

## Types de livrables

**PowerPoint :** Synthèse Exécutive · Investor Deck · Rapport Détaillé · Parties Prenantes · Rapport Annuel

**PDF / Word :** Rapport Complet · Livre Blanc · Synthèse PDF

---

## Calcul des scores

| Pilier | Poids | Indicateurs |
|---|---|---|
| **Environnement** | 40% | CO₂, énergie renouvelable, eau, déchets, Scope 1/2/3 |
| **Social** | 35% | Parité, formation, sécurité, satisfaction, communauté |
| **Gouvernance** | 25% | CA, éthique, cybersécurité, audit, comité RSE |

**Notation :** AAA · AA · A · BBB · BB · B · CCC

---

## Architecture

```
ici/
├── start.sh          ← Lancement Mac/Linux
├── start.bat         ← Lancement Windows
├── backend/
│   ├── main.py               API FastAPI
│   ├── models.py             Modèles de données
│   ├── esg_calculator.py     Moteur de calcul des scores
│   ├── content_generator.py  Génération de texte (100% local)
│   ├── chart_generator.py    Graphiques matplotlib
│   ├── ppt_generator.py      Générateur PowerPoint
│   ├── report_generator.py   Générateur PDF
│   ├── docx_generator.py     Générateur Word
│   └── requirements.txt
└── frontend/
    └── src/                  Interface React
```

---

## Prérequis

- **Python 3.10+** — [python.org](https://www.python.org/downloads/)
- **Node.js 18+** — [nodejs.org](https://nodejs.org/)

Packages Python installés automatiquement : `fastapi`, `uvicorn`, `python-pptx`, `reportlab`, `python-docx`, `matplotlib`, `pillow`, `numpy`, `pydantic`
