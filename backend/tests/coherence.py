"""Banc de cohérence du texte généré.

Génère des entreprises fictives aux profils variés (données complètes,
lacunaires, extrêmes, booléens inconnus) et vérifie des invariants ENTRE
phrases : ce qu'un lecteur attentif relèverait comme contradiction. Chaque
invariant rend la liste de ses violations, lisible telle quelle.

Utilisé par tests/test_coherence.py ; exécutable seul pour un rapport :

    python tests/coherence.py 300
"""
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (ESGRequest, CompanyInfo, EnvironmentalData, SocialData,  # noqa: E402
                    GovernanceData, TaxonomyData, TargetsData)
from esg_calculator import calculate_esg_scores                              # noqa: E402
from content_generator import (generate_esg_content, risks_opportunities,    # noqa: E402
                               compliance_assessment, pillar_headline)
import synthesis as SY                                                       # noqa: E402

SECTEURS = ["Industrie manufacturière", "Transport & logistique", "Construction & BTP",
            "Agroalimentaire", "Énergie", "Commerce & distribution", "Services",
            "Numérique & télécoms", "Tourisme & hôtellerie", "Autre"]

# Enjeu (synthesis.issues) et point d'appui (synthesis.strengths) qui portent
# sur le même indicateur : ils ne peuvent pas coexister dans un dossier.
PAIRES_ENJEU_APPUI = {
    "carbon_intensity": "intensity_good", "independence": "independence_good",
    "integrity": "integrity_clean", "mix": "mix_good", "renewable": "renewable_good",
    "retention": "retention_good", "safety": "safety_good", "skills": "training_good",
    "steering": "steering_good",
}

PILIERS = {"env": "environmental_score", "social": "social_score", "gov": "governance_score"}

# Artefacts de publipostage : un gabarit mal rempli, une valeur Python brute.
ARTEFACTS = re.compile(r"\bNone\b|\bnan\b|\{[a-z_]*\}|\binf\b")


# ── Profils ───────────────────────────────────────────────────────────────

def _maybe(rng, densite, tirage):
    return tirage() if rng.random() < densite else None


def profil(seed: int, lang: str = "fr") -> ESGRequest:
    """Entreprise fictive reproductible. La densité (part des champs
    renseignés) varie d'un profil à l'autre : de lacunaire à complet."""
    rng = random.Random(seed)
    d = rng.choice([0.15, 0.35, 0.6, 0.85, 1.0])
    u = rng.uniform
    m = lambda f: _maybe(rng, d, f)  # noqa: E731
    s1, s2, s3 = m(lambda: u(0, 20000)), m(lambda: u(0, 20000)), m(lambda: u(0, 80000))
    co2 = sum(v for v in (s1, s2, s3) if v is not None) or m(lambda: u(0, 100000))
    return ESGRequest(
        company=CompanyInfo(name=f"Témoin {seed}", sector=rng.choice(SECTEURS), country="France",
                            revenue_eur=rng.choice([None, 2e6, 12e6, 48e6, 300e6]),
                            reporting_year=2025, target_year=2030),
        environmental=EnvironmentalData(
            co2_emissions_tonnes=co2, scope1_emissions=s1, scope2_emissions=s2, scope3_emissions=s3,
            energy_consumption_mwh=m(lambda: u(10, 100000)),
            renewable_energy_percent=m(lambda: rng.choice([0, 100, u(0, 100)])),
            waste_recycled_percent=m(lambda: u(0, 100)),
            water_consumption_m3=m(lambda: u(0, 1e6)),
            biodiversity_initiatives=m(lambda: rng.randint(0, 8))),
        social=SocialData(
            total_employees=m(lambda: rng.randint(5, 5000)),
            female_employees_percent=m(lambda: u(0, 100)),
            employee_turnover_percent=m(lambda: u(0, 45)),
            training_hours_per_employee=m(lambda: u(0, 80)),
            accident_frequency_rate=m(lambda: rng.choice([0, u(0, 60)])),
            customer_satisfaction_score=m(lambda: u(3, 10)),
            community_investment_eur=m(lambda: u(0, 500000))),
        governance=GovernanceData(
            board_members=m(lambda: rng.randint(3, 15)),
            female_board_percent=m(lambda: u(0, 60)),
            independent_board_percent=m(lambda: u(0, 90)),
            ethics_violations=m(lambda: rng.choice([0, 0, 1, 4])),
            corruption_cases=m(lambda: rng.choice([0, 0, 0, 2])),
            data_breaches=m(lambda: rng.choice([0, 0, 1, 3])),
            csr_budget_eur=m(lambda: u(0, 800000)),
            esg_audit_conducted=m(lambda: rng.random() < 0.5),
            sustainability_committee=m(lambda: rng.random() < 0.5)),
        taxonomy=TaxonomyData(turnover_aligned_percent=m(lambda: u(0, 60))),
        targets=_cible(rng),
        language=lang, include_recommendations=True)


def _cible(rng) -> TargetsData:
    """Un profil sur trois déclare une cible climat, parfois incomplète."""
    if rng.random() > 1 / 3:
        return TargetsData()
    base = rng.choice([2019, 2022, 2025])
    return TargetsData(climate_reduction_percent=rng.choice([None, 25, 42, 55.5]),
                       climate_base_year=base, climate_target_year=rng.choice([2030, 2035, 2050]),
                       climate_scopes=rng.choice([None, "1-2", "1-2-3"]),
                       renewable_target_percent=rng.choice([None, 30, 60, 100]),
                       female_employees_target_percent=rng.choice([None, 40, 50]),
                       training_hours_target=rng.choice([None, 20, 35.5]),
                       accident_rate_target=rng.choice([None, 0, 5]))


class Dossier:
    """Tout ce que le texte d'un dossier affirme, calculé une fois."""

    def __init__(self, request: ESGRequest):
        self.r = request
        self.s = calculate_esg_scores(request)
        self.content = generate_esg_content(request, self.s)
        self.overview = SY.overview(request, self.s)
        self.closing = SY.closing(request, self.s)
        self.issues = SY.issues(request, self.s)
        self.strengths = SY.strengths(request, self.s)
        self.risks = risks_opportunities(request, self.s)
        self.compliance = compliance_assessment(request, self.s)
        self.headlines = pillar_headline(request, self.s)

    def notes(self) -> dict[str, float]:
        return {p: getattr(self.s, a) for p, a in PILIERS.items() if getattr(self.s, a) is not None}

    def textes(self) -> list[str]:
        """Toutes les chaînes produites, à plat."""
        out: list[str] = []

        def walk(o):
            if isinstance(o, str):
                out.append(o)
            elif isinstance(o, dict):
                for v in o.values():
                    walk(v)
            elif isinstance(o, (list, tuple)):
                for v in o:
                    walk(v)
            elif hasattr(o, "__dict__"):
                walk(vars(o))
        walk([self.content, self.overview, self.closing, self.risks, self.compliance,
              self.headlines, self.s.strengths, self.s.weaknesses, self.s.recommendations])
        return out


# ── Invariants ────────────────────────────────────────────────────────────

_FRAGILE = re.compile(r"(?:[Ff]ragilités se concentrent sur le pilier|[Ww]eaknesses are "
                      r"concentrated in the) (environnemental|social|de gouvernance|environmental|"
                      r"governance)")
_PILIER_TEXTE = {"environnemental": "env", "environmental": "env", "social": "social",
                 "de gouvernance": "gov", "governance": "gov"}


def fragilites_pas_sur_le_meilleur_pilier(d: Dossier) -> list[str]:
    """Aucune phrase ne dit les fragilités concentrées sur le pilier
    strictement le mieux noté (DETTE § 23)."""
    notes, out = d.notes(), []
    if len(notes) < 2:
        return []
    meilleur = max(notes, key=lambda p: notes[p])
    if sum(1 for v in notes.values() if v == notes[meilleur]) > 1:
        return []
    for texte in d.textes():
        for m in _FRAGILE.finditer(texte):
            if _PILIER_TEXTE[m.group(1)] == meilleur:
                out.append(f"fragilités « concentrées » sur {meilleur}, le mieux noté {notes}")
    return out


def enjeu_et_appui_exclusifs(d: Dossier) -> list[str]:
    """Un même indicateur n'est pas à la fois enjeu et point d'appui."""
    enjeux = {i.key for i in d.issues}
    appuis = {s.key for s in d.strengths}
    return [f"{e} est un enjeu ET {a} un point d'appui"
            for e, a in PAIRES_ENJEU_APPUI.items() if e in enjeux and a in appuis]


def point_fort_pas_point_faible(d: Dossier) -> list[str]:
    """Aucune phrase n'est à la fois point fort et point faible."""
    return [f"« {x} » en point fort et en point faible"
            for x in set(d.s.strengths) & set(d.s.weaknesses)]


_SCORE_CITE = re.compile(r"(Environnement|Social|Gouvernance|Environmental|Governance)"
                         r"[^()]{0,40}\((\d+)/100\)")
_NOM = {"Environnement": "env", "Environmental": "env", "Social": "social",
        "Gouvernance": "gov", "Governance": "gov"}


def scores_cites_exacts(d: Dossier) -> list[str]:
    """Un score de pilier cité « (75/100) » est le score calculé, arrondi."""
    notes, out = d.notes(), []
    for texte in d.textes():
        for nom, val in _SCORE_CITE.findall(texte):
            p = _NOM[nom]
            if p not in notes:
                out.append(f"{nom} cité à {val}/100 alors qu'il n'est pas noté")
            elif abs(round(notes[p]) - int(val)) > 0:
                out.append(f"{nom} cité à {val}/100, calculé {notes[p]}")
    return out


def pilier_dominant_est_le_meilleur(d: Dossier) -> list[str]:
    """« P domine le profil ESG » : P a la meilleure note."""
    notes, out = d.notes(), []
    for texte in d.textes():
        for m in re.finditer(r"(\w+) (?:domine le profil|dominates the)", texte):
            p = _NOM.get(m.group(1))
            if p and notes and notes[p] < max(notes.values()):
                out.append(f"{m.group(1)} « domine » avec {notes[p]} ; notes {notes}")
    return out


def aucun_artefact(d: Dossier) -> list[str]:
    """Ni « None », ni « nan », ni gabarit « {champ} » non rempli."""
    return [f"artefact « {m.group(0)} » dans : {t[:90]}…"
            for t in d.textes() for m in [ARTEFACTS.search(t)] if m]


# Deux générations de texte coexistent dans un même rapport : les points
# forts / faibles de esg_calculator et les enjeux / points d'appui de
# synthesis. Elles ne doivent pas se contredire sur un même indicateur.
# (motif du point faible ou fort, clé synthesis opposée)
FAIBLE_CONTRE_APPUI = [
    (r"[Éé]nergie renouvelable|renewable energy", "renewable_good"),
    (r"[Dd]éséquilibre de genre|[Gg]ender imbalance", "mix_good"),
    (r"heures de formation|[Ff]ormation insuffisante|training", "training_good"),
    (r"accidents?|sécurité au travail|safety", "safety_good"),
    (r"[Aa]bsence d'audit|No independent ESG audit", "steering_good"),
]
FORT_CONTRE_ENJEU = [
    (r"[Tt]aux de recyclage|recycling", "waste"),
    (r"[Ii]nvestissement significatif dans la formation|training", "skills"),
    (r"sécurité au travail|safety", "safety"),
    (r"[Éé]nergie renouvelable|renewable", "renewable"),
]
# Pas de paire « audit conduit » / enjeu « steering » : avec un audit
# déclaré, l'enjeu « steering » ne porte que sur l'absence de comité.


def faible_contre_appui(d: Dossier) -> list[str]:
    """Un point faible (esg_calculator) ne contredit pas un point d'appui (synthesis)."""
    appuis = {s.key for s in d.strengths}
    return [f"point faible « {w} » ET point d'appui {cle}"
            for w in d.s.weaknesses for motif, cle in FAIBLE_CONTRE_APPUI
            if cle in appuis and re.search(motif, w)]


def fort_contre_enjeu(d: Dossier) -> list[str]:
    """Un point fort (esg_calculator) ne contredit pas un enjeu (synthesis)."""
    enjeux = {i.key for i in d.issues}
    return [f"point fort « {f} » ET enjeu {cle}"
            for f in d.s.strengths for motif, cle in FORT_CONTRE_ENJEU
            if cle in enjeux and re.search(motif, f)]


def risque_carbone_contre_appui(d: Dossier) -> list[str]:
    """Le risque « intensité carbone élevée » et le point d'appui « intensité
    maîtrisée » ne coexistent pas."""
    risque = any(re.search(r"[Ii]ntensité carbone élevée|[Hh]igh carbon intensity", t)
                 for t in d.textes())
    appui = any(s.key == "intensity_good" for s in d.strengths)
    return ["risque « intensité carbone élevée » ET point d'appui intensité"] if risque and appui else []


# Formulations qui affirment un fait que le client n'a pas déclaré (DETTE
# § 22). Des formulations ENTIÈRES, jamais un mot nu (DETTE § 0quater) : une
# phrase qui nie ou recommande doit rester possible.
NON_DECLARE = [
    "est planifiée", "is planned",
    "garantit l'intégrité des données publiées dans ce rapport",
    "guarantees the integrity of the data published in this report",
    "Un tiers indépendant a vérifié", "An independent third party has verified",
    "engagement inscrit dans la feuille de route", "commitment set out in the roadmap",
    "documenté dans la feuille de route", "documented area for progress in the governance roadmap",
    "identifié comme tel dans la feuille de route", "inscrite dans la stratégie pluriannuelle",
    "embedded in the multi-year strategy", "objectifs à horizon 3 ans", "3-year objectives",
    "conformément aux engagements de durabilité", "in line with sustainability commitments",
    "couvrant l'intégralité de la chaîne de valeur", "reporting carbone complet",
    "La politique RH cible", "HR policy targets", "L'audit ESG positionne",
    "rend compte directement au Conseil", "reporting directly to the Board",
    "comité de durabilité permanent", "permanent sustainability committee",
    "en cours de structuration", "en déploiement progressif", "en cours de formalisation",
    "en cours de documentation", "is being structured", "are being formalised",
    "is being documented", "opérationnel au niveau du CA",
]


def aucune_affirmation_non_declaree(d: Dossier) -> list[str]:
    """Aucune phrase n'affirme un plan, un engagement ou une vérification
    que le client n'a pas déclarés."""
    return [f"« {f} » dans : {t[:90]}…" for t in d.textes() for f in NON_DECLARE if f in t]


def cible_citee_est_la_cible_saisie(d: Dossier) -> list[str]:
    """Une cible climat n'est citée que si elle est complète, et avec ses
    valeurs saisies ; aucune cible sans saisie."""
    import targets as TG
    from narrative import pct
    c = TG.climate_target(d.r)
    cite = [t for t in d.textes() if "déclare un objectif de réduction" in t
            or "reports a target to reduce" in t]
    if c is None:
        return [f"cible citée sans saisie complète : {t[:80]}…" for t in cite]
    if not cite:
        return ["cible saisie mais jamais citée"]
    attendu = pct(c.reduction, d.r.language).replace(chr(160), " ")
    return [f"cible citée sans « {attendu} » ni {c.target_year} : {t[:80]}…" for t in cite
            if attendu not in t.replace(chr(160), " ") or str(c.target_year) not in t]


def cibles_indicateurs_citees_telles_quelles(d: Dossier) -> list[str]:
    """Chaque cible par indicateur saisie est citée avec sa valeur ; aucune
    phrase de cibles sans saisie."""
    import targets as TG
    cibles = TG.indicator_targets(d.r)
    textes = [t.replace(chr(160), " ") for t in d.textes()]
    marque = ("Cibles déclarées par l'entreprise", "Targets reported by the company")
    cite = [t for t in textes if any(m in t for m in marque)]
    if not cibles:
        return [f"cibles citées sans saisie : {t[:80]}…" for t in cite]
    out = []
    for it in cibles:
        v = TG.fmt_value(it.key, it.target, d.r.language).replace(chr(160), " ")
        label = TG.LIBELLES[d.r.language][it.key]
        if not any(f"{label}: {v}" in t or f"{label} : {v}" in t for t in cite):
            out.append(f"cible « {label} » = {v} jamais citée")
    return out


INVARIANTS = [fragilites_pas_sur_le_meilleur_pilier, enjeu_et_appui_exclusifs,
              point_fort_pas_point_faible, scores_cites_exacts,
              pilier_dominant_est_le_meilleur, aucun_artefact, faible_contre_appui,
              fort_contre_enjeu, risque_carbone_contre_appui,
              aucune_affirmation_non_declaree, cible_citee_est_la_cible_saisie,
              cibles_indicateurs_citees_telles_quelles]


def violations(n: int, invariant, langs=("fr", "en")) -> list[str]:
    out = []
    for seed in range(n):
        for lang in langs:
            for v in invariant(Dossier(profil(seed, lang))):
                out.append(f"[profil {seed} {lang}] {v}")
    return out


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    for inv in INVARIANTS:
        vs = violations(n, inv)
        print(f"\n{inv.__name__} : {len(vs)} violation(s) sur {2 * n} dossiers")
        for v in vs[:6]:
            print("   ", v)
