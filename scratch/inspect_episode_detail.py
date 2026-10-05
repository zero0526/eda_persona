import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
db_path = r'D:\source_code\agent_in_works\claw-master\data\persona-runner.sqlite'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT id, bot_id, profile_id, status, started_at, ended_at, terminal_reason FROM episodes;")
episodes = c.fetchall()
print("=== ALL EPISODES IN DB ===")
for ep in episodes:
    print(ep)

# Check one episode in detail
ep_id = episodes[0][0]
print(f"\n=== INSPECTING EPISODE: {ep_id} ===")

# 1. agent_live_steps
c.execute("SELECT step_index, created_at, payload_json FROM agent_live_steps WHERE episode_id=? ORDER BY step_index LIMIT 2;", (ep_id,))
steps = c.fetchall()
print(f"Total agent_live_steps: {len(steps)} samples shown:")
for s in steps:
    print(f"  Step {s[0]} ({s[1]}):")
    payload = json.loads(s[2])
    print(f"    Keys: {list(payload.keys())}")
    for k in ['intent', 'action', 'surface', 'tool', 'verified', 'thought', 'reason', 'evidence', 'working_memory']:
        if k in payload:
            print(f"      {k}: {str(payload[k])[:80]}")

# 2. episode_events
c.execute("SELECT kind, count(*) FROM episode_events WHERE episode_id=? GROUP BY kind;", (ep_id,))
print("\nEvent counts by kind:", c.fetchall())

c.execute("SELECT kind, payload_json FROM episode_events WHERE episode_id=? LIMIT 2;", (ep_id,))
for ev in c.fetchall():
    print(f"  Event {ev[0]}: {ev[1][:100]}")

# 3. episode_working_memory
c.execute("SELECT snapshot_json FROM episode_working_memory WHERE episode_id=?;", (ep_id,))
wm = c.fetchone()
if wm:
    wm_data = json.loads(wm[0])
    print(f"\nWorking Memory keys: {list(wm_data.keys())}")

# 4. bot and persona
bot_id = episodes[0][1]
c.execute("SELECT * FROM bots WHERE id=?;", (bot_id,))
print("\nBot:", c.fetchone())

conn.close()
