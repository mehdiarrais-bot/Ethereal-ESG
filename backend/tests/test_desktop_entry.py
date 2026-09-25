"""Exécutable Windows : un seul fichier, sans console, fenêtre native.

Le binaire lui-même est vérifié par packaging/smoke_test.py (CI). Ici : la
logique du lanceur (backend/desktop_entry.py) et la forme du spec.
"""
import io
import os
import re
import socket
import sys

import pytest

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND)

import desktop_entry as DE  # noqa: E402


def test_esg_port_impose_le_port(monkeypatch):
    """Le test de fumée impose son port : il ne doit jamais parler à une
    autre instance (application déjà ouverte sur 8000, constaté le 2026-09-25)."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        libre = s.getsockname()[1]
    monkeypatch.setenv("ESG_PORT", str(libre))
    assert DE._choose_port() == (libre, False)


def test_esg_port_occupe_leve_une_erreur(monkeypatch):
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        s.listen()
        monkeypatch.setenv("ESG_PORT", str(s.getsockname()[1]))
        with pytest.raises(RuntimeError, match="ESG_PORT"):
            DE._choose_port()


def test_sans_console_la_sortie_va_dans_un_journal(monkeypatch, tmp_path):
    """console=False : sys.stdout vaut None ; uvicorn et print() doivent
    écrire dans %APPDATA%\\EtherealESG\\ethereal.log au lieu de planter."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    monkeypatch.setattr(sys, "stdout", None)
    monkeypatch.setattr(sys, "stderr", None)
    DE._redirect_output()
    print("ligne de journal")
    sys.stdout.flush()
    journal = tmp_path / "EtherealESG" / "ethereal.log"
    assert "ligne de journal" in journal.read_text(encoding="utf-8")
    sys.stdout.close()


def test_avec_console_rien_n_est_redirige(monkeypatch):
    out = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out)
    monkeypatch.setattr(sys, "stderr", out)
    DE._redirect_output()
    assert sys.stdout is out


def test_spec_un_seul_fichier_sans_console():
    with open(os.path.join(os.path.dirname(BACKEND), "packaging", "ethereal_esg.spec"),
              encoding="utf-8") as f:
        spec = f.read()
    code = "\n".join(l for l in spec.splitlines() if not l.lstrip().startswith("#"))
    assert "COLLECT(" not in code                 # onedir = dossier + COLLECT
    assert re.search(r"console\s*=\s*False", code)
    assert "a.binaries" in code and "a.datas" in code   # tout dans l'exe


def test_fenetre_native_autorise_les_telechargements():
    """Sans ALLOW_DOWNLOADS, WebView2 annule le téléchargement des livrables
    (lien blob + download) ; avec, une boîte « Enregistrer sous » s'ouvre."""
    with open(os.path.join(BACKEND, "desktop_entry.py"), encoding="utf-8") as f:
        assert 'webview.settings["ALLOW_DOWNLOADS"] = True' in f.read()
