import sqlite3
import pandas as pd
from loaders.episode_loader import get_sqlite_path

conn = sqlite3.connect(get_sqlite_path())

print("=== 1. PERSONA_SCHEDULE_SETTINGS ===")
pss = pd.read_sql_query("""
    SELECT s.*, b.persona_id
    FROM persona_schedule_settings s
    JOIN bots b ON s.bot_id = b.id
""", conn)
print(pss.to_string())

print("\n=== 2. PERSONA_SCHEDULE_DAYS ===")
psd = pd.read_sql_query("""
    SELECT d.id, b.persona_id, d.local_date, d.day_of_week, d.is_active, d.target_windows, d.created_at
    FROM persona_schedule_days d
    JOIN bots b ON d.bot_id = b.id
""", conn)
print(psd.to_string())

print("\n=== 3. PLANNING_ATTEMPTS ===")
pa = pd.read_sql_query("""
    SELECT p.id, b.persona_id, p.local_date, p.status, p.attempt_count, p.error_message, p.created_at
    FROM planning_attempts p
    JOIN bots b ON p.bot_id = b.id
""", conn)
print(pa.to_string())
