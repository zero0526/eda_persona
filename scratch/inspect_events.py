import sqlite3
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

db_path = r"D:\source_code\agent_in_works\claw-master\data\persona-runner.sqlite"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT DISTINCT kind, COUNT(*) as cnt FROM episode_events GROUP BY kind")
kinds = cur.fetchall()
print("Distinct event kinds:")
for k in kinds:
    print(f"  {k['kind']}: {k['cnt']}")

print("\nSample of each event kind:")
for k in kinds:
    cur.execute("SELECT payload_json FROM episode_events WHERE kind = ? LIMIT 1", (k["kind"],))
    row = cur.fetchone()
    if row and row["payload_json"]:
        try:
            p = json.loads(row["payload_json"])
            print(f"--- Kind: {k['kind']} ---")
            print(json.dumps(p, indent=2, ensure_ascii=False)[:300])
        except Exception as e:
            print(f"Error parsing {k['kind']}: {e}")

conn.close()
