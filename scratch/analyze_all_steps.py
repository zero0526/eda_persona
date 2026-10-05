import sqlite3
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

db_path = r"D:\source_code\agent_in_works\claw-master\data\persona-runner.sqlite"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT payload_json FROM agent_live_steps")
rows = cur.fetchall()

keys_set = set()
decision_keys_set = set()
outcome_keys_set = set()
debug_keys_set = set()
tools_set = set()

for r in rows:
    if not r[0]:
        continue
    try:
        p = json.loads(r[0])
        keys_set.update(p.keys())
        if "decision" in p and isinstance(p["decision"], dict):
            decision_keys_set.update(p["decision"].keys())
            if "tool" in p["decision"]:
                tools_set.add(p["decision"]["tool"])
        if "outcome" in p and isinstance(p["outcome"], dict):
            outcome_keys_set.update(p["outcome"].keys())
        if "debug" in p and isinstance(p["debug"], dict):
            debug_keys_set.update(p["debug"].keys())
    except Exception as e:
        print("Error parsing step:", e)

print(f"Total steps analyzed: {len(rows)}")
print("Step root keys:", sorted(keys_set))
print("Decision keys:", sorted(decision_keys_set))
print("Outcome keys:", sorted(outcome_keys_set))
print("Debug keys:", sorted(debug_keys_set))
print("Tools encountered:", sorted(tools_set))

conn.close()
