import json
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')

from loaders.loaders.persona_action import PersonaActionLoader

loader = PersonaActionLoader()
df_steps = loader.load_step_records()
df_ep = loader.load_action_logs()

# 1. Tính toán trục thời gian chuẩn hóa (Normalized Time)
# Mỗi phiên có tổng số bước khác nhau (41-64 bước) và thời gian chạy ~600 giây.
# Ta tạo 2 trục thời gian:
# - Step Progress Quartile / Decile: step_progress = (step_index - 1) / (total_steps_in_episode - 1)
# - Time Window (phút): context_elapsed_seconds chia thành các khoảng [0-2m), [2-4m), [4-6m), [6-8m), [8-10m+]
# - Phase (3 Pha hoặc 4 Quartiles): Q1 (0-25%), Q2 (25-50%), Q3 (50-75%), Q4 (75-100%)

df_steps["total_steps_ep"] = df_steps.groupby("episode_id")["step_index"].transform("count")
df_steps["step_progress"] = df_steps["step_index"] / df_steps["total_steps_ep"]

# Tạo 4 khoảng thời gian (Quartiles)
df_steps["time_bin_4"] = pd.cut(
    df_steps["step_progress"],
    bins=[0.0, 0.25, 0.50, 0.75, 1.0001],
    labels=["Q1 (0-25% Early)", "Q2 (25-50% Mid-Early)", "Q3 (50-75% Mid-Late)", "Q4 (75-100% Late)"]
)

# Tạo 5 khoảng thời gian theo phút thực tế
df_steps["time_minutes_bin"] = pd.cut(
    df_steps["context_elapsed_seconds"].fillna(0),
    bins=[-1, 120, 240, 360, 480, 700],
    labels=["0-2 min", "2-4 min", "4-6 min", "6-8 min", "8-10+ min"]
)

print("=" * 80)
print("PHẦN 1: TỐC ĐỘ THỰC THI BIẾN ĐỔI THEO THỜI GIAN (OVERALL & THEO NHÓM)")
print("=" * 80)
vel_by_time_group = df_steps.groupby(["dataset_type", "time_bin_4"], observed=False)["context_action_velocity"].agg(["count", "mean", "std", "median", lambda x: x.quantile(0.75) - x.quantile(0.25)]).rename(columns={"<lambda_0>": "iqr"})
print("\nVận tốc thao tác (context_action_velocity) theo 4 giai đoạn:")
print(vel_by_time_group.round(2).to_string())

print("\n" + "=" * 80)
print("PHẦN 2: TỐC ĐỘ BIẾN ĐỔI THEO THỜI GIAN & THUỘC TÍNH PACE (RIÊNG PERSONA)")
print("=" * 80)
p_steps = df_steps[df_steps["dataset_type"] == "persona"].copy()
vel_by_pace_time = p_steps.groupby(["persona_pace", "time_bin_4"], observed=False)["context_action_velocity"].agg(["count", "mean", "std", "median", lambda x: x.quantile(0.75) - x.quantile(0.25)]).rename(columns={"<lambda_0>": "iqr"})
print("\nVận tốc của Persona phân theo Pace (quick / balanced / slow) qua 4 giai đoạn:")
print(vel_by_pace_time.round(2).to_string())

# Kiểm định Kruskal-Wallis giữa các nhóm pace ở từng giai đoạn
print("\nKiểm định Kruskal-Wallis so sánh vận tốc giữa 3 nhóm pace ở từng giai đoạn:")
for q in ["Q1 (0-25% Early)", "Q2 (25-50% Mid-Early)", "Q3 (50-75% Mid-Late)", "Q4 (75-100% Late)"]:
    sub_q = p_steps[p_steps["time_bin_4"] == q]
    groups = [g["context_action_velocity"].dropna().values for _, g in sub_q.groupby("persona_pace")]
    h_stat, p_val = stats.kruskal(*groups)
    print(f"  * {q}: H-statistic = {h_stat:.3f}, p-value = {p_val:.4e} {'(Có ý nghĩa)' if p_val < 0.05 else '(Không có ý nghĩa)'}")

# Kiểm định Wilcoxon / Mann-Whitney trong nội bộ từng pace (Q1 vs Q4)
print("\nKiểm định biến đổi vận tốc nội bộ từng Pace (Q1 Early vs Q4 Late):")
for pace in ["quick", "balanced", "slow"]:
    sub_pace = p_steps[p_steps["persona_pace"] == pace]
    v_q1 = sub_pace[sub_pace["time_bin_4"] == "Q1 (0-25% Early)"]["context_action_velocity"].dropna()
    v_q4 = sub_pace[sub_pace["time_bin_4"] == "Q4 (75-100% Late)"]["context_action_velocity"].dropna()
    u_stat, p_val = stats.mannwhitneyu(v_q1, v_q4)
    cliffs_d = (2 * u_stat) / (len(v_q1) * len(v_q4)) - 1
    delta_mean = v_q4.mean() - v_q1.mean()
    print(f"  * Pace [{pace}]: Mean Q1 = {v_q1.mean():.2f} -> Q4 = {v_q4.mean():.2f} (Diff = {delta_mean:+.2f}) | Mann-Whitney U = {u_stat}, p = {p_val:.4e}, Cliff's delta = {cliffs_d:+.3f}")

print("\n" + "=" * 80)
print("PHẦN 3: PHÂN BỐ CÁC HÀNH VI (INTENT & RESOLVED_TOOL) THEO THỜI GIAN (PERSONA VS NO-PERSONA)")
print("=" * 80)

# Gom nhóm hành vi thành các Macro-Behaviors chính để dễ quan sát phân phối:
# 1. Khám phá & Cuộn: scroll
# 2. Đọc sâu: read
# 3. Tương tác / Phản ứng: react, like_page, share
# 4. Tìm kiếm chủ đề: search
# 5. Mở chi tiết / Điều hướng: open, home, back, close
# 6. Quan sát trạng thái: observe
# 7. Kết thúc phiên: end_episode / session_status / rest

def map_macro_behavior(row):
    intent = str(row.get("intent", "")).lower()
    tool = str(row.get("tool", "")).lower()
    res = str(row.get("resolved_tool", "")).lower()
    
    if tool == "end_episode" or res == "end_episode":
        return "7. Kết thúc phiên (End Session)"
    if tool in ["rest", "wait_for_feed"]:
        return "8. Nghỉ ngơi & Đợi (Rest/Wait)"
    if intent == "read" or "read" in res:
        return "2. Đọc sâu bài viết (Deep Read)"
    if intent in ["react", "share", "like_page"] or "react" in res:
        return "3. Tương tác xã hội (React/Social)"
    if intent == "search" or "search" in res:
        return "4. Tìm kiếm chủ đề (Search Query)"
    if intent == "scroll" or "scroll" in res:
        return "1. Cuộn & Duyệt lướt (Scroll Feed)"
    if intent in ["open", "home", "back", "close"] or res in ["return_home", "close_detail", "open_search_result", "back_to_discovery"]:
        return "5. Điều hướng giao diện (Navigate/Open/Close)"
    if intent == "observe" or "observe" in res:
        return "6. Quan sát màn hình (Observe Viewport)"
    return "9. Khác (Other)"

df_steps["macro_behavior"] = df_steps.apply(map_macro_behavior, axis=1)

print("\nTỷ lệ phân bố Macro-Behavior theo 4 giai đoạn ở PERSONA (%):")
ct_p = pd.crosstab(df_steps[df_steps["dataset_type"] == "persona"]["time_bin_4"], df_steps[df_steps["dataset_type"] == "persona"]["macro_behavior"], normalize="index") * 100
print(ct_p.round(1).to_string())

print("\nTỷ lệ phân bố Macro-Behavior theo 4 giai đoạn ở NO-PERSONA (%):")
ct_np = pd.crosstab(df_steps[df_steps["dataset_type"] == "no_persona"]["time_bin_4"], df_steps[df_steps["dataset_type"] == "no_persona"]["macro_behavior"], normalize="index") * 100
print(ct_np.round(1).to_string())
