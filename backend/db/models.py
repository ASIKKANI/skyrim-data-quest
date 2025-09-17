from sqlalchemy import Column, Integer, String, JSON, DateTime
from datetime import datetime
from .database import Base

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, index=True)
    subject = Column(String, nullable=True)
    body = Column(String)
    clean_text = Column(String)
    tokens = Column(JSON)         # tokenized body
    email_metadata = Column(JSON)       # headers, domain, IP, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
