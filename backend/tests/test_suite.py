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


def test_no_completed_action_omits_callout_and_sentence():
    """Aucune action cochée -> ni encart, ni phrase de synthèse."""
    full = _completed_actions_pdf_text([])
    assert "ACTIONS ENGAGÉES" not in full.upper()
    # Bannir la FORMULATION, pas le mot : « déclarées » figure aussi
    # legitimement dans la note methodologique (« parts déclarées comme
    # alignées à la Taxonomie UE »). Troisieme fois que ce patron se
    # presente, apres « double materialite » et « sector reference ».
    assert "déclarée engagée" not in full and "déclarées engagées" not in full


# Passe 2 : le ban portait sur le mot nu « preuve », sur les 16 pages du PDF en
# FR et sur une seule chaine en EN. Il interdisait exactement le vocabulaire de
# mise en garde que le projet emploie partout ailleurs (« le cabinet n'a pas
# collecte d'elements de preuve »). Ce sont les formulations qui transforment une
# DECLARATION en fait verifie qui sont bannies -- et le regime est le meme dans
# les deux langues.
FORMULATIONS_DE_VERIFICATION = [
    "preuve à l'appui", "preuves à l'appui", "sur justificatifs",
    "action prouvée", "actions prouvées",
    "vérifié par le cabinet", "vérifiée par le cabinet", "attesté par le cabinet",
    "proof of completion", "evidence provided", "supporting evidence",
    "verified by the firm", "attested by the firm",
]


def _texte_de_l_encart(lang, actions):
    """Le texte que l'outil ecrit AUTOUR des actions engagees : titre de
    l'encart + phrase de synthese. Portee volontairement etroite : le reste
    du rapport reste libre d'employer le mot « preuve »."""
    from i18n import L
    r = make_request(lang, completed_actions=actions)
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    return f'{L(lang)["done_head"]} {c["executive_summary"]}'


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_encart_actions_ne_revendique_aucune_verification(lang):
    """L'outil reporte une declaration du cabinet, il ne prouve rien
    (decision du 2026-09-01). L'encart ne doit donc revendiquer ni preuve,
    ni justificatif, ni verification -- mais le mot « preuve » lui-meme
    reste disponible ailleurs pour ecrire la mise en garde honnete."""
    texte = _texte_de_l_encart(lang, [{"title": "Créer un comité de durabilité au conseil",
                                       "year": 2024}])
    for formulation in FORMULATIONS_DE_VERIFICATION:
        assert formulation.lower() not in texte.lower(),             f"{formulation!r} present dans l'encart ({lang})"
    # Contrepartie positive : la nuance doit rester presente.
    attendu = "déclarée engagée" if lang == "fr" else "reported as underway"
    assert attendu in texte, f"la nuance {attendu!r} a disparu de l'encart ({lang})"


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
    assert "(s)" not in exec3


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

# ── Fixture partagée des livrables gelés ──────────────────────────────────

# Les quatre tests de gel bout-en-bout regeneraient chacun le meme jeu de
# livrables a partir du meme dossier : ~19 s de generation redondante sur une
# suite de 66 s. Ils partagent desormais une fabrique memoisee, ce qui paie la
# generation une fois par cle (langue, variante) et finance l'axe EN a cout
# constant.
#
# Deux variantes, parce que le test des attributions legales a besoin d'un
# conseil sous le seuil pour que la clause CA soit emise :
#   "base"          -> make_request(lang)
#   "ca_sous_seuil" -> idem + female_board_percent = 33


def _textes_des_livrables(r):
    """PDF, one-pager, PPTX et Word d'un meme dossier, rendus en texte brut.

    Les deux PDF passent par PyMuPDF ; PPTX et Word sont lus comme archives
    OOXML, ce qui capture aussi les titres et legendes.
    """
    import re
    import fitz
    from report_generator import generate_pdf_report
    from ppt_generator import generate_pptx
    from docx_generator import generate_word_report
    from onepager_generator import generate_onepager_pdf
    from proposal_generator import generate_proposal_docx
    from main import build_advanced_charts

    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    ch_l = build_advanced_charts(r, s, light_bg=True)

    textes = {}
    for nom, data in (("pdf", generate_pdf_report(r, s, c, ch_l)),
                      ("onepager", generate_onepager_pdf(r, s))):
        doc = fitz.open(stream=data, filetype="pdf")
        textes[nom] = re.sub(r"\s+", " ", "".join(doc[i].get_text() for i in range(doc.page_count)))
    # La lettre de mission etait exclue des tests de gel uniquement pour
    # contourner le faux positif « marche PME/ETI » (DETTE 4bis). Le marqueur
    # ayant ete reecrit en passe 2, l'exclusion n'a plus d'objet.
    for nom, data in (("pptx", generate_pptx(r, s, c, build_advanced_charts(r, s, light_bg=False))),
                      ("docx", generate_word_report(r, s, c, ch_l)),
                      ("lettre", generate_proposal_docx(r, s))):
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            textes[nom] = " ".join(
                z.read(n).decode("utf-8", "ignore") for n in z.namelist() if n.endswith(".xml"))
    return textes


@pytest.fixture(scope="session")
def livrables_geles():
    """Fabrique memoisee : (lang, variante) -> {format: texte}.

    Portee session : chaque cle n'est generee qu'une fois pour toute la
    suite, quel que soit l'ordre d'execution des tests.
    """
    cache = {}

    def _pour(lang="fr", variante="base"):
        cle = (lang, variante)
        if cle not in cache:
            r = make_request(lang)
            if variante == "ca_sous_seuil":
                r.governance.female_board_percent = 33   # sinon la clause CA ne sort pas
            cache[cle] = _textes_des_livrables(r)
        return cache[cle]

    return _pour


# ── Engagements fabriques : trajectoire, cibles, alignements ──────────────

# Le code ne collecte AUCUN objectif chiffre. Il en fabriquait pourtant :
#  - une trajectoire « -42 % a 2030, methodologie SBTi » declenchee par la
#    seule saisie d'un total CO2 (le -42 % etait une constante) ;
#  - une cible par pilier calculee par uplift() : cur + (100-cur)*0.45 + 5 ;
#  - une conformite ESRS E1-4 deduite de cet objectif invente ;
#  - le respect du principe DNSH et des garanties minimales affirme sur la
#    foi de trois pourcentages Taxonomie saisis a la main ;
#  - un alignement SFDR (qui ne vise pas les entreprises non financieres),
#    ISO 14001/26000 (26000 n'est pas certifiable) et six ODD identiques
#    pour tout dossier.
# Verifie le 2026-09-03 contre EFRAG, EUR-Lex, ESMA et ISO.
# NB : le nombre « 42 » nu n'est PAS banni — il figure legitimement comme
# valeur d'indicateur (42 % de renouvelable dans le jeu de test). Seules les
# FORMULATIONS qui ne peuvent venir que de la trajectoire fabriquee le sont.
# Passe 3 : scission par famille. Ces 21 marqueurs sont de PROVENANCE -- ils
# deviennent vrais des que le consultant declare la donnee correspondante. Le
# ban ne vaut donc QUE pour un dossier qui ne porte pas cette donnee, ce qui est
# le cas de tout dossier aujourd'hui (aucun champ ne permet de la saisir).
ENGAGEMENTS_SANS_DONNEE_COLLECTEE = [
    "réduction de 42", "42% reduction", "-42 %", "-42%",
    "Science Based Targets", "SBTi",
    "trajectoire SBTi", "SBTi pathway",
    # L'AFFIRMATION, pas le terme : le rapport mentionne desormais DNSH et
    # les garanties minimales pour dire qu'ils ne sont PAS evalues.
    "dans le respect du principe DNSH",
    "in compliance with the DNSH principle",
    "SFDR", "ISO 14001", "ISO 26000",
    "ODD 7", "ODD 8", "SDG 7", "SDG 8",
    "Cadres de Référence & Alignement ODD", "Reporting Frameworks & SDG Alignment",
    "Chaque pilier fait l'objet d'une cible",
    "Each pillar is assigned a progression target",
]

# Formulation, pas provenance : meme avec des ODD collectes, le 0ter impose de
# dire « themes couverts par les indicateurs » et non « ancree dans les ODD ».
# Ces deux-la restent interdits quelle que soit la donnee.
AFFIRMATIONS_ODD_INTERDITES = [
    "ancrée dans les ODD", "anchored in the UN SDGs",
]

ENGAGEMENTS_FABRIQUES = ENGAGEMENTS_SANS_DONNEE_COLLECTEE + AFFIRMATIONS_ODD_INTERDITES

# Contreparties positives : ce que le rapport doit dire a la place.
REMPLACEMENTS_ATTENDUS = {
    "fr": ["n'a pas communiqué d'objectifs de durabilité chiffrés",
           "ESRS E1-4 demande de publier si et comment"],
    "en": ["has not disclosed quantified sustainability targets",
           "ESRS E1-4 requires disclosing whether and how"],
}


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_aucun_engagement_fabrique_dans_le_texte(lang):
    r = make_request(lang)
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    blob = " ".join(str(v) for v in c.values() if v)
    blob += " " + " ".join(s.strengths + s.weaknesses + s.recommendations)
    for marqueur in ENGAGEMENTS_FABRIQUES:
        assert marqueur.lower() not in blob.lower(), (
            f"{marqueur!r} present dans le texte {lang} alors qu'aucune donnee "
            f"du dossier ne le justifie")


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_les_objectifs_sont_dits_a_definir(lang):
    """Contrepartie positive : le rapport doit dire que les objectifs
    restent a definir, et rappeler ce qu'exige reellement ESRS E1-4."""
    r = make_request(lang)
    s = calculate_esg_scores(r)
    txt = generate_esg_content(r, s)["targets"]
    for attendu in REMPLACEMENTS_ATTENDUS[lang]:
        assert attendu.lower() in txt.lower(), f"{attendu!r} absent du texte {lang}"


def test_ligne_esrs_e1_4_est_non_renseignee_jamais_conforme():
    """L'ancien code declarait « Conforme » des qu'un total CO2 etait saisi,
    sur la foi d'un objectif que l'outil avait lui-meme invente. E1-4 exige
    de DIVULGUER les cibles, pas d'en avoir : sans cible collectee, le seul
    statut defendable est « non renseigne »."""
    from content_generator import compliance_assessment
    r = make_request()                       # make_request() renseigne co2_emissions_tonnes
    assert r.environmental.co2_emissions_tonnes, "le test doit porter sur un dossier AVEC bilan GES"
    s = calculate_esg_scores(r)
    lignes = [l for l in compliance_assessment(r, s) if l["ref"] == "ESRS E1-4"]
    assert len(lignes) == 1
    assert lignes[0]["status"] == "na"
    assert "42" not in str(lignes[0])


@pytest.mark.parametrize("variante", ["base", "ca_sous_seuil"])
@pytest.mark.parametrize("lang", ["fr", "en"])
def test_provenance_sans_donnee_aucun_engagement_dans_les_livrables(livrables_geles, lang, variante):
    """Moitie « SANS la donnee » du differentiel de provenance.

    Ce test ne dit PAS que ces chaines sont interdites pour toujours : il
    dit qu'elles sont interdites DANS CE DOSSIER-CI, qui ne porte aucune
    cible, aucune certification et aucun ODD declares -- parce qu'aucun
    champ ne permet aujourd'hui de les saisir (DETTE.md § 0bis). Le jour
    ou l'etape B les rendra saisissables, un dossier qui les porte devra
    au contraire les CITER : c'est la moitie « avec la donnee », ci-dessous.
    """
    for nom, blob in livrables_geles(lang, variante).items():
        for marqueur in MARQUEURS_DE_PROVENANCE:
            assert marqueur.lower() not in blob.lower(), (
                f"{marqueur!r} apparait dans le {nom} ({lang}/{variante}) alors que "
                f"ce dossier ne porte AUCUNE donnee qui le justifie. Ce n'est pas "
                f"un mot interdit : c'est une affirmation sans source.")


def test_la_couverture_ne_porte_que_le_referentiel_vise():
    """GRI et TCFD figuraient sur la couverture sans qu'aucune donnee ne
    les fonde ; seul le referentiel vise est une donnee saisie."""
    from i18n import L
    for lang in ("fr", "en"):
        d = L(lang)
        assert d["cover_refs"] == "CSRD / ESRS"
        assert d["cover_refs_vsme"] == "VSME (EFRAG)"


# ── Attributions legales des quotas de genre ──────────────────────────────

# Verifie le 2026-09-02 contre les sources officielles :
#  - le quota de 40 % au CONSEIL D'ADMINISTRATION releve de la loi
#    Cope-Zimmermann (n° 2011-103 du 27 janvier 2011) ;
#  - la loi Rixain (2021) vise les cadres dirigeants et les instances
#    dirigeantes, PAS le conseil d'administration ;
#  - AUCUN quota legal de 40 % ne porte sur l'effectif total.
# Le code affirmait les trois a tort. Ces chaines ne doivent pas revenir.
ATTRIBUTIONS_LEGALES_FAUSSES = [
    # Passe 2 : « Rixain » nu interdisait de citer une loi REELLE, y compris
    # correctement (elle vise les cadres dirigeants et les instances dirigeantes).
    # Le marqueur vise desormais la mauvaise ATTRIBUTION, pas la citation.
    "conforme loi Rixain", "objectif Rixain",
    "loi Rixain, transparence salariale UE",
    "objectif légal 40", "legal 40% target",
    # NON REECRITS, et c'est signale : la faute visee ici n'est pas une phrase
    # mais une LIGNE du tableau d'ecarts reglementaires (la parite de l'effectif
    # presentee comme une exigence). Aucune reformulation textuelle ne distingue
    # ce libelle d'un objectif que le client declarerait lui-meme. La faute
    # structurelle est deja couverte par test_ecarts_sans_mixite_effectif.
    "40 % de femmes dans les effectifs", "40% women in the workforce",
]

# Provenance, pas attribution legale (reclassement du 2026-09-05, DETTE 0quater).
# Un objectif de parite DECLARE par le client est un fait -- c'est meme ce que la
# recommandation « Definir des objectifs chiffres de parite » lui demande de
# produire. Le ban ne tient que tant qu'aucun champ ne permet de le saisir :
# a convertir en test differentiel des que l'etape B existe. Assertes ici en
# attendant, pour ne pas perdre la couverture.
PARITE_SANS_DONNEE_COLLECTEE = [
    "objectif 40%", "target 40%", "cible 40 %", "40% target",
]

# La famille provenance au complet : engagements + objectif de parite (29 marqueurs
# annonces au chantier ; 25 dans le code, cf. DETTE.md § 0quater).
MARQUEURS_DE_PROVENANCE = ENGAGEMENTS_SANS_DONNEE_COLLECTEE + PARITE_SANS_DONNEE_COLLECTEE


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_aucune_attribution_legale_fausse_dans_le_texte(lang):
    """Couvre content_generator ET esg_calculator (forces/faiblesses)."""
    r = make_request(lang)
    r.governance.female_board_percent = 33   # sinon la clause CA ne sort pas
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    blob = " ".join(str(v) for v in c.values() if v)
    blob += " " + " ".join(s.strengths + s.weaknesses + s.recommendations)
    for marqueur in ATTRIBUTIONS_LEGALES_FAUSSES:
        assert marqueur.lower() not in blob.lower(), f"{marqueur!r} present dans le texte {lang}"


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_aucune_attribution_legale_fausse_dans_les_livrables(livrables_geles, lang):
    """Bout en bout sur les cinq livrables : le tableau d'ecarts
    reglementaires et le plan d'action passent par la aussi."""
    for nom, blob in livrables_geles(lang, "ca_sous_seuil").items():
        for marqueur in ATTRIBUTIONS_LEGALES_FAUSSES:
            assert marqueur.lower() not in blob.lower(), f"{marqueur!r} present dans le {nom} ({lang})"


def test_quota_du_conseil_attribue_a_cope_zimmermann():
    """Contrepartie positive : la bonne loi est bien citee, et sans
    affirmer qu'elle s'applique a CE client (le code ne connait ni le
    statut cote ni un effectif fiable)."""
    # make_request() ne renseigne pas female_board_percent : sans cette
    # donnee la clause du conseil ne se declenche pas du tout.
    r = make_request()
    r.governance.female_board_percent = 33
    s = calculate_esg_scores(r)
    gouv = generate_esg_content(r, s)["governance"]
    assert "Copé-Zimmermann" in gouv
    assert "pour les sociétés concernées" in gouv
    assert "Rixain" not in gouv

    r_en = make_request("en")
    r_en.governance.female_board_percent = 33
    s_en = calculate_esg_scores(r_en)
    gouv_en = generate_esg_content(r_en, s_en)["governance"]
    assert "Copé-Zimmermann" in gouv_en
    assert "for companies within its scope" in gouv_en


def test_tableau_de_conformite_ne_liste_pas_de_mixite_des_effectifs():
    """Un tableau d'ecarts REGLEMENTAIRES ne peut pas mesurer l'ecart a une
    norme inexistante : la ligne « Mixite des effectifs » a ete retiree."""
    from content_generator import compliance_assessment
    r = make_request()
    s = calculate_esg_scores(r)
    for ligne in compliance_assessment(r, s):
        libelle = " ".join(str(v) for v in ligne.values() if isinstance(v, str))
        assert "Mixité des effectifs" not in libelle
        assert "Workforce gender balance" not in libelle


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
    # Passe 2 (2026-09-05) : les 13 fragments generiques de cette liste ont ete
    # remplaces par la FORMULATION reellement fautive, retrouvee dans les lignes
    # supprimees par 26b3c75 et 33fae44. Un fragment comme « de son secteur » ou
    # « marche PME/ETI » mordait du texte juste : le premier decrit un perimetre,
    # le second est employe legitimement par proposal_generator.py:78 pour nommer
    # le perimetre reglementaire CSRD/VSME.
    # Regle : bannir l'affirmation de comparaison, jamais le nom du secteur.

    # -- Comparaisons chiffrees a une moyenne inventee (deja cibles, inchanges)
    "moyenne de votre secteur", "moyenne de son secteur", "sector average",
    "devance la moyenne", "surperforme son secteur", "outperforms its sector",
    "vs secteur", "vs sector", "Surperformance sectorielle",
    "moyenne sectorielle", "sector comparison uses",

    # -- La « reference sectorielle interne » et ses comparatifs
    #    (ex-« reference sectorielle », ex-« marche ETI/PME », ex-« mid-market »)
    "référence sectorielle interne", "dépasse la référence sectorielle",
    "supérieure à la référence sectorielle", "référence de son secteur",
    "moyennes ESG typiques par secteur",
    "internal sector reference",          # la note methodologique dit « external »
    "sector reference — mid-market",
    "interne du marché PME/ETI",
    "reference base for the SME/mid-cap market",

    # -- Le classement par rapport a des « standards » sectoriels
    #    (ex-« standards sectoriels », ex-« sector standards »)
    "dépassant les standards sectoriels", "supérieur aux standards sectoriels",
    "standards sectoriels reconnus",
    "exceeding recognised sector standards", "above sector standards",
    "recognised sector standards",

    # -- Le rang par rapport a des leaders / pratiques
    #    (ex-« leaders mondiaux », ex-« pratiques du secteur »)
    "alignée avec les leaders mondiaux", "on par with global ESG leaders",
    "meilleures de son secteur", "en tête de son secteur",
    "en deçà des pratiques du secteur",
]

# Contrepartie positive : la grille de notation est interne et non sourcee.
# Ce fait doit etre DECLARE, une fois, dans la note methodologique — un
# retrait silencieux de cette divulgation doit casser le test.
DIVULGATION_GRILLE_INTERNE = {
    "fr": "grille de notation interne",
    "en": "internal scoring grid",
}
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


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_la_grille_interne_est_declaree(lang):
    """La note methodologique doit dire que les seuils sont internes et non
    adosses a un referentiel externe publie. Sans cette divulgation, les
    jugements de niveau du rapport (« eleve », « a surveiller ») n'ont plus
    d'origine declarable."""
    r = make_request(lang)
    s = calculate_esg_scores(r)
    methodo = generate_esg_content(r, s)["methodology"]
    assert DIVULGATION_GRILLE_INTERNE[lang].lower() in methodo.lower()


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_aucune_comparaison_sectorielle_dans_les_livrables(livrables_geles, lang):
    """Bout en bout sur les cinq livrables : PDF, PPTX, Word, one-pager."""
    for nom, blob in livrables_geles(lang).items():
        for marqueur in MARQUEURS_BENCHMARK_INVENTE + MARQUEURS_COUVERTURE_ESRS:
            assert marqueur.lower() not in blob.lower(), f"{marqueur!r} present dans le {nom} ({lang})"


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
    # Passe 2 : « IRO-1 », « SBM-3 », « irremediab » etaient des codes et des
    # radicaux nus. Citer une norme reelle doit rester possible, y compris pour
    # dire qu'on ne la couvre PAS. Ce sont les revendications de conformite et la
    # formule de cotation qui sont bannies, retrouvees dans d9a079a.
    "(IRO-1, SBM-3)",                     # « ... aux normes ESRS 1/ESRS 2 (IRO-1, SBM-3) »
    "aux normes ESRS 1/ESRS 2", "and ESRS 1/ESRS 2",
    "sévérité ×", "severity ×",
    "× irrémédiabilité", "× irremediability",
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


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_materialite_absente_des_livrables_generes(livrables_geles, lang):
    """Bout en bout : les marqueurs ne doivent apparaître dans AUCUN des
    trois formats (PDF, PPTX, Word), titres et légendes compris.

    Le one-pager est ecarte a dessein : il ne l'a jamais couvert, et cette
    passe est a iso-comportement.
    """
    textes = {n: b for n, b in livrables_geles(lang).items()
              if n not in ("onepager", "lettre")}
    for nom, blob in textes.items():
        for marqueur in MARQUEURS_METHODO_INVENTEE:
            assert marqueur.lower() not in blob.lower(), f"{marqueur!r} present dans le {nom} ({lang})"
        for affirmation in AFFIRMATIONS_INTERDITES:
            assert affirmation.lower() not in blob.lower(), f"{affirmation!r} present dans le {nom} ({lang})"


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


# ── Intégrité structurelle du rapport PDF ────────────────────────────────

# Le sommaire (report_generator.py, `_toc_parts`) est câblé EN DUR sur des
# clés i18n : rien ne garantit qu'une entrée corresponde encore à une
# section réellement rendue. Les chantiers de septembre 2026 ont retiré du
# contenu (comparaison sectorielle, engagements fabriqués) ; un retrait de
# section qui oublierait le sommaire laisserait une entrée pointant dans le
# vide, sans qu'aucun test ne le voie.
def _toc_labels(TR):
    """Les dix entrées du sommaire, dans l'ordre où `_toc_parts` les pose."""
    return [TR["pdf_s1"], TR["pdf_s2"], TR["pdf_s3"], TR["pdf_s4"], TR["pdf_s5"],
            TR["pdf_s6"], TR["pdf_diag"], TR["pdf_s7"], TR["roadmap_title"],
            TR["pdf_concl"]]


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_sommaire_numerotation_et_pagination(lang):
    """Trois contrôles structurels sur le PDF, FR et EN :

    1. aucune entrée du sommaire ne pointe dans le vide — chaque libellé
       apparaît AU MOINS DEUX FOIS (une dans le sommaire, une comme titre
       de section rendu) ;
    2. la numérotation des sections va de 1 à 8 sans saut ;
    3. les pieds de page forment une suite continue jusqu'à la dernière page.

    NB méthodologique : on compte les OCCURRENCES, pas les index de page.
    Le sommaire et les deux premiers titres tombent sur la même page, si
    bien qu'un contrôle par numéro de page les déclarerait orphelins à
    tort.

    LIMITE CONNUE : `_toc_parts` est une variable locale de
    `generate_pdf_report`, non importable ; la liste ci-dessus la
    RECOPIE. Le test attrape donc le cas réel (une section retirée du
    corps dont l'entrée survit au sommaire — vérifié par mutation) mais
    PAS l'ajout d'une entrée fantôme directement dans `_toc_parts`.
    Rendre `_toc_parts` extractible lèverait la duplication.
    """
    import re
    import fitz
    from i18n import L
    from report_generator import generate_pdf_report
    from main import build_advanced_charts

    r = make_request(lang)
    s = calculate_esg_scores(r)
    c = generate_esg_content(r, s)
    doc = fitz.open(stream=generate_pdf_report(r, s, c, build_advanced_charts(r, s, light_bg=True)),
                    filetype="pdf")
    entier = re.sub(r"\s+", " ", " ".join(doc[i].get_text() for i in range(doc.page_count)))

    for libelle in _toc_labels(L(lang)):
        attendu = re.sub(r"\s+", " ", libelle).strip()
        assert entier.count(attendu) >= 2, \
            f"entrée de sommaire sans section correspondante : {attendu!r} ({lang})"

    numeros = sorted({int(n) for n in re.findall(r"(?:^| )([1-8])\. [A-ZÉÀ]", entier)})
    assert numeros == list(range(1, 9)), f"numérotation des sections trouée : {numeros} ({lang})"

    pages = [int(n) for n in re.findall(r"\| page (\d+)", entier)]
    assert pages == list(range(2, doc.page_count + 1)), \
        f"pagination discontinue : {pages} pour {doc.page_count} pages ({lang})"


# ── Regle d'admission : un marqueur doit casser sur la faute qu'il vise ────

# Passe 2 (2026-09-05). Les 75 marqueurs ont tous ete ecrits APRES la
# suppression de la faute : ils sont nes verts et n'ont jamais discrimine.
# Chaque marqueur reecrit dans cette passe est donc confronte a la phrase
# reellement supprimee du depot (commits 26b3c75, 33fae44, d9a079a,
# 1b03075), retrouvee par `git log -p -S`. Un marqueur qui ne retrouve pas
# sa propre faute est mort ou vise a cote.
#
# LIMITE CONNUE : ce test prouve que l'assertion se declenche, pas que le
# generateur pourrait encore produire la chaine.
FAUTES_HISTORIQUES = [
    # -- MARQUEURS_BENCHMARK_INVENTE
    ("référence sectorielle interne", "Référence sectorielle interne — marché ETI/PME."),
    ("dépasse la référence sectorielle",
     "L'intensité carbone dépasse la référence sectorielle : l'exposition au coût du carbone constitue un point de vigilance."),
    ("supérieure à la référence sectorielle",
     "L'intensité carbone est très supérieure à la référence sectorielle, une exposition majeure au prix du carbone."),
    ("référence de son secteur",
     "L'intensité carbone est nettement inférieure à la référence de son secteur, signe d'un modèle déjà sobre."),
    ("moyennes ESG typiques par secteur",
     "Base de référence interne — moyennes ESG typiques par secteur (marché ETI/PME)."),
    ("internal sector reference", "The pillar stands 4 pts above the internal sector reference"),
    ("sector reference — mid-market", "Internal sector reference — mid-market."),
    ("interne du marché PME/ETI",
     "la base de référence interne du marché PME/ETI et n'implique aucun transfert de données externe"),
    ("reference base for the SME/mid-cap market",
     "reference base for the SME/mid-cap market and involves no external data transfer"),
    ("dépassant les standards sectoriels",
     "très bonne performance, dépassant les standards sectoriels reconnus"),
    ("supérieur aux standards sectoriels",
     "Taux d'accidents supérieur aux standards sectoriels (TF 6.2)"),
    ("standards sectoriels reconnus",
     "seuils réglementaires et des standards sectoriels reconnus — l'intensité carbone est"),
    ("exceeding recognised sector standards",
     "strong performance, exceeding recognised sector standards"),
    ("above sector standards", "Accident rate above sector standards (rate 6.2)"),
    ("recognised sector standards",
     "indicator against regulatory thresholds and recognised sector standards"),
    ("alignée avec les leaders mondiaux",
     "performance de premier plan, alignée avec les leaders mondiaux ESG"),
    ("on par with global ESG leaders", "leading performance, on par with global ESG leaders"),
    ("meilleures de son secteur",
     "L'intensité carbone se situe parmi les meilleures de son secteur, un atout rare."),
    ("en tête de son secteur",
     "Rapportées au chiffre d'affaires, les émissions placent Acme en tête de son secteur."),
    ("en deçà des pratiques du secteur",
     "À 63 % de déchets recyclés, la valorisation matière d'Acme reste en deçà des pratiques du secteur."),
    # -- MARQUEURS_METHODO_INVENTEE
    ("(IRO-1, SBM-3)",
     "Conformément à la CSRD et aux normes ESRS 1/ESRS 2 (IRO-1, SBM-3), Acme a conduit une analyse."),
    ("aux normes ESRS 1/ESRS 2",
     "Conformément à la CSRD et aux normes ESRS 1/ESRS 2 (IRO-1, SBM-3), Acme a conduit une analyse."),
    ("and ESRS 1/ESRS 2",
     "In accordance with the CSRD and ESRS 1/ESRS 2 (IRO-1, SBM-3), Acme conducted a double assessment."),
    ("× irrémédiabilité",
     "cotation de la matérialité d'impact (sévérité × étendue × irrémédiabilité, pondérée)"),
    ("× irremediability",
     "(severity × scope × irremediability, plus likelihood for potential impacts)"),
    # -- ATTRIBUTIONS_LEGALES_FAUSSES
    ("conforme loi Rixain", "conforme loi Rixain (≥40%)"),
    ("objectif Rixain", "3 pt(s) sous l'objectif Rixain"),
    ("loi Rixain, transparence salariale UE",
     "Renforce la diversité et la conformité (loi Rixain, transparence salariale UE)."),
]


@pytest.mark.parametrize("marqueur,faute", FAUTES_HISTORIQUES,
                         ids=[m for m, _ in FAUTES_HISTORIQUES])
def test_chaque_marqueur_reecrit_casse_sur_sa_faute(marqueur, faute):
    """Le marqueur doit (a) figurer dans une liste reellement assertee et
    (b) retrouver la phrase supprimee qu'il vise."""
    listes = (MARQUEURS_BENCHMARK_INVENTE + MARQUEURS_METHODO_INVENTEE
              + ATTRIBUTIONS_LEGALES_FAUSSES + PARITE_SANS_DONNEE_COLLECTEE)
    assert marqueur in listes, f"{marqueur!r} n'est asserte par aucune liste"
    assert marqueur.lower() in faute.lower(), \
        f"{marqueur!r} ne retrouve pas la faute historique qu'il vise"


def test_aucun_marqueur_reecrit_ne_mord_le_texte_produit():
    """Contrepartie : aucune des formulations reecrites ne doit apparaitre
    dans le texte que le code produit AUJOURD'HUI, FR et EN. Sans ce
    controle, un marqueur pourrait « casser sur sa faute » tout en mordant
    du texte juste."""
    for lang in ("fr", "en"):
        r = make_request(lang)
        s = calculate_esg_scores(r)
        blob = " ".join(str(v) for v in generate_esg_content(r, s).values() if v).lower()
        for marqueur, _ in FAUTES_HISTORIQUES:
            assert marqueur.lower() not in blob, f"{marqueur!r} mord le texte {lang}"


# ── Differentiel de provenance : anti-oubli, puis les deux moities ────────

# Les marqueurs de provenance ne sont PAS fautifs en soi. « SBTi »,
# « ISO 14001 », « ODD 7 », « -42 % », « cible 40 % » deviennent VRAIS des que
# le consultant declare la donnee correspondante. L'invariant a exprimer n'est
# donc pas « cette chaine n'apparait jamais » mais « elle apparait SI ET
# SEULEMENT SI le champ amont est renseigne ».
#
# Moitie « sans la donnee » : ecrivable aujourd'hui -- c'est l'etat du produit.
# Moitie « avec la donnee »  : non exprimable, aucun champ n'existe (DETTE 0bis).

# Motifs de nom de champ qu'introduirait l'etape B. Verifies contre les 62
# champs actuels : aucun ne correspond. NB : « target » nu est exclu a dessein,
# CompanyInfo.target_year existe deja ; de meme « framework », a cause de
# ESGRequest.reporting_framework.
MOTIFS_CHAMPS_ETAPE_B = [
    r"sbti", r"science_based", r"sdg", r"odd",
    r"iso_?\d", r"certification", r"dnsh", r"sfdr", r"commitment",
    r"base(line)?_year",
    r"(reduction|emission|carbon|climate)_target", r"target_(reduction|percent)",
    r"(parity|gender|diversity)_target",
]


def _tous_les_champs_du_modele():
    from models import (ESGRequest, CompanyInfo, EnvironmentalData, SocialData,
                        GovernanceData, TaxonomyData)
    champs = []
    for modele in (ESGRequest, CompanyInfo, EnvironmentalData, SocialData,
                   GovernanceData, TaxonomyData):
        champs += [(modele.__name__, nom) for nom in modele.model_fields]
    return champs


def test_anti_oubli_letape_b_rallume_le_differentiel():
    """LE test qui empeche le differentiel de pourrir en `skip` oublie.

    Tant qu'aucun champ d'engagement n'existe, la moitie « avec la donnee »
    est inecrivable et reste skippee. Le jour ou l'etape B ajoute ces
    champs, CE test casse -- et force a retirer les decorateurs `skip`.
    Ne pas le neutraliser : le supprimer, c'est condamner la moitie
    « avec » a ne jamais etre rallumee.
    """
    import re
    trouves = [(modele, champ) for modele, champ in _tous_les_champs_du_modele()
               for motif in MOTIFS_CHAMPS_ETAPE_B if re.search(motif, champ, re.I)]
    assert not trouves, (
        f"L'etape B semble avoir atterri : {trouves}. "
        "Retirer les @pytest.mark.skip du differentiel de provenance "
        "(tests test_provenance_*_avec_la_donnee) et renseigner ces champs "
        "dans leur corps, deja ecrit. Voir DETTE.md § 0bis.")


# ── Moitie « AVEC la donnee » : ecrite, skippee, pas xfail ────────────────

# POURQUOI `skip` ET JAMAIS `xfail` : les champs ci-dessous n'existent pas
# encore. Les affecter leve une erreur de validation Pydantic -- pas un echec
# d'assertion. Un `xfail` non strict passerait sur CETTE erreur et afficherait
# un voyant vert qui ne mesure rien du tout. `skip` dit la verite : le test
# n'est pas execute.
#
# Le corps est ecrit EN ENTIER : le jour ou l'etape B atterrit, retirer le
# decorateur suffit. Et si quelqu'un oublie de le retirer,
# test_anti_oubli_letape_b_rallume_le_differentiel casse.
_MOTIF_SKIP = ("Etape B non faite : aucun champ ne permet de saisir une cible, "
               "une certification ou un ODD (DETTE.md § 0bis). Retirer ce "
               "decorateur le jour ou ces champs atterrissent -- le corps est "
               "deja ecrit.")


@pytest.mark.skip(reason=_MOTIF_SKIP)
@pytest.mark.parametrize("lang", ["fr", "en"])
def test_provenance_avec_la_donnee_la_cible_declaree_est_citee(lang):
    """Moitie « AVEC la donnee » : un engagement SAISI doit etre CITE.

    Symetrique de test_provenance_sans_donnee_... : la meme chaine qui est
    interdite sans donnee devient obligatoire avec. C'est cette moitie qui
    empeche le garde-fou de degenerer en ban absolu -- et c'est elle qui
    prouve que le garde-fou discrimine au lieu d'interdire.
    """
    r = make_request(lang)
    r.environmental.carbon_reduction_target_percent = 42      # etape B
    r.environmental.baseline_year = 2019                      # etape B
    r.company.claimed_frameworks = ["SBTi"]                   # etape B
    r.company.iso_certifications = ["ISO 14001"]              # etape B
    r.company.selected_sdgs = [7, 13]                         # etape B

    pdf = _textes_des_livrables(r)["pdf"]
    attendus = ["42", "SBTi", "ISO 14001", "2019"]
    attendus.append("ODD 7" if lang == "fr" else "SDG 7")
    for attendu in attendus:
        assert attendu in pdf, (
            f"{attendu!r} a ete DECLARE par le consultant mais n'apparait pas "
            f"dans le rapport {lang} : donnee collectee, jamais imprimee.")


@pytest.mark.skip(reason=_MOTIF_SKIP)
@pytest.mark.parametrize("lang", ["fr", "en"])
def test_provenance_avec_la_donnee_lobjectif_de_parite_est_cite(lang):
    """Idem pour l'objectif de parite : « cible 40 % » est faux tant que
    personne ne l'a declare, VRAI des que le client le declare -- c'est
    meme ce que la recommandation « Definir des objectifs chiffres de
    parite » lui demande de produire."""
    r = make_request(lang)
    r.governance.female_board_percent = 33
    r.governance.gender_parity_target_percent = 40            # etape B

    pdf = _textes_des_livrables(r)["pdf"]
    attendu = "cible 40 %" if lang == "fr" else "40% target"
    assert attendu in pdf, (
        f"{attendu!r} a ete DECLARE comme objectif du client mais n'apparait "
        f"pas dans le rapport {lang}.")
