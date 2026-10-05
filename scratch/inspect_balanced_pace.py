import json
import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

from loaders.loaders.persona_action import PersonaActionLoader

loader = PersonaActionLoader()
df_steps = loader.load_step_records()
df_ep = loader.load_action_logs()

# 1. Tìm tất cả các phiên có persona_pace == 'balanced'
bal_ep = df_ep[df_ep["persona_pace"] == "balanced"]
print("=== CÁC PHIÊN CÓ PERSONA_PACE == 'balanced' ===")
print(bal_ep[["episode_id", "persona_id", "total_steps", "final_elapsed_seconds", "terminal_reason"]].to_string())

# 2. Lấy profile persona vn_000041
with open('data/original_facebook_persona.json', encoding='utf-8') as f:
    personas = json.load(f)

p41 = next((p for p in personas if p.get('persona_id') == 'vn_000041' or p.get('id') == 'vn_000041'), None)
print("\n=== PROFILE PERSONA vn_000041 ===")
if p41:
    print("Demographics:", p41.get("demographics"))
    profile = p41.get("facebook_behavior_profile", {})
    print("Inferred Habits:")
    for h in profile.get("inferredHabits", []):
        print(f"  - [{h.get('id')}]: {h.get('claim')}")
    print("Interests (Strong):", profile.get("interests", {}).get("strong", []))

# 3. Phân tích chi tiết các bước trong phiên balanced (d7a2ce38)
ep_id = bal_ep["episode_id"].iloc[0]
sub = df_steps[df_steps["episode_id"] == ep_id].sort_values("step_index").reset_index(drop=True)
sub["step_progress"] = sub["step_index"] / len(sub)
sub["q"] = pd.cut(sub["step_progress"], bins=[0.0, 0.25, 0.50, 0.75, 1.0001], labels=["Q1", "Q2", "Q3", "Q4"])

# Xem timeline vận tốc
print("\n=== TIMELINE VẬN TỐC THEO BƯỚC CỦA PHIÊN BALANCED ===")
print(sub[["step_index", "q", "resolved_tool", "intent", "context_elapsed_seconds", "context_action_velocity", "verified"]].to_string())
