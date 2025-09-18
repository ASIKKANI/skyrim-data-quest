import os
import joblib
from sklearn.ensemble import IsolationForest

def detect_anomalies(df, save_model=True, model_path="../models/anomaly_model.pkl"):
    """
    Detects anomalies in email data using Isolation Forest on 'hour' and 'day_of_week'.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing at least 'hour' and 'day_of_week' columns
        save_model (bool): Whether to save the trained model
        model_path (str): Path to save the trained Isolation Forest model
    
    Returns:
        pd.DataFrame: Original DataFrame with two new columns:
            - 'anomaly_score': raw predictions from Isolation Forest (-1 = anomaly, 1 = normal)
            - 'is_anomaly': boolean column, True if anomaly
    """
    features = ['hour', 'day_of_week']
    
    # Initialize Isolation Forest
    clf = IsolationForest(contamination=0.05, random_state=42)
    df['anomaly_score'] = clf.fit_predict(df[features])
    df['is_anomaly'] = df['anomaly_score'] == -1
    
    # Save model if requested
    if save_model:
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(clf, model_path)
    
    return df


if __name__ == "__main__":
    from backend.scripts.extract_features import extract_features  # fixed the import
    import pandas as pd

    # Load features
    df = extract_features()

    # Detect anomalies
    df = detect_anomalies(df)

    # Print only anomalous emails
    print(df[df['is_anomaly']])
