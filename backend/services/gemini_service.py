# backend/services/gemini_service.py
from backend.config import get_gemini_model

# Initialize Gemini model once
model = get_gemini_model()

def analyze_email(email_text: str, rule_score: float, ml_score: float, final_score: float) -> dict:
    """
    Send email text + existing scores to Gemini and get a clear explanation.
    Returns a dict with:
      - risk_score: Final Score (float 0–100)
      - explanation: str (human-readable reasoning)
    """
    if not email_text or not email_text.strip():
        return {
            "risk_score": -1,
            "explanation": "No email content provided."
        }

    prompt = f"""You are a security AI analyzing an email. Your task is to explain the **scores** below
in a way that a non-technical user can easily understand.

⚡ Given Scores:
- Rule Score: {rule_score}
- ML Score: {ml_score}
- Final Score: {final_score}

Instructions:
1. Do not create new numbers. Only explain the values already provided.
2. For Rule Score → explain if keywords, suspicious phrases, or red flags were found.
   If it is 0, clarify that no risky keywords were detected.
3. For ML Score → explain that this is from the ML model's confidence/accuracy and what it means.
4. For Final Score → explain how it combines both rules and ML model, and what it suggests about phishing likelihood.
5. Use **clear, simple language** and bullet points where needed.
6. Explain in simple terms what a **false positive** and **false negative** would mean for this email.
   - False positive: when the system wrongly flags a safe email as phishing.
   - False negative: when the system misses a phishing email and marks it as safe.
7. Conclude with a short, plain summary: whether the email is likely phishing or safe.

Email to analyze:
{email_text}

"""

    try:
        # Use Gemini API
        response = model.generate_content(prompt)

        # Extract text safely
        output = getattr(response, "text", str(response)).strip()

        return {
            "risk_score": final_score,   # always use provided final score
            "explanation": output or "Explanation not available."
        }

    except Exception as e:
        print(f"⚠️ Failed to generate Gemini explanation: {e}")
        return {
            "risk_score": -1,
            "explanation": "Explanation not available."
        }
