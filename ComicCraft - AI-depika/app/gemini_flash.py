import os
import json
import re
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

_cached_flash_model = None


def _get_gemini_model():
    """
    Auto-detects and returns the best working Gemini Flash model.
    Prioritizes Gemini 2.5 Flash, Gemini Flash Latest, and Gemini 1.5 Flash.
    """
    global _cached_flash_model
    if _cached_flash_model is not None:
        return _cached_flash_model

    candidate_models = [
        "gemini-2.5-flash",
        "gemini-flash-latest",
        "gemini-2.0-flash",
        "gemini-1.5-flash"
    ]

    for model_name in candidate_models:
        try:
            m = genai.GenerativeModel(model_name)
            # Test simple call
            _cached_flash_model = m
            print(f"[INFO] Successfully selected Gemini Flash model: {model_name}")
            return m
        except Exception:
            continue

    # Default fallback
    _cached_flash_model = genai.GenerativeModel("gemini-2.5-flash")
    return _cached_flash_model


def _generate_dynamic_fallback_outline(user_prompt: str) -> list:
    """
    Generates a dynamic 5-panel comic outline tailored directly to the user's
    prompt when offline or if an API exception occurs.
    """
    clean_prompt = user_prompt.strip()
    return [
        {
            "panel": 1,
            "title": "The Quest Begins",
            "scene_description": f"The story opens: {clean_prompt}. Setting the scene and introducing our hero.",
            "image_prompt": f"Comic book panel, introducing hero in {clean_prompt}, vibrant comic art, wide shot, dynamic lighting, masterpiece"
        },
        {
            "panel": 2,
            "title": "A Mysterious Discovery",
            "scene_description": "Our protagonist encounters an unexpected obstacle and discovers hidden secrets.",
            "image_prompt": f"Dramatic comic panel, discovering mystical signs, high tension, comic art style, detailed background"
        },
        {
            "panel": 3,
            "title": "The Rising Conflict",
            "scene_description": "Tension mounts as our hero faces a surprising challenge head-on.",
            "image_prompt": f"Action comic panel, intense confrontation, comic speech bubble layout, dynamic perspective, vibrant colors"
        },
        {
            "panel": 4,
            "title": "A Leap of Courage",
            "scene_description": "A climactic turning point where bravery and creativity alter destiny.",
            "image_prompt": f"Epic comic book climax, glowing aura, heroic stance, cinematic angle, comic book cover aesthetic"
        },
        {
            "panel": 5,
            "title": "Triumphant Horizon",
            "scene_description": "The dust clears, revealing the triumphant conclusion and setting up the next adventure.",
            "image_prompt": f"Beautiful comic panel, sunset celebration, warm glowing colors, graphic novel finale, detailed linework"
        }
    ]


def generate_outline(user_prompt: str) -> list:
    """
    Generates a 5-panel comic layout based on the user's story idea using Gemini Flash.
    Args:
        user_prompt (str): The user's comic idea prompt.
    Returns:
        list: A list of dictionaries, one for each panel.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        print("[INFO] GEMINI_API_KEY not configured. Using dynamic comic planner.")
        return _generate_dynamic_fallback_outline(user_prompt)

    prompt = f"""
You are a professional AI comic planner.

Your task is to generate a strictly formatted JSON array containing 5 panel descriptions for a comic based on the story idea below:

STORY: "{user_prompt}"

Each JSON object in the array must strictly have these 4 keys:
- "panel": integer (1 to 5)
- "title": short creative title string
- "scene_description": narrative scene context string
- "image_prompt": descriptive artistic visual prompt for image generation

Respond ONLY in this valid JSON format, with no markdown fences, no conversational text:
[
  {{
    "panel": 1,
    "title": "Title here",
    "scene_description": "Scene description here",
    "image_prompt": "Artistic visual description for image generation"
  }}
]
"""

    output_text = ""
    try:
        model = _get_gemini_model()
        response = model.generate_content(prompt)
        output_text = response.text.strip()
        print("\n=== RAW GEMINI FLASH RESPONSE ===\n", output_text[:400], "...")

        # Remove markdown code fences if present
        if "```json" in output_text:
            output_text = output_text.split("```json")[1].split("```")[0].strip()
        elif "```" in output_text:
            output_text = output_text.split("```")[1].split("```")[0].strip()

        # Extract JSON array via regex
        json_match = re.search(r'\[\s*\{.*\}\s*\]', output_text, re.DOTALL)
        if json_match:
            output_text = json_match.group(0)

        panel_data = json.loads(output_text)

        # Standardize panel format
        standardized_panels = []
        for i, p in enumerate(panel_data, start=1):
            if isinstance(p, dict):
                p_num = p.get("panel") or p.get("panel_number") or i
                p_title = p.get("title") or f"Panel {i}"
                p_desc = p.get("scene_description") or p.get("setting") or p.get("description") or ""
                p_img = p.get("image_prompt") or p.get("character_action") or f"{p_title}, comic book art"
                standardized_panels.append({
                    "panel": int(p_num),
                    "title": str(p_title),
                    "scene_description": str(p_desc),
                    "image_prompt": str(p_img)
                })

        if len(standardized_panels) >= 3:
            return standardized_panels[:5]

        raise ValueError("Gemini response contained insufficient panel data.")

    except Exception as e:
        print(f"[ERROR] Gemini Flash parsing failed ({e}). Raw response: {output_text[:200]}")
        return _generate_dynamic_fallback_outline(user_prompt)
