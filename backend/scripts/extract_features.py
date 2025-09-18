import os
import json
import pandas as pd
from datetime import datetime

# Folder containing saved email JSONs
MAILS_FOLDER = os.path.join(os.path.dirname(__file__), "..", "saved_emails")

def extract_features():
    """
    Reads all JSON emails from MAILS_FOLDER and extracts basic features:
    - subject
    - sender
    - hour of sending
    - day of week
    - body length
    Returns a pandas DataFrame.
    """
    emails_data = []

    for filename in os.listdir(MAILS_FOLDER):
        if not filename.lower().endswith(".json"):
            continue  # skip non-JSON files

        filepath = os.path.join(MAILS_FOLDER, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                email = json.load(f)

            headers = email.get("headers", {})
            subject = headers.get("Subject", "").strip()
            sender = headers.get("From", "").strip()
            date_str = headers.get("Date", "").strip()
            body = email.get("body", "")

            # Parse datetime safely
            try:
                dt = datetime.strptime(date_str[:25], "%a, %d %b %Y %H:%M:%S")
                hour = dt.hour
                day_of_week = dt.weekday()
            except Exception:
                hour = -1
                day_of_week = -1

            emails_data.append({
                "subject": subject,
                "sender": sender,
                "hour": hour,
                "day_of_week": day_of_week,
                "body_length": len(body)
            })

        except Exception as e:
            print(f"⚠ Could not parse {filename}: {e}")

    return pd.DataFrame(emails_data)

# Example usage:
if __name__ == "__main__":
    df = extract_features()
    print(df.head())
