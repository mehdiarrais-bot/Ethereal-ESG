"""Suivi annuel : 4ᵉ type de rapport (depuis le 2026-09-28).

Il remplace « Synthèse PDF », qui produisait le rapport complet sous un
autre titre. Document court : ce qui a changé depuis l'exercice précédent,
le plan d'action précédent, les cibles, les priorités à venir.
"""
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "scripts"))

from models import ReportType, ESGRequest                      # noqa: E402
from esg_calculator import calculate_esg_scores                # noqa: E402
from content_generator import generate_esg_content             # noqa: E402
from report_generator import compose_report                    # noqa: E402
from i18n import L                                             # noqa: E402


def _suivi(lang="fr", **modif):
    import fitz
    from make_examples import DEMO
    r = DEMO.model_copy(update={"report_type": ReportType.ANNUAL_FOLLOWUP, "language": lang, **modif})
    s = calculate_esg_scores(r)
    pdf, layout = compose_report(r, s, generate_esg_content(r, s), {})
    doc = fitz.open(stream=pdf, filetype="pdf")
    return doc, layout, " ".join(str(p.get_text()) for p in doc).replace("\n", " ")


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_le_suivi_est_court_et_porte_chaque_section(lang):
    doc, _, texte = _suivi(lang)
    assert 6 <= doc.page_count <= 10, doc.page_count
    TR = L(lang)
    for cle in ("rep_annual_followup", "fu_s1", "fu_s2", "fu_s3", "fu_s4", "fu_s5", "done_head"):
        attendu = TR[cle]
        assert attendu in texte or attendu.upper() in texte, (lang, cle)
    assert ("Évolution depuis l'exercice 2024" if lang == "fr" else "Change since fiscal year 2024") in texte
    assert ("déclare un objectif de réduction" if lang == "fr" else "reports a target to reduce") in texte


def test_chaque_page_courante_porte_du_texte():
    import fitz  # noqa: F401
    doc, layout, _ = _suivi()
    for page in layout["content_pages"]:
        mots = len(re.findall(r"\w+", str(doc[page - 1].get_text())))
        assert mots >= 120, f"page {page} : {mots} mots"


def test_sans_exercice_precedent_ni_action_le_suivi_le_dit():
    _, _, texte = _suivi(previous_data=None, completed_actions=None)
    assert L("fr")["fu_no_prev"][:60] in texte
    assert L("fr")["fu_no_done"] in texte


def test_l_ancienne_synthese_pdf_est_relue_en_rapport_complet():
    from make_examples import DEMO
    d = DEMO.model_dump(mode="json")
    d["report_type"] = "executive_summary_pdf"
    assert ESGRequest.model_validate(d).report_type == ReportType.FULL_REPORT


def test_le_word_d_un_suivi_reste_un_rapport_complet():
    from test_typo import _docx_text
    from docx_generator import generate_word_report
    from make_examples import DEMO
    r = DEMO.model_copy(update={"report_type": ReportType.ANNUAL_FOLLOWUP})
    s = calculate_esg_scores(r)
    texte = _docx_text(generate_word_report(r, s, generate_esg_content(r, s)))
    assert L("fr")["rep_full_report"] in texte and L("fr")["rep_annual_followup"] not in texte
