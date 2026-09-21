"""
Point d'entrée de l'exécutable Windows (PyInstaller).

Responsabilités, et rien d'autre :
  1. Placer les données clients hors du dossier de l'exe (%APPDATA%), AVANT
     l'import de client_store qui fige DATA_DIR à l'import.
  2. Trouver un port : 8000 de préférence ; si une instance tourne déjà,
     ouvrir le navigateur dessus au lieu d'en lancer une seconde.
  3. Démarrer le serveur sur 127.0.0.1 uniquement (jamais exposé au réseau).
  4. Garder la console ouverte sur erreur fatale, pour qu'elle soit lisible.
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
PREFERRED_PORT = 8000
PORT_RANGE = range(8000, 8011)


def _data_dir() -> str:
    base = os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "EtherealESG", "clients")


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


def _open_when_ready(url: str, timeout: float = 60.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url + "/health", timeout=1):
                webbrowser.open(url)
                return
        except Exception:
            time.sleep(0.3)
    print(f"[!] Le serveur n'a pas repondu en {timeout:.0f} s. Ouvrez {url} manuellement.")


def main() -> int:
    if getattr(sys, "frozen", False):
        os.environ.setdefault("ESG_DATA_DIR", _data_dir())

    for port in PORT_RANGE:
        if _is_our_app(port):
            url = f"http://{HOST}:{port}"
            print(f"Ethereal ESG tourne deja sur {url}, ouverture du navigateur.")
            webbrowser.open(url)
            return 0
        if _port_free(port):
            break
    else:
        print(f"[ERREUR] Aucun port libre entre {PORT_RANGE.start} et {PORT_RANGE.stop - 1}.")
        return 1

    # Imports lourds APRÈS la configuration de l'environnement.
    import uvicorn
    from main import app

    url = f"http://{HOST}:{port}"
    print()
    print("  Ethereal ESG")
    print(f"  Adresse        : {url}")
    print(f"  Donnees clients: {os.environ.get('ESG_DATA_DIR', '(dossier du projet)')}")
    print()
    print("  Ne fermez pas cette fenetre tant que vous utilisez l'application.")
    print()

    if not os.environ.get("ESG_NO_BROWSER"):  # utilise par le test de fumee en CI
        threading.Thread(target=_open_when_ready, args=(url,), daemon=True).start()
    uvicorn.run(app, host=HOST, port=port, log_level="warning")
    return 0


if __name__ == "__main__":
    multiprocessing.freeze_support()
    try:
        code = main()
    except Exception:
        traceback.print_exc()
        code = 1
    if code != 0 and getattr(sys, "frozen", False):
        input("\nUne erreur est survenue. Appuyez sur Entree pour fermer...")
    sys.exit(code)
