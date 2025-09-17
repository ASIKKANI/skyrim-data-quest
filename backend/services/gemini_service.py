# backend/services/gemini_service.py
import re
from backend.config import get_gemini_model

# Initialize Gemini model once
model = get_gemini_model()

def analyze_email(email_text: str) -> dict:
    """
    Send email text to Gemini and get risk analysis.
    Returns a dict with:
      - risk_score: int 0–100
      - explanation: str
    """
    if not email_text or not email_text.strip():
        return {
            "risk_score": -1,
            "explanation": "No email content provided."
        }

    prompt = f"""
You are a security AI analyzing an email. Your task is to provide a **clear, detailed explanation** for the risk assessment in a way that a non-technical person can understand.

Instructions:
1. Give a risk score from 0 (safe) to 100 (very risky).
2. Explain **exactly why** the email received this score. Break down the reasoning by pointing out suspicious features detected by the ML model, such as:
   - Suspicious links or domains
   - Unusual sender address
   - Urgent or threatening language
   - Requests for sensitive information
   - Other red flags in the subject or body
3. Include any factors from the rules engine that influenced the score.
4. Write in **simple, clear language**, using bullet points if needed.
5. Conclude with a short summary sentence stating if the email is likely phishing or legitimate.

Email to analyze:
{email_text}
"""


    try:
        # Use Gemini API
        response = model.generate_content(prompt)

        # Extract text from response safely
        output = getattr(response, "text", str(response)).strip()

        return {
            "risk_score": extract_risk_score(output),
            "explanation": output or "Explanation not available."
        }

    except Exception as e:
        print(f"⚠️ Failed to generate Gemini explanation: {e}")
        return {
            "risk_score": -1,
            "explanation": "Explanation not available."
        }


def extract_risk_score(output: str) -> int:
    """
    Extracts first numeric risk score (0–100) from Gemini output.
    If not found, returns -1.
    """
    match = re.search(r"\b(\d{1,3})\b", output)
    if match:
        score = int(match.group(1))
        return min(max(score, 0), 100)  # clamp between 0–100
    return -1
