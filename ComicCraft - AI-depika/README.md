# ComicCraft - AI Comic Story Creator using Gemini Models

ComicCraft is a full-stack, web-based application that automatically crafts personalized 5-panel comic book stories and vivid illustrations based on user prompts. Built with **FastAPI**, **Google Gemini AI models (Gemini Flash & Gemini Pro)**, and **Stable Diffusion**, ComicCraft streamlines the entire creative storytelling process from initial premise to printable PDF publication.

---

## 🌟 Key Features

- **Multi-Modal AI Pipeline**:
  - **Gemini Flash (`models/gemini-1.5-flash`)**: High-speed, structured 5-panel comic planning and prompt engineering.
  - **Gemini Pro (`models/gemini-1.5-pro`)**: Detailed scriptwriting, comic captions, and character dialogue expansion.
  - **Stable Diffusion (`runwayml/stable-diffusion-v1-5`)**: Comic-style panel illustrations with cloud, local GPU, and aesthetic zero-crash fallback support.
- **Dynamic Comic Layout Engine (`layout_builder.py`)**: Assembles panels, scene descriptions, dialogue blocks, and image references into a cohesive narrative sequence.
- **Automated Multi-Page PDF Exporter (`exporters.py`)**: Compiles each panel with its high-resolution illustration, titles, and narration onto structured PDF pages with Unicode font support.
- **Responsive Jinja2 Web UI**: Features a scenic background, quick prompt presets, real-time loading feedback, sequential panel preview, and one-click PDF download with export confirmation.
- **Dual Form & REST API Endpoints**: Full support for both interactive browser sessions and JSON-based API integrations with Swagger documentation.

---

## 📂 Project Architecture & Directory Structure

```
ComicCraft - AI/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI app initialization, CORS, static mounts
│   ├── routes.py             # Route handlers (/, /generate, /generate-comic/json, /export-success, /test-image, /download)
│   ├── gemini_flash.py       # Gemini Flash structured 5-panel outline generator
│   ├── gemini_pro.py         # Gemini Pro story narrative & dialogue writer
│   ├── image_generator.py    # Multi-tier Stable Diffusion & aesthetic panel generator
│   ├── layout_builder.py     # Binds panel metadata, images, and text into layout
│   └── exporters.py          # Multi-page PDF compiler using FPDF
├── templates/
│   ├── index.html            # Comic creator form with scenic background & presets
│   ├── comic_preview.html    # Sequential 5-panel comic preview page with PDF CTA
│   ├── export_success.html   # Download confirmation page with "Create Another" CTA
│   ├── result.html           # Plan inspection view
│   └── all_users.html        # Session activity record view
├── static/
│   ├── css/
│   │   └── style.css         # Styling for forms, comic panels, cards, and animations
│   ├── images/
│   │   └── background.jpg    # Scenic nature background for homepage
│   ├── fonts/
│   │   ├── DejaVuSans.ttf    # Unicode TTF font for PDF generation
│   │   └── DejaVuSans-Bold.ttf
│   ├── panels/               # Storage for generated panel illustrations
│   └── exports/              # Storage for exported comic PDFs
├── .env                      # Active environment variables (API keys)
├── .env.example              # Sample environment template
├── requirements.txt          # Python dependencies
├── test_app.py               # Automated end-to-end test suite
└── README.md                 # Complete setup, running, and testing documentation
```

---

## 🛠️ Prerequisites

- **Operating System**: Windows, macOS, or Linux
- **Python**: Version `3.10` or `3.11` (Python 3.11 recommended)
- **Pip**: Latest version
- **Visual Studio Code (VS Code)** (optional, but recommended)

---

## 🚀 VS Code Setup & Installation Guide

### Step 1: Open the Project in VS Code
1. Launch **Visual Studio Code**.
2. Click **File** > **Open Folder...** and select the `ComicCraft - AI` directory:
   ```
   c:\Users\user\Pictures\ComicCraft - AI
   ```
3. Open the integrated terminal in VS Code using the shortcut:
   `Ctrl + \`` (backtick) or go to **Terminal** > **New Terminal**.

---

### Step 2: Set Up Python Virtual Environment
A virtual environment isolates project dependencies:

#### On Windows (PowerShell / Command Prompt):
```powershell
python -m venv comiccraft-env
.\comiccraft-env\Scripts\activate
```

*(If PowerShell displays an ExecutionPolicy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and then run activate again).*

#### On macOS / Linux:
```bash
python3 -m venv comiccraft-env
source comiccraft-env/bin/activate
```

---

### Step 3: Install Required Dependencies
With the virtual environment activated, install all required packages:
```bash
pip install -r requirements.txt
```

---

### Step 4: Configure API Keys (`.env`)
Create or edit your `.env` file in the project root:
```env
# Google Gemini API Key (Get a free API key at https://aistudio.google.com/)
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Hugging Face API Token (Optional, for Cloud Stable Diffusion at https://huggingface.co/settings/tokens)
HF_API_KEY=your_huggingface_token_here

# Server host and port
HOST=127.0.0.1
PORT=8000
```

> **Zero-Setup Demo Mode**:
> ComicCraft is engineered with robust fallbacks. If `GEMINI_API_KEY` or `HF_API_KEY` is not provided, the application will automatically activate its built-in AI comic planner and stylized illustration generator so you can test all UI flows, layout generation, and PDF downloads immediately without errors!

---

## 💻 Running the Application

Start the FastAPI application with Uvicorn and live hot-reloading:

```bash
uvicorn app.main:app --reload
```

You will see output similar to:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 🌐 Accessing the Application

1. **Web Interface (Homepage)**:
   Open your browser and navigate to:
   👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

2. **Interactive API Documentation (Swagger UI)**:
   Explore and test all REST endpoints interactively:
   👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

3. **Alternative API Documentation (ReDoc)**:
   👉 **[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)**

---

## 🧪 Testing & Verification

### Method 1: Interactive Browser Testing

#### Scenario 1: Create an Epic Comic Strip
1. Open `http://127.0.0.1:8000`.
2. Fill in:
   - **Story Prompt**: `A brave fox exploring an enchanted forest.`
   - **Main Character Name**: `Free`
   - **Setting**: `Forest`
   - **Story Tone**: `Dramatic`
   - **Art Style**: `Realistic`
3. Click **Generate Comic**.
4. Review the 5 generated panels with illustrations, captions, and narrative dialogue on the `Your Comic Preview` page.
5. Click **Download Your Comic as PDF**.
6. The PDF will download to your device and you will be routed to the confirmation page (`/export-success`).

#### Scenario 2: Iterate with a Light-Hearted / Humorous Tone
1. Return to the homepage or click **Go Create Another Comic**.
2. Change the **Story Tone** to `Funny` and **Art Style** to `Comic Book`.
3. Generate again to see how Gemini and the pipeline adapt the narrative, dialogue, and visuals to match the selected mood!

---

### Method 2: Automated Test Suite

A comprehensive test script (`test_app.py`) is included to verify all system endpoints:
```bash
python test_app.py
```

This automatically validates:
1. `GET /health` - System health check.
2. `GET /` - Homepage form rendering.
3. `GET /test-image` - Direct image generation utility.
4. `POST /generate-comic/json` - End-to-end 5-panel comic generation via JSON API.
5. `GET /download` - PDF file delivery and byte integrity.
6. `POST /generate` - Form submission and HTML preview rendering.
7. `GET /export-success` - Export success confirmation page.

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Renders the ComicCraft homepage form (`index.html`) |
| `POST` | `/generate` | Accepts HTML form inputs, runs AI pipeline, and renders `comic_preview.html` |
| `POST` | `/generate-comic/json` | REST API accepting JSON (`PromptRequest`), returns structured layout and PDF URL |
| `GET` | `/export-success` | Renders export confirmation page (`export_success.html`) |
| `GET` | `/test-image` | Generates a single test illustration from a prompt query parameter |
| `GET` | `/download` | Downloads a specific generated PDF file as an attachment |
| `GET` | `/health` | Returns application health status |
| `GET` | `/docs` | Interactive Swagger UI API documentation |

---

## 🎨 Technology Stack

- **Backend Framework**: FastAPI (Asynchronous ASGI)
- **Web Server**: Uvicorn
- **Templating**: Jinja2 (HTML5 / Modern CSS)
- **AI Models**:
  - Google Gemini 1.5 Flash (Structured outline planning)
  - Google Gemini 1.5 Pro (Rich story script & dialogue writing)
  - Stable Diffusion 1.5 (Comic panel imagery)
- **PDF Generation**: FPDF2 with Unicode TTF support
- **Image Processing**: Pillow (PIL)

---

## 💡 Troubleshooting & Tips

- **Missing API Key**:
  If you haven't added your Gemini API key yet, the application will automatically use its internal comic planner and aesthetic graphics engine. To use real Gemini 1.5 models, add your key to `.env` and restart the server.
- **Port In Use (8000)**:
  If port 8000 is occupied, run with a different port:
  ```bash
  uvicorn app.main:app --port 8080 --reload
  ```
- **Local GPU Diffusers**:
  To use local GPU Stable Diffusion instead of cloud or fallback, install PyTorch with CUDA and `diffusers`:
  ```bash
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
  pip install diffusers transformers accelerate
  ```
