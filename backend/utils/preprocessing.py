import re
import html
from bs4 import BeautifulSoup
from typing import Dict, List

def clean_html(raw_html: str) -> str:
    """Remove HTML tags and return plain text."""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text()

def normalize_text(text: str) -> str:
    """Lowercase, remove extra spaces, decode HTML entities."""
    text = text.lower()
    text = html.unescape(text)       # e.g., &amp; → &
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def tokenize(text: str) -> List[str]:
    """Simple tokenizer: extract word tokens. Can replace with NLTK/Spacy later."""
    return re.findall(r"\b\w+\b", text)

def preprocess_email_body(body: str, subject: str = "") -> Dict[str, any]:
    """
    Preprocess email body (and optional subject) into clean text and tokens.
    
    Parameters:
        body (str): Email body content.
        subject (str, optional): Email subject. Defaults to empty string.
        
    Returns:
        dict: {
            "clean_text": str,  # normalized text
            "tokens": List[str] # tokenized words
        }
    """
    combined = f"{subject} {body}".strip()
    cleaned = clean_html(combined)
    normalized = normalize_text(cleaned)
    tokens = tokenize(normalized)
    return {
        "clean_text": normalized,
        "tokens": tokens
    }
