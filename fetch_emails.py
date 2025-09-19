#!/usr/bin/env python3
"""
fetch_emails.py
---------------
Fetch unread Gmail emails, save them as JSON, run ML prediction,
and generate Gemini NLP explanation directly.
Robust and fault-tolerant for hackathon scenarios.
"""

import imaplib
import email
import time
import os
import json
from datetime import datetime
from bs4 import BeautifulSoup
from email.header import decode_header

# ML + Gemini imports
from backend.ml.inference import run_model_pipeline
from backend.services.gemini_service import analyze_email

# ----------------------------
# CONFIGURATION
# ----------------------------
EMAIL_ACCOUNT = "radio.heads1709@gmail.com"  # Replace with your Gmail
APP_PASSWORD = "gdjunmbwlmndvezg"            # Replace with App Password
IMAP_HOST = "imap.gmail.com"

SAVE_DIR = "saved_emails"
PARSED_DIR = "parsed_emails"
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(PARSED_DIR, exist_ok=True)

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def clean_html(raw_html: str) -> str:
    """Remove HTML tags and return plain text."""
    return BeautifulSoup(raw_html, "html.parser").get_text()

def extract_body(msg) -> str:
    """Extract plain text or HTML body from email.message.Message object."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type in ["text/plain", "text/html"]:
                try:
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    return clean_html(body) if content_type == "text/html" else body
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
    """Save raw email as JSON file and return the filepath."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    sender = sanitize_filename(email_dict.get("from", "unknown"))
    filename = f"email-{timestamp}-{sender}.json"
    filepath = os.path.join(SAVE_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(email_dict, f, indent=2, ensure_ascii=False)
    return filepath

def save_parsed_result(parsed_dict: dict) -> str:
    """Save ML + Gemini parsed results."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"parsed-{timestamp}-{sanitize_filename(parsed_dict.get('from','unknown'))}.json"
    filepath = os.path.join(PARSED_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(parsed_dict, f, ensure_ascii=False, indent=2)
    return filepath

def decode_mime_words(s):
    """Decode MIME encoded words to human readable string."""
    if not s:
        return ""
    decoded_fragments = []
    for frag, encoding in decode_header(s):
        if isinstance(frag, bytes):
            try:
                decoded_fragments.append(frag.decode(encoding or "utf-8", errors="replace"))
            except Exception:
                decoded_fragments.append(frag.decode("utf-8", errors="replace"))
        else:
            decoded_fragments.append(frag)
    return ''.join(decoded_fragments)

# ----------------------------
# MAIN FETCH FUNCTION
# ----------------------------
def fetch_and_analyze_emails():
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
        try:
            status, data = mail.fetch(e_id, "(RFC822)")
            raw_email_bytes = data[0][1]
            msg = email.message_from_bytes(raw_email_bytes)

            email_dict = {
                "from": decode_mime_words(msg.get("From", "")),
                "subject": decode_mime_words(msg.get("Subject", "")),
                "date": msg.get("Date", ""),
                "body": extract_body(msg),
                "headers": dict(msg.items()),
            }

            # Save raw email
            json_path = save_email_as_json(email_dict)
            print(f"✅ Saved raw email to {json_path}")

            # Run ML pipeline
            ml_result = run_model_pipeline(email_dict)
            print(f"📊 ML Result: {ml_result}")

            # Multiply all scores by 100 and round to 2 decimals
            for key in ["ml_score", "rule_score", "final_score", "risk_score"]:
                if key in ml_result and isinstance(ml_result[key], (int, float)):
                    ml_result[key] = round(ml_result[key] * 100, 2)

            # Pass the scaled scores to Gemini
            try:
                gemini_result = analyze_email(
                    email_dict["body"],
                    rule_score=ml_result.get("rule_score", 0),
                    ml_score=ml_result.get("ml_score", 0),
                    final_score=ml_result.get("final_score", 0)
                )
            except Exception as gem_e:
                print(f"⚠️ Failed to generate Gemini explanation: {gem_e}")
                gemini_result = {"explanation": "Not available due to error."}

            # Save parsed result
            parsed_dict = {
                "email": {
                    "from": email_dict.get("from"),
                    "subject": email_dict.get("subject"),
                    "date": email_dict.get("date"),
                    "body": email_dict.get("body"),
                    "headers": email_dict.get("headers")
                },
                "ml_result": ml_result,
                "gemini_result": gemini_result
            }
            parsed_path = save_parsed_result(parsed_dict)
            print(f"✅ Saved parsed result to {parsed_path}")
            print("-" * 80)

        except Exception as e:
            print(f"⚠️ Failed to process email ID {e_id}: {e}")

    mail.logout()

# ----------------------------
# RUN SCRIPT PERIODICALLY
# ----------------------------
if __name__ == "__main__":
    while True:
        fetch_and_analyze_emails()
        print("⏳ Waiting 60 seconds for next check...\n")
        time.sleep(30)
