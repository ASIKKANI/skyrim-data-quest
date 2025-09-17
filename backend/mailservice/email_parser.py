from backend.db.database import SessionLocal
from backend.db.models import Email
from backend.utils.preprocessing import preprocess_email_body
from backend.utils.metadata_parser import parse_headers, parse_sender

def parse_email(raw_email: dict) -> dict:
    headers = raw_email.get("headers", {})
    body = raw_email.get("body", "")
    sender = raw_email.get("from", "")

    tokens = preprocess_email_body(body)
    email_metadata = parse_headers(headers)
    email_metadata["sender"] = parse_sender(sender)

    parsed = {
        "tokens": tokens,
        "clean_text": " ".join(tokens),
        "metadata": email_metadata
    }

    return parsed


def store_parsed_email(raw_email: dict):
    db = SessionLocal()
    parsed = parse_email(raw_email)

    email = Email(
        sender=parsed["metadata"]["sender"]["email"],
        subject=parsed["metadata"].get("subject"),
        body=raw_email.get("body"),
        clean_text=parsed["clean_text"],
        tokens=parsed["tokens"],
        email_metadata=parsed["metadata"],
    )

    db.add(email)
    db.commit()
    db.refresh(email)

    return email
