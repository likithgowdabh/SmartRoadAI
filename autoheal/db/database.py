import sqlite3
import pandas as pd
import os

DB_PATH = "d:/codeclash/autoheal/data/autoheal.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            machine_id TEXT,
            health REAL,
            risk TEXT,
            action TEXT,
            reason TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(df):
    """
    Saves the latest row to the database.
    Required fields: timestamp, machine_id, health, risk, action_str, reason
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = df["timestamp"].iloc[0]
    machine_id = df["machine_id"].iloc[0]
    health = df["health"].iloc[0]
    risk = df["risk"].iloc[0]
    action = df["result"].iloc[0] # The string result of the action
    reason = df["reason"].iloc[0]
    
    cursor.execute('''
        INSERT INTO logs (timestamp, machine_id, health, risk, action, reason)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (timestamp, machine_id, health, risk, action, reason))
    
    conn.commit()
    conn.close()

def get_history(limit=10):
    conn = sqlite3.connect(DB_PATH)
    df_history = pd.read_sql_query(f"SELECT timestamp, health, risk, action FROM logs ORDER BY id DESC LIMIT {limit}", conn)
    conn.close()
    return df_history

# Initialize DB on import
init_db()
