import os
import traceback
from fastapi import APIRouter, Request, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.exporters import save_pdf

# Setup router and template engine
router = APIRouter()
templates = Jinja2Templates(directory="templates")


# Pydantic schema for JSON API requests
class PromptRequest(BaseModel):
    prompt: str = Field(..., description="Story prompt or main idea", example="A brave fox exploring an enchanted forest.")
    character_name: str = Field(..., description="Hero of the comic", example="Free")
    setting: str = Field(..., description="Location of the story", example="forest")
    tone: str = Field(..., description="Tone or mood of the comic", example="dramatic")
    style: str = Field(..., description="Visual art style preference", example="anime")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Renders the homepage form where users configure and submit their comic prompt.
    """
    return templates.TemplateResponse(request=request, name="index.html")


@router.post("/generate", response_class=HTMLResponse)
async def generate_comic(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    style: str = Form(...)
):
    """
    Handles form submission, coordinates multi-modal AI generation pipeline
    (Gemini Flash + Gemini Pro + Stable Diffusion), and returns comic_preview.html.
    """
    try:
        # Combine user inputs into a structured full prompt
        full_prompt = (
            f"{prompt}\n"
            f"The main character is {character_name}.\n"
            f"The setting is a {setting}.\n"
            f"The tone is {tone}. The art style is {style}."
        )

        print(f"\n[INFO] Starting Comic Generation for: {character_name} in {setting} ({style} style)")

        # Step 1: Generate 5-panel comic outline with Gemini Flash
        outline = generate_outline(full_prompt)

        if not isinstance(outline, list) or not all(isinstance(p, dict) and "image_prompt" in p for p in outline):
            raise ValueError("Invalid outline structure received from Gemini Flash response.")

        # Step 2: Generate rich story narration and dialogues with Gemini Pro
        full_story = generate_story(outline)

        # Step 3: Generate visual illustrations for each panel
        images = []
        for i, panel in enumerate(outline):
            if i > 0:
                import time
                time.sleep(1.2)
            img = generate_image(panel.get("image_prompt", prompt))
            images.append(img)

        # Step 4: Organize and bind into structured comic layout
        layout = build_comic_layout(images, full_story, outline)

        # Step 5: Compile comic into downloadable PDF with FPDF
        pdf_path = save_pdf(layout)
        web_pdf_path = "/" + pdf_path.replace("\\", "/").lstrip("/")

        # Render preview template
        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": layout,
                "pdf_path": web_pdf_path,
                "character_name": character_name,
                "setting": setting,
                "tone": tone,
                "style": style,
                "prompt": prompt
            }
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-comic/json")
async def generate_comic_json(req: PromptRequest):
    """
    API endpoint accepting a JSON payload to generate a full comic,
    returning structured JSON data and PDF download path.
    """
    try:
        full_prompt = (
            f"{req.prompt}\n"
            f"The main character is {req.character_name}.\n"
            f"The setting is a {req.setting}.\n"
            f"The tone is {req.tone}. The art style is {req.style}."
        )

        # Pipeline execution
        outline = generate_outline(full_prompt)
        full_story = generate_story(outline)
        images = []
        for i, panel in enumerate(outline):
            if i > 0:
                import time
                time.sleep(1.2)
            img = generate_image(panel.get("image_prompt", req.prompt))
            images.append(img)
        layout = build_comic_layout(images, full_story, outline)
        pdf_path = save_pdf(layout)
        web_pdf_path = "/" + pdf_path.replace("\\", "/").lstrip("/")

        return JSONResponse(content={
            "status": "success",
            "message": "Comic generated successfully",
            "character_name": req.character_name,
            "setting": req.setting,
            "tone": req.tone,
            "style": req.style,
            "layout": layout,
            "pdf_path": web_pdf_path
        })
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, pdf_path: str = Query("", description="Path to generated PDF")):
    """
    Displays the export confirmation page after downloading the comic.
    """
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={"pdf_path": pdf_path}
    )


@router.get("/test-image")
async def test_image(prompt: str = Query("A futuristic city at sunset, sci-fi, cinematic, artstation", description="Test prompt for image generator")):
    """
    Developer utility endpoint to test image generation directly without a full comic run.
    """
    try:
        image_path = generate_image(prompt)
        web_path = "/" + image_path.replace("\\", "/").lstrip("/")
        return {
            "message": "Image generated successfully",
            "path": web_path
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download")
async def download_file(path: str = Query(..., description="Relative path of file to download")):
    """
    Serves a file (such as the generated PDF) as a direct attachment download.
    """
    clean_path = path.lstrip("/\\")
    if not os.path.exists(clean_path):
        raise HTTPException(status_code=404, detail="Requested file not found.")
    filename = os.path.basename(clean_path)
    return FileResponse(clean_path, filename=filename, media_type="application/pdf")


@router.get("/result", response_class=HTMLResponse)
async def view_result(request: Request):
    """View generated AI plan template."""
    return templates.TemplateResponse(request=request, name="result.html", context={"outline": []})


@router.get("/all-users", response_class=HTMLResponse)
async def view_all_users(request: Request):
    """View all users / activity records template."""
    return templates.TemplateResponse(request=request, name="all_users.html")

