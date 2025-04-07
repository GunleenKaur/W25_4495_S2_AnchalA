import pickle
import re
import os

# Load models safely
model_path = "../models/" 
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model directory {model_path} not found!")

try:
    with open(f"{model_path}/naive_bayes.pkl", "rb") as f:
        nb_model = pickle.load(f)
    with open(f"{model_path}/xgboost.pkl", "rb") as f:
        xgb_model = pickle.load(f)
    with open(f"{model_path}/vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
except (FileNotFoundError, pickle.UnpicklingError) as e:
    raise RuntimeError(f"Error loading model files: {e}")

def clean_text(text):
    """Cleans email text by removing non-alphabetic characters and converting to lowercase."""
    text = re.sub(r'[^a-zA-Z]', ' ', str(text))
    return text.lower()

def classify_mail(text, model="naive_bayes"):
    """Classifies an email as spam (1) or not spam (0)."""
    cleaned_text = clean_text(text)
    vectorized_text = vectorizer.transform([cleaned_text])

    if model == "naive_bayes":
        return nb_model.predict(vectorized_text)[0]
    elif model == "xgboost":
        return xgb_model.predict(vectorized_text)[0]
    else:
        raise ValueError("Invalid model selected! Choose 'naive_bayes' or 'xgboost'.")

if __name__ == "__main__":
    sample_email = "Congratulations! You've won a free iPhone! Click here to claim."
    print(f"Prediction (Naïve Bayes): {classify_mail(sample_email, 'naive_bayes')}")
    print(f"Prediction (XGBoost): {classify_mail(sample_email, 'xgboost')}")
