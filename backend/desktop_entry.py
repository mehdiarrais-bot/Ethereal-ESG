"""
Point d'entrée de l'exécutable Windows (PyInstaller : un seul fichier, sans
console). Double-clic -> l'application s'ouvre dans sa propre fenêtre.

Responsabilités, et rien d'autre :
  1. Placer les données clients hors de l'exe (%APPDATA%), AVANT l'import
     de client_store qui fige DATA_DIR à l'import.
  2. Journaliser dans %APPDATA%\\EtherealESG\\ethereal.log : sans console,
     sys.stdout et sys.stderr valent None.
  3. Trouver un port : 8000 de préférence ; si une instance tourne déjà,
     ouvrir une fenêtre sur elle au lieu d'en lancer une seconde.
  4. Servir sur 127.0.0.1 uniquement (jamais exposé au réseau), dans un fil
     d'arrière-plan ; la fenêtre native (pywebview, moteur WebView2 de
     Windows) occupe le fil principal. Fermer la fenêtre arrête le serveur.
  5. Signaler une erreur fatale dans une boîte de dialogue Windows.

ESG_NO_WINDOW=1 (test de fumée en CI) : serveur seul, sans fenêtre, jusqu'à
l'arrêt du processus ; ESG_PORT impose le port (le test ne doit pas tomber
sur une autre instance). Si WebView2 est absent, repli sur le navigateur.
"""
import multiprocessing
import os
import socket
import sys
import threading
import time
import traceback
import urllib.request
import webbrowser

HOST = "127.0.0.1"
PORT_RANGE = range(8000, 8011)
TITLE = "Ethereal ESG"
WINDOW_SIZE = (1440, 900)
WINDOW_MIN_SIZE = (1100, 700)
STARTUP_TIMEOUT_S = 60.0


def _app_dir() -> str:
    base = os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "EtherealESG")


def _redirect_output() -> None:
    """Sans console, écrire dans un journal plutôt que dans le vide (uvicorn
    et les print() planteraient sur sys.stdout = None)."""
    if sys.stdout is not None and sys.stderr is not None:
        return
    os.makedirs(_app_dir(), exist_ok=True)
    log = open(os.path.join(_app_dir(), "ethereal.log"), "a", encoding="utf-8", buffering=1)
    sys.stdout = sys.stdout or log
    sys.stderr = sys.stderr or log


def _show_error(message: str) -> None:
    print(message)
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, message, TITLE, 0x10)  # MB_ICONERROR


def _is_our_app(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://{HOST}:{port}/health", timeout=1) as r:
            return b"Ethereal ESG" in r.read()
    except Exception:
        return False


def _port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOST, port))
            return True
        except OSError:
            return False


def _wait_ready(url: str) -> bool:
    deadline = time.monotonic() + STARTUP_TIMEOUT_S
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url + "/health", timeout=1):
                return True
        except Exception:
            time.sleep(0.2)
    return False


def _choose_port() -> tuple[int, bool]:
    """(port, instance_existante). Lève RuntimeError si tout est occupé."""
    forced = os.environ.get("ESG_PORT")
    if forced:
        if not _port_free(int(forced)):
            raise RuntimeError(f"Port {forced} (ESG_PORT) déjà utilisé.")
        return int(forced), False
    for port in PORT_RANGE:
        if _is_our_app(port):
            return port, True
        if _port_free(port):
            return port, False
    raise RuntimeError(f"Aucun port libre entre {PORT_RANGE.start} et {PORT_RANGE.stop - 1}.")


def _open_window(url: str) -> bool:
    """Fenêtre native, bloquante jusqu'à sa fermeture : True. Si WebView2 est
    indisponible, repli sur le navigateur, non bloquant : False."""
    try:
        import webview  # pyright: ignore[reportMissingImports]  # dépendance de l'exe seule (packaging/requirements-desktop.txt)
        # Les livrables se téléchargent (lien blob + download) : sans ce
        # réglage, WebView2 ignorerait le téléchargement.
        webview.settings["ALLOW_DOWNLOADS"] = True
        webview.create_window(TITLE, url, width=WINDOW_SIZE[0], height=WINDOW_SIZE[1],
                              min_size=WINDOW_MIN_SIZE)
        webview.start()
        return True
    except Exception:
        traceback.print_exc()
        webbrowser.open(url)
        return False


def _start_server(port: int):
    import uvicorn
    from main import app  # import lourd, APRÈS la configuration de l'environnement
    server = uvicorn.Server(uvicorn.Config(app, host=HOST, port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True, name="serveur")
    thread.start()
    return server, thread


def main() -> int:
    if getattr(sys, "frozen", False):
        os.environ.setdefault("ESG_DATA_DIR", os.path.join(_app_dir(), "clients"))
    headless = bool(os.environ.get("ESG_NO_WINDOW") or os.environ.get("ESG_NO_BROWSER"))

    port, existing = _choose_port()
    url = f"http://{HOST}:{port}"
    if existing:
        print(f"{TITLE} tourne déjà sur {url} : ouverture d'une fenêtre.")
        if not headless:
            _open_window(url)
        return 0

    server, thread = _start_server(port)
    print(f"{TITLE} — {url} — données : {os.environ.get('ESG_DATA_DIR', '(dossier du projet)')}")
    if not _wait_ready(url):
        raise RuntimeError(f"Le serveur n'a pas répondu en {STARTUP_TIMEOUT_S:.0f} s.")
    if headless:
        thread.join()
        return 0
    if not _open_window(url):
        thread.join()  # repli navigateur : pas de fenêtre à fermer, on sert
        return 0
    server.should_exit = True  # fenêtre fermée : on arrête proprement
    thread.join(timeout=5)
    return 0


if __name__ == "__main__":
    multiprocessing.freeze_support()
    _redirect_output()
    try:
        code = main()
    except Exception as exc:
        traceback.print_exc()
        _show_error(f"Ethereal ESG n'a pas pu démarrer :\n\n{exc}\n\n"
                    f"Détails : {os.path.join(_app_dir(), 'ethereal.log')}")
        code = 1
    sys.exit(code)
