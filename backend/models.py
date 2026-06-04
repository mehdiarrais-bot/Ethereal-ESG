from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class PresentationType(str, Enum):
    EXECUTIVE_SUMMARY = "executive_summary"
    INVESTOR_DECK = "investor_deck"
    DETAILED_REPORT = "detailed_report"
    STAKEHOLDER_BRIEF = "stakeholder_brief"
    ANNUAL_REPORT = "annual_report"


class AestheticTheme(str, Enum):
    CORPORATE_BLUE = "corporate_blue"
    GREEN_NATURE = "green_nature"
    DARK_PREMIUM = "dark_premium"
    MINIMAL_WHITE = "minimal_white"


class ReportType(str, Enum):
    WHITE_PAPER = "white_paper"
    FULL_REPORT = "full_report"
    EXECUTIVE_SUMMARY_PDF = "executive_summary_pdf"


class EnvironmentalData(BaseModel):
    co2_emissions_tonnes: Optional[float] = None
    energy_consumption_mwh: Optional[float] = None
    renewable_energy_percent: Optional[float] = None
    water_consumption_m3: Optional[float] = None
    waste_generated_tonnes: Optional[float] = None
    waste_recycled_percent: Optional[float] = None
    biodiversity_initiatives: Optional[int] = None
    scope1_emissions: Optional[float] = None
    scope2_emissions: Optional[float] = None
    scope3_emissions: Optional[float] = None


class SocialData(BaseModel):
    total_employees: Optional[int] = None
    female_employees_percent: Optional[float] = None
    employee_turnover_percent: Optional[float] = None
    training_hours_per_employee: Optional[float] = None
    work_accidents: Optional[int] = None
    accident_frequency_rate: Optional[float] = None
    community_investment_eur: Optional[float] = None
    local_suppliers_percent: Optional[float] = None
    customer_satisfaction_score: Optional[float] = None
    disabled_employees_percent: Optional[float] = None


class GovernanceData(BaseModel):
    board_members: Optional[int] = None
    female_board_percent: Optional[float] = None
    independent_board_percent: Optional[float] = None
    ethics_violations: Optional[int] = None
    corruption_cases: Optional[int] = None
    data_breaches: Optional[int] = None
    csr_budget_eur: Optional[float] = None
    esg_audit_conducted: Optional[bool] = None
    sustainability_committee: Optional[bool] = None


class CompanyInfo(BaseModel):
    name: str
    sector: str
    country: str
    revenue_eur: Optional[float] = None
    reporting_year: int = 2024
    logo_description: Optional[str] = None


class ESGRequest(BaseModel):
    company: CompanyInfo
    environmental: EnvironmentalData
    social: SocialData
    governance: GovernanceData
    presentation_type: PresentationType = PresentationType.EXECUTIVE_SUMMARY
    aesthetic_theme: AestheticTheme = AestheticTheme.CORPORATE_BLUE
    report_type: ReportType = ReportType.FULL_REPORT
    language: str = "fr"
    include_recommendations: bool = True
    include_benchmarks: bool = True


class ESGScores(BaseModel):
    environmental_score: float
    social_score: float
    governance_score: float
    total_esg_score: float
    carbon_intensity: Optional[float] = None
    energy_intensity: Optional[float] = None
    gender_parity_index: Optional[float] = None
    safety_index: Optional[float] = None
    governance_quality: Optional[float] = None
    rating: str
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
