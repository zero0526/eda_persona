import sqlite3
import json
import pandas as pd
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect("data/persona-runner.sqlite")
cursor = conn.cursor()

# Map bot_id to persona_id
cursor.execute("SELECT id, persona_id FROM bots;")
bot_map = dict(cursor.fetchall())
print("Bot map:", bot_map)

# Check entity_affinities
cursor.execute("SELECT * FROM entity_affinities;")
cols = [c[1] for c in cursor.description]
affs = [dict(zip(cols, r)) for r in cursor.fetchall()]
print(f"\nEntity affinities ({len(affs)}):")
for a in affs:
    p_id = bot_map.get(a['bot_id'], a['bot_id'])
    print(f"[{p_id}] {a['entity_type']}: {a['display_name']} (key: {a['entity_key']}) | affinity: {a['affinity']}, familiarity: {a['familiarity']}")
    print(f"   URL: {a['url']}")
    print(f"   Episodes: {a['episode_ids_json']}")

# Check habit_facts
cursor.execute("SELECT bot_id, kind, value_json FROM habit_facts;")
facts = cursor.fetchall()
print(f"\nHabit facts ({len(facts)}):")
for b, k, val in facts:
    p_id = bot_map.get(b, b)
    print(f"[{p_id}] {k}: {val[:120]}")

conn.close()
