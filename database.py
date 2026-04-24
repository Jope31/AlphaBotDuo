"""SQLite state management for AlphaBot to handle concurrency."""

import sqlite3
import json
import time

DB_FILE = "alphabot_state.db"


def get_connection():
    return sqlite3.connect(DB_FILE, timeout=10.0)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Existing tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bot_state (
            id INTEGER PRIMARY KEY,
            data TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS execution_lock (
            id INTEGER PRIMARY KEY,
            is_locked INTEGER,
            timestamp REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chart_history (
            id INTEGER PRIMARY KEY,
            data TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vix_cache (
            id INTEGER PRIMARY KEY,
            vix_value REAL,
            timestamp REAL
        )
    """)

    # NEW: 5-Day Historical Chart Archive
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chart_archive (
            date TEXT,
            symphony_id TEXT,
            data TEXT,
            UNIQUE(date, symphony_id)
        )
    """)

    cursor.execute(
        "INSERT OR IGNORE INTO execution_lock (id, is_locked, timestamp) VALUES (1, 0, 0)"
    )
    cursor.execute("INSERT OR IGNORE INTO bot_state (id, data) VALUES (1, '{}')")
    cursor.execute("INSERT OR IGNORE INTO chart_history (id, data) VALUES (1, '{}')")
    cursor.execute("INSERT OR IGNORE INTO vix_cache (id, vix_value, timestamp) VALUES (1, 20.0, 0)")

    conn.commit()
    conn.close()


# --- Lock Management ---
def acquire_lock():
    conn = get_connection()
    cursor = conn.cursor()
    current_time = time.time()

    cursor.execute("SELECT is_locked, timestamp FROM execution_lock WHERE id = 1")
    row = cursor.fetchone()

    if row[0] == 1 and (current_time - row[1] < 60):
        conn.close()
        return False

    cursor.execute(
        "UPDATE execution_lock SET is_locked = 1, timestamp = ? WHERE id = 1", (current_time,)
    )
    conn.commit()
    conn.close()
    return True


def release_lock():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE execution_lock SET is_locked = 0 WHERE id = 1")
    conn.commit()
    conn.close()


# --- State Management ---
def load_state():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM bot_state WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return json.loads(row[0]) if row else {}


def save_state(state_dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE bot_state SET data = ? WHERE id = 1", (json.dumps(state_dict),))
    conn.commit()
    conn.close()


# --- Intraday Chart History Management ---
def load_chart_history():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM chart_history WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return json.loads(row[0]) if row else {}


def save_chart_history(chart_dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE chart_history SET data = ? WHERE id = 1", (json.dumps(chart_dict),))
    conn.commit()
    conn.close()


# --- Historical Archive Management (NEW) ---
def save_chart_archive(date_str, symphony_id, data):
    """Saves a symphony's completed intraday chart data into the permanent archive."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO chart_archive (date, symphony_id, data)
        VALUES (?, ?, ?)
    """,
        (date_str, symphony_id, json.dumps(data)),
    )
    conn.commit()
    conn.close()


def get_rolling_5day_chart(current_date_str):
    """Retrieves the last 5 trading days of minute-by-minute data for the Autotuner."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get the 5 most recent distinct dates
    cursor.execute("SELECT DISTINCT date FROM chart_archive ORDER BY date DESC LIMIT 5")
    dates = [row[0] for row in cursor.fetchall()]

    if not dates:
        conn.close()
        return {}

    # Get all records for those dates
    placeholders = ",".join("?" * len(dates))
    cursor.execute(
        f"SELECT date, symphony_id, data FROM chart_archive WHERE date IN ({placeholders})", dates
    )

    history_5d = {}
    for row in cursor.fetchall():
        date, sym_id, data_json = row[0], row[1], row[2]
        if sym_id not in history_5d:
            history_5d[sym_id] = {}
        history_5d[sym_id][date] = json.loads(data_json)

    conn.close()
    return history_5d


# --- VIX Cache Management ---
def get_vix_cache():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT vix_value, timestamp FROM vix_cache WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return {"vix_value": row[0], "timestamp": row[1]} if row else None


def set_vix_cache(vix_value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE vix_cache SET vix_value = ?, timestamp = ? WHERE id = 1", (vix_value, time.time())
    )
    conn.commit()
    conn.close()


# Initialize tables on import
init_db()
