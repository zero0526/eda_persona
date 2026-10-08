import sqlite3
import json
import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('data/persona-runner.sqlite')

query = """
SELECT b.persona_id, aw.id, aw.local_date, aw.start_at, aw.end_at, aw.max_actions, aw.surface_bias, aw.state, aw.reason
FROM activity_windows aw
JOIN bots b ON aw.bot_id = b.id
ORDER BY b.persona_id, aw.start_at
"""
df_aw = pd.read_sql_query(query, conn)
print("Activity windows total:", len(df_aw))

# Calculate duration for each activity window
df_aw['start_dt'] = pd.to_datetime(df_aw['start_at'])
df_aw['end_dt'] = pd.to_datetime(df_aw['end_at'])
df_aw['dur_min'] = (df_aw['end_dt'] - df_aw['start_dt']).dt.total_seconds() / 60.0

summary = df_aw.groupby('persona_id').agg(
    n_windows=('id', 'count'),
    mean_dur=('dur_min', 'mean'),
    std_dur=('dur_min', 'std'),
    min_dur=('dur_min', 'min'),
    max_dur=('dur_min', 'max'),
    unique_dates=('local_date', 'nunique')
).reset_index()
print("\n--- Summary Activity Windows ---")
print(summary.to_string())

print("\n--- Check planning_attempts request / response ---")
cursor = conn.cursor()
cursor.execute("SELECT b.persona_id, pa.local_date, pa.request_json, pa.response_json FROM planning_attempts pa JOIN bots b ON pa.bot_id = b.id LIMIT 4;")
for row in cursor.fetchall():
    print(f"\nPlanning attempt for {row[0]} on {row[1]}:")
    req = json.loads(row[2]) if row[2] else {}
    resp = json.loads(row[3]) if row[3] else {}
    print("  Request keys:", list(req.keys()))
    if 'persona' in req:
        print("  Req persona summary/circadian:", req.get('circadian', req.get('contract', {}).get('circadian')))
    print("  Response:", json.dumps(resp, ensure_ascii=False)[:300])

