"""Aperçu vivant du sélecteur de gabarit (POST /api/preview, 2026-09-28).

Couverture + « coup d'œil » du gabarit demandé, avec les données du dossier,
en PNG. Sans pypdfium2, 503 : l'interface garde la vignette.
"""
import io
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_suite import dossier_a_transparente  # noqa: E402


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app, base_url="http://localhost")


@pytest.mark.parametrize("theme", ["aurora", "annuel", "institutionnel", "portrait", "terre", "galerie"])
def test_apercu_de_chaque_gabarit(client, theme):
    from PIL import Image
    corps = dossier_a_transparente().model_dump(mode="json")
    corps["aesthetic_theme"] = theme
    r = client.post("/api/preview", json=corps)
    assert r.status_code == 200 and r.headers["content-type"] == "image/png"
    im = Image.open(io.BytesIO(r.content))
    assert im.mode == "RGBA" and im.width > 2 * im.height * 0.6      # deux pages A4 côte à côte
    alpha = im.getchannel("A").getpixel((im.width // 2, im.height // 2))
    assert alpha == 0                                                 # l'écart entre pages est transparent


def test_l_apercu_porte_les_donnees_du_dossier():
    from esg_calculator import calculate_esg_scores
    from report_generator import preview_pdf
    import fitz
    r = dossier_a_transparente()
    doc = fitz.open(stream=preview_pdf(r, calculate_esg_scores(r)), filetype="pdf")
    assert doc.page_count == 2
    texte = " ".join(str(p.get_text()) for p in doc)
    assert r.company.name in texte and "coup d" in texte


def test_sans_pypdfium2_repli_503(client, monkeypatch):
    import preview

    def indisponible(_pdf):
        raise preview.PreviewUnavailable("absent")
    monkeypatch.setattr(preview, "render", indisponible)
    assert client.post("/api/preview", json=dossier_a_transparente().model_dump(mode="json")).status_code == 503
