import pandas as pd
import random
from datetime import datetime

class DataSimulator:
    def __init__(self):
        self.machine_id = "M-101"

    def generate_data(self):
        # Specific ranges defined
        # temp: 60-90, vibration: 0.2-1.0, voltage: 210-270
        data = {
            "timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            "machine_id": [self.machine_id],
            "temp": [round(random.uniform(60, 90), 2)],
            "vibration": [round(random.uniform(0.2, 1.0), 3)],
            "voltage": [round(random.uniform(210, 270), 1)]
        }
        return pd.DataFrame(data)

    def trigger_anomaly(self, anomaly_type):
        """Forces an anomaly for demonstration purposes."""
        data = self.generate_data()
        if anomaly_type == "Overheating":
            data.loc[0, "temp"] = round(random.uniform(91, 105), 2)
        elif anomaly_type == "High Vibration":
            data.loc[0, "vibration"] = round(random.uniform(1.1, 2.0), 3)
        elif anomaly_type == "Voltage Spike":
            data.loc[0, "voltage"] = round(random.uniform(271, 300), 1)
        return data

# Singleton-like instance for easy import
simulator = DataSimulator()

def generate_data():
    return simulator.generate_data()
