from fastapi import FastAPI
from backend.routes import detect

# ----------------------------
# APP INITIALIZATION
# ----------------------------
app = FastAPI(
    title="Social Engineering Detection API",
    description="API for parsing and detecting phishing/malicious emails",
    version="1.0.0"
)

# ----------------------------
# ROUTES
# ----------------------------
@app.get("/", tags=["Health Check"])
def home():
    """Basic health check endpoint."""
    return {"message": "✅ FastAPI backend is running!"}

# Include detection routes
app.include_router(detect.router, prefix="/api", tags=["Detection"])
