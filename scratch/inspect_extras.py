import sqlite3
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

db_path = r"D:\source_code\agent_in_works\claw-master\data\persona-runner.sqlite"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("--- search_history sample ---")
cur.execute("SELECT * FROM search_history LIMIT 2")
for r in cur.fetchall():
    print(dict(r))

print("\n--- habit_facts sample ---")
cur.execute("SELECT * FROM habit_facts LIMIT 2")
for r in cur.fetchall():
    d = dict(r)
    d["value_json"] = json.loads(d["value_json"]) if d["value_json"] else None
    print(d)

print("\n--- benchmark_trials sample ---")
cur.execute("SELECT * FROM benchmark_trials WHERE episode_id IS NOT NULL LIMIT 2")
for r in cur.fetchall():
    d = dict(r)
    if d.get("report_json"):
        d["report_json"] = json.loads(d["report_json"])
    print(d)

conn.close()
