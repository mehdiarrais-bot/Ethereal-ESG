"""
Gestion des dossiers clients — stockage 100 % local (JSON sur disque).

Chaque dossier : {id, name, sector, created_at, updated_at, form,
score_history: [{year, saved_at, scores{env,social,gov,total,rating}}]}.
L'historique est indexé par exercice (reporting_year) : une sauvegarde
du même exercice remplace l'entrée, un nouvel exercice s'ajoute —
ce qui permet le suivi année après année d'un même client.
"""
import json
import os
import re
import uuid
from datetime import datetime, timezone

DATA_DIR = os.environ.get(
    "ESG_DATA_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "clients"),
)

_ID_RE = re.compile(r"^[0-9a-f]{32}$")


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _path(client_id: str) -> str:
    if not _ID_RE.match(client_id):
        raise ValueError("invalid client id")
    return os.path.join(DATA_DIR, f"{client_id}.json")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _atomic_write(path: str, data: dict):
    """Écriture atomique (temp + rename) : une coupure en cours d'écriture
    ne peut pas corrompre un dossier existant."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(tmp, path)


# Statuts du mini-CRM (cycle de vie d'une mission freelance)
STATUSES = ("prospect", "signed", "delivered", "archived")


def list_clients() -> list:
    """Liste synthétique, triée par date de mise à jour décroissante."""
    _ensure_dir()
    out = []
    for fn in os.listdir(DATA_DIR):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(DATA_DIR, fn), encoding="utf-8") as f:
                d = json.load(f)
            last = d["score_history"][-1] if d.get("score_history") else None
            out.append({
                "id": d["id"], "name": d.get("name", "—"),
                "sector": d.get("sector", ""), "updated_at": d.get("updated_at", ""),
                "status": d.get("status", "prospect"),
                "years": [h["year"] for h in d.get("score_history", [])],
                "last_score": (last or {}).get("scores", {}).get("total"),
                "last_rating": (last or {}).get("scores", {}).get("rating"),
                # trajectoire condensée pour la vue portefeuille
                "history": [{"year": h["year"], "total": h["scores"].get("total")}
                            for h in d.get("score_history", [])],
            })
        except Exception:
            continue  # fichier corrompu : ignoré de la liste
    out.sort(key=lambda c: c["updated_at"], reverse=True)
    return out


def set_status(client_id: str, status: str) -> dict:
    """Change le statut CRM d'un dossier."""
    if status not in STATUSES:
        raise ValueError("invalid status")
    d = get_client(client_id)
    d["status"] = status
    d["updated_at"] = _now()
    _atomic_write(_path(client_id), d)
    return d


def export_all() -> bytes:
    """Archive zip de tous les dossiers (sauvegarde portable)."""
    import zipfile
    _ensure_dir()
    buf = __import__("io").BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for fn in sorted(os.listdir(DATA_DIR)):
            if fn.endswith(".json"):
                z.write(os.path.join(DATA_DIR, fn), arcname=fn)
    buf.seek(0)
    return buf.read()


def import_archive(data: bytes) -> dict:
    """Restaure une archive zip de dossiers. Fusion par id (l'archive gagne).
    Retourne {imported, skipped}."""
    import zipfile
    _ensure_dir()
    imported, skipped = 0, 0
    with zipfile.ZipFile(__import__("io").BytesIO(data)) as z:
        for info in z.infolist():
            fn = os.path.basename(info.filename)
            if not fn.endswith(".json"):
                continue
            stem = fn[:-5]
            if not _ID_RE.match(stem):
                skipped += 1
                continue
            try:
                d = json.loads(z.read(info).decode("utf-8"))
                if d.get("id") != stem or "form" not in d:
                    skipped += 1
                    continue
                _atomic_write(_path(stem), d)
                imported += 1
            except Exception:
                skipped += 1
    return {"imported": imported, "skipped": skipped}


def get_client(client_id: str) -> dict:
    with open(_path(client_id), encoding="utf-8") as f:
        return json.load(f)


def save_client(form: dict, scores: dict, client_id: str = None) -> dict:
    """Crée ou met à jour un dossier ; l'historique de scores est mis à
    jour pour l'exercice courant (remplacement) ou complété (nouvel exercice)."""
    _ensure_dir()
    now = _now()
    company = form.get("company", {}) or {}
    year = int(company.get("reporting_year") or 0)

    if client_id:
        d = get_client(client_id)
    else:
        d = {"id": uuid.uuid4().hex, "created_at": now, "score_history": []}

    d["name"] = (company.get("name") or "Sans nom").strip()[:200]
    d["sector"] = (company.get("sector") or "")[:100]
    d["updated_at"] = now
    d["form"] = form

    entry = {"year": year, "saved_at": now, "scores": scores}
    hist = [h for h in d.get("score_history", []) if h["year"] != year]
    hist.append(entry)
    hist.sort(key=lambda h: h["year"])
    d["score_history"] = hist

    _atomic_write(_path(d["id"]), d)
    return d


def delete_client(client_id: str) -> bool:
    p = _path(client_id)
    if os.path.exists(p):
        os.remove(p)
        return True
    return False
