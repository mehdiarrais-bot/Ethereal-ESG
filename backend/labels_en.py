"""
Libellés anglais des indicateurs : (libellé, unité, aide).

Source unique partagée par le questionnaire anglais (affichage et en-têtes
du CSV exporté) et par import_data (synonymes reconnus à la réimportation).
Module sans dépendance pour éviter tout import circulaire.
"""

FIELD_META_EN = {
    "name": ("Company name", "", "Legal name as it should appear on the report."),
    "sector": ("Business sector", "", "E.g. Manufacturing, Services, Transport, Food processing."),
    "country": ("Country", "", ""),
    "revenue_eur": ("Revenue", "€", "For the reporting year. Used to compute intensities."),
    "reporting_year": ("Reporting year", "", "The year the data relates to."),
    "target_year": ("Target horizon", "", "Target year of your trajectory, often 2030."),
    "presenter_name": ("Contact person", "", "Who will present the report internally."),
    "presenter_title": ("Their position", "", ""),

    "co2_emissions_tonnes": ("Total CO₂ emissions", "t CO₂e", "All scopes combined, if known."),
    "energy_consumption_mwh": ("Energy consumption", "MWh", "All energy: electricity, gas, fuels."),
    "renewable_energy_percent": ("Renewable energy share", "%", "In your total energy mix."),
    "water_consumption_m3": ("Water consumption", "m³", "Volume withdrawn over the year."),
    "waste_generated_tonnes": ("Waste generated", "t", ""),
    "waste_recycled_percent": ("Waste recycling rate", "%", ""),
    "biodiversity_initiatives": ("Biodiversity initiatives", "count", "Concrete actions: planting, protected areas, etc."),
    "scope1_emissions": ("Scope 1 emissions", "t CO₂e", "Direct emissions: your boilers, your vehicle fleet."),
    "scope2_emissions": ("Scope 2 emissions", "t CO₂e", "From purchased energy, mainly electricity."),
    "scope3_emissions": ("Scope 3 emissions", "t CO₂e", "Value chain: purchases, transport, use of sold products."),

    "total_employees": ("Total headcount", "people", "Full-time equivalent at year end."),
    "female_employees_percent": ("Share of women in workforce", "%", ""),
    "employee_turnover_percent": ("Employee turnover rate", "%", "Departures relative to average headcount."),
    "training_hours_per_employee": ("Training per employee", "h/yr", "Average training hours per person."),
    "work_accidents": ("Workplace accidents", "count", "With lost time, over the year."),
    "accident_frequency_rate": ("Accident frequency rate", "FR", "Lost-time accidents × 1,000,000 / hours worked."),
    "community_investment_eur": ("Community investment", "€", "Sponsorship, local partnerships, foundation."),
    "local_suppliers_percent": ("Share of local suppliers", "%", ""),
    "customer_satisfaction_score": ("Customer satisfaction", "/10", ""),
    "disabled_employees_percent": ("Employees with disabilities", "%", ""),

    "board_members": ("Board members", "count", "Board of directors or supervisory board."),
    "female_board_percent": ("Women on the board", "%", "French legal reference threshold: 40%."),
    "independent_board_percent": ("Independent directors", "%", "AFEP-MEDEF reference: 50%."),
    "ethics_violations": ("Ethics breaches identified", "count", "Over the year. Zero is a valid answer."),
    "corruption_cases": ("Corruption cases", "count", ""),
    "data_breaches": ("Cybersecurity incidents", "count", "Reported data breaches."),
    "csr_budget_eur": ("CSR budget", "€", "Resources dedicated to the approach."),
    "esg_audit_conducted": ("Third-party verified reporting", "", "Has an independent body audited your ESG data?"),
    "sustainability_committee": ("Sustainability committee", "", "Is there a dedicated body at board level?"),

    "turnover_aligned_percent": ("Taxonomy-aligned revenue", "%", ""),
    "capex_aligned_percent": ("Aligned investments (CapEx)", "%", ""),
    "opex_aligned_percent": ("Aligned expenses (OpEx)", "%", ""),
}
