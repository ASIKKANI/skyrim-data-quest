# backend/ml/inference.py
import os
import json
from backend.models.phishing_model import PhishingModel
from backend.models.rules_engine import RuleEngine
from backend.services.gemini_service import analyze_email  # updated service

# Path to ML model
MODEL_PATH = os.path.join("backend", "models", "phishing_model.pkl")


def run_model_pipeline(email_data: dict):
    """
    Run ML + Rules Engine on a raw email (dict).
    Returns a dict with:
      - ml_score
      - rule_score
      - final_score
      - prediction
      - explanation (from Gemini)
    """
    # -------------------- ML Prediction --------------------
    ml_model = PhishingModel(model_path=MODEL_PATH)
    try:
        ml_model.load_model()
        ml_result = ml_model.predict(email_data)
        ml_score = ml_result.get("probability", 0.5)  # fallback score
    except Exception as e:
        print(f"⚠️ ML model not loaded: {e}. Using fallback score 0.5")
        ml_score = 0.5

    # -------------------- Rules Engine --------------------
    rule_engine = RuleEngine()
    rule_score = rule_engine.evaluate(email_data)

    # -------------------- Weighted Final Score --------------------
    final_score = 0.7 * ml_score + 0.3 * rule_score
    prediction_label = "Phishing" if final_score > 0.5 else "Legitimate"

    result = {
        "ml_score": ml_score,
        "rule_score": rule_score,
        "final_score": final_score,
        "prediction": prediction_label
    }

    # -------------------- Gemini Explanation --------------------
    # -------------------- Gemini Explanation --------------------
    try:
        clean_text = email_data.get("body", "") or email_data.get("clean_text", "") or str(email_data)
        gemini_result = analyze_email(
            clean_text,
            rule_score,
            ml_score,
            final_score
        )
        result["explanation"] = gemini_result.get("explanation", "Explanation not available.")
        result["risk_score"] = gemini_result.get("risk_score", -1)
    except Exception as e:
        print(f"⚠️ Failed to generate Gemini explanation: {e}")
        result["explanation"] = "Explanation not available."
        result["risk_score"] = -1


    return result


# -------------------- CLI USAGE --------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Predict phishing email from JSON file with ML+Rules and Gemini explanation"
    )
    parser.add_argument("--file", required=True, help="Path to the saved email JSON file")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File {args.file} not found.")
        exit(1)

    # Load email JSON
    with open(args.file, "r", encoding="utf-8") as f:
        email_data = json.load(f)

    # Run pipeline
    prediction = run_model_pipeline(email_data)

    # Print nicely
    print("\n===== Prediction Result =====")
    for key, value in prediction.items():
        print(f"{key}: {value}")
