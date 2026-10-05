import sys
from pathlib import Path
import json

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from loaders.episode_loader import list_episodes, load_episode

print("1. Testing list_episodes()...")
episodes = list_episodes()
print(f"Found {len(episodes)} episodes:")
for ep in episodes:
    print(f"  - ID: {ep['id']} | Persona: {ep['persona_id']} | Status: {ep['status']} | Steps: {ep['step_count']} | Duration: {ep['duration_seconds']}s")

print("\n2. Testing load_episode() on completed episode with highest steps...")
target_id = episodes[0]["id"] # 9e8baabb-5691-4c15-b278-0b5534c6ee08
print(f"Loading episode {target_id}...")

full_ep = load_episode(target_id)
print("\nSuccessfully loaded FullEpisodeSchema!")
print("Summary:")
summary = full_ep.get_summary()
print(json.dumps(summary, indent=2, ensure_ascii=False))

print("\n3. Testing to_steps_dataframe()...")
df_steps = full_ep.to_steps_dataframe()
print(f"Steps DataFrame shape: {df_steps.shape}")
print("Columns:", list(df_steps.columns))
print(df_steps[["step_index", "intent", "surface", "tool", "verified", "gesture_pace", "gesture_total_px", "primary_dimension"]].head(10))

print("\n4. Testing to_events_dataframe()...")
df_events = full_ep.to_events_dataframe()
print(f"Events DataFrame shape: {df_events.shape}")
print(df_events["kind"].value_counts())

print("\n5. Testing to_searches_dataframe()...")
df_searches = full_ep.to_searches_dataframe()
print(f"Searches count: {len(df_searches)}")
if not df_searches.empty:
    print(df_searches[["step_index", "query", "purpose", "verified"]])

print("\n6. Testing to_deltas_dataframe()...")
df_deltas = full_ep.to_deltas_dataframe()
print(f"Memory deltas count: {len(df_deltas)}")
if not df_deltas.empty:
    print(df_deltas[["record_type", "record_key", "operation"]])

print("\n7. Testing loading ALL other episodes in database to ensure zero validation errors...")
for ep in episodes:
    ep_id = ep["id"]
    try:
        e = load_episode(ep_id)
        df_s = e.to_steps_dataframe()
        print(f"  [OK] Episode {ep_id}: {len(e.steps)} steps, {len(e.events)} events, status={e.metadata.status}")
    except Exception as err:
        print(f"  [FAILED] Episode {ep_id}: {err}")
        raise err

print("\nALL EPISODES LOADED AND VALIDATED SUCCESSFULLY!")
