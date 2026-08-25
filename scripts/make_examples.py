#!/usr/bin/env python3
"""
Régénère les livrables d'exemple publiés dans examples/.

Données entièrement fictives — aucune donnée client réelle ne doit jamais
entrer ici. Le jeu couvre volontairement les cas intéressants : historique
pluriannuel, actions réalisées, notes du consultant, couleurs de marque.

    python scripts/make_examples.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "backend"))
OUT = os.path.join(ROOT, "examples")

from models import (ESGRequest, CompanyInfo, EnvironmentalData, SocialData,  # noqa: E402
                    GovernanceData, TaxonomyData)
from esg_calculator import calculate_esg_scores                              # noqa: E402
from content_generator import generate_esg_content                           # noqa: E402
from ppt_generator import generate_pptx                                      # noqa: E402
from report_generator import generate_pdf_report                             # noqa: E402
from docx_generator import generate_word_report                              # noqa: E402
from onepager_generator import generate_onepager_pdf                         # noqa: E402
from proposal_generator import generate_proposal_docx                        # noqa: E402
from questionnaire_generator import generate_questionnaire_html              # noqa: E402
from main import build_advanced_charts, build_extras                         # noqa: E402

# Société fictive de démonstration
DEMO = ESGRequest(
    company=CompanyInfo(
        name="Acme Industries", sector="Industrie manufacturière", country="France",
        revenue_eur=48_000_000, reporting_year=2025, target_year=2030,
        presenter_name="J. Martin", presenter_title="Directrice Générale",
        key_initiatives="le programme Cap Climat 2027, l'installation photovoltaïque du site de Lyon",
        ceo_quote="La performance durable est au cœur de notre stratégie industrielle : "
                  "chaque euro investi doit créer de la valeur pour nos clients et pour la planète."),
    environmental=EnvironmentalData(
        co2_emissions_tonnes=8200, scope1_emissions=1200, scope2_emissions=2100,
        scope3_emissions=4900, renewable_energy_percent=42, waste_recycled_percent=63,
        water_consumption_m3=120000, energy_consumption_mwh=21500),
    social=SocialData(
        female_employees_percent=34, training_hours_per_employee=22,
        accident_frequency_rate=6.2, total_employees=320, employee_turnover_percent=11),
    governance=GovernanceData(
        esg_audit_conducted=False, sustainability_committee=True, data_breaches=1,
        ethics_violations=0, independent_board_percent=45, board_members=9,
        female_board_percent=44),
    taxonomy=TaxonomyData(turnover_aligned_percent=38, capex_aligned_percent=52,
                          opex_aligned_percent=20),
    language="fr", aesthetic_theme="corporate_blue",
    include_recommendations=True, include_benchmarks=True,
    # Historique : fait apparaître l'évolution N-1 et la trajectoire
    previous_scores={"year": 2024, "env": 58.0, "social": 50.0, "gov": 60.0, "total": 55.9},
    score_history=[
        {"year": 2023, "env": 48.0, "social": 46.0, "gov": 55.0, "total": 49.4},
        {"year": 2024, "env": 58.0, "social": 50.0, "gov": 60.0, "total": 55.9},
    ],
    # Suivi de mission : preuve d'exécution du plan précédent
    completed_actions=[
        {"title": "Créer un comité de durabilité au conseil", "year": 2024},
        {"title": "Porter la formation à 20h/employé/an minimum", "year": 2024},
    ],
    # Valeur ajoutée humaine du consultant
    consultant_notes={
        "global": "La priorité 2026 est la fiabilisation du reporting énergie avant "
                  "l'audit de certification prévu au troisième trimestre.",
        "env": "Le site de Lyon concentre près de 70 % des émissions du périmètre : "
               "c'est là que se joue la trajectoire.",
        "gov": "Le comité de durabilité fonctionne, mais doit formaliser ses comptes "
               "rendus pour être opposable lors de la vérification.",
    },
)


def main():
    os.makedirs(OUT, exist_ok=True)
    scores = calculate_esg_scores(DEMO)
    content = generate_esg_content(DEMO, scores)
    logo, art = build_extras(DEMO)

    charts_dark = {"cover_art": art} if art else {}
    charts_dark.update(build_advanced_charts(DEMO, scores, light_bg=False))
    charts_light = {"cover_art": art} if art else {}
    charts_light.update(build_advanced_charts(DEMO, scores, light_bg=True))

    files = {
        "Rapport-ESG.pdf": generate_pdf_report(DEMO, scores, content, charts_light, logo_bytes=logo),
        "Presentation.pptx": generate_pptx(DEMO, scores, content, charts_dark, logo_bytes=logo),
        "Rapport-ESG.docx": generate_word_report(DEMO, scores, content, logo_bytes=logo),
        "Synthese-1-page.pdf": generate_onepager_pdf(DEMO, scores),
        "Lettre-de-mission.docx": generate_proposal_docx(DEMO, scores),
        "Questionnaire_collecte_Acme_2025.html": generate_questionnaire_html(
            DEMO.company.name, DEMO.company.reporting_year,
            DEMO.company.presenter_name).encode("utf-8"),
    }
    for name, data in files.items():
        path = os.path.join(OUT, name)
        with open(path, "wb") as f:
            f.write(data)
        print(f"  {name:42s} {len(data) // 1024:5d} Ko")

    print(f"\nScore de démonstration : {scores.total_esg_score}/100 ({scores.rating})")


if __name__ == "__main__":
    print("Génération des livrables d'exemple (données fictives)\n")
    main()
