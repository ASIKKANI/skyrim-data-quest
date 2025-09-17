import imaplib
import email
import requests
import time
from bs4 import BeautifulSoup

# ----------------------------
# CONFIGURATION
# ----------------------------
EMAIL_ACCOUNT = "radio.heads1709@gmail.com"       # Replace with your Gmail
APP_PASSWORD = "gdjunmbwlmndvezg"      # Replace with the App Password
IMAP_HOST = "imap.gmail.com"
API_URL = "http://127.0.0.1:8000/api/parse_email"  # Your FastAPI parser endpoint

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def clean_html(raw_html: str) -> str:
    """Remove HTML tags and return plain text."""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text()

def extract_body(msg):
    """Extract plain text or HTML body from email.message.Message object."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type in ["text/plain", "text/html"]:
                try:
                    body = part.get_payload(decode=True).decode()
                    if content_type == "text/html":
                        body = clean_html(body)
                    return body
                except:
                    continue
    else:
        body = msg.get_payload(decode=True).decode()
        return clean_html(body)
    return ""

def fetch_and_parse_emails():
    # Connect to Gmail
    mail = imaplib.IMAP4_SSL(IMAP_HOST)
    mail.login(EMAIL_ACCOUNT, APP_PASSWORD)
    mail.select("inbox")

    # Fetch unread emails
    status, messages = mail.search(None, 'UNSEEN')
    email_ids = messages[0].split()

    if not email_ids:
        print("No new emails found.")
        return

    for e_id in email_ids:
        status, data = mail.fetch(e_id, "(RFC822)")
        raw_email_bytes = data[0][1]
        msg = email.message_from_bytes(raw_email_bytes)

        # Build the raw email dict
        raw_email_dict = {
            "from": msg.get("From"),
            "body": extract_body(msg),
            "headers": dict(msg.items())
        }

        # Send to parser API
        try:
            response = requests.post(API_URL, json=raw_email_dict)
            print(f"Email from {raw_email_dict['from']} parsed. API response:")
            print(response.json())
        except Exception as e:
            print(f"Failed to send email to parser API: {e}")

    mail.logout()

# ----------------------------
# RUN SCRIPT PERIODICALLY
# ----------------------------
if __name__ == "__main__":
    while True:
        fetch_and_parse_emails()
        print("Waiting 30 seconds for next check...\n")
        time.sleep(30)  # check for new emails every 60 seconds
