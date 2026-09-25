"""
Synthèse ESG « une page » (PDF A4 dessiné au canvas).

Le document que le dirigeant transfère à son board : score hero + évolution,
barres par pilier vs secteur, forces/axes/risques/opportunités, top-3 actions.
Toutes les données proviennent des mêmes fonctions que les rapports complets.
"""
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib.utils import simpleSplit

from esg_calculator import NON_NOTE, score_label
from models import ESGRequest, ESGScores
from i18n import L
from pdf_kit import Kit, clean as pdf_txt


def generate_onepager_pdf(request: ESGRequest, scores: ESGScores) -> bytes:
    import typo
    with typo.language(request.language):  # nombres à la française via pdf_txt
        return _onepager(request, scores)


def _onepager(request: ESGRequest, scores: ESGScores) -> bytes:
    from content_generator import risks_opportunities, enriched_recommendations
    from esg_advanced import esg_maturity

    en = request.language == "en"
    # Couleurs et polices du gabarit (couleurs de marque du client incluses)
    kit = Kit(request)
    pal = dict(kit.c, secondary=kit.c["muted"], text=kit.c["ink"])
    f, fb, fi, fd = kit.f["body"], kit.f["body_b"], kit.f["body_i"], kit.f["display"]
    on_primary, soft = kit.c["on_primary"], kit.c["accent_on_primary"]
    TR = L(request.language)
    W, H = A4
    M = 1.4 * cm

    mat = esg_maturity(request, scores)
    ro = risks_opportunities(request, scores)
    recs = enriched_recommendations(request, scores)[:3]
    red = colors.HexColor("#E74C3C")

    buf = io.BytesIO()
    c = pdfcanvas.Canvas(buf, pagesize=A4)
    c.setTitle(pdf_txt(f"Synthèse ESG — {request.company.name}"))
    c.setFillColor(pal["paper"]); c.rect(0, 0, W, H, fill=1, stroke=0)

    def txt(x, y, s, font, size, color, max_w=None):
        c.setFont(font, size)
        c.setFillColor(color)
        s = pdf_txt(s)
        if max_w:
            lines = simpleSplit(s, font, size, max_w)
            for i, ln in enumerate(lines):
                c.drawString(x, y - i * size * 1.25, ln)
            return len(lines)
        c.drawString(x, y, s)
        return 1

    # ── Bandeau supérieur ──────────────────────────────────────────────────
    c.setFillColor(pal["primary"]); c.rect(0, H - 4.4 * cm, W, 4.4 * cm, fill=1, stroke=0)
    c.setFillColor(pal["accent"]); c.rect(0, H - 4.4 * cm, W, 0.09 * cm, fill=1, stroke=0)
    txt(M, H - 1.25 * cm, ("ESG ONE-PAGER" if en else "SYNTHÈSE ESG — UNE PAGE"),
        fb, 9, soft)
    txt(M, H - 2.15 * cm, request.company.name, fd, 24, on_primary)
    txt(M, H - 2.8 * cm, f"{request.company.sector}  |  "
        + (f"FY {request.company.reporting_year}" if en else f"Exercice {request.company.reporting_year}")
        + "  |  " + (TR["cover_refs_vsme"] if getattr(request, "reporting_framework", "csrd") == "vsme" else TR["cover_refs"]),
        f, 9, soft)
    # Maturité
    from content_generator import maturite_libelle
    txt(M, H - 3.75 * cm, (("ESG maturity: " if en else "Maturité ESG : ") + maturite_libelle(mat, TR)),
        fb, 10, on_primary)

    # Score hero (droite du bandeau)
    sc = score_label(scores.total_esg_score)
    c.setFont(fd, 54); c.setFillColor(on_primary)
    c.drawRightString(W - M - 2.5 * cm, H - 3.1 * cm, sc)
    if scores.total_esg_score is not None:
        txt(W - M - 2.3 * cm, H - 3.1 * cm, "/100", f, 12, soft)
    # Note
    c.setFillColor(soft)
    c.roundRect(W - M - 1.85 * cm, H - 2.0 * cm, 1.85 * cm, 0.85 * cm, 5, fill=1, stroke=0)
    c.setFont(fb, 20); c.setFillColor(pal["primary"])
    c.drawCentredString(W - M - 0.925 * cm, H - 1.78 * cm, pdf_txt(scores.rating or NON_NOTE))
    # Évolution N-1
    prev = getattr(request, "previous_scores", None)
    from content_generator import _ecart
    d = _ecart(scores.total_esg_score, prev.get("total")) if prev else None
    if prev and d is not None:
        col = soft
        lbl = (f"+{d:.0f}" if d >= 0.5 else f"{d:.0f}" if d <= -0.5 else "=")
        c.setFont(fb, 12); c.setFillColor(col)
        c.drawRightString(W - M, H - 3.9 * cm, pdf_txt(f"{lbl} pts vs {prev['year']}"))

    # ── Barres par pilier vs secteur ───────────────────────────────────────
    y0 = H - 5.4 * cm
    # Repère sectoriel retiré : il pointait une moyenne inventée (cf. note
    # dans esg_advanced.py). Restent les scores absolus, qui sont vrais.
    txt(M, y0, ("PILLAR SCORES" if en else "SCORES PAR PILIER"), fb, 9, pal["secondary"])
    bars = [(TR["chart_env"], scores.environmental_score, pal["env"]),
            (TR["chart_soc"], scores.social_score, pal["social"]),
            (TR["chart_gov"], scores.governance_score, pal["gov"])]
    bw = W - 2 * M - 4.2 * cm
    for i, (lab, v, col) in enumerate(bars):
        by = y0 - 0.75 * cm - i * 0.85 * cm
        txt(M, by + 0.06 * cm, lab, fb, 9, pal["text"])
        bx = M + 3.2 * cm
        c.setFillColor(pal["rule"]); c.roundRect(bx, by, bw, 0.32 * cm, 3, fill=1, stroke=0)
        if v is not None:  # pilier non noté : piste vide et « — »
            c.setFillColor(col); c.roundRect(bx, by, bw * min(100, v) / 100, 0.32 * cm, 3, fill=1, stroke=0)
        c.setFont(fb, 9); c.setFillColor(col)
        c.drawString(bx + bw + 0.15 * cm, by + 0.04 * cm, score_label(v))

    # ── Digest 2×2 ────────────────────────────────────────────────────────
    gy = y0 - 4.35 * cm
    box_w = (W - 2 * M - 0.5 * cm) / 2
    box_h = 3.35 * cm

    def digest_box(x, y, head, items, col, tags=False):
        c.setFillColor(pal["panel"]); c.rect(x, y - box_h, box_w, box_h, fill=1, stroke=0)
        c.setFillColor(col); c.rect(x, y - box_h, 0.09 * cm, box_h, fill=1, stroke=0)
        txt(x + 0.35 * cm, y - 0.55 * cm, head.upper(), fb, 9, col)
        yy = y - 1.1 * cm
        for it in items[:3]:
            s = it if isinstance(it, str) else f'{it["tag"]} — {it["text"]}'
            n = txt(x + 0.35 * cm, yy, "• " + s, f, 8, pal["text"], max_w=box_w - 0.7 * cm)
            yy -= n * 8 * 1.25 + 4
            if yy < y - box_h + 0.3 * cm:
                break

    digest_box(M, gy, TR["digest_strengths"], scores.strengths, pal["env"])
    digest_box(M + box_w + 0.5 * cm, gy, TR["digest_weak"], scores.weaknesses, red)
    digest_box(M, gy - box_h - 0.4 * cm, TR["digest_risks"], ro["risks"], red)
    digest_box(M + box_w + 0.5 * cm, gy - box_h - 0.4 * cm, TR["digest_opps"], ro["opportunities"], pal["env"])

    # ── Top-3 actions ─────────────────────────────────────────────────────
    ay = gy - 2 * box_h - 1.15 * cm
    txt(M, ay, TR["digest_actions"].upper(), fb, 9, pal["secondary"])
    for i, r in enumerate(recs):
        ry = ay - 0.55 * cm - i * 1.0 * cm
        c.setFillColor(pal["accent"]); c.circle(M + 0.25 * cm, ry - 0.1 * cm, 0.27 * cm, fill=1, stroke=0)
        c.setFont(fb, 10); c.setFillColor(pal["paper"])
        c.drawCentredString(M + 0.25 * cm, ry - 0.22 * cm, str(i + 1))
        txt(M + 0.75 * cm, ry, r["title"], fb, 9.5, pal["primary"])
        txt(M + 0.75 * cm, ry - 0.42 * cm,
            f'{r["objective"]}  ·  {r["owner"]}  ·  {r["horizon"]}', f, 8, pal["muted"])

    # ── Pied de page ──────────────────────────────────────────────────────
    c.setStrokeColor(pal["accent"]); c.setLineWidth(1)
    c.line(M, 1.35 * cm, W - M, 1.35 * cm)
    txt(M, 0.9 * cm, TR["gen_auto"], fi, 7, pal["muted"])
    c.setFont(fi, 7); c.setFillColor(pal["muted"])
    c.drawRightString(W - M, 0.9 * cm, pdf_txt(f"© {request.company.reporting_year} {request.company.name}"))

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()
