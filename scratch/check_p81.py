import json
import sys
from pathlib import Path
from loaders.loaders.persona_action import PersonaActionLoader

sys.stdout.reconfigure(encoding='utf-8')

# 2. Load steps of episode 2cbcde75
loader = PersonaActionLoader()
df_steps = loader.load_step_records()
ep_id = "2cbcde75-15d8-4223-a1a3-22c69aca9b6d"
sub = df_steps[df_steps["episode_id"] == ep_id].sort_values("step_index")

print(f"\n=== EPISODE {ep_id[:8]} TIMELINE AROUND REST (STEPS 27 - 35) ===")
cols = [
    "step_index", "tool", "resolved_tool", "intent", 
    "context_elapsed_seconds", "context_action_velocity", 
    "context_rest_count", "context_rest_accumulated_seconds", 
    "persona_pace", "persona_rest_style", "verified"
]
print(sub[(sub["step_index"] >= 27) & (sub["step_index"] <= 35)][cols].to_string(index=False))

# Check detailed reason/intent at steps 28, 29, 30, 31, 32
for s in [28, 29, 30, 31, 32]:
    r = sub[sub["step_index"] == s].iloc[0]
    print(f"\n--- STEP {s} ---")
    print(f"  Tool: {r['tool']} | Resolved: {r['resolved_tool']} | Verified: {r['verified']}")
    print(f"  Intent: {r['intent']}")
    print(f"  Reason: {r['reason']}")
    print(f"  Elapsed Sec: {r['context_elapsed_seconds']} | Action Velocity: {r['context_action_velocity']} | Rest Sec: {r['context_rest_accumulated_seconds']}")
    print(f"  Thread Topic: {r['wm_current_thread_topic']}")

# 3. Action type distribution Pre vs Post
pre = sub[sub["step_index"] < 30]
post = sub[sub["step_index"] >= 30]
print("\n=== PRE-REST TOOLS (N=29) ===")
print(pre["tool"].value_counts().to_string())
print("\n=== POST-REST TOOLS (N=24) ===")
print(post["tool"].value_counts().to_string())

print("\n=== PRE-REST VERIFIED RATE ===")
print(f"Pre: {pre['verified'].mean():.1%} ({pre['verified'].sum()}/{len(pre)})")
print(f"Post: {post['verified'].mean():.1%} ({post['verified'].sum()}/{len(post)})")

print("\n=== ELAPSED SECONDS JUMP AROUND REST ===")
for s in [28, 29, 30, 31]:
    r = sub[sub["step_index"] == s].iloc[0]
    print(f"Step {s}: elapsed_seconds = {r['context_elapsed_seconds']}, rest_accumulated = {r['context_rest_accumulated_seconds']}")
