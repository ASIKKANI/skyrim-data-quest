# backend/models/phishing_model.py
import json
import os
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

class PhishingModel:
    def __init__(self, model_path="phishing_model.pkl", dataset_csv="phishing_email_dataset.csv"):
        self.model_path = model_path
        self.dataset_csv = dataset_csv
        self.model = None

    def load_json_email(self, json_file):
        """Load email JSON from file and return combined text."""
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        body = data.get("body", "")
        subject = data.get("headers", {}).get("Subject", "")
        from_email = data.get("from", "")
        text = f"{subject} {body} {from_email}"
        return text

    def train_from_csv(self):
        """Train model from CSV dataset and save as PKL."""
        if not os.path.exists(self.dataset_csv):
            print(f"CSV dataset not found at {self.dataset_csv}. Cannot train model.")
            return

        df = pd.read_csv(self.dataset_csv)
        X = df['subject'].fillna('') + " " + df['body'].fillna('') + " " + df['from_email'].fillna('')
        y = df['is_phishing']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(stop_words="english", max_features=5000)),
            ("clf", LogisticRegression(solver="liblinear"))
        ])

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        print("Model trained from CSV. Test set evaluation:")
        print(classification_report(y_test, y_pred))

        with open(self.model_path, "wb") as f:
            pickle.dump(pipeline, f)
        print(f"Model saved as {self.model_path}")
        self.model = pipeline

    def load_model(self):
        """Load existing PKL model, or train if missing."""
        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
            print(f"Model loaded from {self.model_path}")
        else:
            print("Model not found. Attempting to train from CSV dataset...")
            self.train_from_csv()
            if not self.model:
                print("⚠️ ML model not loaded: training failed or CSV missing.")

    def predict(self, email_input):
        """
        Accepts either a file path to JSON or a dictionary of email data.
        Returns phishing prediction and probability.
        """
        if not self.model:
            print("⚠️ ML model not loaded. Using fallback score 0.5")
            return {"is_phishing": 0, "probability": 0.5}

        # Determine if input is dict or file path
        if isinstance(email_input, str):
            text = self.load_json_email(email_input)
        elif isinstance(email_input, dict):
            subject = email_input.get("headers", {}).get("Subject", "")
            body = email_input.get("body", "")
            from_email = email_input.get("from", "")
            text = f"{subject} {body} {from_email}"
        else:
            raise ValueError("Input must be a dict or a JSON file path")

        pred = self.model.predict([text])[0]
        prob = self.model.predict_proba([text])[0][1]  # Probability of phishing
        return {"is_phishing": int(pred), "probability": float(prob)}


# CLI usage for testing
if __name__ == "__main__":
    pm = PhishingModel()
    pm.load_model()

    # Example test file
    test_json = "backend/saved_emails/message-1.json"
    if os.path.exists(test_json):
        result = pm.predict(test_json)
        print("\n===== Prediction Result =====")
        for k, v in result.items():
            print(f"{k}: {v}")
    else:
        print(f"Test file {test_json} not found.")
