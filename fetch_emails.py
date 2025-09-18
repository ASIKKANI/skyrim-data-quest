#!/usr/bin/env python3
"""
fetch_emails.py
---------------
Fetch unread Gmail emails, save them as JSON, run ML prediction,
and generate Gemini NLP explanation directly.
"""

import imaplib
import email
import time
import os
import json
from datetime import datetime
from bs4 import BeautifulSoup

# Import your ML and Gemini modules
from backend.ml.inference import run_model_pipeline
from backend.services.gemini_service import analyze_email

# ----------------------------
# CONFIGURATION
# ----------------------------
EMAIL_ACCOUNT = "radio.heads1709@gmail.com"  # Replace with your Gmail
APP_PASSWORD = "gdjunmbwlmndvezg"            # Replace with App Password
IMAP_HOST = "imap.gmail.com"
SAVE_DIR = "parsed_emails"
os.makedirs(SAVE_DIR, exist_ok=True)

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def clean_html(raw_html: str) -> str:
    """Remove HTML tags and return plain text."""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text()

def extract_body(msg) -> str:
    """Extract plain text or HTML body from email.message.Message object."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type in ["text/plain", "text/html"]:
                try:
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    if content_type == "text/html":
                        body = clean_html(body)
                    return body
                except Exception:
                    continue
    else:
        try:
            body = msg.get_payload(decode=True).decode(errors="ignore")
            return clean_html(body)
        except Exception:
            return ""
    return ""

def sanitize_filename(text: str) -> str:
    """Make text safe for filenames."""
    return "".join(c for c in text if c.isalnum() or c in ("-", "_"))

def save_email_as_json(email_dict: dict) -> str:
    """Save raw email as JSON file in saved_emails/ and return filepath."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    sender = sanitize_filename(email_dict.get("from", "unknown"))
    filename = f"email-{timestamp}-{sender}.json"
    filepath = os.path.join(SAVE_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(email_dict, f, indent=2, ensure_ascii=False)
    return filepath

# ----------------------------
# MAIN FETCH FUNCTION
# ----------------------------
def fetch_and_analyze_emails():
    """Fetch unread emails, save them, run ML + Gemini analysis."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST)
        mail.login(EMAIL_ACCOUNT, APP_PASSWORD)
        mail.select("inbox")
    except Exception as e:
        print(f"❌ Failed to connect to Gmail: {e}")
        return

    status, messages = mail.search(None, "UNSEEN")
    email_ids = messages[0].split()

    if not email_ids:
        print("📭 No new emails found.")
        mail.logout()
        return

    for e_id in email_ids:
        status, data = mail.fetch(e_id, "(RFC822)")
        raw_email_bytes = data[0][1]
        msg = email.message_from_bytes(raw_email_bytes)

        email_dict = {
            "from": msg.get("From", ""),
            "subject": msg.get("Subject", ""),
            "date": msg.get("Date", ""),
            "body": extract_body(msg),
            "headers": dict(msg.items()),
        }

        # Save locally
        json_path = save_email_as_json(email_dict)
        print(f"✅ Saved raw email to {json_path}")

        # Run ML + Rules pipeline
        ml_result = run_model_pipeline(email_dict)
        print(f"📊 ML Result: {ml_result}")

        # Generate Gemini explanation
        gemini_result = analyze_email(
            email_dict["body"],
            rule_score=ml_result["rule_score"],
            ml_score=ml_result["ml_score"],
            final_score=ml_result["final_score"]
        )
        print(f"💬 Gemini Explanation:\n{gemini_result['explanation']}")
        print("-" * 80)

    mail.logout()

# ----------------------------
# RUN SCRIPT PERIODICALLY
# ----------------------------
if __name__ == "__main__":
    while True:
        fetch_and_analyze_emails()
        print("⏳ Waiting 60 seconds for next check...\n")
        time.sleep(60)
