from flask import Flask, request, jsonify
import joblib
from xgboost import XGBClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

app = Flask(__name__)

# Load vectorizer and model
vectorizer = joblib.load("vectorizer.pkl")
model = joblib.load("xgb_model.pkl")

@app.route('/api/check_spam', methods=['POST'])
def check_spam():
    data = request.get_json()
    text = data['text']
    vector = vectorizer.transform([text])
    prediction = model.predict(vector)
    return jsonify({'is_spam': bool(prediction[0])})

if __name__ == '__main__':
    app.run(debug=True)
