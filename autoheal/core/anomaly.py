import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.05, random_state=42)
        # Train on "normal" data representing the healthy bounds
        np.random.seed(42)
        normal_temp = np.random.uniform(60, 90, 500)
        normal_vib = np.random.uniform(0.2, 1.0, 500)
        normal_volt = np.random.uniform(210, 270, 500)
        
        train_data = pd.DataFrame({
            "temp": normal_temp,
            "vibration": normal_vib,
            "voltage": normal_volt
        })
        self.model.fit(train_data)

    def detect(self, df):
        """
        Takes a single row DataFrame and returns it with an 'anomaly' column
        """
        features = df[["temp", "vibration", "voltage"]]
        # predict returns 1 for inliers, -1 for outliers
        prediction = self.model.predict(features)
        
        # We need output: anomaly = 1 (if outlier) or 0 (if normal)
        anomaly = 1 if prediction[0] == -1 else 0
        df["anomaly"] = anomaly
        return df

detector = AnomalyDetector()

def detect_anomaly(df):
    return detector.detect(df)
