import sqlite3
import json
import pandas as pd
import re
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from loaders.action_loader import ActionLoader
loader = ActionLoader()
histories = loader.load_all_personas()
df = loader.to_unified_actions_dataframe(histories)

# Look at all action_url patterns
print("=== ACTION URL ANALYSIS ===")
# Extract groups
group_urls = df[df['action_url'].str.contains(r'/groups/', na=False)][['persona_id', 'session_order', 'step_index', 'action_url', 'intent', 'reason']]
print(f"Total group actions: {len(group_urls)}")
for idx, r in group_urls.head(15).iterrows():
    print(f"[{r['persona_id']} S{r['session_order']}] {r['intent']} | URL: {r['action_url']}")
    print(f"   Reason: {r['reason'][:120]}")

# Extract pages / posts / photos
post_urls = df[df['action_url'].str.contains(r'/posts/|/photo/|permalink|/reel/|fbid', na=False)][['persona_id', 'session_order', 'step_index', 'action_url', 'intent', 'reason']]
print(f"\nTotal post/photo/reel actions: {len(post_urls)}")

# Check if any URL appears across MULTIPLE sessions or MULTIPLE personas!
url_counts = df['action_url'].dropna().value_counts()
cross_urls = url_counts[url_counts > 1]
print("\n=== URLs APPEARING MULTIPLE TIMES ===")
for url, cnt in cross_urls.items():
    sub = df[df['action_url'] == url]
    personas = sub['persona_id'].unique().tolist()
    sessions = sub['session_order'].unique().tolist()
    sess_ids = sub['session_id'].unique().tolist()
    print(f"\nURL ({cnt} times, {len(sess_ids)} distinct sessions, Personas: {personas}, Sessions: {sessions}):")
    print(f"  {url}")
    print(f"  Sample reason: {sub['reason'].iloc[0][:120]}")

# Check interest_threads across sessions
conn = sqlite3.connect("data/persona-runner.sqlite")
cursor = conn.cursor()
cursor.execute("SELECT bot_id, thread_key, title, summary, episode_ids_json FROM interest_threads;")
threads = cursor.fetchall()
print("\n=== INTEREST THREADS ACROSS SESSIONS ===")
for b, k, title, summary, eps_json in threads:
    eps = json.loads(eps_json) if eps_json else []
    print(f"Bot: {b} | Key: {k} | Title: {title} | Sessions count: {len(eps)}")
    if len(eps) > 1:
        print(f"  *** CROSS-SESSION THREAD: {title} in {len(eps)} sessions! ***")
        print(f"  Summary: {summary[:150]}")

conn.close()
