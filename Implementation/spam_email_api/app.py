from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)

# Load trained model (ensure the model file exists)
model = joblib.load('spam_model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    email_text = data.get("email_text", "")
    prediction = model.predict([email_text])[0]
    return jsonify({'spam': bool(prediction)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
