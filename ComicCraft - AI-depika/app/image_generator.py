import os
import re
import uuid
import random
import urllib.parse
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY", "").strip()
PANELS_DIR = os.path.join("static", "panels")
os.makedirs(PANELS_DIR, exist_ok=True)

# Lazy-loaded local diffusers pipeline
_local_pipe = None


def sanitize_filename(prompt: str) -> str:
    """
    Sanitizes prompt into a safe, unique filename for saving in static/panels.
    """
    clean = re.sub(r'[^a-zA-Z0-9_-]', '_', prompt[:30]).strip('_')
    if not clean:
        clean = "panel"
    unique_suffix = uuid.uuid4().hex[:8]
    return f"{clean}_{unique_suffix}.jpg"


def _generate_with_local_diffusers(prompt: str, output_path: str) -> bool:
    """
    Generates real comic illustrations using Stable Diffusion 1.5 (runwayml/stable-diffusion-v1-5)
    accelerated on the NVIDIA RTX 4050 GPU as specified in the PDF project documentation.
    """
    global _local_pipe
    try:
        import torch
        from diffusers import StableDiffusionPipeline

        if not torch.cuda.is_available():
            print("[INFO] CUDA not available, bypassing local GPU pipeline.")
            return False

        if _local_pipe is None:
            device = "cuda"
            dtype = torch.float16
            gpu_name = torch.cuda.get_device_name(0)
            print(f"[INFO] Initializing Stable Diffusion (runwayml/stable-diffusion-v1-5) on {gpu_name} ({dtype})...")

            # Load model matching Milestone 1 Activity 1.1 of project documentation
            _local_pipe = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=dtype,
                safety_checker=None
            )
            _local_pipe = _local_pipe.to(device)
            _local_pipe.enable_attention_slicing()
            print("[INFO] Stable Diffusion pipeline loaded successfully on GPU!")

        enhanced_prompt = f"comic book art style, graphic novel illustration, {prompt}, masterpiece, vivid vibrant colors, crisp ink lines, detailed scene"

        # Generate image using pipe(prompt).images[0] matching PDF page 10
        image = _local_pipe(
            enhanced_prompt,
            num_inference_steps=20,
            guidance_scale=7.5
        ).images[0]

        image.save(output_path, "JPEG", quality=92)
        print(f"[SUCCESS] Real Stable Diffusion illustration generated via GPU: {output_path}")
        return True

    except Exception as e:
        print(f"[WARNING] Local GPU Stable Diffusion encountered: {e}")
        return False


def _generate_with_ai_cloud(prompt: str, output_path: str) -> bool:
    """
    Cloud AI image generation fallback if GPU is not loaded.
    """
    import requests
    import time
    clean_prompt = re.sub(r'^(Anime style|Comic book style|Dramatic|Funny)[,:]?\s*', '', prompt, flags=re.IGNORECASE)
    short_prompt = clean_prompt[:110].strip()
    enhanced_prompt = f"comic book art, {short_prompt}, vibrant colors, sharp lines, cinematic, high quality"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ComicCraft/1.0"
    }

    for attempt in range(2):
        try:
            seed = random.randint(100, 99999)
            encoded = urllib.parse.quote(enhanced_prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=512&nologo=true&seed={seed}"

            response = requests.get(url, headers=headers, timeout=28)
            if response.status_code == 200 and len(response.content) > 3000:
                from io import BytesIO
                image = Image.open(BytesIO(response.content))
                image.convert("RGB").save(output_path, "JPEG", quality=92)
                print(f"[SUCCESS] Real AI comic artwork generated: {output_path}")
                return True
            time.sleep(2)
        except Exception:
            time.sleep(1)

    return False


def generate_image(prompt: str, filename: str = None) -> str:
    """
    Generates a comic-style image based on prompt and saves it to static/panels/.

    Pipeline Priority:
    1. Local Stable Diffusion (runwayml/stable-diffusion-v1-5) on NVIDIA RTX 4050 GPU (PDF Milestone 1/2)
    2. Cloud AI Image Generator (Stable Diffusion / Flux)

    Returns:
        str: Relative path to saved image (e.g. static/panels/panel_xxx.jpg).
    """
    if not filename:
        filename = sanitize_filename(prompt)

    if not filename.endswith((".jpg", ".png", ".jpeg")):
        filename += ".jpg"

    path = os.path.join("static", "panels", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # 1. Primary: Run local Stable Diffusion on RTX 4050 GPU (Matches PDF)
    if _generate_with_local_diffusers(prompt, path):
        return path.replace("\\", "/")

    # 2. Secondary: Cloud AI image generator
    if _generate_with_ai_cloud(prompt, path):
        return path.replace("\\", "/")

    raise RuntimeError(f"Failed to generate AI image for prompt: {prompt}")
