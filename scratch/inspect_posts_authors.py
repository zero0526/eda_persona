import sqlite3
import pandas as pd
from pathlib import Path
import json
import re

db_path = "data/persona-runner.sqlite"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in cursor.fetchall()]
print(f"Tables in {db_path}:", tables)

for t in tables:
    cursor.execute(f"PRAGMA table_info({t});")
    cols = [c[1] for c in cursor.fetchall()]
    cursor.execute(f"SELECT count(*) FROM {t};")
    cnt = cursor.fetchone()[0]
    print(f"\nTable: {t} ({cnt} rows)")
    print("  Columns:", cols)

# Sample episodes table
cursor.execute("SELECT * FROM episodes LIMIT 1;")
row = cursor.fetchone()
if row:
    cursor.execute("PRAGMA table_info(episodes);")
    cols = [c[1] for c in cursor.fetchall()]
    sample_ep = dict(zip(cols, row))
    print("\nSample episode columns:", list(sample_ep.keys()))

# Check agent_live_steps table
cursor.execute("PRAGMA table_info(agent_live_steps);")
step_cols = [c[1] for c in cursor.fetchall()]
print("\nagent_live_steps columns:", step_cols)

cursor.execute("SELECT * FROM agent_live_steps LIMIT 3;")
rows = cursor.fetchall()
for i, r in enumerate(rows):
    d = dict(zip(step_cols, r))
    print(f"\n--- Step {i+1} ---")
    for k in ['step_index', 'action_type', 'target_id', 'target_text', 'action_url', 'intent', 'surface', 'reason']:
        if k in d:
            val = str(d[k])[:100]
            print(f"  {k}: {val}")

conn.close()
