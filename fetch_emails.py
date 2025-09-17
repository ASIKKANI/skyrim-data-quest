#!/usr/bin/env python3
"""
fetch_emails.py
---------------
Fetch unread Gmail emails, save them as JSON, and send them to FastAPI parser.
"""

import imaplib
import email
import requests
import time
import os
import json
from datetime import datetime
from bs4 import BeautifulSoup

# ----------------------------
# CONFIGURATION
# ----------------------------
EMAIL_ACCOUNT = "radio.heads1709@gmail.com"     # Replace with your Gmail
APP_PASSWORD = "gdjunmbwlmndvezg"               # Replace with App Password
IMAP_HOST = "imap.gmail.com"
API_URL = "http://127.0.0.1:8000/api/parse_email"  # FastAPI parser endpoint

SAVE_DIR = "saved_emails"
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


def save_email_as_json(email_dict: dict):
    """Save raw email as JSON file in saved_emails/."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    sender = sanitize_filename(email_dict.get("from", "unknown"))
    filename = f"email-{timestamp}-{sender}.json"
    filepath = os.path.join(SAVE_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(email_dict, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved raw email to {filepath}")


def fetch_and_parse_emails():
    """Fetch unread emails, save them, and send to parser API."""
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

        # Build raw email dict
        raw_email_dict = {
            "from": msg.get("From", ""),
            "subject": msg.get("Subject", ""),
            "date": msg.get("Date", ""),
            "body": extract_body(msg),
            "headers": dict(msg.items()),
        }

        # 1. Save locally as JSON
        save_email_as_json(raw_email_dict)

        # 2. Send to parser API
        try:
            response = requests.post(API_URL, json=raw_email_dict, timeout=10)
            print(f"📩 Email from {raw_email_dict['from']} parsed. API response:")
            print(response.json())
        except Exception as e:
            print(f"❌ Failed to send email to parser API: {e}")

    mail.logout()


# ----------------------------
# RUN SCRIPT PERIODICALLY
# ----------------------------
if __name__ == "__main__":
    while True:
        fetch_and_parse_emails()
        print("⏳ Waiting 30 seconds for next check...\n")
        time.sleep(30)
