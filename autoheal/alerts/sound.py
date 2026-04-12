def trigger_alert(df):
    """
    Returns an alert level and an optional ui component trigger.
    LOW -> no alert
    MEDIUM -> warning
    HIGH -> UI alert
    CRITICAL -> RED screen + sound
    """
    risk = df["risk"].iloc[0]
    action = df["action"].iloc[0] # Action token
    
    # We define CRITICAL mapping: if we are shutting down or extremely risky.
    alert_level = risk
    if action == "shutdown" or (risk == "HIGH" and df["temp"].iloc[0] > 90):
        alert_level = "CRITICAL"
        
    df["alert_level"] = alert_level
    return df
