# Plateforme ESG / RSE — Générateur Automatique de Livrables

Application web complète pour générer automatiquement des rapports ESG/RSE professionnels (PDF, livres blancs) et des présentations PowerPoint esthétiques à partir de données ESG saisies.

## Fonctionnalités

- **Saisie guidée** des données ESG (Environnement, Social, Gouvernance)
- **Calcul automatique** des scores ESG par pilier et score global avec notation (AAA → CCC)
- **Génération IA** du contenu narratif via Claude (Anthropic)
- **PowerPoint** professionnel avec 4 thèmes et 5 types de présentation
- **PDF** (rapport complet, livre blanc, synthèse exécutive)
- **Graphiques** automatiques : radar, barres, camembert émissions, jauges
- **Alignement** ODD, GRI, TCFD, CSRD intégré

## Thèmes disponibles

| Thème | Usage |
|-------|-------|
| **Corporate Blue** | Finance, industrie, reporting classique |
| **Green Nature** | RSE impact-first, environnement |
| **Dark Premium** | Investisseurs, haut de gamme |
| **Minimal White** | Moderne, focus data |

## Types de présentation PowerPoint

- Synthèse Exécutive
- Investor Deck ESG
- Rapport Détaillé
- Communication Parties Prenantes
- Rapport Annuel RSE

## Installation

### Avec Docker (recommandé)

```bash
export ANTHROPIC_API_KEY=your_key_here
docker-compose up --build
```

Frontend : http://localhost:3000
API : http://localhost:8000

### Sans Docker

**Backend :**
```bash
cd backend
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
uvicorn main:app --reload --port 8000
```

**Frontend :**
```bash
cd frontend
npm install
npm run dev
```

## Architecture

```
├── backend/
│   ├── main.py              # FastAPI — endpoints
│   ├── models.py            # Pydantic models
│   ├── esg_calculator.py    # Moteur de calcul ESG
│   ├── chart_generator.py   # Graphiques matplotlib
│   ├── ppt_generator.py     # Générateur PowerPoint (python-pptx)
│   ├── report_generator.py  # Générateur PDF (reportlab)
│   └── ai_content.py        # Contenu IA via Claude
└── frontend/
    └── src/
        ├── App.jsx
        ├── components/
        │   ├── Header.jsx
        │   ├── Sidebar.jsx
        │   ├── ResultsPanel.jsx
        │   ├── FormField.jsx
        │   └── steps/
        │       ├── StepCompany.jsx
        │       ├── StepEnvironmental.jsx
        │       ├── StepSocial.jsx
        │       ├── StepGovernance.jsx
        │       └── StepOutput.jsx
```

## Endpoints API

| Méthode | URL | Description |
|---------|-----|-------------|
| POST | `/api/calculate` | Calcul des scores ESG |
| POST | `/api/generate/pptx` | Génère et télécharge le PowerPoint |
| POST | `/api/generate/pdf` | Génère et télécharge le PDF |

## Calcul des scores

- **Environnement (40%)** : émissions, renouvelable, eau, déchets, scope 1/2/3
- **Social (35%)** : parité, formation, sécurité, satisfaction, communauté
- **Gouvernance (25%)** : CA, éthique, cybersécurité, audit, comité RSE
