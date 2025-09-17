import tldextract
from email.utils import parseaddr
from datetime import datetime

def extract_sender(email_address: str) -> dict:
    """Split full sender into name + domain details."""
    name, addr = parseaddr(email_address)
    domain_info = tldextract.extract(addr)
    return {
        "name": name,
        "email": addr,
        "domain": domain_info.domain + "." + domain_info.suffix,
        "subdomain": domain_info.subdomain
    }

def parse_metadata(raw_meta: dict) -> dict:
    """
    Normalize raw metadata into standard format.
    Expected raw_meta keys: { 'sender', 'received_time', 'ip', ... }
    """
    sender_info = extract_sender(raw_meta.get("sender", ""))
    
    parsed = {
        "sender_name": sender_info["name"],
        "sender_email": sender_info["email"],
        "sender_domain": sender_info["domain"],
        "received_time": raw_meta.get("received_time", datetime.utcnow().isoformat()),
        "ip": raw_meta.get("ip", None),
        "headers": raw_meta.get("headers", {})
    }
    return parsed

    # backend/utils/metadata_parser.py

def parse_headers(headers: dict) -> dict:
    """
    Extract relevant metadata from email headers.
    Example: Subject, Date, Received IP, etc.
    """
    metadata = {
        "subject": headers.get("Subject"),
        "date": headers.get("Date"),
        "received": headers.get("Received"),
        # Add more fields if needed
    }
    return metadata

def parse_sender(sender_str: str) -> dict:
    """
    Parse sender info: email address, name, domain
    """
    import re
    match = re.match(r"(.*)<(.*)>", sender_str)
    if match:
        name, email = match.groups()
    else:
        name, email = None, sender_str
    domain = email.split("@")[-1] if "@" in email else None
    return {"name": name, "email": email, "domain": domain}
