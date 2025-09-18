# SKYRIM: Email Phishing Detection & NLP Explainer

A full-stack project to fetch Gmail emails, detect phishing attempts using ML, and provide NLP-based explanations with Gemini AI.

---

## Features

- 📧 **Fetch unread emails from Gmail via IMAP**  
  - Connects to Gmail using the IMAP protocol.  
  - Retrieves unread emails including sender, subject, body, attachments, and timestamp.  
  - **Workflow:** Connect → Search → Retrieve → Process.

- 📝 **Save fetched emails as structured JSON files**  
  - Converts emails into structured JSON format for easy storage and further analysis.  
  - Stored in the `saved_emails/` folder.  
  - **Workflow:** Parse email → Convert to dictionary → Save JSON.

- 🛡️ **Detect phishing emails using a trained Machine Learning model**  
  - Custom ML model predicts whether an email is phishing or safe.  
  - Features include sender info, keywords, links, and common phishing patterns.  
  - **Workflow:** Extract features → Predict phishing probability → Save result in JSON.

- 🤖 **Generate explanations and insights from emails using Gemini NLP**  
  - Uses Gemini AI to provide human-readable explanations of suspicious content.  
  - Helps users understand why an email might be phishing.  
  - **Workflow:** Send email content to Gemini → Receive explanation → Store in JSON.

- ⚡ **Expose API endpoints via FastAPI for automation and integration**  
  - Provides endpoints to interact with emails and predictions.  
  - Users can:
    - List all fetched emails.  
    - Get details of a specific email.  
    - Send new email content for phishing detection & NLP explanation.  
  - **Workflow:** Start FastAPI → Receive request → Query JSON or run prediction → Return JSON.

- 🐳 **Dockerized for easy deployment**  
  - Entire system runs in Docker containers for consistent environments.  
  - Simplifies setup by including all dependencies and scripts.  
  - **Workflow:** Dockerfile → Build container → Run fetcher + FastAPI server.

---

## Workflow Overview

1. **Initialization**  
   - Load environment variables (Gmail credentials, API keys).  
   - Start Docker container or run Python scripts locally.  

2. **Email Fetching**  
   - Connect to Gmail via IMAP.  
   - Fetch unread emails.  

3. **Email Processing**  
   - Parse emails and convert to JSON.  
   - Extract features for ML detection.  

4. **Phishing Detection**  
   - ML model predicts phishing probability.  
   - Results are appended to JSON files.  

5. **NLP Explanation**  
   - Gemini AI generates explanations for email content.  
   - Explanations are stored alongside predictions.  

6. **API Exposure**  
   - FastAPI provides endpoints for:
     - Fetching email data.  
     - Real-time phishing analysis.  

7. **Storage & Logging**  
   - All email data, predictions, and explanations are saved locally for records.

---

## Tech Stack

- **Backend:** Python 3.10+  
- **Framework:** FastAPI  
- **Email Handling:** IMAP (`imaplib`, `email`)  
- **ML & NLP:** Custom phishing model + Gemini NLP  
- **Storage:** JSON files  
- **Containerization:** Docker & Docker Compose  
- **Other Libraries:** BeautifulSoup, Requests, Pydantic, Uvicorn  

---

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/ASIKKANI/skyrim-email-detection.git
cd skyrim-email-detection
