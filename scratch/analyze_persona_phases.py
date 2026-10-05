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

print("=== TỔNG QUAN 8 PHIÊN (EPISODES SUMMARY) ===")
cols_ep = ["episode_id", "persona_id", "dataset_type", "total_steps", "duration_seconds", "termination_cause", "persona_pace", "persona_rest_style", "has_rest"]
available = [c for c in cols_ep if c in df_ep.columns]
print(df_ep[available].to_string())

print("\n=== QUỸ ĐẠO VẬN TỐC THEO 3 GIAI ĐOẠN (EARLY 0-33%, MID 33-66%, LATE 66-100%) THEO TỪNG PHIÊN ===")
records = []
for ep_id, ep_df in df_steps.groupby("episode_id"):
    ep_df = ep_df.sort_values("step_index").reset_index(drop=True)
    n = len(ep_df)
    dtype = ep_df["dataset_type"].iloc[0]
    p_id = ep_df["persona_id"].iloc[0]
    
    # Chia 3 giai đoạn
    g1 = ep_df.iloc[: int(n * 0.33)]
    g2 = ep_df.iloc[int(n * 0.33): int(n * 0.67)]
    g3 = ep_df.iloc[int(n * 0.67):]
    
    v1 = g1["context_action_velocity"].dropna().mean()
    v2 = g2["context_action_velocity"].dropna().mean()
    v3 = g3["context_action_velocity"].dropna().mean()
    
    # Số lần end_episode được gọi trong G3
    end_calls_g3 = (g3["tool"] == "end_episode").sum() if "tool" in g3.columns else 0
    
    records.append({
        "episode_id": ep_id[:8],
        "dataset_type": dtype,
        "persona_id": p_id,
        "total_steps": n,
        "v_early (0-33%)": round(v1, 2) if pd.notnull(v1) else np.nan,
        "v_mid (33-66%)": round(v2, 2) if pd.notnull(v2) else np.nan,
        "v_late (66-100%)": round(v3, 2) if pd.notnull(v3) else np.nan,
        "delta_v (Late - Early)": round(v3 - v1, 2) if pd.notnull(v1) and pd.notnull(v3) else np.nan,
        "end_calls_late": end_calls_g3
    })

df_trajectory = pd.DataFrame(records)
print(df_trajectory.to_string())

print("\n=== TRÍCH XUẤT CÁC LÝ DO (REASONS) Ở 5 BƯỚC CUỐI CÙNG CỦA CÁC PHIÊN PERSONA ===")
p_eps = df_steps[df_steps["dataset_type"] == "persona"]["episode_id"].unique()
for ep_id in p_eps:
    ep_df = df_steps[df_steps["episode_id"] == ep_id].sort_values("step_index")
    p_id = ep_df["persona_id"].iloc[0]
    print(f"\n--- Persona Episode {ep_id[:8]} ({p_id}) ---")
    last_5 = ep_df.tail(5)
    for _, r in last_5.iterrows():
        tool = r.get("tool", "")
        res_tool = r.get("resolved_tool", "")
        reason = str(r.get("reason", ""))[:120]
        step_i = r.get("step_index", "")
        print(f"  Step {step_i} [{tool} -> {res_tool}]: {reason}")
