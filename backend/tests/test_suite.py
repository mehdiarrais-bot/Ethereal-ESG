"""
Suite de tests de la plateforme ESG.

Lancer depuis backend/ :  python -m pytest tests/ -q
Couvre : génération des 5 livrables (FR/EN × thèmes), endpoints dossiers
clients (CRUD, statut, backup), branding, grilles carbone sectorielles,
qualité du texte (pas de « (s) » de publipostage), pack complet.
"""
import io
import sys
import os
import zipfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (ESGRequest, CompanyInfo, EnvironmentalData, SocialData,
                    GovernanceData, TaxonomyData)
from esg_calculator import calculate_esg_scores
from content_generator import generate_esg_content


def make_request(lang="fr", theme="corporate_blue", **overrides):
    base = dict(
        company=CompanyInfo(name="Acme Industries", sector="Industrie manufacturière",
                            country="France", revenue_eur=48_000_000,
                            reporting_year=2025, target_year=2030,
                            presenter_name="J. Martin", presenter_title="Directrice Générale"),
        environmental=EnvironmentalData(co2_emissions_tonnes=8200, scope1_emissions=1200,
                                        scope2_emissions=2100, scope3_emissions=4900,
                                        renewable_energy_percent=42, waste_recycled_percent=63),
        social=SocialData(female_employees_percent=34, training_hours_per_employee=22,
                          accident_frequency_rate=6.2, employee_count=320),
        governance=GovernanceData(esg_audit_conducted=False, sustainability_committee=True,
                                  data_breaches=1, independent_board_percent=45),
        taxonomy=TaxonomyData(turnover_aligned_percent=38, capex_aligned_percent=52),
        language=lang, aesthetic_theme=theme,
        include_recommendations=True, include_benchmarks=True,
    )
    base.update(overrides)
    return ESGRequest(**base)


@pytest.fixture(scope="module")
def scores():
    return calculate_esg_scores(make_request())


# ── Livrables : chaque format, chaque langue, plusieurs thèmes ────────────

THEMES = ["corporate_blue", "dark_premium", "minimal_white", "green_nature"]


@pytest.mark.parametrize("lang", ["fr", "en"])
@pytest.mark.parametrize("theme", THEMES)
def test_pptx_generates(lang, theme):
    from ppt_generator import generate_pptx
    from main import build_advanced_charts
    r = make_request(lang, theme)
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    data = generate_pptx(r, s, c, build_advanced_charts(r, s, light_bg=False))
    assert data[:2] == b"PK"


@pytest.mark.parametrize("lang", ["fr", "en"])
@pytest.mark.parametrize("theme", THEMES)
def test_pdf_generates(lang, theme):
    from report_generator import generate_pdf_report
    from main import build_advanced_charts
    r = make_request(lang, theme)
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    data = generate_pdf_report(r, s, c, build_advanced_charts(r, s, light_bg=True))
    assert data[:4] == b"%PDF"


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_docx_and_proposal_generate(lang):
    from docx_generator import generate_word_report
    from proposal_generator import generate_proposal_docx
    r = make_request(lang)
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    assert generate_word_report(r, s, c)[:2] == b"PK"
    assert generate_proposal_docx(r, s)[:2] == b"PK"


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_onepager_single_page(lang):
    import fitz
    from onepager_generator import generate_onepager_pdf
    r = make_request(lang)
    s = calculate_esg_scores(r)
    data = generate_onepager_pdf(r, s)
    assert data[:4] == b"%PDF"
    assert fitz.open(stream=data, filetype="pdf").page_count == 1


def test_yoy_and_trend_sections():
    import fitz
    from report_generator import generate_pdf_report
    from main import build_advanced_charts
    r = make_request(
        previous_scores={"year": 2024, "env": 58.0, "social": 55.0, "gov": 60.0, "total": 56.5},
        score_history=[
            {"year": 2023, "env": 48.0, "social": 50.0, "gov": 55.0, "total": 50.4},
            {"year": 2024, "env": 58.0, "social": 55.0, "gov": 60.0, "total": 56.5},
        ])
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    assert "2024" in c["executive_summary"]  # phrase d'évolution N-1
    pdf = generate_pdf_report(r, s, c, build_advanced_charts(r, s, light_bg=True))
    doc = fitz.open(stream=pdf, filetype="pdf")
    full = "".join(doc[i].get_text() for i in range(doc.page_count))
    assert "trajectoire ESG mesurée" in full  # section trajectoire présente


# ── Qualité du texte ──────────────────────────────────────────────────────

@pytest.mark.parametrize("lang", ["fr", "en"])
def test_no_mail_merge_plurals(lang):
    """Aucun « (s) » de publipostage dans le contenu généré."""
    r = make_request(lang)
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    blob = " ".join(str(v) for v in c.values() if v)
    blob += " " + " ".join(s.strengths + s.weaknesses)
    assert "(s)" not in blob


def test_no_generated_automatically_tell():
    from i18n import L
    for lang in ("fr", "en"):
        assert "automatiq" not in L(lang)["gen_auto"].lower()
        assert "automatic" not in L(lang)["gen_auto"].lower()


def test_initiatives_and_quote_injected():
    r = make_request(company=CompanyInfo(
        name="Acme", sector="Industrie", country="France", revenue_eur=48e6,
        reporting_year=2025, key_initiatives="programme Cap Climat",
        ceo_quote="Notre cap est fixé."))
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    assert "Cap Climat" in c["executive_summary"]
    assert r.company.ceo_quote == "Notre cap est fixé."


def test_consultant_notes_rendered_and_absent():
    import fitz
    from report_generator import generate_pdf_report
    from main import build_advanced_charts
    notes = {"global": "Note de synthese du consultant.",
             "env": "Le site de Lyon concentre les emissions."}
    r = make_request(consultant_notes=notes)
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    pdf = generate_pdf_report(r, s, c, build_advanced_charts(r, s, light_bg=True))
    doc = fitz.open(stream=pdf, filetype="pdf")
    full = "".join(doc[i].get_text() for i in range(doc.page_count))
    assert full.count("ANALYSE DU CONSULTANT") == 2
    assert "site de Lyon" in full
    # sans notes : aucun encart
    r2 = make_request()
    c2 = generate_esg_content(r2, s)
    pdf2 = generate_pdf_report(r2, s, c2, build_advanced_charts(r2, s, light_bg=True))
    doc2 = fitz.open(stream=pdf2, filetype="pdf")
    assert not any("ANALYSE DU CONSULTANT" in doc2[i].get_text() for i in range(doc2.page_count))


# ── Scoring sectoriel & diagnostic ────────────────────────────────────────

def test_sector_carbon_grids_differ():
    def env_score(sector):
        r = make_request(company=CompanyInfo(name="X", sector=sector, country="France",
                                             revenue_eur=48e6, reporting_year=2025))
        return calculate_esg_scores(r).environmental_score
    services, industry = env_score("Services"), env_score("Industrie manufacturière")
    assert industry > services  # même intensité, grille sectorielle différente


def test_compliance_assessment_statuses():
    from content_generator import compliance_assessment
    r = make_request()
    rows = compliance_assessment(r, calculate_esg_scores(r))
    assert len(rows) >= 6
    statuses = {row["status"] for row in rows}
    assert statuses <= {"ok", "partial", "no", "na"}
    # audit absent dans la fixture → non conforme attendu
    audit = next(row for row in rows if "tiers" in row["req"] or "assurance" in row["req"].lower())
    assert audit["status"] == "no"


def test_risks_have_ratings_sorted():
    from content_generator import risks_opportunities
    r = make_request()
    ro = risks_opportunities(r, calculate_esg_scores(r))
    prios = [item["priority"] for item in ro["risks"]]
    assert prios == sorted(prios)  # P1 avant P2 avant P3
    assert all(item.get("impact") and item.get("likelihood") for item in ro["risks"])


# ── Branding ──────────────────────────────────────────────────────────────

def test_branding_deterministic_and_distinct():
    from branding import auto_brand, validate_colors
    a, b = auto_brand("Acme Industries"), auto_brand("BioVallée SAS")
    assert a == auto_brand("Acme Industries")
    assert a != b
    assert validate_colors(a) is not None
    assert validate_colors({"primary": "oops", "accent": "#zzz"}) is None
    # primaire trop claire assombrie (elle porte du texte blanc)
    p, _ = validate_colors({"primary": "#FFFFFF", "accent": "#3366CC"})
    from branding import _luminance
    assert _luminance(p) <= 0.45


def test_branded_generation():
    from report_generator import generate_pdf_report
    from main import build_advanced_charts
    from branding import auto_brand
    r = make_request(custom_colors=auto_brand("Acme Industries"))
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    assert generate_pdf_report(r, s, c, build_advanced_charts(r, s, light_bg=True))[:4] == b"%PDF"


# ── API : dossiers clients & pack ─────────────────────────────────────────

@pytest.fixture()
def client(tmp_path, monkeypatch):
    import client_store
    monkeypatch.setattr(client_store, "DATA_DIR", str(tmp_path))
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)


FORM = {
    "company": {"name": "Acme", "sector": "Industrie", "country": "France",
                "revenue_eur": 48e6, "reporting_year": 2025},
    "environmental": {"co2_emissions_tonnes": 8200},
    "social": {}, "governance": {}, "language": "fr",
}


def test_clients_crud_and_history(client):
    cid = client.post("/api/clients", json={"form": FORM}).json()["id"]
    # même exercice : remplacement, pas de doublon
    assert len(client.post("/api/clients", json={"id": cid, "form": FORM}).json()["score_history"]) == 1
    # nouvel exercice : historique complété
    f2 = dict(FORM); f2["company"] = dict(FORM["company"], reporting_year=2026)
    hist = client.post("/api/clients", json={"id": cid, "form": f2}).json()["score_history"]
    assert [h["year"] for h in hist] == [2025, 2026]
    # statut CRM
    assert client.patch(f"/api/clients/{cid}/status", json={"status": "signed"}).json()["status"] == "signed"
    assert client.patch(f"/api/clients/{cid}/status", json={"status": "zzz"}).status_code == 422
    # ids invalides
    assert client.get("/api/clients/zzz").status_code in (404, 422)
    assert client.post("/api/clients", json={"form": {"company": {}}}).status_code == 422
    # suppression
    assert client.delete(f"/api/clients/{cid}").status_code == 200
    assert client.get("/api/clients").json() == []


def test_backup_roundtrip(client):
    cid = client.post("/api/clients", json={"form": FORM}).json()["id"]
    client.patch(f"/api/clients/{cid}/status", json={"status": "delivered"})
    z = client.get("/api/clients-export")
    assert z.content[:2] == b"PK"
    client.delete(f"/api/clients/{cid}")
    r = client.post("/api/clients-import",
                    files={"file": ("b.zip", z.content, "application/zip")})
    assert r.json()["imported"] == 1
    restored = client.get("/api/clients").json()[0]
    assert restored["id"] == cid and restored["status"] == "delivered"


def test_pack_contains_five_deliverables(client):
    r = client.post("/api/generate/pack", json=FORM)
    assert r.status_code == 200
    names = zipfile.ZipFile(io.BytesIO(r.content)).namelist()
    assert len(names) == 5
    exts = sorted(n.rsplit(".", 1)[1] for n in names)
    assert exts == ["docx", "docx", "pdf", "pdf", "pptx"]
