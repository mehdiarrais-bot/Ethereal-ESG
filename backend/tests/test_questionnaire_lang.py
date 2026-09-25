"""
Questionnaire de collecte : la langue demandée est réellement appliquée,
et le CSV produit dans chaque langue reste réimportable.

Défaut ciblé : l'endpoint ignorait request.language, un client anglophone
recevait un questionnaire français identique octet pour octet.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from import_data import FIELD_SPECS, _LOOKUP, _norm, build_form  # noqa: E402
from questionnaire_generator import generate_questionnaire_html  # noqa: E402


def _html(lang):
    return generate_questionnaire_html(company_name="Acme", year=2025,
                                       consultant="J. Martin", lang=lang)


def test_html_lang_attribute_follows_request():
    assert '<html lang="fr">' in _html("fr")
    assert '<html lang="en">' in _html("en")


def test_english_questionnaire_has_no_french_ui_text():
    en = _html("en")
    # Formulations françaises visibles par le client (interface, pas données)
    for fr in ("Comment procéder", "Télécharger le fichier", "Tout effacer",
               "Votre entreprise", "Je ne sais pas", "Exercice 2025",
               "champ renseigné", "Effacer toutes les réponses"):
        assert fr not in en, f"texte français dans le questionnaire EN : {fr!r}"


def test_french_questionnaire_unchanged_in_substance():
    fr = _html("fr")
    for s in ("Comment procéder", "Télécharger le fichier", "Votre entreprise"):
        assert s in fr


def test_every_field_has_an_english_label():
    from questionnaire_generator import FIELD_META_EN
    missing = [key for _, key, _, _ in FIELD_SPECS if key not in FIELD_META_EN]
    assert not missing, f"libellés anglais manquants : {missing}"


def test_english_csv_labels_resolve_to_their_own_field():
    """Chaque en-tête du CSV anglais doit être réimporté vers le bon champ."""
    en = _html("en")
    m = re.search(r"const SCHEMA = (\[.*?\]);\n", en)
    assert m
    schema = m.group(1)
    import json
    for sec in json.loads(schema):
        for f in sec["fields"]:
            hit = _LOOKUP.get(_norm(f["csv"]))
            assert hit is not None, f"en-tête non reconnu à l'import : {f['csv']!r}"
            assert hit[1] == f["key"], f"{f['csv']!r} importé vers {hit[1]} au lieu de {f['key']}"


def test_english_csv_roundtrip_with_yes_no():
    form = build_form([("Field", "Value"),
                          ("Company name", "Acme"),
                          ("Scope 1 emissions", "1200"),
                          ("Sustainability committee", "Yes"),
                          ("Third-party verified reporting", "No")])["sections"]
    assert form["company"]["name"] == "Acme"
    assert form["environmental"]["scope1_emissions"] == 1200
    assert form["governance"]["sustainability_committee"] is True
    assert form["governance"]["esg_audit_conducted"] is False


def test_endpoint_passes_request_language():
    """Le défaut d'origine était dans l'endpoint, pas dans le générateur."""
    from fastapi.testclient import TestClient
    from main import app
    from test_suite import make_request
    client = TestClient(app)
    for lang in ("fr", "en"):
        body = make_request(lang=lang).model_dump(mode="json")
        r = client.post("/api/generate/questionnaire", json=body)
        assert r.status_code == 200
        assert f'<html lang="{lang}">' in r.text, f"questionnaire {lang} servi dans une autre langue"
