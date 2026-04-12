def compute_health(df):
    """
    Computes the health score for a given dataframe row.
    Formula: health = 100 - (temp*0.3 + vibration*30 + anomaly*40)
    Clamp: 0–100
    """
    temp = df["temp"].iloc[0]
    vib = df["vibration"].iloc[0]
    anomaly = df["anomaly"].iloc[0]
    
    health_score = 100 - (temp * 0.3 + vib * 30 + anomaly * 40)
    
    # Clamp to 0-100
    health_score = max(0, min(100, health_score))
    
    df["health"] = health_score
    return df
