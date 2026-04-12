from core.rules import evaluate_rules

# Shared global state
machine_state = {
    "status": "RUNNING",
    "cooling": False,
    "load": 100
}

def get_action_string(action_token):
    if action_token == "cooling": return "Cooling activated"
    if action_token == "shutdown": return "Machine shutdown"
    if action_token == "reduce_load": return "Load reduced"
    return "None"

def get_action(row):
    return evaluate_rules(row.to_frame().T)

def apply_action(action_token):
    global machine_state
    
    if action_token == "shutdown":
        machine_state["status"] = "OFF"
    elif action_token == "cooling":
        machine_state["cooling"] = True
    elif action_token == "reduce_load":
        machine_state["load"] = max(0, machine_state["load"] - 20)
    elif action_token == "none":
        # Reset if everything normal (optional)
        machine_state["cooling"] = False
        machine_state["status"] = "RUNNING"
        if machine_state["load"] < 100:
            machine_state["load"] = min(100, machine_state["load"] + 10)
            
    return get_action_string(action_token)
