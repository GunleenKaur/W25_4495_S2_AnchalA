import joblib
from flask import Flask, request, jsonify
from pathlib import Path

app = Flask(__name__)

# Correct path to spam_model.pkl
model_path = Path(__file__).parent.parent / "spam_model.pkl"

# Load the spam detection model using joblib
model = joblib.load(model_path)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    email_text = data.get('subject', '') + " " + data.get('snippet', '')

    # Make prediction
    prediction = model.predict([email_text])[0]
    
    return jsonify({'is_spam': bool(prediction)})

if __name__ == '__main__':
    app.run(debug=True)
