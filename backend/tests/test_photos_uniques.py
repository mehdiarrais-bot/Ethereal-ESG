"""Une photo n'apparaît qu'une fois par rapport (demande du 2026-09-28).

Avant : la photo de couverture revenait jusqu'à 3 fois (couverture, bandeau
du « coup d'œil », quatrième), celle de l'environnement jusqu'à 3 fois
(Galerie), et les tuiles social / gouvernance restaient vides sans photo
fournie. La répartition (photo_bank) est planifiée à la création du Kit.
"""
import base64
import io
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_suite import dossier_a_transparente              # noqa: E402
from models import AestheticTheme                          # noqa: E402
from pdf_kit import Kit, assets_dir                        # noqa: E402
import photo_bank                                          # noqa: E402

SECTEURS = ["Industrie manufacturière", "Transport & logistique", "Construction & BTP",
            "Agroalimentaire", "Énergie", "Commerce & distribution", "Services",
            "Numérique & télécoms", "Tourisme & hôtellerie", "Autre"]


def _dossier(theme, secteur, photos=None):
    r = dossier_a_transparente()
    r = r.model_copy(update={"aesthetic_theme": theme, "report_photos": photos,
                             "company": r.company.model_copy(update={"sector": secteur})})
    return r


@pytest.mark.parametrize("theme", list(AestheticTheme), ids=lambda t: t.value)
@pytest.mark.parametrize("secteur", SECTEURS)
def test_aucune_photo_deux_fois_et_aucun_emplacement_vide(theme, secteur):
    k = Kit(_dossier(theme, secteur))
    origines = [o for o, _ in k._photos.values()]
    assert len(origines) == len(set(origines)), origines
    attendus = [p for p in photo_bank.document_places(k.layout["cover"], k.layout["glance"])
                if p != "company_section"]                  # photo de l'entreprise seulement
    assert all(k.photo(p) for p in attendus), [p for p in attendus if not k.photo(p)]


def _jpeg(couleur):
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (400, 300), couleur).save(buf, "JPEG")
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def test_les_photos_du_client_passent_en_premier_et_une_seule_fois():
    photos = {"cover": _jpeg("red"), "company": _jpeg("blue"), "social": _jpeg("green")}
    k = Kit(_dossier(AestheticTheme("galerie"), "Services", photos))
    plan = {p: o for p, (o, _) in k._photos.items()}
    assert plan["cover"] == "client:cover"
    assert plan["company_section"] == "client:company"     # section « L'entreprise en bref »
    assert plan["cover_social"] == "client:social"
    assert plan["glance_social"].startswith("bank:people")  # la photo client n'est pas répétée
    assert not plan["back"].startswith("client:")


def test_la_banque_est_complete_et_creditee():
    dossier = os.path.join(assets_dir(), "photos")
    credits = open(os.path.join(dossier, "CREDITS.md"), encoding="utf8").read()
    noms = set(photo_bank.NATURE) | set(photo_bank.GOVERNANCE)
    for fam in ("industrie", "transport", "construction", "agro", "energie", "commerce",
                "services", "numerique", "tourisme"):
        noms |= {f"sector-{fam}", f"sector-{fam}-2", f"sector-{fam}-3"}
        if fam != "energie":
            noms.add(f"people-{fam}")
    noms |= {"sector-general", "sector-general-2", "sector-general-3", "people-general",
             "people-general-2"}
    for n in sorted(noms):
        assert os.path.isfile(os.path.join(dossier, f"{n}.jpg")), n
        assert f"{n}.jpg" in credits, f"{n}.jpg sans crédit"


def test_mention_de_la_banque_exacte():
    photos = {s: _jpeg("grey") for s in ("cover", "company", "environment")}
    k = Kit(_dossier(AestheticTheme("aurora"), "Services", photos))
    assert not k.uses_bank(("cover",)) and k.uses_bank()    # la 4e de couverture vient de la banque


def test_emplacement_inconnu_refuse():
    with pytest.raises(KeyError):
        Kit(dossier_a_transparente()).photo("bandeau")
