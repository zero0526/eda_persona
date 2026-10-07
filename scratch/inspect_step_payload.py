import sqlite3
import json
import pandas as pd
from loaders.action_loader import ActionLoader

conn = sqlite3.connect("data/persona-runner.sqlite")
cursor = conn.cursor()

# Check agent_live_steps
cursor.execute("SELECT episode_id, step_index, payload_json FROM agent_live_steps WHERE payload_json IS NOT NULL AND length(payload_json) > 5 LIMIT 5;")
rows = cursor.fetchall()
print(f"Found {len(rows)} sample non-empty steps:")
for ep_id, step_idx, p_str in rows:
    try:
        p = json.loads(p_str)
        print(f"\nStep {step_idx} keys:", list(p.keys()))
        for k in ['target', 'post', 'author', 'group', 'page', 'url', 'action', 'dom_target', 'target_text', 'entity']:
            if k in p:
                print(f"  {k}: {p[k]}")
    except Exception as e:
        print("JSON parse error:", e)

# Check all tables where posts, authors, or groups might be recorded
# Let's inspect entity_affinities table
cursor.execute("SELECT * FROM entity_affinities;")
cols = [c[1] for c in cursor.description] if cursor.description else []
rows = cursor.fetchall()
print(f"\nEntity affinities ({len(rows)} rows):")
for r in rows:
    print(r)

# Check interest_threads table
cursor.execute("SELECT id, bot_id, thread_key, title, summary, episode_ids_json FROM interest_threads LIMIT 10;")
rows = cursor.fetchall()
print(f"\nInterest threads ({len(rows)} rows):")
for r in rows:
    print(r)

# Check episode_events table
cursor.execute("SELECT DISTINCT kind, count(*) FROM episode_events GROUP BY kind;")
print("\nEpisode events kinds:")
for k, cnt in cursor.fetchall():
    print(f"  {k}: {cnt}")

cursor.execute("SELECT kind, payload_json FROM episode_events WHERE payload_json IS NOT NULL AND length(payload_json) > 5 LIMIT 5;")
for k, p_str in cursor.fetchall():
    try:
        p = json.loads(p_str)
        print(f"\nEvent {k} keys:", list(p.keys()))
        print("  Sample data:", str(p)[:200])
    except:
        pass

conn.close()

# Also inspect ActionLoader to see how actions are parsed
loader = ActionLoader()
histories = loader.load_all_personas()
df = loader.to_unified_actions_dataframe(histories)

print("\n--- df_actions inspection ---")
print("Total actions:", len(df))
print("Non-null target_id count:", df['target_id'].notna().sum())
print("Unique target_id count:", df['target_id'].nunique())
print("Top target_ids:")
print(df['target_id'].value_counts().head(10))

print("\nNon-null action_url count:", df['action_url'].notna().sum())
print("Unique action_url count:", df['action_url'].nunique())
print("Top action_urls:")
print(df['action_url'].value_counts().head(10))

print("\nNon-null target_text count:", df['target_text'].notna().sum())
print("Sample target_texts:")
for t in df['target_text'].dropna().head(10):
    print("  *", repr(t[:100]))
