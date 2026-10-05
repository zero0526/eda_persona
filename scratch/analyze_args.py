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

act_actions = set()
args_keys = set()
sample_args_by_tool = {}

for r in rows:
    if not r[0]:
        continue
    p = json.loads(r[0])
    dec = p.get("decision", {})
    t = dec.get("tool")
    args = dec.get("args", {})
    if t not in sample_args_by_tool:
        sample_args_by_tool[t] = args
    if t == "act":
        act_actions.add(args.get("action"))
        args_keys.update(args.keys())

print("Act actions encountered:", sorted(list(str(x) for x in act_actions)))
print("Act args keys:", sorted(args_keys))
print("\nSample args by tool:")
for t, a in sample_args_by_tool.items():
    print(f"Tool {t}: {a}")

conn.close()
