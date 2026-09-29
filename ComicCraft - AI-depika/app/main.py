import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routes import router

# Load environment configuration
load_dotenv()

# Initialize FastAPI application
app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="Automated AI Comic Strip Creator utilizing Gemini Flash, Gemini Pro, and Stable Diffusion.",
    version="1.0.0"
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure required static directories exist
os.makedirs("static/panels", exist_ok=True)
os.makedirs("static/exports", exist_ok=True)
os.makedirs("static/fonts", exist_ok=True)
os.makedirs("static/images", exist_ok=True)
os.makedirs("static/css", exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include application routes
app.include_router(router)


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint to verify server status."""
    return {
        "status": "healthy",
        "service": "ComicCraft AI",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    print(f"Starting ComicCraft Server at http://{host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
