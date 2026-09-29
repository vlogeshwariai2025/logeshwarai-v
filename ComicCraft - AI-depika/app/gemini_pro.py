import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"[WARNING] genai.configure error: {e}")

_cached_pro_model = None


def _get_gemini_model():
    """
    Auto-detects and returns the best available live Gemini model for comic scriptwriting.
    Prioritizes models with active quota: gemini-2.5-flash, gemini-flash-latest, gemini-3.1-pro-preview.
    """
    global _cached_pro_model
    if _cached_pro_model is not None:
        return _cached_pro_model

    candidate_models = [
        "gemini-2.5-flash",
        "gemini-flash-latest",
        "gemini-3.1-pro-preview",
        "gemini-2.5-pro"
    ]

    for model_name in candidate_models:
        try:
            m = genai.GenerativeModel(model_name)
            _cached_pro_model = m
            print(f"[INFO] Successfully selected Gemini model for story writing: {model_name}")
            return m
        except Exception:
            continue

    _cached_pro_model = genai.GenerativeModel("gemini-2.5-flash")
    return _cached_pro_model


def _generate_dynamic_fallback_story(outline: list) -> str:
    """
    Fallback story script generator customized dynamically from the outline.
    """
    story_parts = []
    for idx, panel in enumerate(outline, start=1):
        if isinstance(panel, dict):
            title = panel.get("title", f"Panel {idx}")
            desc = panel.get("scene_description", "")
        else:
            title = f"Scene {idx}"
            desc = str(panel)

        part = f"""**Panel {idx}: {title}**
{desc}
**CAPTION:** The journey deepens as the mystery unfolds.
**NARRATION:** Determined and resolute, our protagonist presses forward. "Whatever lies ahead, we are ready!" """
        story_parts.append(part)

    return "\n\n".join(story_parts)


def generate_story(outline: list) -> str:
    """
    Generates a detailed comic story with narration and character dialogue
    from a list of comic panel outlines using Gemini.

    Args:
        outline (list): A list of dicts or strings representing each comic panel's idea.

    Returns:
        str: The generated comic story text.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        print("[INFO] GEMINI_API_KEY not configured. Using dynamic comic scriptwriter.")
        return _generate_dynamic_fallback_story(outline)

    # Format the panel outline as a numbered list for clarity
    formatted_items = []
    for i, item in enumerate(outline):
        if isinstance(item, dict):
            title = item.get("title", "")
            desc = item.get("scene_description", "")
            formatted_items.append(f"Panel {i+1}: {title} - {desc}")
        else:
            formatted_items.append(f"Panel {i+1}: {item}")
    formatted_outline = "\n".join(formatted_items)

    prompt = f"""
You are a professional comic book writer.

Given the following panel breakdown, write a dynamic comic-style story with captivating narration, atmospheric captions, and character dialogues for each panel.

Panel Outline:
{formatted_outline}

Formatting Guidelines:
- Format each panel strictly starting with:
  **Panel <number>: <Title>**
- Under each panel, provide:
  - 1 sentence of scene context
  - **CAPTION:** ambient descriptions, sound effects, or environmental mood
  - **NARRATION:** character actions, thoughts, and spoken dialogues with quotation marks
- Keep each panel punchy, entertaining, and connected into a complete 5-panel story arc.
"""

    try:
        model = _get_gemini_model()
        response = model.generate_content(prompt)
        story_text = response.text.strip()
        print("\n=== RAW GEMINI PRO STORY RESPONSE ===\n", story_text[:350], "...")
        return story_text
    except Exception as e:
        print(f"[ERROR] Error generating story with Gemini: {e}")
        return _generate_dynamic_fallback_story(outline)
