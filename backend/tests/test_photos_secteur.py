"""Couvertures par secteur (banque CC0, ajoutées le 2026-09-26).

La photo de couverture suit la famille de secteur du client ; une photo
fournie par l'entreprise prime ; un secteur non reconnu garde la photo du
gabarit. Chaque fichier a sa provenance dans CREDITS.md.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_suite import make_request             # noqa: E402
from models import CompanyInfo                  # noqa: E402
from pdf_kit import Kit, bank_photo, assets_dir  # noqa: E402
from analysis import _FAMILIES                  # noqa: E402
from report_designs import design               # noqa: E402

FAMILLES = [f for f, _ in _FAMILIES]


def _req(sector, **kw):
    return make_request(company=CompanyInfo(name="X", sector=sector, country="France",
                                            reporting_year=2025, target_year=2030), **kw)


def test_chaque_famille_a_sa_photo_et_sa_provenance():
    credits = open(os.path.join(assets_dir(), "photos", "CREDITS.md"), encoding="utf-8").read()
    for fam in FAMILLES:
        assert bank_photo(f"sector-{fam}"), fam
        assert f"sector-{fam}.jpg" in credits and "CC0" in credits, fam


def test_la_couverture_suit_le_secteur():
    assert Kit(_req("Logistique & Transport")).photo("cover") == bank_photo("sector-transport")
    assert Kit(_req("Numérique & Tech")).photo("cover") == bank_photo("sector-numerique")


def test_secteur_non_reconnu_garde_la_photo_du_gabarit():
    r = _req("Autre")
    assert Kit(r).photo("cover") == bank_photo(design(r.aesthetic_theme)["photos"]["cover"])


def test_l_environnement_reste_un_paysage():
    r = _req("Logistique & Transport")
    assert Kit(r).photo("environment") == bank_photo(design(r.aesthetic_theme)["photos"]["environment"])


def test_la_photo_du_client_prime():
    import base64, io
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (40, 30), (10, 20, 30)).save(buf, format="JPEG")
    url = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    k = Kit(_req("Logistique & Transport", report_photos={"cover": url}))
    assert k.photo("cover") != bank_photo("sector-transport")
