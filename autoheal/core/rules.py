def evaluate_rules(df):
    """
    Evaluates machine rules against data limits.
    Returns primary action token: 'shutdown', 'cooling', 'reduce_load', or 'none'
    Priority: shutdown > limit rules
    """
    temp = df["temp"].iloc[0]
    voltage = df["voltage"].iloc[0]
    vib = df["vibration"].iloc[0]
    
    if voltage > 250:
        return "shutdown"
    elif temp > 80:
        return "cooling"
    elif vib > 0.7:
        return "reduce_load"
    
    return "none"
