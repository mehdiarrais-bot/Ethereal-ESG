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
    SUNSET_TERRACOTTA = "sunset_terracotta"
    OCEAN_DEEP = "ocean_deep"
    ROYAL_PURPLE = "royal_purple"


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


_LOGO_RE = re.compile(r'^data:image/(png|jpeg|jpg);base64,([A-Za-z0-9+/=\r\n]+)$')
MAX_LOGO_BYTES = 1_500_000  # 1,5 Mo décodé


def decode_logo(data_url: Optional[str]) -> Optional[bytes]:
    """Décode un logo data-URL déjà validé. Retourne None si absent/invalide."""
    if not data_url:
        return None
    m = _LOGO_RE.match(data_url)
    if not m:
        return None
    import base64
    try:
        return base64.b64decode(m.group(2), validate=False)
    except Exception:
        return None


class CompanyInfo(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    sector: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=1, max_length=100)
    revenue_eur: Optional[float] = Field(None, ge=0, le=1e13)
    reporting_year: int = Field(2024, ge=2000, le=2035)
    logo_description: Optional[str] = Field(None, max_length=200)
    presenter_name: Optional[str] = Field(None, max_length=100)
    presenter_title: Optional[str] = Field(None, max_length=100)
    logo_base64: Optional[str] = Field(None, max_length=2_100_000)

    @field_validator('name', 'sector', 'country', mode='before')
    @classmethod
    def sanitize(cls, v):
        return sanitize_text(str(v) if v is not None else '')

    @field_validator('presenter_name', 'presenter_title', mode='before')
    @classmethod
    def sanitize_optional(cls, v):
        if v is None or v == '':
            return None
        return sanitize_text(str(v), 100)

    @field_validator('logo_base64', mode='after')
    @classmethod
    def check_logo(cls, v):
        if not v:
            return None
        m = _LOGO_RE.match(v)
        if not m:
            raise ValueError("Logo invalide : format PNG ou JPEG attendu")
        import base64, io as _io
        try:
            raw = base64.b64decode(m.group(2), validate=False)
        except Exception:
            raise ValueError("Logo invalide : encodage base64 illisible")
        if len(raw) > MAX_LOGO_BYTES:
            raise ValueError("Logo trop volumineux (max 1,5 Mo)")
        try:
            from PIL import Image as PILImage
            img = PILImage.open(_io.BytesIO(raw))
            img.verify()
            img = PILImage.open(_io.BytesIO(raw))
            if img.width > 4000 or img.height > 4000:
                raise ValueError("Logo trop grand (max 4000×4000 pixels)")
        except ValueError:
            raise
        except Exception:
            raise ValueError("Logo invalide : le fichier n'est pas une image lisible")
        return v

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
    include_cover_image: bool = True


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
