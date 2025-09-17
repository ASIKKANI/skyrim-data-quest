from dotenv import load_dotenv
import os
import google.generativeai as genai

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()  # loads .env from project root

# ----------------------------
# Gemini API Key
# ----------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY is missing! Add it to your .env file.")

# ----------------------------
# Configure Gemini Client
# ----------------------------
genai.configure(api_key=GEMINI_API_KEY)

# ----------------------------
# Helper: Get a Gemini Model
# ----------------------------
def get_gemini_model(model_name: str = "gemini-1.5-flash"):
    """
    Returns a configured Gemini model instance.

    Args:
        model_name (str): Gemini model to use. Default is 'gemini-1.5-flash'.

    Usage:
        from backend.config import get_gemini_model
        model = get_gemini_model()
        response = model.generate_content("Hello world")
    """
    try:
        return genai.GenerativeModel(model_name)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Gemini model '{model_name}': {e}")
