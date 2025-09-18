# backend/scripts/run_pipeline.py
import os
import json
import pandas as pd
from extract_features import extract_features
from detect_anomalies import detect_anomalies

# Path to saved emails (JSON files)
MAILS_FOLDER = os.path.join(os.path.dirname(__file__), "..", "saved_emails")

def load_nlp_results(filename):
    """Load ML/Gemini results from email JSON file."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            email = json.load(f)
        ml_result = email.get("ml_result", {})
        gemini_result = email.get("gemini_result", {})
        return {"ml_result": ml_result, "gemini_result": gemini_result}
    except Exception as e:
        print(f"⚠ Could not load NLP results from {filename}: {e}")
        return {"ml_result": {}, "gemini_result": {}}


def run_email_pipeline():
    """
    Run full email pipeline:
    1. Extract features
    2. Detect anomalies
    3. Load NLP results for expandable view
    """
    df_emails = extract_features()

    if df_emails.empty:
        print("⚠ No emails found or failed to extract features.")
        return []

    df_emails = detect_anomalies(df_emails)

    # Add NLP results for each email
    email_details = []
    for idx, row in df_emails.iterrows():
        filename = os.path.join(MAILS_FOLDER, os.listdir(MAILS_FOLDER)[idx])
        nlp_results = load_nlp_results(filename)

        email_details.append({
            "subject": row["subject"],
            "sender": row["sender"],
            "hour": row["hour"],
            "day_of_week": row["day_of_week"],
            "body_length": row["body_length"],
            "anomaly_score": row["anomaly_score"],
            "is_anomaly": row["is_anomaly"],
            "nlp_results": nlp_results  # expandable section in frontend
        })

    return email_details


if __name__ == "__main__":
    results = run_email_pipeline()
    for email in results:
        print(f"Subject: {email['subject']} | Anomaly: {email['is_anomaly']}")
        print(f"  + NLP Results available (expand in UI)")
