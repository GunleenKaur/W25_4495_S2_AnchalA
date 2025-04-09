import pandas as pd
import numpy as np
import re
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import os
import kagglehub

# Download the Enron dataset
path = kagglehub.dataset_download("wcukierski/enron-email-dataset")
print("Path to dataset files:", path)

# Load the dataset
csv_path = os.path.join(path, "emails.csv")
df = pd.read_csv(csv_path)

# Preprocess: Extract email body
def extract_body(message):
    parts = message.split('\n\n', 1)
    return parts[1] if len(parts) > 1 else parts[0]

df['Body'] = df['message'].apply(extract_body)

# Simulate labels
def simulate_label(body):
    spam_keywords = ['win', 'free', 'offer', 'click', 'buy']
    return 'spam' if any(keyword in body.lower() for keyword in spam_keywords) else 'ham'

df['Label'] = df['Body'].apply(simulate_label)
df = df[['Body', 'Label']]

# Sample a subset
df = df.sample(n=1000, random_state=42)

# Clean text
def clean_text(text):
    text = re.sub(r'[^a-zA-Z]', ' ', str(text))
    return text.lower()

df["Body"] = df["Body"].apply(clean_text)

# Feature extraction
vectorizer = TfidfVectorizer(stop_words="english", max_features=3000)
X = vectorizer.fit_transform(df["Body"])
y = np.where(df["Label"] == "spam", 1, 0)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Training samples: {X_train.shape[0]}, Test samples: {X_test.shape[0]}")

# Train Naïve Bayes
nb_model = MultinomialNB()
nb_model.fit(X_train, y_train)
y_pred_nb = nb_model.predict(X_test)
y_prob_nb = nb_model.predict_proba(X_test)[:, 1]  # For ROC-AUC

# Naïve Bayes Metrics
nb_accuracy = accuracy_score(y_test, y_pred_nb)
nb_precision = precision_score(y_test, y_pred_nb)
nb_recall = recall_score(y_test, y_pred_nb)
nb_f1 = f1_score(y_test, y_pred_nb)
nb_roc_auc = roc_auc_score(y_test, y_prob_nb)
nb_confusion = confusion_matrix(y_test, y_pred_nb)
nb_specificity = nb_confusion[0, 0] / (nb_confusion[0, 0] + nb_confusion[0, 1])  # TN / (TN + FP)

print("Naïve Bayes Performance:")
print(f"Accuracy: {nb_accuracy:.4f}")
print(f"Precision: {nb_precision:.4f}")
print(f"Recall: {nb_recall:.4f}")
print(f"F1-Score: {nb_f1:.4f}")
print(f"ROC-AUC: {nb_roc_auc:.4f}")
print(f"Specificity: {nb_specificity:.4f}")
print(f"Confusion Matrix:\n{nb_confusion}")

# Train XGBoost
xgb_model = XGBClassifier(
    max_depth=7,
    learning_rate=0.05,
    n_estimators=200,
    subsample=0.8,
    colsample_bytree=0.8,
    n_jobs=-1
)
xgb_model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
y_pred_xgb = xgb_model.predict(X_test)
y_prob_xgb = xgb_model.predict_proba(X_test)[:, 1]  # For ROC-AUC

# XGBoost Metrics
xgb_accuracy = accuracy_score(y_test, y_pred_xgb)
xgb_precision = precision_score(y_test, y_pred_xgb)
xgb_recall = recall_score(y_test, y_pred_xgb)
xgb_f1 = f1_score(y_test, y_pred_xgb)
xgb_roc_auc = roc_auc_score(y_test, y_prob_xgb)
xgb_confusion = confusion_matrix(y_test, y_pred_xgb)
xgb_specificity = xgb_confusion[0, 0] / (xgb_confusion[0, 0] + xgb_confusion[0, 1])

print("\nXGBoost Performance:")
print(f"Accuracy: {xgb_accuracy:.4f}")
print(f"Precision: {xgb_precision:.4f}")
print(f"Recall: {xgb_recall:.4f}")
print(f"F1-Score: {xgb_f1:.4f}")
print(f"ROC-AUC: {xgb_roc_auc:.4f}")
print(f"Specificity: {xgb_specificity:.4f}")
print(f"Confusion Matrix:\n{xgb_confusion}")

# Save models
os.makedirs("../models", exist_ok=True)
with open("../models/naive_bayes.pkl", "wb") as f:
    pickle.dump(nb_model, f)
with open("../models/xgboost.pkl", "wb") as f:
    pickle.dump(xgb_model, f)
with open("../models/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("\nModels trained and saved successfully!")