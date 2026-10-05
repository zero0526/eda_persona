import json
import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

from loaders.loaders.persona_action import PersonaActionLoader

loader = PersonaActionLoader()
df_steps = loader.load_step_records()

print("=== TRÍCH XUẤT CÁC LÝ DO (REASONS) Ở 5 BƯỚC CUỐI CÙNG CỦA CÁC PHIÊN NO-PERSONA ===")
no_p_eps = df_steps[df_steps["dataset_type"] == "no_persona"]["episode_id"].unique()
for ep_id in no_p_eps:
    ep_df = df_steps[df_steps["episode_id"] == ep_id].sort_values("step_index")
    print(f"\n--- No-Persona Episode {ep_id[:8]} (Total steps: {len(ep_df)}) ---")
    last_5 = ep_df.tail(8)
    for _, r in last_5.iterrows():
        tool = r.get("tool", "")
        res_tool = r.get("resolved_tool", "")
        reason = str(r.get("reason", ""))[:120]
        step_i = r.get("step_index", "")
        sit_steps = r.get("wm_situational_steps", "")
        print(f"  Step {step_i} [{tool} -> {res_tool}] (sit_steps={sit_steps}): {reason}")
