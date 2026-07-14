import os
import io
import re
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.datastructures import MutableHeaders

from models import ESGRequest, ESGScores, AestheticTheme, decode_logo
from esg_calculator import calculate_esg_scores
from image_bank import cover_art
from chart_generator import radar_chart, score_bars_chart, emissions_breakdown_chart, gauge_chart
from ppt_generator import generate_pptx
from report_generator import generate_pdf_report
from docx_generator import generate_word_report
from content_generator import generate_esg_content
import import_data

SAFE_NAME_RE = re.compile(r'[^\w\-]')

def safe_name(name: str) -> str:
    return SAFE_NAME_RE.sub('_', name)


SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "no-referrer",
}

MAX_BODY_BYTES = 2_500_000  # 2,5 Mo (logo base64 inclus)


class SecurityMiddleware:
    """Pure ASGI middleware: body size limit + security headers."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            request = Request(scope, receive)

            # Body size check for POST requests
            if request.method == "POST":
                cl = request.headers.get("content-length")
                if cl and int(cl) > MAX_BODY_BYTES:
                    resp = JSONResponse(status_code=413, content={"detail": "Request too large"})
                    await resp(scope, receive, send)
                    return
                body = await request.body()
                if len(body) > MAX_BODY_BYTES:
                    resp = JSONResponse(status_code=413, content={"detail": "Request too large"})
                    await resp(scope, receive, send)
                    return
                # Rebuild receive: yield the buffered body ONCE, then delegate
                # to the original receive (disconnect events). Returning the body
                # forever would spin StreamingResponse.listen_for_disconnect
                # into a busy-loop that freezes the whole event loop.
                original_receive = receive
                body_sent = False

                async def receive_with_body():
                    nonlocal body_sent
                    if not body_sent:
                        body_sent = True
                        return {"type": "http.request", "body": body, "more_body": False}
                    return await original_receive()

                receive = receive_with_body

            # Inject security headers into response
            async def send_with_headers(message):
                if message["type"] == "http.response.start":
                    headers = MutableHeaders(scope=message)
                    for k, v in SECURITY_HEADERS.items():
                        headers.append(k, v)
                await send(message)

            await self.app(scope, receive, send_with_headers)
        else:
            await self.app(scope, receive, send)


app = FastAPI(title="ESG Platform API", version="1.0.0")


@app.on_event("startup")
async def warmup():
    """Pre-warm matplotlib on startup so first download request is fast."""
    import asyncio, concurrent.futures

    def _warm():
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(1, 1, figsize=(2, 2))
            ax.plot([0, 1], [0, 1])
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            plt.close(fig)
        except Exception:
            pass

    loop = asyncio.get_event_loop()
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    loop.run_in_executor(executor, _warm)


app.add_middleware(SecurityMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
def health():
    return {"status": "ok", "service": "ESG Platform"}


@app.get("/api/warmup")
def warmup_endpoint():
    """Endpoint to explicitly trigger matplotlib pre-warming."""
    return {"status": "warming"}


@app.post("/api/calculate")
def calculate(request: ESGRequest):
    """Calculate ESG scores without generating documents."""
    scores = calculate_esg_scores(request)
    return scores


# ── Dossiers clients (stockage local, workflow multi-clients) ────────────
import client_store


@app.get("/api/clients")
def clients_list():
    return client_store.list_clients()


@app.get("/api/clients/{client_id}")
def clients_get(client_id: str):
    try:
        return client_store.get_client(client_id)
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="Dossier introuvable")


@app.post("/api/clients")
def clients_save(payload: dict):
    """Sauvegarde un dossier : {form: <ESGRequest-like>, id?: str}.
    Le formulaire est validé, les scores calculés et historisés par exercice."""
    form = payload.get("form")
    if not isinstance(form, dict):
        raise HTTPException(status_code=422, detail="Champ 'form' manquant")
    try:
        request = ESGRequest(**form)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Formulaire invalide : {e}")
    s = calculate_esg_scores(request)
    scores = {"env": s.environmental_score, "social": s.social_score,
              "gov": s.governance_score, "total": s.total_esg_score, "rating": s.rating}
    cid = payload.get("id")
    try:
        d = client_store.save_client(form, scores, client_id=cid)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dossier introuvable")
    except ValueError:
        raise HTTPException(status_code=422, detail="Identifiant invalide")
    return {"id": d["id"], "name": d["name"], "updated_at": d["updated_at"],
            "score_history": d["score_history"]}


@app.patch("/api/clients/{client_id}/status")
def clients_set_status(client_id: str, payload: dict):
    """Statut CRM du dossier : prospect / signed / delivered / archived."""
    try:
        d = client_store.set_status(client_id, str(payload.get("status", "")))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dossier introuvable")
    except ValueError:
        raise HTTPException(status_code=422, detail="Statut ou identifiant invalide")
    return {"id": d["id"], "status": d["status"], "updated_at": d["updated_at"]}


@app.get("/api/clients-export")
def clients_export():
    """Sauvegarde portable : zip de tous les dossiers clients."""
    data = client_store.export_all()
    return StreamingResponse(
        io.BytesIO(data), media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="dossiers_esg_backup.zip"'})


@app.post("/api/clients-import")
async def clients_import(file: UploadFile = File(...)):
    """Restaure une sauvegarde zip de dossiers (fusion par identifiant)."""
    data = await file.read()
    if len(data) > MAX_BODY_BYTES:
        raise HTTPException(status_code=413, detail="Archive trop volumineuse")
    try:
        return client_store.import_archive(data)
    except Exception:
        raise HTTPException(status_code=422, detail="Archive invalide")


@app.delete("/api/clients/{client_id}")
def clients_delete(client_id: str):
    try:
        if not client_store.delete_client(client_id):
            raise HTTPException(status_code=404, detail="Dossier introuvable")
    except ValueError:
        raise HTTPException(status_code=422, detail="Identifiant invalide")
    return {"ok": True}


MAX_IMPORT_BYTES = 2_000_000  # 2 Mo


@app.get("/api/import/template")
def import_template():
    """Renvoie un modèle CSV clé/valeur à remplir."""
    return PlainTextResponse(
        "﻿" + import_data.template_csv(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="modele_esg.csv"'},
    )


@app.post("/api/import")
async def import_file(file: UploadFile = File(...)):
    """Parse un CSV/Excel et renvoie les sections de formulaire pré-remplies."""
    data = await file.read()
    if len(data) > MAX_IMPORT_BYTES:
        raise HTTPException(status_code=413, detail="Fichier trop volumineux (max 2 Mo)")
    try:
        pairs = import_data.parse_upload(file.filename, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=400, detail="Fichier illisible : vérifiez le format (CSV ou XLSX)")
    result = import_data.build_form(pairs)
    if not result["matched"]:
        raise HTTPException(status_code=422,
                            detail="Aucun champ reconnu. Utilisez le modèle CSV téléchargeable.")
    return result


def build_extras(request: ESGRequest) -> tuple:
    """Logo décodé + illustration de couverture générée localement."""
    logo_bytes = decode_logo(request.company.logo_base64)
    art = None
    if request.include_cover_image:
        try:
            art = cover_art(request.aesthetic_theme, request.company.name)
        except Exception as e:
            print(f"Cover art error: {e}")
    return logo_bytes, art


def build_advanced_charts(request: ESGRequest, scores, light_bg: bool) -> dict:
    """Graphiques ESG avancés : matérialité, objectifs, trajectoire carbone, taxonomie."""
    from esg_advanced import materiality_topics, esg_targets, taxonomy_summary, sector_benchmark
    from chart_generator import (materiality_matrix, targets_chart,
                                 carbon_trajectory_chart, taxonomy_chart, benchmark_chart)
    theme = request.aesthetic_theme
    lang = request.language
    brand = getattr(request, 'custom_colors', None)
    out = {}
    try:
        out["materiality"] = materiality_matrix(
            materiality_topics(request, scores, lang), theme, light_bg=light_bg, lang=lang, brand=brand)
    except Exception as e:
        print(f"Materiality chart error: {e}")
    try:
        tg = esg_targets(request, scores, lang)
        out["targets"] = targets_chart(tg["pillars"], theme, light_bg=light_bg, lang=lang, brand=brand)
        if tg["carbon"]:
            out["carbon_trajectory"] = carbon_trajectory_chart(tg["carbon"], theme, light_bg=light_bg, lang=lang, brand=brand)
    except Exception as e:
        print(f"Targets chart error: {e}")
    try:
        tx = taxonomy_summary(request)
        if tx:
            out["taxonomy"] = taxonomy_chart(tx, theme, light_bg=light_bg, lang=lang, brand=brand)
    except Exception as e:
        print(f"Taxonomy chart error: {e}")
    try:
        bm = sector_benchmark(request, scores)
        comp = {"env": scores.environmental_score, "social": scores.social_score,
                "gov": scores.governance_score, "global": scores.total_esg_score}
        out["benchmark"] = benchmark_chart(comp, bm["avg"], theme, light_bg=light_bg, lang=lang, brand=brand)
    except Exception as e:
        print(f"Benchmark chart error: {e}")
    try:
        from content_generator import enriched_recommendations
        from chart_generator import priority_matrix_chart
        recs = enriched_recommendations(request, scores)
        if recs:
            out["priority"] = priority_matrix_chart(recs, theme, light_bg=light_bg, lang=lang, brand=brand)
    except Exception as e:
        print(f"Priority chart error: {e}")
    try:
        # Trajectoire pluriannuelle : exercices passés + exercice courant recalculé
        hist = getattr(request, "score_history", None) or []
        year = request.company.reporting_year
        pts = [h for h in hist if h["year"] < year]
        pts.append({"year": year, "env": scores.environmental_score,
                    "social": scores.social_score, "gov": scores.governance_score,
                    "total": scores.total_esg_score})
        if len(pts) >= 2:
            from chart_generator import score_trend_chart
            out["trend"] = score_trend_chart(pts, theme, light_bg=light_bg, lang=lang, brand=brand)
    except Exception as e:
        print(f"Trend chart error: {e}")
    return out


@app.post("/api/generate/pptx")
def generate_presentation(request: ESGRequest):
    """Generate PowerPoint presentation."""
    scores = calculate_esg_scores(request)
    content = generate_esg_content(request, scores)
    logo_bytes, art = build_extras(request)

    chart_images = {}
    if art:
        chart_images["cover_art"] = art
    try:
        chart_images["radar"] = radar_chart(scores, request.aesthetic_theme, lang=request.language, brand=getattr(request, "custom_colors", None))
    except Exception as e:
        print(f"Radar chart error: {e}")
    try:
        chart_images["bars"] = score_bars_chart(scores, request.aesthetic_theme, lang=request.language, brand=getattr(request, "custom_colors", None))
    except Exception as e:
        print(f"Bars chart error: {e}")

    env = request.environmental
    if any(v is not None for v in (env.scope1_emissions, env.scope2_emissions, env.scope3_emissions)):
        try:
            chart_images["emissions_pie"] = emissions_breakdown_chart(
                env.scope1_emissions, env.scope2_emissions, env.scope3_emissions,
                request.aesthetic_theme, lang=request.language,
                brand=getattr(request, "custom_colors", None)
            )
        except Exception as e:
            print(f"Pie chart error: {e}")

    chart_images.update(build_advanced_charts(request, scores, light_bg=False))

    pptx_bytes = generate_pptx(request, scores, content, chart_images, logo_bytes=logo_bytes)

    filename = f"ESG_{safe_name(request.company.name)}_{request.company.reporting_year}.pptx"
    return StreamingResponse(
        io.BytesIO(pptx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.post("/api/generate/pdf")
def generate_report(request: ESGRequest):
    """Generate PDF report or white paper."""
    scores = calculate_esg_scores(request)
    content = generate_esg_content(request, scores)
    logo_bytes, art = build_extras(request)

    chart_images = {}
    if art:
        chart_images["cover_art"] = art
    try:
        chart_images["radar"] = radar_chart(scores, request.aesthetic_theme, light_bg=True, lang=request.language,
                                            brand=getattr(request, "custom_colors", None))
    except Exception as e:
        print(f"Radar chart error: {e}")

    env = request.environmental
    if any(v is not None for v in (env.scope1_emissions, env.scope2_emissions, env.scope3_emissions)):
        try:
            chart_images["emissions_pie"] = emissions_breakdown_chart(
                env.scope1_emissions, env.scope2_emissions, env.scope3_emissions,
                request.aesthetic_theme, light_bg=True, lang=request.language,
                brand=getattr(request, "custom_colors", None)
            )
        except Exception as e:
            print(f"Pie chart error: {e}")

    chart_images.update(build_advanced_charts(request, scores, light_bg=True))

    pdf_bytes = generate_pdf_report(request, scores, content, chart_images, logo_bytes=logo_bytes)

    type_suffix = {
        "white_paper": "Livre_Blanc",
        "full_report": "Rapport_ESG",
        "executive_summary_pdf": "Synthèse_Exécutive",
    }.get(request.report_type.value, "Rapport")

    filename = f"{type_suffix}_{safe_name(request.company.name)}_{request.company.reporting_year}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.post("/api/generate/all")
def generate_all(request: ESGRequest):
    """Calculate scores and return metadata + trigger downloads."""
    scores = calculate_esg_scores(request)
    content = generate_esg_content(request, scores)
    return {
        "scores": scores.model_dump(),
        "content_preview": {k: v[:150] + "..." if len(v) > 150 else v
                            for k, v in content.items()},
        "company": request.company.name,
        "reporting_year": request.company.reporting_year,
    }


@app.post("/api/generate/docx")
def generate_word(request: ESGRequest):
    """Generate Word document report."""
    scores = calculate_esg_scores(request)
    content = generate_esg_content(request, scores)
    logo_bytes, art = build_extras(request)
    adv_charts = build_advanced_charts(request, scores, light_bg=True)
    docx_bytes = generate_word_report(request, scores, content,
                                      logo_bytes=logo_bytes, cover_art=art,
                                      charts=adv_charts)
    type_suffix = {
        "white_paper": "Livre_Blanc",
        "full_report": "Rapport_ESG",
        "executive_summary_pdf": "Synthèse_Exécutive",
    }.get(request.report_type.value, "Rapport")
    filename = f"{type_suffix}_{safe_name(request.company.name)}_{request.company.reporting_year}.docx"
    return StreamingResponse(
        io.BytesIO(docx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.post("/api/generate/pack")
def generate_pack(request: ESGRequest):
    """Pack complet : tous les livrables de la mission dans un zip."""
    import zipfile
    from onepager_generator import generate_onepager_pdf
    from proposal_generator import generate_proposal_docx
    scores = calculate_esg_scores(request)
    content = generate_esg_content(request, scores)
    logo_bytes, art = build_extras(request)
    charts_dark = {}
    if art:
        charts_dark["cover_art"] = art
    brand = getattr(request, "custom_colors", None)
    try:
        charts_dark["radar"] = radar_chart(scores, request.aesthetic_theme, lang=request.language, brand=brand)
        charts_dark["bars"] = score_bars_chart(scores, request.aesthetic_theme, lang=request.language, brand=brand)
        env = request.environmental
        if any(v is not None for v in (env.scope1_emissions, env.scope2_emissions, env.scope3_emissions)):
            charts_dark["emissions_pie"] = emissions_breakdown_chart(
                env.scope1_emissions, env.scope2_emissions, env.scope3_emissions,
                request.aesthetic_theme, lang=request.language, brand=brand)
    except Exception as e:
        print(f"Pack charts error: {e}")
    charts_dark.update(build_advanced_charts(request, scores, light_bg=False))
    charts_light = {k: v for k, v in charts_dark.items() if k == "cover_art"}
    try:
        charts_light["radar"] = radar_chart(scores, request.aesthetic_theme, light_bg=True,
                                            lang=request.language, brand=brand)
    except Exception:
        pass
    charts_light.update(build_advanced_charts(request, scores, light_bg=True))

    base = f"{safe_name(request.company.name)}_{request.company.reporting_year}"
    files = {}
    files[f"Presentation_{base}.pptx"] = generate_pptx(request, scores, content, charts_dark, logo_bytes=logo_bytes)
    files[f"Rapport_ESG_{base}.pdf"] = generate_pdf_report(request, scores, content, charts_light, logo_bytes=logo_bytes)
    files[f"Rapport_ESG_{base}.docx"] = generate_word_report(request, scores, content, logo_bytes=logo_bytes)
    files[f"Synthese_1page_{base}.pdf"] = generate_onepager_pdf(request, scores)
    files[f"Lettre_de_mission_{base}.docx"] = generate_proposal_docx(request, scores)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for fn, data in files.items():
            z.writestr(fn, data)
    buf.seek(0)
    return StreamingResponse(
        buf, media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="Pack_ESG_{base}.zip"'})


@app.post("/api/generate/onepager")
def generate_onepager(request: ESGRequest):
    """Synthèse ESG une page (PDF) — le document que le dirigeant transfère."""
    from onepager_generator import generate_onepager_pdf
    scores = calculate_esg_scores(request)
    pdf_bytes = generate_onepager_pdf(request, scores)
    filename = f"Synthese_1page_{safe_name(request.company.name)}_{request.company.reporting_year}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes), media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@app.post("/api/generate/proposal")
def generate_proposal(request: ESGRequest):
    """Lettre de mission ESG (Word) — document commercial du consultant."""
    from proposal_generator import generate_proposal_docx
    scores = calculate_esg_scores(request)
    docx_bytes = generate_proposal_docx(request, scores)
    filename = f"Lettre_de_mission_{safe_name(request.company.name)}_{request.company.reporting_year}.docx"
    return StreamingResponse(
        io.BytesIO(docx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
