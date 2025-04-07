import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime 
import re
from bs4 import BeautifulSoup
import numpy as np
from predict import classify_mail

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

logger.info("Adding CORS middleware...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mail.google.com", "chrome-extension://fgjhigfohfhifhfcapjenpefnnhlfmgm"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
logger.info("CORS middleware added.")

DATABASE_URL = "postgresql://postgres:mysecretpassword@localhost:5432/email_classification_db"
logger.info(f"Connecting to database at {DATABASE_URL}...")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
logger.info("Database connection established.")

class Email(Base):
    __tablename__ = "email_classification"
    logger.info("Defining Email table schema...")
    id = Column(Integer, primary_key=True, index=True)
    email_text = Column(Text)
    model_used = Column(Text)
    is_spam = Column(Boolean)
    logger.info("Email table schema defined.")

class ProcessedEmail(Base):
    __tablename__ = "processed_email"
    logger.info("Defining ProcessedEmail table schema...")
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String, unique=True)
    processed_at = Column(DateTime)
    logger.info("ProcessedEmail table schema defined.")

Base.metadata.create_all(bind=engine)
logger.info("Database tables created.")

class EmailInput(BaseModel):
    text: str
    model: str

class ProcessRequest(BaseModel):
    emailId: str
    emailText: str

@app.post("/classify")
async def classify_email(input: EmailInput):
    logger.info("Received classification request.")
    session = SessionLocal()
    try:
        logger.info("Extracting plain text from input...")
        plain_text = BeautifulSoup(input.text, "html.parser").get_text()
        plain_text = re.sub(r'[^\x20-\x7E\n\r\t]', '', plain_text)
        plain_text = re.sub(r'\s+', ' ', plain_text)
        plain_text = plain_text.strip()
        logger.info("Checking for spam...")
        # is_spam = "spam" in plain_text.lower()
        is_spam=int(classify_mail(plain_text))
        email_entry = Email(
            email_text=plain_text,
            model_used=re.sub(r'<[^>]*>', '', input.model),
            is_spam=is_spam
        )
        logger.info("Storing email entry in database...")
        session.add(email_entry)
        session.commit()
        logger.info("Email classified and stored.")
        return {"email": plain_text, "model": input.model, "spam": is_spam}
    except Exception as e:
        session.rollback()
        logger.error(f"Error in classify_email: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        logger.info("Closing database session.")
        session.close()

@app.post("/emails/process")
async def process_email(request: ProcessRequest):
    logger.info("Received email processing request.")
    session = SessionLocal()
    try:
        logger.info("Checking if email is already processed...")
        existing_email = session.query(ProcessedEmail).filter_by(email_id=request.emailId).first()
        if existing_email:
            logger.info("Email already processed.")
            return {"status": "processed"}

        logger.info("Storing new processed email entry...")
        new_email = ProcessedEmail(
            email_id=request.emailId,
            processed_at=datetime.now()
        )
        session.add(new_email)
        session.commit()
        logger.info("Email processing completed.")
        return {"status": "stored"}
    except IntegrityError:
        session.rollback()
        logger.warning("Email already processed (Integrity Error).")
        return {"status": "already processed"}
    finally:
        logger.info("Closing database session.")
        session.close()

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server on port 9005")
    uvicorn.run("__main__:app", host="0.0.0.0", port=9005, reload=True)
