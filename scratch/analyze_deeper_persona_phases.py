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

# 1. Phân nhóm Pacing trong Persona
p_steps = df_steps[df_steps["dataset_type"] == "persona"].copy()
p_eps = df_ep[df_ep["dataset_type"] == "persona"].copy()

print("=== 1. TƯƠNG QUAN GIỮA PERSONA_PACE VÀ QUỸ ĐẠO VẬN TỐC ===")
p_steps["phase"] = pd.cut(
    p_steps.groupby("episode_id")["step_index"].transform(lambda x: (x - x.min()) / (x.max() - x.min())),
    bins=[-0.01, 0.33, 0.67, 1.0],
    labels=["Phase 1 (Burst/Early)", "Phase 2 (Regulation/Mid)", "Phase 3 (Satiation/Late)"]
)

pace_phase_summary = p_steps.groupby(["persona_pace", "phase"], observed=False)["context_action_velocity"].agg(["count", "mean", "std", "median"])
print(pace_phase_summary.round(2).to_string())

print("\n=== 2. THỜI ĐIỂM XUẤT HIỆN Ý ĐỊNH THOÁT PHIÊN ĐẦU TIÊN (FIRST EXIT INTENT STEP) ===")
exit_records = []
for ep_id, ep_df in p_steps.groupby("episode_id"):
    ep_df = ep_df.sort_values("step_index")
    n = len(ep_df)
    p_id = ep_df["persona_id"].iloc[0]
    pace = ep_df["persona_pace"].iloc[0]
    
    # Tìm bước đầu tiên có tool == 'end_episode' hoặc reason chứa 'kết thúc' / 'hết phiên'
    exit_steps = ep_df[(ep_df["tool"] == "end_episode") | (ep_df["reason"].fillna("").str.contains("hết phiên|kết thúc|hoàn thành", case=False))]
    first_exit_step = int(exit_steps["step_index"].min()) if len(exit_steps) > 0 else n
    first_exit_pct = (first_exit_step / n) * 100
    
    # Tích lũy tại thời điểm đó
    reads_at_exit = ep_df.loc[ep_df["step_index"] <= first_exit_step, "tool"].isin(["read_visible_post"]).sum()
    searches_at_exit = ep_df.loc[ep_df["step_index"] <= first_exit_step, "tool"].isin(["search_topics", "search_feed"]).sum()
    
    exit_records.append({
        "episode_id": ep_id[:8],
        "persona_id": p_id,
        "pace": pace,
        "total_steps": n,
        "first_exit_intent_step": first_exit_step,
        "exit_onset_pct": round(first_exit_pct, 1),
        "total_end_calls": (ep_df["tool"] == "end_episode").sum()
    })

print(pd.DataFrame(exit_records).to_string(index=False))

print("\n=== 3. SO SÁNH Ý ĐỊNH (REASONS) PHA 3: PERSONA VS NO-PERSONA ===")
late_steps = df_steps.groupby("episode_id").apply(lambda x: x.sort_values("step_index").tail(10)).reset_index(drop=True)
p_late_meta = late_steps[late_steps["dataset_type"] == "persona"]["reason"].fillna("").str.contains("đã đọc|đã tìm kiếm|hoàn thành|hết thời|thời lượng", case=False).mean()
no_p_late_stuck = late_steps[late_steps["dataset_type"] == "no_persona"]["reason"].fillna("").str.contains("kẹt|lỗi|deadlock|close lỗi", case=False).mean()
print(f"Persona Phase 3: Tỷ lệ bước có lý do tự đánh giá hoàn thành nhiệm vụ (Meta-Cognitive Evaluation): {p_late_meta * 100:.1f}%")
print(f"No-Persona Phase 3: Tỷ lệ bước có lý do báo lỗi/kẹt giao diện (UI Stuck/Error): {no_p_late_stuck * 100:.1f}%")
