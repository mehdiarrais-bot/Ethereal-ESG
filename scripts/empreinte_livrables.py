#!/usr/bin/env python3
"""
Empreinte des livrables PowerPoint et Word, pour prouver qu'une refonte ne
change rien au rendu.

Écrit, pour 19 dossiers fictifs (6 gabarits × 2 langues, dossier de test,
couleurs du client, sans recommandations, autres types de présentation et
de rapport, dossier vide, logo et illustration de couverture), toutes les
parties XML des fichiers générés (horodatages retirés) et l'empreinte SHA-1
des images. Deux exécutions sur le même code donnent le même fichier.

    python scripts/empreinte_livrables.py avant.txt   # code d'origine
    python scripts/empreinte_livrables.py apres.txt   # code modifié
    cmp avant.txt apres.txt                           # doit être silencieux

Servi pour le découpage de generate_pptx / generate_word_report
(2026-09-25). Données entièrement fictives.
"""
import hashlib
import io
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for chemin in ("backend", "scripts", os.path.join("backend", "tests")):
    sys.path.insert(0, os.path.join(ROOT, chemin))
os.chdir(os.path.join(ROOT, "backend"))

from PIL import Image                                                        # noqa: E402

import make_examples as mx                                                   # noqa: E402
from test_suite import make_request                                         # noqa: E402
from models import AestheticTheme, ESGRequest, PresentationType, ReportType  # noqa: E402
from esg_calculator import calculate_esg_scores                             # noqa: E402
from content_generator import generate_esg_content                          # noqa: E402
from ppt_generator import generate_pptx                                     # noqa: E402
from docx_generator import generate_word_report                             # noqa: E402
from main import build_advanced_charts, build_extras                        # noqa: E402
from branding import auto_brand                                             # noqa: E402

_HORODATAGE = re.compile(r"<dcterms:(created|modified)[^>]*>[^<]*</dcterms:\1>")


def _parties(data: bytes) -> str:
    """Parties XML en clair (sans horodatage), autres parties par SHA-1."""
    z = zipfile.ZipFile(io.BytesIO(data))
    out = []
    for nom in sorted(z.namelist()):
        contenu = z.read(nom)
        if nom.endswith(".xml") or nom.endswith(".rels"):
            out.append(f"--- {nom}\n{_HORODATAGE.sub('', contenu.decode('utf-8'))}")
        else:
            out.append(f"--- {nom} sha1={hashlib.sha1(contenu).hexdigest()}")
    return "\n".join(out)


def _cas() -> list:
    cas = [(f"demo-{theme.value}-{lang}",
            mx.DEMO.model_copy(update={"aesthetic_theme": theme, "language": lang}))
           for theme in AestheticTheme for lang in ("fr", "en")]
    cas += [
        ("tests-fr", make_request("fr")),
        ("tests-marque-en", make_request("en", custom_colors=auto_brand("NovaFlux"))),
        ("sans-recos-investisseurs-fr", make_request("fr", include_recommendations=False,
                                                     presentation_type=PresentationType.INVESTOR_DECK)),
        ("rapport-annuel-en", make_request("en", presentation_type=PresentationType.ANNUAL_REPORT)),
        ("livre-blanc-fr", make_request("fr", report_type=ReportType.WHITE_PAPER)),
        ("synthese-en", make_request("en", report_type=ReportType.EXECUTIVE_SUMMARY_PDF)),
        ("vide-fr", ESGRequest(company={"name": "Vide", "sector": "Services", "country": "France",
                                        "reporting_year": 2025},
                               environmental={}, social={}, governance={}, language="fr")),
    ]
    return cas


def _logo() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (120, 60), (20, 90, 60)).save(buf, "PNG")
    return buf.getvalue()


def main(sortie: str) -> None:
    logo_client = _logo()
    cas = _cas()
    with open(sortie, "w", encoding="utf-8") as out:
        for nom, req in cas:
            s = calculate_esg_scores(req)
            c = generate_esg_content(req, s)
            logo, art = build_extras(req)
            if nom.startswith("demo-portrait") or nom.startswith("demo-terre") or nom == "tests-fr":
                logo = logo_client  # un logo client, sur des couvertures de styles différents
            sombres = {"cover_art": art} if art else {}
            sombres.update(build_advanced_charts(req, s, light_bg=False))
            clairs = build_advanced_charts(req, s, light_bg=True)
            out.write(f"===== {nom} PPTX\n" + _parties(generate_pptx(req, s, c, sombres, logo_bytes=logo)) + "\n")
            art_word = art if nom.startswith("demo-") else None  # illustration de couverture Word
            out.write(f"===== {nom} DOCX\n" + _parties(generate_word_report(
                req, s, c, logo_bytes=logo, cover_art=art_word, charts=clairs)) + "\n")
    print("ok", len(cas), "cas")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
