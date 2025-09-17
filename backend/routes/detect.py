from fastapi import APIRouter, HTTPException
from backend.mailservice.email_parser import parse_email
from backend.db.database import SessionLocal
from backend.db.models import Email

router = APIRouter()

@router.post("/parse_email")
def parse_and_store_email(raw_email: dict):
    """
    Accepts a raw email JSON, parses it, stores it in the DB, and returns the parsed result.
    """
    db = SessionLocal()
    try:
        # Parse the raw email
        parsed = parse_email(raw_email)

        # Create Email record
        email = Email(
            sender=parsed["metadata"]["sender"]["email"],
            subject=parsed["metadata"].get("subject"),
            body=raw_email.get("body"),
            clean_text=parsed["clean_text"],
            tokens=parsed["tokens"],
            email_metadata=parsed["metadata"],  # Make sure this matches your model
        )

        # Add and commit to DB
        db.add(email)
        db.commit()
        db.refresh(email)

        return {
            "status": "success",
            "email_id": email.id,
            "parsed": parsed
        }

    except Exception as e:
        db.rollback()  # Undo any partial DB changes
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()  # Ensure DB session always closes
