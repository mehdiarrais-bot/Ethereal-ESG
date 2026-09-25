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
    """Gabarits éditoriaux des livrables — jetons dans report_designs.py."""
    AURORA = "aurora"
    ANNUEL = "annuel"
    INSTITUTIONNEL = "institutionnel"
    PORTRAIT = "portrait"
    TERRE = "terre"
    GALERIE = "galerie"


class ReportType(str, Enum):
    WHITE_PAPER = "white_paper"
    FULL_REPORT = "full_report"
    EXECUTIVE_SUMMARY_PDF = "executive_summary_pdf"


# ── Sub-models ────────────────────────────────────────────────────────────────
class EnvironmentalData(BaseModel):
    co2_emissions_tonnes: Optional[float] = Field(default=None, ge=0, le=1e9)
    energy_consumption_mwh: Optional[float] = Field(default=None, ge=0, le=1e9)
    renewable_energy_percent: Optional[float] = Field(default=None, ge=0, le=100)
    water_consumption_m3: Optional[float] = Field(default=None, ge=0, le=1e10)
    waste_generated_tonnes: Optional[float] = Field(default=None, ge=0, le=1e8)
    waste_recycled_percent: Optional[float] = Field(default=None, ge=0, le=100)
    biodiversity_initiatives: Optional[int] = Field(default=None, ge=0, le=9999)
    scope1_emissions: Optional[float] = Field(default=None, ge=0, le=1e9)
    scope2_emissions: Optional[float] = Field(default=None, ge=0, le=1e9)
    scope3_emissions: Optional[float] = Field(default=None, ge=0, le=1e9)

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
    total_employees: Optional[int] = Field(default=None, ge=0, le=10_000_000)
    female_employees_percent: Optional[float] = Field(default=None, ge=0, le=100)
    employee_turnover_percent: Optional[float] = Field(default=None, ge=0, le=100)
    training_hours_per_employee: Optional[float] = Field(default=None, ge=0, le=10_000)
    work_accidents: Optional[int] = Field(default=None, ge=0, le=1_000_000)
    accident_frequency_rate: Optional[float] = Field(default=None, ge=0, le=10_000)
    community_investment_eur: Optional[float] = Field(default=None, ge=0, le=1e12)
    local_suppliers_percent: Optional[float] = Field(default=None, ge=0, le=100)
    customer_satisfaction_score: Optional[float] = Field(default=None, ge=0, le=10)
    disabled_employees_percent: Optional[float] = Field(default=None, ge=0, le=100)

    @model_validator(mode='after')
    def clamp_and_clean(self):
        for field in ['community_investment_eur', 'training_hours_per_employee',
                      'accident_frequency_rate']:
            v = getattr(self, field)
            if v is not None and not math.isfinite(v):
                setattr(self, field, None)
        return self


class TaxonomyData(BaseModel):
    """Alignement Taxonomie UE (part du CA / CapEx / OpEx alignés, en %)."""
    turnover_aligned_percent: Optional[float] = Field(default=None, ge=0, le=100)
    capex_aligned_percent: Optional[float] = Field(default=None, ge=0, le=100)
    opex_aligned_percent: Optional[float] = Field(default=None, ge=0, le=100)

    @model_validator(mode='after')
    def clean(self):
        for f in ['turnover_aligned_percent', 'capex_aligned_percent', 'opex_aligned_percent']:
            v = getattr(self, f)
            if v is not None and not math.isfinite(v):
                setattr(self, f, None)
        return self


class GovernanceData(BaseModel):
    board_members: Optional[int] = Field(default=None, ge=0, le=999)
    female_board_percent: Optional[float] = Field(default=None, ge=0, le=100)
    independent_board_percent: Optional[float] = Field(default=None, ge=0, le=100)
    ethics_violations: Optional[int] = Field(default=None, ge=0, le=100_000)
    corruption_cases: Optional[int] = Field(default=None, ge=0, le=100_000)
    data_breaches: Optional[int] = Field(default=None, ge=0, le=100_000)
    csr_budget_eur: Optional[float] = Field(default=None, ge=0, le=1e12)
    esg_audit_conducted: Optional[bool] = None
    sustainability_committee: Optional[bool] = None
    # Statut de la société : le code AFEP-MEDEF ne vise que les sociétés
    # cotées qui s'y réfèrent (moitié d'indépendants, un tiers si contrôlée).
    # Sans ces réponses, aucune référence AFEP-MEDEF n'est imprimée.
    listed_company: Optional[bool] = None
    controlled_company: Optional[bool] = None

    @model_validator(mode='after')
    def clamp_and_clean(self):
        if self.csr_budget_eur is not None and not math.isfinite(self.csr_budget_eur):
            self.csr_budget_eur = None
        return self


_LOGO_RE = re.compile(r'^data:image/(png|jpeg|jpg);base64,([A-Za-z0-9+/=\r\n]+)$')
MAX_LOGO_BYTES = 1_500_000  # 1,5 Mo décodé


MAX_PHOTO_BYTES = 1_500_000  # 1,5 Mo décodé par photo (réduite côté navigateur)


def _check_image_data_url(v: str, max_bytes: int, what: str) -> str:
    """Valide une image data-URL PNG/JPEG : encodage, poids, lisibilité, taille."""
    m = _LOGO_RE.match(v) if isinstance(v, str) else None
    if not m:
        raise ValueError(f"{what} invalide : format PNG ou JPEG attendu")
    import base64, io as _io
    try:
        raw = base64.b64decode(m.group(2), validate=False)
    except Exception:
        raise ValueError(f"{what} invalide : encodage base64 illisible")
    if len(raw) > max_bytes:
        raise ValueError(f"{what} trop volumineux (max {max_bytes / 1e6:.1f} Mo)".replace(".", ","))
    try:
        from PIL import Image as PILImage
        img = PILImage.open(_io.BytesIO(raw))
        img.verify()
        img = PILImage.open(_io.BytesIO(raw))
        if img.width > 4000 or img.height > 4000:
            raise ValueError(f"{what} trop grand (max 4000×4000 pixels)")
    except ValueError:
        raise
    except Exception:
        raise ValueError(f"{what} invalide : le fichier n'est pas une image lisible")
    return v


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
    revenue_eur: Optional[float] = Field(default=None, ge=0, le=1e13)
    reporting_year: int = Field(default=2024, ge=2000, le=2035)
    target_year: int = Field(default=2030, ge=2025, le=2050)
    logo_description: Optional[str] = Field(default=None, max_length=200)
    presenter_name: Optional[str] = Field(default=None, max_length=100)
    presenter_title: Optional[str] = Field(default=None, max_length=100)
    logo_base64: Optional[str] = Field(default=None, max_length=2_100_000)
    # Initiatives/projets internes (séparés par ; ou ,), tissés dans les textes
    # pour ancrer le rapport dans la réalité de l'entreprise.
    key_initiatives: Optional[str] = Field(default=None, max_length=600)
    # Mot du dirigeant : citation libre, mise en scène en ouverture des livrables.
    ceo_quote: Optional[str] = Field(default=None, max_length=500)

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

    @field_validator('key_initiatives', mode='before')
    @classmethod
    def sanitize_initiatives(cls, v):
        if v is None or v == '':
            return None
        return sanitize_text(str(v), 600)

    @field_validator('ceo_quote', mode='before')
    @classmethod
    def sanitize_quote(cls, v):
        if v is None or v == '':
            return None
        return sanitize_text(str(v), 500)

    @field_validator('logo_base64', mode='after')
    @classmethod
    def check_logo(cls, v):
        if not v:
            return None
        return _check_image_data_url(v, MAX_LOGO_BYTES, "Logo")

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
    taxonomy: TaxonomyData = Field(default_factory=lambda: TaxonomyData())
    presentation_type: PresentationType = PresentationType.EXECUTIVE_SUMMARY
    aesthetic_theme: AestheticTheme = AestheticTheme.AURORA
    report_type: ReportType = ReportType.FULL_REPORT
    language: str = Field(default="fr", pattern=r'^(fr|en)$')
    # Référentiel visé : CSRD complet ou VSME (norme volontaire PME, EFRAG).
    # Ajuste l'analyse des écarts (exigences optionnelles vs requises).
    reporting_framework: str = Field(default="csrd", pattern=r'^(csrd|vsme)$')
    include_recommendations: bool = True
    include_cover_image: bool = True
    # Photos fournies par l'entreprise, par emplacement (cf. report_designs.
    # CLIENT_PHOTO_SLOTS) : data-URL PNG/JPEG. Un emplacement vide est comblé
    # par la banque locale de photos d'illustration.
    report_photos: Optional[dict] = None
    # Actions du plan précédent marquées « réalisées » par le consultant
    # (suivi de mission) : [{title, year}, ...]
    completed_actions: Optional[list] = None

    @field_validator('aesthetic_theme', mode='before')
    @classmethod
    def map_legacy_theme(cls, v):
        """Les dossiers enregistrés avant le 2026-09-23 portent les sept
        anciens thèmes : ils sont relus sous le gabarit le plus proche."""
        from report_designs import LEGACY_THEMES
        return LEGACY_THEMES.get(v, v) if isinstance(v, str) else v

    @field_validator('report_photos', mode='before')
    @classmethod
    def check_photos(cls, v):
        if not v:
            return None
        if not isinstance(v, dict):
            raise ValueError("Photos : dictionnaire emplacement -> image attendu")
        from report_designs import CLIENT_PHOTO_SLOTS
        out = {}
        for slot, data_url in v.items():
            if slot not in CLIENT_PHOTO_SLOTS:
                raise ValueError(f"Emplacement photo inconnu : {slot}")
            if data_url:
                out[slot] = _check_image_data_url(data_url, MAX_PHOTO_BYTES, "Photo")
        return out or None

    @field_validator('completed_actions', mode='before')
    @classmethod
    def check_completed(cls, v):
        if not v:
            return None
        out = []
        for item in v:
            try:
                title = sanitize_text(str(item["title"]), 200)
                if title:
                    out.append({"title": title, "year": int(item.get("year") or 0)})
            except (KeyError, TypeError, ValueError):
                continue
        return out[:12] or None

    # Analyses libres du consultant, affichées dans des encarts dédiés
    # « L'analyse du consultant » : {global, env, social, gov}
    consultant_notes: Optional[dict] = None

    @field_validator('consultant_notes', mode='before')
    @classmethod
    def check_notes(cls, v):
        if not v or not isinstance(v, dict):
            return None
        out = {}
        for key in ("global", "env", "social", "gov"):
            note = v.get(key)
            if note and str(note).strip():
                out[key] = sanitize_text(str(note), 1000)
        return out or None

    # Couleurs de marque du client : {primary: '#RRGGBB', accent: '#RRGGBB'}.
    # Décline le thème choisi aux couleurs du client (PPTX, PDF, graphiques).
    custom_colors: Optional[dict] = None

    @field_validator('custom_colors', mode='before')
    @classmethod
    def check_custom_colors(cls, v):
        if not v:
            return None
        import re as _re
        hx = _re.compile(r'^#?[0-9a-fA-F]{6}$')
        try:
            p, a = str(v.get("primary", "")), str(v.get("accent", ""))
            if hx.match(p) and hx.match(a):
                return {"primary": p if p.startswith('#') else '#' + p,
                        "accent": a if a.startswith('#') else '#' + a}
        except AttributeError:
            pass
        return None  # couleurs invalides : thème standard

    # Scores de l'exercice précédent (issus de l'historique du dossier client)
    # pour afficher l'évolution année sur année dans les livrables.
    # Forme : {year, env, social, gov, total}
    previous_scores: Optional[dict] = None
    # Historique complet des exercices du dossier client (trajectoire
    # pluriannuelle) : [{year, env, social, gov, total}, ...]
    score_history: Optional[list] = None

    @field_validator('score_history', mode='before')
    @classmethod
    def check_history(cls, v):
        if not v:
            return None
        out = []
        for h in v:
            try:
                out.append({"year": int(h["year"]), "env": float(h["env"]),
                            "social": float(h["social"]), "gov": float(h["gov"]),
                            "total": float(h["total"])})
            except (KeyError, TypeError, ValueError):
                continue  # entrée incomplète ignorée
        out.sort(key=lambda h: h["year"])
        return out[:15] or None

    @field_validator('previous_scores', mode='before')
    @classmethod
    def check_previous(cls, v):
        if not v:
            return None
        try:
            return {"year": int(v["year"]), "env": float(v["env"]),
                    "social": float(v["social"]), "gov": float(v["gov"]),
                    "total": float(v["total"])}
        except (KeyError, TypeError, ValueError):
            return None  # historique incomplet : ignoré silencieusement


class ESGScores(BaseModel):
    # None : pilier sans aucun indicateur, ou moins de deux piliers pour le
    # global (esg_calculator.global_score). Jamais de valeur par défaut.
    environmental_score: Optional[float]
    social_score: Optional[float]
    governance_score: Optional[float]
    total_esg_score: Optional[float]
    carbon_intensity: Optional[float] = None
    energy_intensity: Optional[float] = None
    gender_parity_index: Optional[float] = None
    safety_index: Optional[float] = None
    governance_quality: Optional[float] = None
    rating: Optional[str]
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
