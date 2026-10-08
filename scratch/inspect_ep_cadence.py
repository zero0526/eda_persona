import sqlite3
import json

conn = sqlite3.connect('data/persona-runner.sqlite')
cursor = conn.cursor()

query = """
SELECT e.id, b.persona_id, e.contract_id, e.started_at, e.ended_at, bc.schema_version, bc.contract_json
FROM episodes e
JOIN bots b ON e.bot_id = b.id
LEFT JOIN behavioral_contracts bc ON e.contract_id = bc.id
ORDER BY b.persona_id, e.started_at
"""
cursor.execute(query)
rows = cursor.fetchall()
for r in rows:
    ep_id, pid, cid, start, end, s_ver, c_json = r
    c = json.loads(c_json) if c_json else {}
    cadence = c.get('navigation', {}).get('scrollCadence')
    print(f"Persona: {pid} | Ep: {ep_id[:8]} | Start: {start} | Cadence in Contract: {cadence} | Contract ID: {cid}")
