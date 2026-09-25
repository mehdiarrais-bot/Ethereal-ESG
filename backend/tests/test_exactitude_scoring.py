"""Chantier « exactitude du scoring » (2026-09-24) : barème TF sourcé,
AFEP-MEDEF limité aux sociétés cotées, parité au conseil avec son champ
d'application légal, corruption dans le score, drapeaux morts retirés.

Sources vérifiées (cf. DETTE.md § 0octies, 1, 2, 3bis, 8) :
- Assurance Maladie – Risques professionnels, rapport annuel 2024, tableau 8 ;
- Code Afep-Medef des sociétés cotées, version de décembre 2022 ;
- art. L225-18-1 du Code de commerce (Légifrance, version en vigueur).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models import (ESGRequest, CompanyInfo, EnvironmentalData, SocialData,
                    GovernanceData, TaxonomyData)
from esg_calculator import calculate_esg_scores, TF_NATIONAL_2024, TF_SOURCE
from content_generator import generate_esg_content, compliance_assessment


def _req(lang="fr", revenue=48_000_000, staff=None, **gov):
    return ESGRequest(
        company=CompanyInfo(name="Témoin SA", sector="Industrie manufacturière",
                            country="France", revenue_eur=revenue, reporting_year=2025),
        environmental=EnvironmentalData(), social=SocialData(total_employees=staff),
        governance=GovernanceData(**gov), taxonomy=TaxonomyData(), language=lang)


def _gov_text(r):
    return generate_esg_content(r, calculate_esg_scores(r))["governance"]


def _afep_rows(r):
    return [g for g in compliance_assessment(r, calculate_esg_scores(r))
            if "AFEP" in str(g)]


# ── Taux de fréquence ──────────────────────────────────────────────────────

def test_tf_sous_la_moyenne_nationale_nest_pas_un_axe_de_progres():
    r = _req()
    r.social.accident_frequency_rate = 12
    s = calculate_esg_scores(r)
    assert not any("accident" in w.lower() for w in s.weaknesses)
    r.social.accident_frequency_rate = TF_NATIONAL_2024 + 2
    s = calculate_esg_scores(r)
    assert any("accident" in w.lower() for w in s.weaknesses)


def test_note_methodologique_cite_la_source_du_bareme_tf():
    for lang in ("fr", "en"):
        r = _req(lang)
        r.social.accident_frequency_rate = 10
        assert TF_SOURCE in generate_esg_content(r, calculate_esg_scores(r))["methodology"]


# ── AFEP-MEDEF ─────────────────────────────────────────────────────────────

def test_afep_absent_si_statut_non_declare_ou_non_cotee():
    for listed in (None, False):
        r = _req(independent_board_percent=30, listed_company=listed)
        assert "AFEP" not in _gov_text(r)
        assert _afep_rows(r) == []


def test_afep_seuil_moitie_si_cotee_capital_disperse():
    r = _req(independent_board_percent=45, listed_company=True, controlled_company=False)
    assert "recommandation AFEP-MEDEF de 50 %" in _gov_text(r)
    assert "appliquer ou expliquer" in _gov_text(r)
    rows = _afep_rows(r)
    assert len(rows) == 1 and "no" in str(rows[0])


def test_afep_seuil_tiers_si_cotee_controlee():
    r = _req(independent_board_percent=40, listed_company=True, controlled_company=True)
    text = _gov_text(r)
    assert "recommandation AFEP-MEDEF de 33 %" in text and "contrôlée" in text
    rows = _afep_rows(r)
    assert len(rows) == 1 and "ok" in str(rows[0])


def test_plus_de_conformite_afep_affirmee():
    r = _req(independent_board_percent=80)
    assert "conforme AFEP" not in _gov_text(r)


# ── Parité au conseil ──────────────────────────────────────────────────────

def test_parite_hors_champ_si_les_donnees_le_montrent():
    text = _gov_text(_req(revenue=12_000_000, staff=90, female_board_percent=20))
    assert "hors du champ" in text and "L225-18-1" in text
    assert "sous les 40 %" not in text     # pas d'écart mesuré à une norme qui ne vise pas


def test_parite_dans_le_champ_sans_affirmer_lobligation():
    text = _gov_text(_req(revenue=300_000_000, staff=1200, female_board_percent=30))
    assert "sous les 40 %" in text and "peut relever" in text
    en = _gov_text(_req("en", revenue=300_000_000, staff=1200, female_board_percent=30))
    assert "below 40%" in en and "may fall within" in en


# ── Corruption ─────────────────────────────────────────────────────────────

def test_corruption_penalise_le_score_et_se_lit_dans_le_texte():
    propre = calculate_esg_scores(_req(corruption_cases=0, sustainability_committee=True))
    un_cas = _req(corruption_cases=1, sustainability_committee=True)
    s = calculate_esg_scores(un_cas)
    assert s.governance_score < propre.governance_score
    assert "un cas de corruption enregistré" in _gov_text(un_cas)
    assert any("corruption" in w for w in s.weaknesses)
    deux = _req("en", corruption_cases=2)
    assert "two corruption cases recorded" in _gov_text(deux)


# ── Questionnaire et drapeaux ──────────────────────────────────────────────

def test_questionnaire_porte_les_conditions_dapplicabilite():
    from questionnaire_generator import generate_questionnaire_html
    for lang, attendus in (("fr", ("L225-18-1", "250 salariés permanents", "sociétés cotées",
                                   "Société cotée", "Société contrôlée")),
                           ("en", ("L225-18-1", "250 permanent employees", "listed companies",
                                   "Listed company", "Controlled company"))):
        html = generate_questionnaire_html("X", 2025, lang=lang)
        for a in attendus:
            assert a in html, (lang, a)
        assert "Référence AFEP-MEDEF : 50 %" not in html
        assert "AFEP-MEDEF reference: 50%" not in html


def test_drapeaux_morts_retires():
    assert "include_benchmarks" not in ESGRequest.model_fields
    from esg_calculator import calculate_environmental_score
    _, details = calculate_environmental_score(EnvironmentalData(co2_emissions_tonnes=5000),
                                               48_000_000, "Industrie manufacturière")
    assert "carbon_intensity" in details
    assert "carbon_grid_sector_specific" not in details
    root = Path(__file__).resolve().parents[2] / "frontend" / "src"
    for f in root.rglob("*.js*"):
        assert "include_benchmarks" not in f.read_text(encoding="utf-8"), f
