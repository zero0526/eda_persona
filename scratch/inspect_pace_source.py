import sqlite3
import json
import re

conn = sqlite3.connect('data/persona-runner.sqlite')
cursor = conn.cursor()

cursor.execute("""
    SELECT de.episode_id, de.step_index, de.action, de.evidence_json, e.bot_id, b.persona_id
    FROM decision_evidence de
    JOIN episodes e ON de.episode_id = e.id
    JOIN bots b ON e.bot_id = b.id
    WHERE de.evidence_json LIKE '%pace=%'
    LIMIT 15
""")
rows = cursor.fetchall()
print(f"Total found sample: {len(rows)}")
for r in rows[:6]:
    print(f"Persona: {r[5]}, Ep: {r[0][:8]}, Step: {r[1]}, Action: {r[2]}")
    ev = json.loads(r[3]) if r[3] else {}
    print(f"  evidence_json: {ev}")

print("\n--- Inspect distinct pace values by persona and episode ---")
cursor.execute("""
    SELECT b.persona_id, de.episode_id, de.evidence_json
    FROM decision_evidence de
    JOIN episodes e ON de.episode_id = e.id
    JOIN bots b ON e.bot_id = b.id
    WHERE de.evidence_json LIKE '%pace=%'
""")
all_rows = cursor.fetchall()
from collections import defaultdict
pace_per_ep = defaultdict(lambda: defaultdict(set))
for pid, ep, ev_json in all_rows:
    m = re.search(r'pace=(\w+)', ev_json)
    if m:
        pace_per_ep[pid][ep].add(m.group(1))

for pid in sorted(pace_per_ep.keys()):
    print(f"\nPersona: {pid}")
    for ep, paces in pace_per_ep[pid].items():
        print(f"  Session {ep[:8]}: {paces}")
