import imaplib
import email
from email.header import decode_header
import json
import requests

# --- CONFIGURE ---
EMAIL_ADDRESS = "radio.heads1709@gmail.com"
APP_PASSWORD = "gdjunmbwlmndvezg"  # Use Google App Password if 2FA is on
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

BACKEND_API = "http://127.0.0.1:8000/api/parse_email"  # Your FastAPI endpoint

# --- CONNECT TO GMAIL ---
def connect_to_gmail():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL_ADDRESS, APP_PASSWORD)
    return mail

# --- FETCH EMAILS ---
def fetch_unread_emails(mail):
    mail.select("inbox")  # You can also fetch from a specific label
    status, messages = mail.search(None, 'UNSEEN')  # Fetch unread emails
    email_ids = messages[0].split()
    return email_ids

# --- PARSE EMAIL CONTENT ---
def parse_email_message(msg):
    # Extract headers
    headers = {}
    for header in ["Subject", "From", "Date", "Received"]:
        value = msg.get(header, "")
        if value:
            if header == "Subject":
                decoded, encoding = decode_header(value)[0]
                if isinstance(decoded, bytes):
                    decoded = decoded.decode(encoding or "utf-8")
                headers[header] = decoded
            else:
                headers[header] = value

    # Extract body (plain text or HTML)
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type in ["text/plain", "text/html"] and "attachment" not in content_disposition:
                body_bytes = part.get_payload(decode=True)
                if body_bytes:
                    body += body_bytes.decode(part.get_content_charset() or "utf-8")
    else:
        body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8")

    sender = msg.get("From", "")

    return {
        "from": sender,
        "body": body,
        "headers": headers
    }

# --- SEND TO BACKEND ---
def send_to_backend(email_data):
    response = requests.post(BACKEND_API, json=email_data)
    if response.status_code == 200:
        print("Email stored successfully:", response.json())
    else:
        print("Failed to store email:", response.text)

# --- MAIN ---
def main():
    mail = connect_to_gmail()
    email_ids = fetch_unread_emails(mail)
    print(f"Found {len(email_ids)} unread emails.")

    for eid in email_ids:
        status, data = mail.fetch(eid, "(RFC822)")
        raw_email = email.message_from_bytes(data[0][1])
        parsed_email = parse_email_message(raw_email)
        send_to_backend(parsed_email)

    mail.logout()

if __name__ == "__main__":
    main()
