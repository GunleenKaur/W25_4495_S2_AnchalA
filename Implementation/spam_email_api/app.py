from flask import Flask, request, jsonify
import joblib
import traceback
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend interaction

try:
    # Load trained model (ensure the model file exists)
    model = joblib.load('spam_model.pkl')
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None  # Handle missing model scenario

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model not loaded. Check logs for details.'}), 500
    
    try:
        data = request.get_json()
        email_text = data.get("email_text", "").strip()
        
        if not email_text:
            return jsonify({'error': 'No email text provided.'}), 400
        
        prediction = model.predict([email_text])[0]
        return jsonify({'spam': bool(prediction)})
    
    except Exception as e:
        print(f"Error during prediction: {traceback.format_exc()}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
