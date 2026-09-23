"""API locale : refus des requêtes venant d'un site web tiers, import borné.

Audit du 2026-09-24 : deux attaques reproduites depuis une page web ouverte
dans le navigateur du consultant pendant que l'application tourne —
l'import d'une archive par formulaire intersite (dossier écrasé) et la
lecture de l'API par rebinding DNS. Chaque test ci-dessous rejoue l'une
d'elles et doit échouer si la protection est retirée.
"""
import io
import json
import os
import sys
import zipfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FORM = {"company": {"name": "Acme", "sector": "Industrie", "country": "France",
                    "reporting_year": 2025},
        "environmental": {}, "social": {}, "governance": {}, "language": "fr"}
CID = "a" * 32


@pytest.fixture()
def client(tmp_path, monkeypatch):
    import client_store
    monkeypatch.setattr(client_store, "DATA_DIR", str(tmp_path))
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)


def _archive(dossiers: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, payload in dossiers.items():
            z.writestr(name, payload if isinstance(payload, (bytes, str)) else json.dumps(payload))
    return buf.getvalue()


def test_import_par_formulaire_intersite_refuse(client):
    """L'attaque reproduite : formulaire multipart posté depuis un autre site."""
    r = client.post("/api/clients-import",
                    files={"file": ("x.zip", _archive({f"{CID}.json": {"id": CID, "form": FORM}}),
                                    "application/zip")},
                    headers={"Origin": "https://site-tiers.example"})
    assert r.status_code == 403
    assert client.get("/api/clients").json() == []


@pytest.mark.parametrize("headers", [
    {"Origin": "null"},                              # iframe sandboxée, fichier local
    {"Sec-Fetch-Site": "cross-site"},                # navigateur sans en-tête Origin
    {"Origin": "http://localhost.site-tiers.example"},
])
def test_ecriture_depuis_une_origine_etrangere_refusee(client, headers):
    assert client.post("/api/clients", json={"form": FORM}, headers=headers).status_code == 403
    assert client.delete(f"/api/clients/{CID}", headers=headers).status_code == 403


def test_rebinding_dns_refuse(client):
    """Un domaine tiers résolu vers 127.0.0.1 ne lit pas les dossiers."""
    assert client.get("/api/clients", headers={"Host": "attaquant.example"}).status_code == 403
    assert client.get("/api/clients", headers={"Host": "attaquant.example:8000"}).status_code == 403


@pytest.mark.parametrize("origin", [None, "http://localhost:8000", "http://127.0.0.1:51234",
                                    "http://localhost:5173"])
def test_interface_locale_acceptee(client, origin):
    """L'interface servie en local (exe, Vite, Docker) n'est jamais bloquée."""
    headers = {"Origin": origin} if origin else {}
    assert client.post("/api/clients", json={"form": FORM}, headers=headers).status_code == 200


def test_hotes_autorises_par_defaut():
    import main
    assert main.request_refusal("GET", {"host": "localhost:8000"}) is None
    assert main.request_refusal("GET", {"host": "127.0.0.1:61000"}) is None
    assert main.request_refusal("GET", {"host": "[::1]:8000"}) is None
    assert main.request_refusal("POST", {"host": "localhost", "origin": "https://x.example"})


def test_ecoute_locale_par_defaut():
    """`python main.py` n'expose plus l'API sur le réseau (0.0.0.0)."""
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py"),
               encoding="utf-8").read()
    assert 'host="0.0.0.0"' not in src
    assert 'os.environ.get("ESG_HOST", "127.0.0.1")' in src


# ── Import d'archive ──────────────────────────────────────────────────────

def test_dossier_invalide_ignore(client):
    """Un dossier que le modèle refuserait à la saisie n'est pas écrit."""
    bad = dict(FORM, company=dict(FORM["company"], logo_base64="data:image/png;base64,AAAA"))
    r = client.post("/api/clients-import", files={"file": ("x.zip", _archive({
        f"{CID}.json": {"id": CID, "form": bad},
        f"{'b' * 32}.json": {"id": "b" * 32, "form": FORM}}), "application/zip")})
    assert r.json() == {"imported": 1, "skipped": 1}


def test_bombe_de_decompression_bornee(client, monkeypatch):
    import client_store
    monkeypatch.setattr(client_store, "MAX_DOSSIER_BYTES", 10_000)
    enorme = json.dumps({"id": CID, "form": FORM, "pad": "0" * 1_000_000})  # ~1 Mo, compresse à ~1 Ko
    r = client.post("/api/clients-import",
                    files={"file": ("x.zip", _archive({f"{CID}.json": enorme}), "application/zip")})
    assert r.json() == {"imported": 0, "skipped": 1}


def test_volume_total_borne(client, monkeypatch):
    import client_store
    monkeypatch.setattr(client_store, "MAX_ARCHIVE_TOTAL", 1_000)
    dossiers = {f"{c * 32}.json": {"id": c * 32, "form": FORM} for c in "abcdef"}
    r = client.post("/api/clients-import", files={"file": ("x.zip", _archive(dossiers), "application/zip")})
    assert r.status_code == 422 and "volume" in r.json()["detail"]
