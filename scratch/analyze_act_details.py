import sqlite3
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

db_path = r"D:\source_code\agent_in_works\claw-master\data\persona-runner.sqlite"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT payload_json FROM agent_live_steps WHERE json_extract(payload_json, '$.decision.tool') = 'act' LIMIT 5")
rows = cur.fetchall()

for idx, r in enumerate(rows):
    p = json.loads(r[0])
    dec = p.get("decision", {})
    out = p.get("outcome", {})
    print(f"--- Step {idx+1} ---")
    print("actionSummary:", dec.get("actionSummary"))
    print("args.intent:", dec.get("args", {}).get("intent"))
    print("outcome.verified:", out.get("verified"))
    print("outcome.evidence:", out.get("evidence"))
    print("outcome.raw keys:", list(out.get("raw", {}).keys()) if isinstance(out.get("raw"), dict) else type(out.get("raw")))

conn.close()
