import sqlite3
import json
import re
import pandas as pd
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect("data/persona-runner.sqlite")
cursor = conn.cursor()

# Map episode_id to persona_id and session_order
cursor.execute("""
    SELECT e.id, b.persona_id, w.start_at
    FROM episodes e
    JOIN bots b ON e.bot_id = b.id
    LEFT JOIN activity_windows w ON e.window_id = w.id
    ORDER BY b.persona_id, w.start_at;
""")
episodes_info = cursor.fetchall()
ep_map = {}
p_order = {}
for ep_id, p_id, start_at in episodes_info:
    p_order[p_id] = p_order.get(p_id, 0) + 1
    ep_map[ep_id] = {'persona_id': p_id, 'session_order': p_order[p_id]}

cursor.execute("SELECT episode_id, kind, payload_json FROM episode_events WHERE kind IN ('observation', 'tool_result');")
events = cursor.fetchall()

post_interactions = []
for ep_id, kind, p_str in events:
    if not p_str or len(p_str) < 10:
        continue
    try:
        p = json.loads(p_str)
        info = ep_map.get(ep_id, {'persona_id': 'unknown', 'session_order': 0})
        
        if kind == 'tool_result':
            ev = p.get('evidence', '')
            tc = p.get('target_candidate', {})
            tool = p.get('resolved_tool', p.get('tool', ''))
            
            post_interactions.append({
                'episode_id': ep_id,
                'persona_id': info['persona_id'],
                'session_order': info['session_order'],
                'kind': kind,
                'tool': tool,
                'evidence': str(ev),
                'target_candidate': tc if isinstance(tc, dict) else {},
            })
    except Exception as e:
        pass

df_posts = pd.DataFrame(post_interactions)
print(f"Captured {len(df_posts)} tool results.")

# Let's inspect target_candidate structures across all rows
tc_keys = set()
for tc in df_posts['target_candidate']:
    if isinstance(tc, dict):
        tc_keys.update(tc.keys())
print("All keys found in target_candidate:", sorted(tc_keys))

# Inspect sample target_candidate that are non-empty
non_empty_tc = [tc for tc in df_posts['target_candidate'] if tc]
print(f"\nNon-empty target_candidates: {len(non_empty_tc)}")
for tc in non_empty_tc[:5]:
    print("  *", tc)

# Search for authors, pages, groups in evidence string
print("\n=== SAMPLE EVIDENCE STRINGS (checking for author/page/group/url) ===")
for ev in df_posts['evidence'].dropna().head(15):
    print("  Evidence:", ev[:150])

conn.close()
