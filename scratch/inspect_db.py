import sqlite3
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

db_path = r"D:\source_code\agent_in_works\claw-master\data\persona-runner.sqlite"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get table names
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]

report = {}
for t in tables:
    cur.execute(f"PRAGMA table_info({t})")
    cols = [{'name': c[1], 'type': c[2], 'notnull': bool(c[3]), 'pk': bool(c[5])} for c in cur.fetchall()]
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    cnt = cur.fetchone()[0]
    report[t] = {'columns': cols, 'count': cnt}

os.makedirs("scratch", exist_ok=True)
with open("scratch/db_schema_summary.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"Done. Inspected {len(tables)} tables.")
