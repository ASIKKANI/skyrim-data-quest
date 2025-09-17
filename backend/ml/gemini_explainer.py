# backend/ml/gemini_explainer.py
from backend.config import get_gemini_model
import re

# Get the Gemini model instance
model = get_gemini_model()

def generate_email_explanation(email_data: dict, prediction: dict) -> str:
    """
    Use Gemini API to generate an explanation and risk analysis for an email.
    Returns a string explanation.
    """
    prompt = f"""
You are a security analyst. Analyze the following email:

Subject: {email_data.get('headers', {}).get('Subject', '')}
From: {email_data.get('from', '')}
Body: {email_data.get('body', '')}

Prediction: {prediction['prediction']}
ML score: {prediction['ml_score']:.2f}
Rule score: {prediction['rule_score']:.2f}
Final score: {prediction['final_score']:.2f}

Provide a concise explanation why this email is considered {prediction['prediction']}.
Give a risk assessment and any red flags in simple bullet points.
"""

    try:
        # Use the modern API
        response = model.generate_content(prompt)
        explanation = response.text
    except Exception as e:
        print(f"⚠️ Failed to generate Gemini explanation: {e}")
        explanation = "Explanation not available."

    return explanation
