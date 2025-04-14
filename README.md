# Spam Email Detector: Chrome Extension with Python Backend

This project is a browser-based spam email detection system that integrates directly into Gmail using a Chrome extension. It uses machine learning models to classify emails as spam or not spam, powered by a Python FastAPI backend and trained on the Enron dataset.

---

##  Features

- Real-time spam detection in Gmail
- Machine Learning-based classification using Naive Bayes and XGBoost
- Chrome Extension UI for easy interaction
- FastAPI backend with database integration
- Trained on real-world Enron email dataset

---

## System Architecture

```text
Gmail → Chrome Extension → Backend API (FastAPI) → ML Model → Result → UI Display

## Backend (FastAPI)

cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
python -m uvicorn src.Backend:app --reload --port 9005


## Chrome Extension
1.	Go to chrome://extensions
2.	Enable "Developer Mode"
3.	Click "Load unpacked" and select the extension/ folder
4.	Open Gmail – the extension will scan the email content automatically
