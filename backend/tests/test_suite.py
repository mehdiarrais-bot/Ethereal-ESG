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


def _completed_actions_pdf_text(actions):
    """Texte du PDF, espaces normalisés. ReportLab coupe les paragraphes en
    fin de ligne selon la largeur disponible (dépend du thème/de la police) ;
    PyMuPDF restitue ces coupures comme de vrais retours à la ligne. On les
    aplatit ici pour tester le contenu tel qu'il se lit, pas la position du
    retour à la ligne — sinon le test devient fragile au thème utilisé."""
    import re
    import fitz
    from report_generator import generate_pdf_report
    from main import build_advanced_charts
    r = make_request(completed_actions=actions)
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    pdf = generate_pdf_report(r, s, c, build_advanced_charts(r, s, light_bg=True))
    doc = fitz.open(stream=pdf, filetype="pdf")
    raw = "".join(doc[i].get_text() for i in range(doc.page_count))
    return re.sub(r"\s+", " ", raw)


def test_completed_action_renders_callout_and_sentence():
    """Une action cochée -> encart "Actions engagées" + phrase de synthèse
    présents, et le mot "preuve" n'apparaît nulle part (verrouille qu'il ne
    soit pas réintroduit — décision explicite du 2026-09-01 : l'outil
    reporte une déclaration du cabinet, il ne prouve rien). Le titre de
    l'encart a été harmonisé le même jour pour ne plus affirmer une
    réalisation ("Actions réalisées") que la phrase en dessous nuance déjà."""
    full = _completed_actions_pdf_text(
        [{"title": "Créer un comité de durabilité au conseil", "year": 2024}])
    assert "ACTIONS ENGAGÉES" in full.upper()
    assert "déclarée engagée" in full
    assert "Créer un comité de durabilité au conseil" in full
    assert "preuve" not in full.lower()


def test_no_completed_action_omits_callout_and_sentence():
    """Aucune action cochée -> ni encart, ni phrase de synthèse."""
    full = _completed_actions_pdf_text([])
    assert "ACTIONS ENGAGÉES" not in full.upper()
    assert "déclarée" not in full and "déclarées" not in full
    assert "preuve" not in full.lower()


def test_completed_actions_singular_plural_agreement():
    """« une action … engagée » au singulier, « N actions … engagées » au
    pluriel — pas de « (s) » de publipostage, pas de désaccord."""
    one = {"title": "Créer un comité de durabilité au conseil", "year": 2024}
    two = [one, {"title": "Porter la formation à 20h/employé/an minimum", "year": 2024}]

    r1 = make_request(completed_actions=[one])
    s1 = calculate_esg_scores(r1)
    exec1 = generate_esg_content(r1, s1)["executive_summary"]
    assert "une action est déclarée engagée : « Créer un comité de durabilité au conseil »." in exec1
    assert "(s)" not in exec1

    r2 = make_request(completed_actions=two)
    s2 = calculate_esg_scores(r2)
    exec2 = generate_esg_content(r2, s2)["executive_summary"]
    assert ("deux actions sont déclarées engagées, dont "
            "« Créer un comité de durabilité au conseil » "
            "et « Porter la formation à 20h/employé/an minimum ».") in exec2
    assert "(s)" not in exec2

    # Anglais : même exigence d'accord, formulation retenue
    r3 = make_request(lang="en", completed_actions=two)
    s3 = calculate_esg_scores(r3)
    exec3 = generate_esg_content(r3, s3)["executive_summary"]
    assert ('two actions are reported as underway, including '
            '"Créer un comité de durabilité au conseil" '
            'and "Porter la formation à 20h/employé/an minimum".') in exec3
    assert "proof" not in exec3.lower() and "(s)" not in exec3


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
    assert statuses <= {"ok", "partial", "no", "na", "oos"}
    # audit absent dans la fixture → non conforme attendu
    audit = next(row for row in rows if "tiers" in row["req"] or "assurance" in row["req"].lower())
    assert audit["status"] == "no"



def _gap_rows(framework):
    """Tableau d'écarts pour une entreprise dont l'audit et le Scope 3 manquent."""
    from content_generator import compliance_assessment
    r = ESGRequest(
        company=CompanyInfo(name="X", sector="Industrie", country="France",
                            revenue_eur=48e6, reporting_year=2025),
        environmental=EnvironmentalData(co2_emissions_tonnes=8200, scope1_emissions=1200,
                                        scope2_emissions=2100),   # Scope 3 absent
        social=SocialData(female_employees_percent=34),
        governance=GovernanceData(esg_audit_conducted=False,      # audit connu : non
                                  sustainability_committee=True),
        language="fr", reporting_framework=framework)
    return {row["req"]: row for row in compliance_assessment(r, calculate_esg_scores(r))}


def test_vsme_never_fabricates_reference_codes():
    """Aucune référence ne doit être réécrite : « VSME/ESRS … » n'existe pas."""
    csrd, vsme = _gap_rows("csrd"), _gap_rows("vsme")
    for req, row in vsme.items():
        assert "VSME/" not in row["ref"], f"référence fabriquée : {row['ref']}"
        # La référence citée reste strictement celle du texte d'origine
        assert row["ref"] == csrd[req]["ref"], f"référence réécrite pour « {req} »"


def test_vsme_statuses_frozen():
    """Gèle les reclassements VSME : seuls ces trois passent hors périmètre,
    et uniquement quand l'exigence n'est pas satisfaite."""
    csrd, vsme = _gap_rows("csrd"), _gap_rows("vsme")
    hors_perimetre = {req for req, row in vsme.items() if row["status"] == "oos"}
    assert hors_perimetre == {
        "Émissions de la chaîne de valeur (Scope 3)",
        "Vérification du reporting par un tiers",
        "Publication des indicateurs Taxonomie UE",
    }, hors_perimetre
    # Toutes les autres lignes gardent exactement leur statut CSRD
    for req, row in vsme.items():
        if req not in hors_perimetre:
            assert row["status"] == csrd[req]["status"], f"statut modifié pour « {req} »"


def test_vsme_out_of_scope_is_not_not_reported():
    """Une donnée connue mais non exigée ne doit pas s'afficher « Non renseigné »."""
    from i18n import L
    vsme = _gap_rows("vsme")
    audit = vsme["Vérification du reporting par un tiers"]
    assert audit["status"] == "oos" and audit["status"] != "na"
    assert L("fr")["st_oos"] != L("fr")["st_na"]
    # La note ne rattache l'exigence à aucun module de la norme
    assert "module" not in audit["note"].lower()
    assert "optionnel" not in audit["note"].lower()


def test_vsme_out_of_scope_excluded_from_engagement_letter_gaps():
    """Une exigence hors périmètre n'est pas un écart à vendre au prospect."""
    vsme = _gap_rows("vsme")
    gaps = [r for r in vsme.values() if r["status"] in ("no", "partial")]
    assert all(r["status"] != "oos" for r in gaps)
    assert "Vérification du reporting par un tiers" not in {r["req"] for r in gaps}


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


# ── Glossaire ─────────────────────────────────────────────────────────────

# ── Élision devant la raison sociale ──────────────────────────────────────

@pytest.mark.parametrize("nom,attendu", [
    ("EcoGroup", True), ("Air Liquide", True), ("Orange", True),
    ("Élan Conseil", True), ("Œnologie SAS", True), ("Ubisoft", True),
    ("Total", False), ("Michelin", False), ("Société Générale", False),
    # h : jamais elide, faute de pouvoir distinguer h muet et h aspire
    ("Hermès", False), ("Honda", False),
    # y : jamais elide non plus ("d'Yves" serait juste, "d'Yaourts" faux)
    ("Yves Rocher", False), ("Yaourts du Nord", False),
    # un nom commencant par un chiffre ne s'elide pas
    ("1Energie", False), ("3M France", False),
])
def test_detection_elision(nom, attendu):
    from content_generator import besoin_elision
    assert besoin_elision(nom) is attendu, f"{nom!r} mal detecte"


def test_elider_ne_touche_que_le_nom_du_client():
    """La transformation cible le nom du client apres « de »/« que », et
    rien d'autre : aucun autre mot du texte ne doit bouger."""
    from content_generator import elider
    txt = ("Le point fort de EcoGroup est la gouvernance. Les emissions de "
           "EcoGroup baissent. La demarche de transition et le plan de "
           "Total restent inchanges.")
    out = elider(txt, "EcoGroup")
    assert "d'EcoGroup est la gouvernance" in out
    assert "emissions d'EcoGroup baissent" in out
    assert "de EcoGroup" not in out
    # intact : « de transition » (mot commun) et « de Total » (autre nom)
    assert "demarche de transition" in out
    assert "plan de Total" in out


def test_elider_ne_fait_rien_sur_un_nom_a_consonne():
    from content_generator import elider
    txt = "Le point fort de Total est la gouvernance."
    assert elider(txt, "Total") == txt


@pytest.mark.parametrize("nom,attendu_dans,absent_du_texte", [
    ("EcoGroup", "d'EcoGroup", "de EcoGroup"),
    ("Total", "de Total", "d'Total"),
])
def test_elision_dans_le_texte_genere(nom, attendu_dans, absent_du_texte):
    """Bout en bout sur le contenu genere : les paragraphes (ancien
    generateur ET systeme de clauses) passent par l'elision."""
    r = make_request()
    r.company.name = nom
    s = calculate_esg_scores(r)
    blob = " ".join(str(v) for v in generate_esg_content(r, s).values() if v)
    assert attendu_dans in blob
    assert absent_du_texte not in blob


def test_elision_du_titre_de_la_section_positionnement():
    """Le titre « le point fort de X » est visible sur les trois formats."""
    from content_generator import benchmark_verdict
    r = make_request()
    r.company.name = "EcoGroup"
    s = calculate_esg_scores(r)
    titre = benchmark_verdict(r, s)["title"]
    assert "d'EcoGroup" in titre and "de EcoGroup" not in titre


# ── Aucune comparaison à un secteur inventé, aucune couverture ESRS affirmée ─

# La table SECTOR_BENCHMARKS (15 triplets ecrits a la main, sans source) a ete
# supprimee le 2026-09-02, avec tous les ecarts chiffres qu'elle imprimait.
# S'y ajoutait une affirmation de couverture normative que rien ne verifie.
MARQUEURS_BENCHMARK_INVENTE = [
    "référence sectorielle", "internal sector reference", "sector reference",
    "moyenne de votre secteur", "moyenne de son secteur", "sector average",
    "devance la moyenne", "surperforme son secteur", "outperforms its sector",
    "vs secteur", "vs sector", "Surperformance sectorielle",
    "marché ETI/PME", "marché PME/ETI", "mid-market",
]
MARQUEURS_COUVERTURE_ESRS = [
    "couvre les principales exigences",
    "covers the main requirements",
    "répond aux attendus des normes",
    "addresses ESRS G1",
    "s'inscrit dans le périmètre de la norme ESRS S1",
    "falls within the scope of ESRS S1",
]


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_aucune_comparaison_sectorielle_dans_le_texte(lang):
    """Ni ecart chiffre vs un secteur invente, ni affirmation de couverture
    normative — les deux etaient concatenees sur les trois piliers."""
    r = make_request(lang)
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    blob = " ".join(str(v) for v in c.values() if v)
    for marqueur in MARQUEURS_BENCHMARK_INVENTE + MARQUEURS_COUVERTURE_ESRS:
        assert marqueur.lower() not in blob.lower(), f"{marqueur!r} present dans le texte {lang}"


def test_aucune_comparaison_sectorielle_dans_les_livrables():
    """Bout en bout sur les cinq livrables : PDF, PPTX, Word, one-pager."""
    import re
    import fitz
    from report_generator import generate_pdf_report
    from ppt_generator import generate_pptx
    from docx_generator import generate_word_report
    from onepager_generator import generate_onepager_pdf
    from main import build_advanced_charts

    r = make_request()
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    ch_l = build_advanced_charts(r, s, light_bg=True)

    textes = {}
    for nom, data in (("pdf", generate_pdf_report(r, s, c, ch_l)),
                      ("onepager", generate_onepager_pdf(r, s))):
        doc = fitz.open(stream=data, filetype="pdf")
        textes[nom] = re.sub(r"\s+", " ", "".join(doc[i].get_text() for i in range(doc.page_count)))
    for nom, data in (("pptx", generate_pptx(r, s, c, build_advanced_charts(r, s, light_bg=False))),
                      ("docx", generate_word_report(r, s, c, ch_l))):
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            textes[nom] = " ".join(
                z.read(n).decode("utf-8", "ignore") for n in z.namelist() if n.endswith(".xml"))

    for nom, blob in textes.items():
        for marqueur in MARQUEURS_BENCHMARK_INVENTE + MARQUEURS_COUVERTURE_ESRS:
            assert marqueur.lower() not in blob.lower(), f"{marqueur!r} present dans le {nom}"


def test_positionnement_interne_est_vrai_et_coherent():
    """Le remplacement doit dire vrai : le pilier note "point fort" est bien
    le mieux note, celui note "priorite" le moins bien, et l'ecart affiche
    correspond a la difference reelle."""
    from content_generator import benchmark_verdict
    r = make_request()
    s = calculate_esg_scores(r)
    bv = benchmark_verdict(r, s)
    pil = {"env": s.environmental_score, "social": s.social_score, "gov": s.governance_score}
    assert bv["lead"] == max(pil, key=lambda k: pil[k])
    assert bv["lag"] == min(pil, key=lambda k: pil[k])
    assert bv["gap"] == pil[bv["lead"]] - pil[bv["lag"]]
    meilleur = pil[bv["lead"]]
    for row in bv["rows"]:
        assert row["delta"] == pil[row["key"]] - meilleur
    assert [r_["score"] for r_ in bv["rows"]] == sorted((r_["score"] for r_ in bv["rows"]), reverse=True)
    assert bv["rows"][0]["delta"] == 0        # le meilleur pilier a un ecart nul


# ── Priorisation des enjeux : aucune méthodologie ESRS inventée ───────────

# Marqueurs d'une méthodologie de double matérialité que le code NE CONDUIT
# PAS (ni consultation des parties prenantes, ni cotation dédiée des IRO).
# Le texte les affirmait pourtant jusqu'au 2026-09-02 : materiality_topics()
# se contente de dériver deux valeurs des scores et des indicateurs déclarés.
MARQUEURS_METHODO_INVENTEE = [
    "IRO-1", "SBM-3", "sévérité ×", "severity ×", "irrémédiab", "irremediab",
    "validation interne par la gouvernance", "internal validation by ESG governance",
]

# À distinguer du précédent : l'expression « double matérialité » RESTE
# légitime dans le livrable, mais UNIQUEMENT pour s'en démarquer ("ne se
# substitue pas à..."). Ce sont les tournures affirmant l'avoir conduite qui
# sont interdites.
AFFIRMATIONS_INTERDITES = [
    "a conduit une analyse de double matérialité",
    "conducted a double materiality assessment",
    "a conduit une double matérialité",
    "analyse de double matérialité couvrant",
]


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_materialite_ne_revendique_pas_de_methodologie_esrs(lang):
    """Le texte de priorisation ne doit revendiquer ni processus IRO, ni
    cotation sévérité × étendue × irrémédiabilité, ni validation par une
    gouvernance — rien de tout cela n'est calculé."""
    r = make_request(lang)
    s = calculate_esg_scores(r)
    txt = generate_esg_content(r, s)["materiality"]
    for marqueur in MARQUEURS_METHODO_INVENTEE:
        assert marqueur.lower() not in txt.lower(), f"{marqueur!r} present dans le texte {lang}"
    for affirmation in AFFIRMATIONS_INTERDITES:
        assert affirmation.lower() not in txt.lower(), f"{affirmation!r} present dans le texte {lang}"


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_materialite_dit_explicitement_ce_qu_elle_n_est_pas(lang):
    """La mise en garde est le coeur de la correction : sans elle, une
    cartographie dérivée des scores se lit comme une analyse réglementaire."""
    r = make_request(lang)
    s = calculate_esg_scores(r)
    txt = generate_esg_content(r, s)["materiality"]
    if lang == "fr":
        assert "cartographie de priorisation" in txt.lower()
        assert "ne se substitue pas" in txt.lower()
        assert "esrs 1" in txt.lower()
    else:
        assert "prioritisation map" in txt.lower()
        assert "does not constitute" in txt.lower()
        assert "esrs 1" in txt.lower()


def test_materialite_absente_des_livrables_generes():
    """Bout en bout : les marqueurs ne doivent apparaître dans AUCUN des
    trois formats (PDF, PPTX, Word), titres et légendes compris."""
    import re
    import fitz
    from report_generator import generate_pdf_report
    from ppt_generator import generate_pptx
    from docx_generator import generate_word_report
    from main import build_advanced_charts

    r = make_request()
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)

    pdf = generate_pdf_report(r, s, c, build_advanced_charts(r, s, light_bg=True))
    doc = fitz.open(stream=pdf, filetype="pdf")
    textes = {"pdf": re.sub(r"\s+", " ", "".join(doc[i].get_text() for i in range(doc.page_count)))}

    for nom, data in (("pptx", generate_pptx(r, s, c, build_advanced_charts(r, s, light_bg=False))),
                      ("docx", generate_word_report(r, s, c, build_advanced_charts(r, s, light_bg=True)))):
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            textes[nom] = " ".join(
                z.read(n).decode("utf-8", "ignore") for n in z.namelist() if n.endswith(".xml"))

    for nom, blob in textes.items():
        for marqueur in MARQUEURS_METHODO_INVENTEE:
            assert marqueur.lower() not in blob.lower(), f"{marqueur!r} present dans le {nom}"
        for affirmation in AFFIRMATIONS_INTERDITES:
            assert affirmation.lower() not in blob.lower(), f"{affirmation!r} present dans le {nom}"


def test_priorisation_ne_depend_pas_du_nom_de_lentreprise():
    """Le jit (decalage +/-0,6 derive du hash du nom) faisait varier toutes
    les notes selon la raison sociale : deux entreprises aux donnees
    identiques n'avaient pas la meme cartographie. Supprime."""
    from esg_advanced import materiality_topics
    a = make_request()
    b = make_request()
    b.company.name = "Zephyr Industries SAS"
    ta = materiality_topics(a, calculate_esg_scores(a))
    tb = materiality_topics(b, calculate_esg_scores(b))
    assert [(t["impact"], t["financial"]) for t in ta] == \
           [(t["impact"], t["financial"]) for t in tb]


def test_glossary_filters_to_report_content():
    from glossary import glossary_entries
    full = glossary_entries(make_request())
    terms = [e["term"] for e in full]
    assert "CSRD" in terms and "Scopes 1, 2 et 3" in terms
    assert all(e["definition"] for e in full)
    # Rapport minimal : les termes sans objet disparaissent
    minimal = ESGRequest(
        company=CompanyInfo(name="B", sector="Services", country="France", reporting_year=2025),
        environmental=EnvironmentalData(), social=SocialData(), governance=GovernanceData(),
        reporting_framework="vsme")
    mt = [e["term"] for e in glossary_entries(minimal)]
    assert "VSME" in mt and "CSRD" not in mt          # référentiel visé seulement
    assert "Taxonomie européenne" not in mt           # aucun indicateur aligné
    assert len(mt) < len(terms)


def test_glossary_rendered_in_pdf():
    import fitz
    from report_generator import generate_pdf_report
    from main import build_advanced_charts
    r = make_request()
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    pdf = generate_pdf_report(r, s, c, build_advanced_charts(r, s, light_bg=True))
    doc = fitz.open(stream=pdf, filetype="pdf")
    full = "".join(doc[i].get_text() for i in range(doc.page_count))
    assert "Glossaire" in full
    assert "Double matérialité" in full


# ── Questionnaire de collecte ─────────────────────────────────────────────

def test_questionnaire_is_offline_and_complete():
    from questionnaire_generator import generate_questionnaire_html
    from import_data import FIELD_SPECS
    doc = generate_questionnaire_html("Acme", 2025, "J. Martin")
    # Autonomie : aucune ressource distante
    assert "http://" not in doc and "https://" not in doc
    assert "<script" in doc and "localStorage" in doc
    # Tout champ importable doit être collectable
    for _section, key, _typ, _labels in FIELD_SPECS:
        assert f'data-key="{key}"' in doc, f"champ absent du questionnaire : {key}"


def test_questionnaire_endpoint(client):
    r = client.post("/api/generate/questionnaire", json=FORM)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    assert "Collecte_ESG_Acme" in r.headers["content-disposition"]
    assert b"<!doctype html>" in r.content[:40].lower()


def test_questionnaire_csv_reimports(client):
    """Le CSV que produit le questionnaire doit repasser par l'import."""
    from questionnaire_generator import _fields_by_section
    rows = ["Champ;Valeur"]
    sample = {"name": "Acme", "sector": "Industrie", "revenue_eur": "48000000",
              "reporting_year": "2025", "scope3_emissions": "4900",
              "esg_audit_conducted": "Non", "sustainability_committee": "Oui"}
    for _sec, fields in _fields_by_section():
        for csv_label, key, _typ, _meta in fields:
            rows.append(f"{csv_label};{sample.get(key, '')}")
    csv_bytes = ("﻿" + "\r\n".join(rows)).encode("utf-8")
    r = client.post("/api/import", files={"file": ("c.csv", csv_bytes, "text/csv")})
    assert r.status_code == 200
    sec = r.json()["sections"]
    assert sec["company"]["revenue_eur"] == 48000000
    assert sec["company"]["reporting_year"] == 2025
    assert sec["environmental"]["scope3_emissions"] == 4900
    assert sec["governance"]["esg_audit_conducted"] is False
    assert sec["governance"]["sustainability_committee"] is True
    assert r.json()["unmatched"] == []
