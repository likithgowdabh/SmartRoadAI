import pandas as pd
import sys
import os

# Add autoheal root to path to ensure modules are found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulator.data_simulator import simulator
from core.anomaly import detect_anomaly
from core.health import compute_health
from core.decision import make_decision
from core.explain import generate_reason
from core.actions import get_action, apply_action, machine_state
from alerts.sound import trigger_alert
from db.database import save_to_db

def run_pipeline(manual_anomaly=None):
    """
    Executes the full AutoHeal AI pipeline.
    """
    if manual_anomaly:
        data = simulator.trigger_anomaly(manual_anomaly)
    else:
        data = simulator.generate_data()
        
    data = detect_anomaly(data)
    data = compute_health(data)
    data = make_decision(data)
    data = generate_reason(data)

    # Action engine
    data["action"] = data.apply(get_action, axis=1)
    data["result"] = data["action"].apply(apply_action)

    data = trigger_alert(data)
    save_to_db(data)

    return data, machine_state
