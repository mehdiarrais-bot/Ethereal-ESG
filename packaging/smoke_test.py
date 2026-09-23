"""
Test de fumee de l'executable construit.

Usage : python packaging/smoke_test.py dist/EtherealESG/EtherealESG[.exe]

Verifie, sur le binaire reel (pas sur le code source) :
  - le serveur demarre et l'interface est servie (pas une 404 JSON) ;
  - les 5 livrables + le questionnaire sortent en FR et en EN, non vides,
    avec la bonne signature de format ;
  - un dossier client sauvegarde atterrit dans ESG_DATA_DIR (hors de l'exe) ;
  - le rapport PDF est compose dans les polices embarquees du gabarit
    (preuve que backend/assets/ a bien ete inclus dans l'executable).
Toute anomalie fait echouer le script (code retour 1).
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"

PAYLOAD = {
    "company": {"name": "Acme Industries", "sector": "Industrie manufacturière",
                "country": "France", "revenue_eur": 48_000_000,
                "reporting_year": 2025, "target_year": 2030,
                "presenter_name": "J. Martin", "presenter_title": "Directrice Générale"},
    "environmental": {"co2_emissions_tonnes": 8200, "scope1_emissions": 1200,
                      "scope2_emissions": 2100, "scope3_emissions": 4900,
                      "renewable_energy_percent": 42, "waste_recycled_percent": 63},
    "social": {"female_employees_percent": 34, "training_hours_per_employee": 22,
               "accident_frequency_rate": 6.2, "employee_count": 320},
    "governance": {"esg_audit_conducted": False, "sustainability_committee": True,
                   "data_breaches": 1, "independent_board_percent": 45},
    "taxonomy": {"turnover_aligned_percent": 38, "capex_aligned_percent": 52},
    "aesthetic_theme": "aurora",
}

# endpoint -> signature attendue en tete de fichier
DELIVERABLES = {
    "pdf": b"%PDF",
    "pptx": b"PK",
    "docx": b"PK",
    "onepager": b"%PDF",
    "proposal": b"PK",
    "questionnaire": b"<",
}


def request(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.status, r.headers.get("content-type", ""), r.read()


def main(exe):
    failures = []
    data_dir = tempfile.mkdtemp(prefix="esg_smoke_")
    env = dict(os.environ, ESG_DATA_DIR=data_dir, ESG_NO_BROWSER="1")
    proc = subprocess.Popen([exe], env=env, stdin=subprocess.DEVNULL)
    try:
        for _ in range(120):
            try:
                request("GET", "/health")
                break
            except Exception:
                if proc.poll() is not None:
                    print(f"[ECHEC] L'executable s'est arrete (code {proc.returncode}).")
                    return 1
                time.sleep(1)
        else:
            print("[ECHEC] Le serveur n'a pas demarre en 120 s.")
            return 1

        _, ctype, body = request("GET", "/")
        if "text/html" not in ctype or b"<div id=\"root\"" not in body:
            failures.append(f"interface non servie (content-type={ctype})")

        for lang in ("fr", "en"):
            for name, magic in DELIVERABLES.items():
                label = f"{name}/{lang}"
                try:
                    status, _, out = request("POST", f"/api/generate/{name}",
                                             dict(PAYLOAD, language=lang))
                except urllib.error.HTTPError as e:
                    failures.append(f"{label} : HTTP {e.code}")
                    continue
                ok = status == 200 and len(out) > 1000 and out.lstrip()[:len(magic)] == magic
                if name == "questionnaire" and f'<html lang="{lang}">'.encode() not in out:
                    ok = False  # servi dans la mauvaise langue
                if name == "pdf" and b"Newsreader" not in out:
                    ok = False  # assets/ non embarques : repli silencieux en base-14
                print(f"  {'OK ' if ok else 'KO '} {label:<18} {len(out):>9} octets")
                if not ok:
                    failures.append(f"{label} : statut {status}, {len(out)} octets")

        _, _, out = request("POST", "/api/clients", {"form": dict(PAYLOAD, language="fr")})
        cid = json.loads(out)["id"]
        if not os.path.isfile(os.path.join(data_dir, f"{cid}.json")):
            failures.append(f"dossier client absent de ESG_DATA_DIR ({data_dir})")
        else:
            print(f"  OK  persistance client dans {data_dir}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()

    if failures:
        print("\n[ECHEC]\n  - " + "\n  - ".join(failures))
        return 1
    print("\n[OK] Test de fumee reussi.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
