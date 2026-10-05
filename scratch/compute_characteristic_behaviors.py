import sys
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')

from loaders.loaders.persona_action import PersonaActionLoader
from algorithms.standardized_residuals import compute_standardized_residuals
from algorithms.temporal_velocity_and_behavior_profiler import compute_temporal_velocity_by_pace

loader = PersonaActionLoader()
df_steps = loader.load_step_records()

# Chuẩn hóa time_bin_4
res = compute_temporal_velocity_by_pace(df_steps)
df = res["df_processed"]

def map_macro_behavior(row):
    intent = str(row.get("intent", "")).lower()
    tool = str(row.get("tool", "")).lower()
    res_tool = str(row.get("resolved_tool", "")).lower()
    if tool == "end_episode" or res_tool == "end_episode":
        return "End Session"
    if tool in ["rest", "wait_for_feed"]:
        return "Rest/Wait"
    if intent == "read" or "read" in res_tool:
        return "Deep Read"
    if intent in ["react", "share", "like_page"] or "react" in res_tool:
        return "React/Social"
    if intent == "search" or "search" in res_tool:
        return "Search Query"
    if intent == "scroll" or "scroll" in res_tool:
        return "Scroll Feed"
    if intent in ["open", "home", "back", "close"] or res_tool in ["return_home", "close_detail", "open_search_result", "back_to_discovery"]:
        return "Navigate"
    if intent == "observe" or "observe" in res_tool:
        return "Observe"
    return "Other"

df["macro_behavior"] = df.apply(map_macro_behavior, axis=1)

# TÍNH TOÁN CHO NHÓM PERSONA
p_df = df[df["dataset_type"] == "persona"]
ct_p = pd.crosstab(p_df["time_bin_4"], p_df["macro_behavior"])

print("=== 1. HABERMAN STANDARDIZED RESIDUALS (Z-SCORES) CHO NHÓM PERSONA ===")
# Haberman Residuals: z_ij = (O - E) / sqrt(E * (1 - r_i) * (1 - c_j))
res_p = compute_standardized_residuals(ct_p)
print(res_p.round(2).to_string())

print("\n=== 2. LIFT RATIO CHO NHÓM PERSONA (Lift = P(B|Q) / P(B)) ===")
p_overall = p_df["macro_behavior"].value_counts(normalize=True)
lift_p = pd.DataFrame(index=ct_p.index, columns=ct_p.columns)
for q in ct_p.index:
    sub_q = p_df[p_df["time_bin_4"] == q]
    p_q = sub_q["macro_behavior"].value_counts(normalize=True)
    for b in ct_p.columns:
        lift_p.loc[q, b] = round(float(p_q.get(b, 0.0) / p_overall.get(b, 1e-6)), 2)
print(lift_p.to_string())

print("\n" + "="*80)
print("=== 3. HABERMAN STANDARDIZED RESIDUALS CHO NHÓM NO-PERSONA ===")
np_df = df[df["dataset_type"] == "no_persona"]
ct_np = pd.crosstab(np_df["time_bin_4"], np_df["macro_behavior"])
res_np = compute_standardized_residuals(ct_np)
print(res_np.round(2).to_string())

print("\n=== 4. LIFT RATIO CHO NHÓM NO-PERSONA ===")
np_overall = np_df["macro_behavior"].value_counts(normalize=True)
lift_np = pd.DataFrame(index=ct_np.index, columns=ct_np.columns)
for q in ct_np.index:
    sub_q = np_df[np_df["time_bin_4"] == q]
    p_q = sub_q["macro_behavior"].value_counts(normalize=True)
    for b in ct_np.columns:
        lift_np.loc[q, b] = round(float(p_q.get(b, 0.0) / np_overall.get(b, 1e-6)), 2)
print(lift_np.to_string())
