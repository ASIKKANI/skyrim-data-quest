from fastapi import FastAPI
from backend.routes import detect
from dotenv import load_dotenv
import os

# Local imports
from backend.routes import detect

# ----------------------------
# ENV + CONFIG
# ----------------------------
load_dotenv()  # Load variables from .env file
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("❌ Missing GEMINI_API_KEY. Please set it in your .env file.")

# ----------------------------
# APP INITIALIZATION
# ----------------------------
app = FastAPI(
    title="Social Engineering Detection API",
    description="API for parsing and detecting phishing/malicious emails using Gemini",
    version="1.0.0"
)

# ----------------------------
# ROUTES
# ----------------------------
@app.get("/", tags=["Health Check"])
def health_check():
    """Basic health check endpoint."""
    return {"status": "ok", "message": "✅ FastAPI backend is running!"}

# Detection-related routes
app.include_router(detect.router, prefix="/api", tags=["Detection"])
