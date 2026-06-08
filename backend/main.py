import os
import io
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from models import ESGRequest, ESGScores, AestheticTheme
from esg_calculator import calculate_esg_scores
from chart_generator import radar_chart, score_bars_chart, emissions_breakdown_chart, gauge_chart
from ppt_generator import generate_pptx
from report_generator import generate_pdf_report
from docx_generator import generate_word_report
from ai_content import generate_esg_content

app = FastAPI(title="ESG Platform API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "ESG Platform"}


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

    filename = f"ESG_{request.company.name.replace(' ', '_')}_{request.company.reporting_year}.pptx"
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

    filename = f"{type_suffix}_{request.company.name.replace(' ', '_')}_{request.company.reporting_year}.pdf"
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
    filename = f"{type_suffix}_{request.company.name.replace(' ', '_')}_{request.company.reporting_year}.docx"
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
