import math
import re
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from enum import Enum

# ── Sanitisation ──────────────────────────────────────────────────────────────
_HTML_TAG_RE = re.compile(r'<[^>]+>')
_CTRL_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')
MAX_TEXT_LEN = 200


def sanitize_text(v: str, max_len: int = MAX_TEXT_LEN) -> str:
    if not isinstance(v, str):
        return str(v)[:max_len]
    v = _HTML_TAG_RE.sub('', v)   # retire balises HTML/script
    v = _CTRL_RE.sub('', v)        # retire caractères de contrôle
    return v.strip()[:max_len]


def safe_float(v, lo: float = 0.0, hi: float = 1e12) -> Optional[float]:
    """Clamp + reject NaN/Inf."""
    if v is None:
        return None
    if not math.isfinite(v):
        return None
    return max(lo, min(hi, v))


# ── Enums ─────────────────────────────────────────────────────────────────────
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


# ── Sub-models ────────────────────────────────────────────────────────────────
class EnvironmentalData(BaseModel):
    co2_emissions_tonnes: Optional[float] = Field(None, ge=0, le=1e9)
    energy_consumption_mwh: Optional[float] = Field(None, ge=0, le=1e9)
    renewable_energy_percent: Optional[float] = Field(None, ge=0, le=100)
    water_consumption_m3: Optional[float] = Field(None, ge=0, le=1e10)
    waste_generated_tonnes: Optional[float] = Field(None, ge=0, le=1e8)
    waste_recycled_percent: Optional[float] = Field(None, ge=0, le=100)
    biodiversity_initiatives: Optional[int] = Field(None, ge=0, le=9999)
    scope1_emissions: Optional[float] = Field(None, ge=0, le=1e9)
    scope2_emissions: Optional[float] = Field(None, ge=0, le=1e9)
    scope3_emissions: Optional[float] = Field(None, ge=0, le=1e9)

    @model_validator(mode='after')
    def clamp_and_clean(self):
        for field in ['co2_emissions_tonnes', 'energy_consumption_mwh',
                      'water_consumption_m3', 'waste_generated_tonnes',
                      'scope1_emissions', 'scope2_emissions', 'scope3_emissions']:
            v = getattr(self, field)
            if v is not None and not math.isfinite(v):
                setattr(self, field, None)
        return self


class SocialData(BaseModel):
    total_employees: Optional[int] = Field(None, ge=0, le=10_000_000)
    female_employees_percent: Optional[float] = Field(None, ge=0, le=100)
    employee_turnover_percent: Optional[float] = Field(None, ge=0, le=100)
    training_hours_per_employee: Optional[float] = Field(None, ge=0, le=10_000)
    work_accidents: Optional[int] = Field(None, ge=0, le=1_000_000)
    accident_frequency_rate: Optional[float] = Field(None, ge=0, le=10_000)
    community_investment_eur: Optional[float] = Field(None, ge=0, le=1e12)
    local_suppliers_percent: Optional[float] = Field(None, ge=0, le=100)
    customer_satisfaction_score: Optional[float] = Field(None, ge=0, le=10)
    disabled_employees_percent: Optional[float] = Field(None, ge=0, le=100)

    @model_validator(mode='after')
    def clamp_and_clean(self):
        for field in ['community_investment_eur', 'training_hours_per_employee',
                      'accident_frequency_rate']:
            v = getattr(self, field)
            if v is not None and not math.isfinite(v):
                setattr(self, field, None)
        return self


class GovernanceData(BaseModel):
    board_members: Optional[int] = Field(None, ge=0, le=999)
    female_board_percent: Optional[float] = Field(None, ge=0, le=100)
    independent_board_percent: Optional[float] = Field(None, ge=0, le=100)
    ethics_violations: Optional[int] = Field(None, ge=0, le=100_000)
    corruption_cases: Optional[int] = Field(None, ge=0, le=100_000)
    data_breaches: Optional[int] = Field(None, ge=0, le=100_000)
    csr_budget_eur: Optional[float] = Field(None, ge=0, le=1e12)
    esg_audit_conducted: Optional[bool] = None
    sustainability_committee: Optional[bool] = None

    @model_validator(mode='after')
    def clamp_and_clean(self):
        if self.csr_budget_eur is not None and not math.isfinite(self.csr_budget_eur):
            self.csr_budget_eur = None
        return self


class CompanyInfo(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    sector: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=1, max_length=100)
    revenue_eur: Optional[float] = Field(None, ge=0, le=1e13)
    reporting_year: int = Field(2024, ge=2000, le=2035)
    logo_description: Optional[str] = Field(None, max_length=200)

    @field_validator('name', 'sector', 'country', mode='before')
    @classmethod
    def sanitize(cls, v):
        return sanitize_text(str(v) if v is not None else '')

    @field_validator('revenue_eur', mode='after')
    @classmethod
    def check_finite(cls, v):
        if v is not None and not math.isfinite(v):
            return None
        return v


class ESGRequest(BaseModel):
    company: CompanyInfo
    environmental: EnvironmentalData
    social: SocialData
    governance: GovernanceData
    presentation_type: PresentationType = PresentationType.EXECUTIVE_SUMMARY
    aesthetic_theme: AestheticTheme = AestheticTheme.CORPORATE_BLUE
    report_type: ReportType = ReportType.FULL_REPORT
    language: str = Field("fr", pattern=r'^(fr|en)$')
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
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
