# backend/routes/detect.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict

from backend.mailservice.email_parser import parse_email
from backend.db.database import SessionLocal
from backend.db.models import Email
from backend.ml.inference import run_model_pipeline
from backend.services.gemini_service import analyze_email

router = APIRouter()

# -------------------- DB Session Dependency --------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------- Email Parse & Analyze --------------------
@router.post("/parse_email")
def parse_and_store_email(raw_email: Dict, db: Session = Depends(get_db)):
    """
    Parse raw email JSON, run ML+rules for risk scoring,
    generate explanation via Gemini, and store in DB.
    """
    try:
        # 1. Parse raw email
        parsed = parse_email(raw_email)

        # 2. Run ML + Rules pipeline
        model_result = run_model_pipeline(parsed)  
        # model_result = {"ml_score": float, "rule_score": float, "final_score": float, "prediction": str}

        # 3. Prepare email text for Gemini explanation
        email_text_for_gemini = (
            parsed.get("clean_text") or
            raw_email.get("body", "") or
            parsed.get("metadata", {}).get("subject", "")
        )

        # 4. Generate explanation using Gemini API
        gemini_result = analyze_email(email_text_for_gemini)
        explanation = gemini_result.get("explanation", "Explanation not available.")
        
        # 5. Create DB record
        email_record = Email(
            sender=parsed.get("metadata", {}).get("sender", {}).get("email", ""),
            subject=parsed.get("metadata", {}).get("subject", ""),
            body=raw_email.get("body", ""),
            clean_text=parsed.get("clean_text", ""),
            tokens=parsed.get("tokens", []),
            email_metadata=parsed.get("metadata", {}),

            # Risk info
            ml_score=model_result.get("ml_score", 0.0),
            rule_score=model_result.get("rule_score", 0.0),
            final_score=model_result.get("final_score", 0.0),
            prediction=model_result.get("prediction", "Unknown"),
            risk_explanation=explanation,
        )

        # 6. Save to DB
        db.add(email_record)
        db.commit()
        db.refresh(email_record)

        # 7. Return result
        return {
            "status": "success",
            "email_id": email_record.id,
            "parsed": parsed,
            "model_result": model_result,
            "explanation": explanation,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to parse/analyze email: {e}")
