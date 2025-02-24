Spam Email Detector

This project is a spam email detection system built using a machine learning model. It includes a Flask-based backend API and a simple frontend to interact with the system.

Features

Detects spam emails using a trained ML model

REST API for classification

Frontend UI for user-friendly email input

Lightweight and easy to deploy

Installation & Setup

Create and Activate Virtual Environment
python -m venv venv     # Create virtual environment
venv\Scripts\activate     # Activate on Windows

Install Flask for Backend API
pip install flask

Install Machine Learning Libraries
pip install scikit-learn pandas numpy

Install Serialization and Model Handling
pip install joblib

Install Chrome Extension Development Dependencies
pip install flask-cors


After installing these, you can run the Flask server:

python app.py


Takes an email text and returns whether it is spam or not

Example Request

{
  "email": "Congratulations! You have won a free lottery. Click here to claim."
}

Example Response

{
  "prediction": "spam"
}

Troubleshooting

1. Virtual Environment Not Found

Ensure you are in the correct directory and run:

python -m venv venv
venv\Scripts\activate  # For Windows
source venv/bin/activate  # For macOS/Linux

2. Scikit-Learn Import Error

If you see an error like No module named 'sklearn.__check_build._check_build', run:

pip install --no-cache-dir --upgrade scikit-learn

3. Flask Server Not Starting

Ensure all dependencies are installed: pip install -r requirements.txt

Run python app.py from the backend folder

Future Improvements

Add email attachments processing

Implement deep learning-based spam detection

Improve UI design
