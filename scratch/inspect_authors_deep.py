import sqlite3
import json
import pandas as pd
import re

conn = sqlite3.connect("data/persona-runner.sqlite")
cursor = conn.cursor()

# 1. Inspect decision_evidence
cursor.execute("SELECT episode_id, step_index, action, evidence_json FROM decision_evidence LIMIT 5;")
rows = cursor.fetchall()
print(f"Sample decision_evidence ({len(rows)}):")
for ep, step, act, ev_str in rows:
    try:
        ev = json.loads(ev_str)
        print(f"\nStep {step} act={act} keys={list(ev.keys())}")
        print("  Sample:", str(ev)[:300])
    except Exception as e:
        print("Error:", e)

# 2. Inspect tool_result payloads
cursor.execute("SELECT payload_json FROM episode_events WHERE kind='tool_result' LIMIT 5;")
rows = cursor.fetchall()
print(f"\nSample tool_result events ({len(rows)}):")
for r in rows:
    try:
        p = json.loads(r[0])
        print("Keys:", list(p.keys()))
        if 'evidence' in p:
            print("  evidence:", str(p['evidence'])[:200])
        if 'target_candidate' in p:
            print("  target_candidate:", str(p['target_candidate'])[:200])
        if 'args' in p:
            print("  args:", p['args'])
    except Exception as e:
        print("Error:", e)

# 3. Inspect URLs and target text from action_url and target_id across all steps
from loaders.action_loader import ActionLoader
loader = ActionLoader()
histories = loader.load_all_personas()
df = loader.to_unified_actions_dataframe(histories)

# Check all action_urls
urls = df[df['action_url'].notna()][['persona_id', 'session_order', 'step_index', 'action_url', 'intent', 'reason']].copy()
print(f"\nTotal actions with action_url: {len(urls)}")
print("Sample URLs with reasons:")
for idx, r in urls.head(10).iterrows():
    print(f"[{r['persona_id']} S{r['session_order']} Step {r['step_index']}] {r['intent']} -> URL: {r['action_url']}")
    print(f"   Reason: {r['reason'][:100]}")

conn.close()
