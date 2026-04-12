def decide_risk(row):
    anomaly = row["anomaly"]
    temp = row["temp"]
    health = row["health"]
    
    if anomaly == 1 and temp > 75:
        return "HIGH"
    elif health < 70:
        return "MEDIUM"
    else:
        return "LOW"

def estimate_rul(row):
    temp = row["temp"]
    rul = max(1, int((100 - temp) / 2))
    return rul

def calculate_business_impact(row):
    downtime_hours = 6
    cost_per_hour = 25000
    loss = downtime_hours * cost_per_hour
    
    return {
        "downtime_hours": downtime_hours,
        "loss": loss
    }

def recommend_action(row):
    risk = row["risk"]
    if risk == "HIGH":
        return "Inspect immediately"
    elif risk == "MEDIUM":
        return "Schedule maintenance"
    else:
        return "No action required"

def make_decision(df):
    """
    Applies decision logic across the dataframe row.
    """
    df["risk"] = df.apply(decide_risk, axis=1)
    df["rul"] = df.apply(estimate_rul, axis=1)
    
    impact = calculate_business_impact(df.iloc[0])
    df["downtime_hours"] = impact["downtime_hours"]
    df["loss"] = impact["loss"]
    
    df["recommendation"] = df.apply(recommend_action, axis=1)
    
    return df
