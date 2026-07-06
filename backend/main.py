import os
import io
import re
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.datastructures import MutableHeaders

from models import ESGRequest, ESGScores, AestheticTheme
from esg_calculator import calculate_esg_scores
from chart_generator import radar_chart, score_bars_chart, emissions_breakdown_chart, gauge_chart
from ppt_generator import generate_pptx
from report_generator import generate_pdf_report
from docx_generator import generate_word_report
from content_generator import generate_esg_content

SAFE_NAME_RE = re.compile(r'[^\w\-]')

def safe_name(name: str) -> str:
    return SAFE_NAME_RE.sub('_', name)


SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "no-referrer",
}

MAX_BODY_BYTES = 100_000  # 100 KB


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
                # Rebuild receive so the body can still be read downstream
                async def receive_with_body():
                    return {"type": "http.request", "body": body, "more_body": False}
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


@app.post("/api/generate/pptx")
def generate_presentation(request: ESGRequest):
    """Generate PowerPoint presentation."""
    scores = calculate_esg_scores(request)
    content = generate_esg_content(request, scores)

    chart_images = {}
    try:
        chart_images["radar"] = radar_chart(scores, request.aesthetic_theme)
    except Exception as e:
        print(f"Radar chart error: {e}")
    try:
        chart_images["bars"] = score_bars_chart(scores, request.aesthetic_theme)
    except Exception as e:
        print(f"Bars chart error: {e}")

    env = request.environmental
    if env.scope1_emissions or env.scope2_emissions or env.scope3_emissions:
        try:
            chart_images["emissions_pie"] = emissions_breakdown_chart(
                env.scope1_emissions, env.scope2_emissions, env.scope3_emissions,
                request.aesthetic_theme
            )
        except Exception as e:
            print(f"Pie chart error: {e}")

    pptx_bytes = generate_pptx(request, scores, content, chart_images)

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

    chart_images = {}
    try:
        chart_images["radar"] = radar_chart(scores, request.aesthetic_theme)
    except Exception as e:
        print(f"Radar chart error: {e}")

    env = request.environmental
    if env.scope1_emissions or env.scope2_emissions or env.scope3_emissions:
        try:
            chart_images["emissions_pie"] = emissions_breakdown_chart(
                env.scope1_emissions, env.scope2_emissions, env.scope3_emissions,
                request.aesthetic_theme
            )
        except Exception as e:
            print(f"Pie chart error: {e}")

    pdf_bytes = generate_pdf_report(request, scores, content, chart_images)

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
    docx_bytes = generate_word_report(request, scores, content)
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


# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
