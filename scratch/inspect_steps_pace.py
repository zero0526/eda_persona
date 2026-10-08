import sqlite3
import json
import re

conn = sqlite3.connect('data/persona-runner.sqlite')
cursor = conn.cursor()

cursor.execute("""
    SELECT als.episode_id, als.step_index, als.payload_json, b.persona_id
    FROM agent_live_steps als
    JOIN episodes e ON als.episode_id = e.id
    JOIN bots b ON e.bot_id = b.id
    WHERE als.payload_json LIKE '%pace=%'
    LIMIT 10
""")
rows = cursor.fetchall()
for r in rows[:5]:
    print(f"\nPersona: {r[3]}, Ep: {r[0][:8]}, Step: {r[1]}")
    p = json.loads(r[2])
    # print keys and where pace appears
    print("  Keys:", list(p.keys()))
    for k, v in p.items():
        if isinstance(v, str) and 'pace=' in v:
            print(f"    {k}: {v}")
        elif isinstance(v, dict):
            for subk, subv in v.items():
                if isinstance(subv, str) and 'pace=' in subv:
                    print(f"    {k}.{subk}: {subv}")

print("\n--- Summary of pace values across all episodes ---")
cursor.execute("""
    SELECT b.persona_id, als.episode_id, als.payload_json
    FROM agent_live_steps als
    JOIN episodes e ON als.episode_id = e.id
    JOIN bots b ON e.bot_id = b.id
    WHERE als.payload_json LIKE '%pace=%'
""")
from collections import defaultdict
pace_per_ep = defaultdict(lambda: defaultdict(list))
for pid, ep, payload in cursor.fetchall():
    matches = re.findall(r'pace=(\w+)', payload)
    for m in matches:
        pace_per_ep[pid][ep].append(m)

for pid in sorted(pace_per_ep.keys()):
    print(f"\n*** Persona: {pid} ***")
    for ep, paces in pace_per_ep[pid].items():
        pace_counts = {x: paces.count(x) for x in set(paces)}
        print(f"  Session {ep[:8]}: {pace_counts}")
