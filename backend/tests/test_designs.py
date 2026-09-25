"""Gabarits éditoriaux des livrables (chantier du 2026-09-23).

Couvre : source unique des gabarits, reprise des anciens thèmes, photos
fournies par l'entreprise (validation et priorité sur la banque), banque de
photos et polices embarquées, sommaire paginé, absence de toute référence
externe dans les pages composées, route /api/designs.

Lancer depuis backend/ :  python -m pytest tests/ -q
"""
import base64
import io
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_suite import make_request                          # noqa: E402
from esg_calculator import calculate_esg_scores              # noqa: E402
from content_generator import generate_esg_content           # noqa: E402
from models import AestheticTheme, ESGRequest                # noqa: E402
import report_designs as RD                                  # noqa: E402

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _jpeg_data_url(color="#B03A2E", size=(800, 500)) -> str:
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, "JPEG")
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def _pdf(request):
    import fitz
    from report_generator import generate_pdf_report
    s = calculate_esg_scores(request)
    c = generate_esg_content(request, s)
    return fitz.open(stream=generate_pdf_report(request, s, c, {}), filetype="pdf")


def _text(doc) -> str:
    return re.sub(r"\s+", " ", " ".join(str(doc[i].get_text()) for i in range(doc.page_count)))


# ── Source unique ─────────────────────────────────────────────────────────

def test_chaque_theme_a_un_gabarit_complet():
    ref = RD.DESIGNS[RD.DEFAULT_DESIGN]
    assert set(RD.DESIGNS) == set(AestheticTheme)
    for theme, d in RD.DESIGNS.items():
        assert set(d["colors"]) == set(ref["colors"]), theme
        assert set(d["photos"]) == set(RD.BANK_SLOTS), theme
        for key in ("cover", "glance", "header", "kpi", "radius"):
            assert key in d["layout"], (theme, key)
        for v in d["colors"].values():
            assert re.fullmatch(r"#[0-9A-F]{6}", v), (theme, v)


def test_aucun_generateur_ne_redefinit_une_palette_de_theme():
    """Les générateurs convertissent report_designs ; ils ne portent plus de
    table de couleurs par thème (il y en avait cinq avant le chantier)."""
    for fichier in ("report_generator.py", "ppt_generator.py", "docx_generator.py",
                    "chart_generator.py", "onepager_generator.py", "proposal_generator.py",
                    "image_bank.py"):
        src = open(os.path.join(BACKEND, fichier), encoding="utf-8").read()
        for ancien in ("CORPORATE_BLUE", "GREEN_NATURE", "DARK_PREMIUM", "THEME_HEX = {",
                       "THEME_COLORS = {", "PALETTE = {", "ART_SPECS"):
            assert ancien not in src, f"{fichier} contient encore {ancien}"


@pytest.mark.parametrize("ancien,nouveau", sorted(RD.LEGACY_THEMES.items()))
def test_ancien_theme_relu_sous_le_gabarit_le_plus_proche(ancien, nouveau):
    assert make_request(theme=ancien).aesthetic_theme.value == nouveau


def test_theme_inconnu_refuse():
    with pytest.raises(Exception):
        make_request(theme="neon_galaxy")


# ── Assets embarqués ──────────────────────────────────────────────────────

def test_photos_de_la_banque_presentes_et_creditees():
    from pdf_kit import bank_photo, assets_dir
    credits = open(os.path.join(assets_dir(), "photos", "CREDITS.md"), encoding="utf-8").read()
    noms = {n for d in RD.DESIGNS.values() for n in d["photos"].values()}
    for nom in noms:
        assert bank_photo(nom), f"photo absente : {nom}.jpg"
        ligne = next((l for l in credits.splitlines() if l.startswith(f"| {nom}.jpg")), None)
        assert ligne, f"{nom}.jpg absent de CREDITS.md"
        assert "Public domain" in ligne or "CC0" in ligne, f"licence non libre : {ligne}"


def test_polices_embarquees_et_licence_ofl():
    from pdf_kit import assets_dir, font_family
    for d in RD.DESIGNS.values():
        for fam in (d["fonts"]["display"], d["fonts"]["body"]):
            assert os.path.isfile(os.path.join(assets_dir(), "fonts", fam, "OFL.txt")), fam
            noms = font_family(fam)
            assert all(n.startswith(fam) for n in noms.values()), f"repli base-14 pour {fam}"


@pytest.mark.parametrize("theme", [t.value for t in AestheticTheme])
def test_le_pdf_est_compose_dans_les_polices_du_gabarit(theme):
    doc = _pdf(make_request(theme=theme))
    polices = {f[3] for i in range(doc.page_count) for f in doc[i].get_fonts()}
    d = RD.design(theme)
    for fam in (d["fonts"]["display"], d["fonts"]["body"]):
        assert any(fam in p for p in polices), f"{fam} absente du PDF {theme} : {polices}"


# ── Photos fournies par l'entreprise ──────────────────────────────────────

def test_photo_client_prioritaire_sur_la_banque():
    from pdf_kit import Kit, bank_photo
    url = _jpeg_data_url()
    k = Kit(make_request(report_photos={"cover": url}))
    assert k.photo("cover") == base64.b64decode(url.split(",", 1)[1])
    assert k.photo("environment") == bank_photo(k.d["photos"]["environment"])


@pytest.mark.parametrize("slot", ["company", "social", "governance"])
def test_aucune_photo_d_illustration_hors_sujet(slot):
    """Retour utilisateur du 2026-09-24 : « des images aléatoires à des
    emplacements aléatoires ». Hors couverture et environnement, seule une
    photo fournie par l'entreprise peut apparaître ; sinon, rien."""
    from pdf_kit import Kit
    for theme in AestheticTheme:
        assert Kit(make_request(theme=theme.value)).photo(slot) is None
    url = _jpeg_data_url()
    assert Kit(make_request(report_photos={slot: url})).photo(slot)


def test_emplacement_photo_inconnu_refuse():
    with pytest.raises(Exception, match="Emplacement photo inconnu"):
        make_request(report_photos={"hero": _jpeg_data_url()})


def test_photo_non_image_refusee():
    faux = "data:image/png;base64," + base64.b64encode(b"pas une image").decode()
    with pytest.raises(Exception, match="Photo invalide"):
        make_request(report_photos={"cover": faux})


def test_photo_client_integree_au_pdf():
    """La photo de couverture fournie se retrouve dans le PDF (une image de
    plus que le rendu avec la banque seule n'est pas un critère : on vérifie
    la couleur du pixel central de la couverture Terre, occupée par la photo)."""
    doc = _pdf(make_request(theme="terre", report_photos={"cover": _jpeg_data_url("#B03A2E")}))
    pix = doc[0].get_pixmap(dpi=30)
    r, g, b = pix.pixel(pix.width // 2, int(pix.height * 0.3))
    assert r > 140 and g < 90 and b < 80, (r, g, b)


# ── Structure du rapport ──────────────────────────────────────────────────

def test_sommaire_renvoie_aux_bonnes_pages():
    """Le numéro affiché au sommaire est la page où la section commence."""
    from i18n import L
    doc = _pdf(make_request())
    TR = L("fr")
    toc = str(doc[1].get_text())
    assert TR["toc_title"] in toc
    for label in (TR["pdf_s1"], TR["pdf_s6"], TR["pdf_concl"]):
        m = re.search(re.escape(label) + r"\s+(\d{2})", toc)
        assert m, f"pas de numéro de page pour {label!r}"
        page = int(m.group(1))
        titre = label.split(". ", 1)[1]
        assert titre in str(doc[page - 1].get_text()), f"{label!r} annoncé page {page}"


def test_pages_composees_presentes():
    from i18n import L
    TR = L("fr")
    texte = _text(_pdf(make_request(company=make_request().company.model_copy(
        update={"ceo_quote": "Notre cap est fixé.", "key_initiatives": "programme Cap Climat"}))))
    for attendu in (TR["ed_company"], TR["ed_word"], TR["ed_glance"], TR["ed_focus"],
                    TR["ed_closing"], TR["ed_photo_note"], "programme Cap Climat"):
        assert attendu.lower() in texte.lower(), attendu


@pytest.mark.parametrize("theme", [t.value for t in AestheticTheme])
def test_aucune_reference_externe_dans_les_pages_composees(theme):
    """Les maquettes affichaient une « médiane sectorielle NAF » et un radar
    à six dimensions : données absentes du modèle, donc interdites (règle 9)."""
    texte = _text(_pdf(make_request(theme=theme))).lower()
    for interdit in ("médiane", "mediane", "naf 22", "moyenne sectorielle", "capital humain"):
        assert interdit not in texte, f"{interdit!r} dans le gabarit {theme}"


def test_rapport_anglais_compose():
    from i18n import L
    texte = _text(_pdf(make_request(lang="en", theme="galerie")))
    assert L("en")["ed_glance"] in texte and "coup d" not in texte


# ── API ───────────────────────────────────────────────────────────────────

def test_route_designs_sert_la_source_unique():
    from fastapi.testclient import TestClient
    from main import app
    data = TestClient(app).get("/api/designs").json()
    assert [d["id"] for d in data["designs"]] == [t.value for t in AestheticTheme]
    assert data["photo_slots"] == list(RD.CLIENT_PHOTO_SLOTS)
    aurora = data["designs"][0]
    assert aurora["colors"] == RD.DESIGNS[AestheticTheme.AURORA]["colors"]


def test_dossier_ancien_relu_avec_le_nouveau_gabarit(tmp_path, monkeypatch):
    import client_store
    monkeypatch.setattr(client_store, "DATA_DIR", str(tmp_path))
    from fastapi.testclient import TestClient
    from main import app
    c = TestClient(app)
    form = {"company": {"name": "Acme", "sector": "Industrie", "country": "France",
                        "reporting_year": 2025},
            "environmental": {}, "social": {}, "governance": {}, "language": "fr",
            "aesthetic_theme": "dark_premium"}
    cid = c.post("/api/clients", json={"form": form}).json()["id"]
    assert c.get(f"/api/clients/{cid}").json()["form"]["aesthetic_theme"] == "portrait"


def test_vignettes_du_selecteur_presentes():
    racine = os.path.dirname(BACKEND)
    for t in AestheticTheme:
        assert os.path.isfile(os.path.join(racine, "frontend", "public", "designs", f"{t.value}.jpg")), t


# ── Pagination (retour utilisateur du 2026-09-24) ─────────────────────────

def _layout(request):
    from report_generator import compose_report
    s = calculate_esg_scores(request)
    return compose_report(request, s, generate_esg_content(request, s), {})


def _jeu_de_donnees(nom: str):
    if nom == "demo":
        sys.path.insert(0, os.path.join(os.path.dirname(BACKEND), "scripts"))
        from make_examples import DEMO
        return DEMO
    return make_request()


# Un cas par combinaison (24) : chaque rendu est indépendant, ce qui permet
# de les répartir entre processus (pytest -n auto) — le test séquentiel
# prenait 47 s, le quart de la suite.
@pytest.mark.parametrize("theme", list(AestheticTheme), ids=lambda t: t.value)
@pytest.mark.parametrize("lang", ["fr", "en"])
@pytest.mark.parametrize("jeu", ["demo", "tests"])
def test_aucune_sequence_ne_finit_sur_une_page_presque_vide(jeu, lang, theme):
    """« Un bloc trop gros qui déborde sur une page pour 2-4 lignes » : la
    dernière page de chaque séquence de pages courantes (avant une page
    composée) doit être remplie au moins à SPARSE_FILL. 24 cas : deux jeux
    de données, deux langues, six gabarits."""
    from report_generator import _sparse_runs, SPARSE_FILL
    req = _jeu_de_donnees(jeu).model_copy(update={"aesthetic_theme": theme, "language": lang})
    _, layout = _layout(req)
    assert not _sparse_runs(layout), [(p, f) for p, _r, f in layout["pages"] if f < SPARSE_FILL]


def test_la_detection_de_debord_casse_sur_l_ancien_etat():
    """Règle d'admission : le garde-fou doit reconnaître le cas signalé
    (rapport EcoGroup : séquence finie sur une page remplie à 28 %)."""
    from report_generator import _sparse_runs
    assert _sparse_runs({"pages": [(5, 1, 0.75), (6, 1, 0.84), (7, 1, 0.28)]}) == {1}
    assert _sparse_runs({"pages": [(5, 1, 0.75), (6, 1, 0.5)]}) == set()
    assert _sparse_runs({"pages": [(9, 2, 0.1)]}) == set()   # page unique : pas un débord


def test_tableau_jamais_coupe_en_laissant_moins_de_trois_lignes():
    from report_generator import GuardedTable
    rows = [["en-tête"]] + [[f"ligne {i}"] for i in range(10)]
    t = GuardedTable(rows, colWidths=[200], rowHeights=[20] * 11, repeatRows=1)
    t.wrap(200, 1000)
    assert t.split(200, 65) == []          # 2 lignes seulement avant le saut : refusé
    parts = t.split(200, 105)              # 4 lignes avant, 6 après : accepté
    assert len(parts) == 2
    assert t.split(200, 205) == []         # 9 lignes avant, 1 seule après : refusé


def test_paragraphes_sans_veuves_ni_orphelines():
    from pdf_kit import Kit
    from report_generator import build_styles
    S = build_styles(Kit(make_request()))
    for nom in ("body", "lead", "bullet"):
        assert S[nom].allowWidows == 0 and S[nom].allowOrphans == 0, nom


# ── Texte analytique (narrative.py) ───────────────────────────────────────

def _textes_narratifs(req):
    import narrative as NR
    from content_generator import (risks_opportunities, compliance_assessment,
                                   enriched_recommendations, roadmap_12m)
    s = calculate_esg_scores(req)
    ro, gaps = risks_opportunities(req, s), compliance_assessment(req, s)
    recs, rm = enriched_recommendations(req, s), roadmap_12m(req, s)
    out = NR.company_paragraphs(req, "CSRD / ESRS")
    for p in ("env", "social", "gov"):
        out += NR.pillar_paragraphs(req, s, p) + [NR.levers_sentence(req, recs, p)]
    out += [NR.ghg_paragraph(req) or "", NR.act1_intro(req, s, gaps, ro["risks"]),
            NR.act2_intro(req, recs, rm), NR.gaps_intro(req, gaps, "CSRD / ESRS"),
            NR.risks_intro(req, ro["risks"]), NR.recs_intro(req, recs), NR.roadmap_intro(req, rm)]
    return out


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_texte_narratif_respecte_les_garde_fous(lang):
    from test_suite import FORMULATIONS_DE_VERIFICATION, _affirme_une_conformite
    for req in (make_request(lang), make_request(lang, environmental=make_request().environmental
                                                 .model_copy(update={"scope3_emissions": None}))):
        for texte in _textes_narratifs(req):
            assert "(s)" not in texte and "{" not in texte and "}" not in texte, texte
            assert " 1 actions" not in texte and " 1 recommandations" not in texte, texte
            assert not _affirme_une_conformite(texte), texte
            bas = texte.lower()
            for f in FORMULATIONS_DE_VERIFICATION:
                assert f not in bas, (f, texte)


def test_texte_cite_la_grille_du_score():
    """La tranche citée est celle de bands.py, et la pastille du PDF aussi."""
    import narrative as NR
    from bands import classer
    from report_generator import _status
    req = make_request()                                  # 42 % renouvelable
    tranche = classer("renewable_energy_percent", 42)
    assert any(f"42 %, un niveau {tranche}" in t for t in NR.indicator_readings(req, "env"))
    assert _status(req, "renewable_energy_percent", 42) == {"solide": "good", "exemplaire": "good",
                                                             "satisfaisant": "warn"}.get(tranche or "", "bad")


def test_indicateurs_manquants_listes_et_jamais_commentes():
    import narrative as NR
    req = make_request()                                  # pas de volume de déchets
    texte = " ".join(NR.pillar_paragraphs(req, calculate_esg_scores(req), "env"))
    assert "Restent à documenter" in texte and "le volume de déchets" in texte
    assert "biodiversité sont déclarées" not in texte


def test_le_rapport_porte_du_texte_sur_chaque_page_courante():
    """« Un manque cruel de texte réel » : chaque page courante porte au
    moins 120 mots de texte (tableaux compris), et le rapport de
    démonstration dépasse 3 500 mots."""
    import fitz
    sys.path.insert(0, os.path.join(os.path.dirname(BACKEND), "scripts"))
    from make_examples import DEMO
    pdf, layout = _layout(DEMO)
    doc = fitz.open(stream=pdf, filetype="pdf")
    mots = lambda i: len(re.findall(r"\w+", str(doc[i].get_text())))
    assert sum(mots(i) for i in range(doc.page_count)) > 3500
    for page in layout["content_pages"]:
        assert mots(page - 1) >= 120, f"page {page} : {mots(page - 1)} mots"
