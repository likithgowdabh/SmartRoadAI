def generate_reason(df):
    """
    Returns human-readable explanation of why a condition exists.
    """
    temp = df["temp"].iloc[0]
    voltage = df["voltage"].iloc[0]
    vib = df["vibration"].iloc[0]
    anomaly = df["anomaly"].iloc[0]
    
    reasons = []
    if voltage > 250:
        reasons.append("Voltage spike")
    if temp > 80:
        reasons.append("Overheating")
    if vib > 0.7:
        reasons.append("High vibration detected")
        
    if not reasons and anomaly == 1:
        reasons.append("Unidentified multi-variate anomaly")
        
    if not reasons:
        reasons.append("Normal")
        
    df["reason"] = " | ".join(reasons)
    return df
