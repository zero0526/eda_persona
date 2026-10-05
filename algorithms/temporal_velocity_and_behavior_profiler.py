"""
Module: temporal_velocity_and_behavior_profiler.py
Mục đích:
1. Thống kê tốc độ thực thi hành động (context_action_velocity) biến đổi theo thời gian (4 giai đoạn Q1-Q4).
2. Phân tích tương quan giữa quỹ đạo biến đổi vận tốc với thuộc tính pace trong facebook behavior (quick, balanced, slow) cho nhóm Persona.
3. Thống kê phân bố các macro-behavior theo thời gian biến đổi, đối sánh giữa Persona và No-Persona.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path


def compute_temporal_velocity_by_pace(df_steps: pd.DataFrame) -> Dict[str, Any]:
    """
    Phân tích vận tốc thực thi hành động theo 4 giai đoạn tiến trình phiên
    và kiểm định sự phân hóa theo thuộc tính persona_pace.
    """
    df = df_steps.copy()
    
    # 1. Tính toán trục thời gian chuẩn hóa (Normalized Time)
    df["total_steps_ep"] = df.groupby("episode_id")["step_index"].transform("count")
    df["step_progress"] = df["step_index"] / df["total_steps_ep"]
    
    df["time_bin_4"] = pd.cut(
        df["step_progress"],
        bins=[0.0, 0.25, 0.50, 0.75, 1.0001],
        labels=["Q1 (0-25% Early)", "Q2 (25-50% Mid-Early)", "Q3 (50-75% Mid-Late)", "Q4 (75-100% Late)"]
    )
    
    # 2. Vận tốc theo nhóm tổng thể (Persona vs No-Persona)
    vel_by_group = df.groupby(["dataset_type", "time_bin_4"], observed=False)["context_action_velocity"].agg(
        count="count",
        mean="mean",
        std="std",
        median="median",
        iqr=lambda x: float(x.quantile(0.75) - x.quantile(0.25))
    ).reset_index()
    
    # 3. Phân tích riêng nhóm Persona theo persona_pace
    p_df = df[df["dataset_type"] == "persona"].copy()
    vel_by_pace = p_df.groupby(["persona_pace", "time_bin_4"], observed=False)["context_action_velocity"].agg(
        count="count",
        mean="mean",
        std="std",
        median="median",
        iqr=lambda x: float(x.quantile(0.75) - x.quantile(0.25))
    ).reset_index()
    
    # 4. Kiểm định Kruskal-Wallis giữa các nhóm pace tại từng giai đoạn
    kw_records = []
    for q in ["Q1 (0-25% Early)", "Q2 (25-50% Mid-Early)", "Q3 (50-75% Mid-Late)", "Q4 (75-100% Late)"]:
        sub_q = p_df[p_df["time_bin_4"] == q]
        groups = [g["context_action_velocity"].dropna().values for _, g in sub_q.groupby("persona_pace")]
        h_stat, p_val = stats.kruskal(*groups)
        kw_records.append({
            "phase": q,
            "kruskal_h": round(float(h_stat), 3),
            "p_value": float(p_val),
            "is_significant": bool(p_val < 0.05)
        })
    df_kw = pd.DataFrame(kw_records)
    
    # 5. Kiểm định biến đổi nội bộ từng nhóm Pace (Q1 Early vs Q4 Late)
    internal_records = []
    for pace in ["quick", "balanced", "slow"]:
        sub_p = p_df[p_df["persona_pace"] == pace]
        v_q1 = sub_p[sub_p["time_bin_4"] == "Q1 (0-25% Early)"]["context_action_velocity"].dropna()
        v_q4 = sub_p[sub_p["time_bin_4"] == "Q4 (75-100% Late)"]["context_action_velocity"].dropna()
        u_stat, p_val = stats.mannwhitneyu(v_q1, v_q4)
        n1, n2 = len(v_q1), len(v_q4)
        cliffs_d = float((2 * u_stat) / (n1 * n2) - 1) if n1 * n2 > 0 else 0.0
        internal_records.append({
            "persona_pace": pace,
            "q1_mean": round(float(v_q1.mean()), 2),
            "q4_mean": round(float(v_q4.mean()), 2),
            "diff_q4_minus_q1": round(float(v_q4.mean() - v_q1.mean()), 2),
            "mann_whitney_u": float(u_stat),
            "p_value": float(p_val),
            "cliffs_delta": round(cliffs_d, 3),
            "effect_size": "Large" if abs(cliffs_d) >= 0.474 else ("Medium" if abs(cliffs_d) >= 0.33 else "Small")
        })
    df_internal = pd.DataFrame(internal_records)
    
    return {
        "df_processed": df,
        "vel_by_group": vel_by_group,
        "vel_by_pace": vel_by_pace,
        "kruskal_wallis_by_phase": df_kw,
        "internal_pace_evolution": df_internal
    }


def compute_temporal_behavior_distribution(df_steps_processed: pd.DataFrame) -> Dict[str, Any]:
    """
    Thống kê phân bố của các macro-behavior theo 4 giai đoạn thời gian,
    đối sánh riêng cho nhóm Persona và nhóm No-Persona.
    """
    df = df_steps_processed.copy()
    
    def map_macro_behavior(row):
        intent = str(row.get("intent", "")).lower()
        tool = str(row.get("tool", "")).lower()
        res = str(row.get("resolved_tool", "")).lower()
        
        if tool == "end_episode" or res == "end_episode":
            return "7. Kết thúc phiên (End Session)"
        if tool in ["rest", "wait_for_feed"]:
            return "8. Nghỉ ngơi / Đợi (Rest/Wait)"
        if intent == "read" or "read" in res:
            return "2. Đọc sâu bài viết (Deep Read)"
        if intent in ["react", "share", "like_page"] or "react" in res:
            return "3. Tương tác xã hội (React/Social)"
        if intent == "search" or "search" in res:
            return "4. Tìm kiếm chủ đề (Search Query)"
        if intent == "scroll" or "scroll" in res:
            return "1. Cuộn & Duyệt lướt (Scroll Feed)"
        if intent in ["open", "home", "back", "close"] or res in ["return_home", "close_detail", "open_search_result", "back_to_discovery"]:
            return "5. Điều hướng giao diện (Navigate)"
        if intent == "observe" or "observe" in res:
            return "6. Quan sát màn hình (Observe)"
        return "9. Khác (Other)"
    
    df["macro_behavior"] = df.apply(map_macro_behavior, axis=1)
    
    # Bảng chéo Persona
    p_df = df[df["dataset_type"] == "persona"]
    ct_p = pd.crosstab(p_df["time_bin_4"], p_df["macro_behavior"], normalize="index") * 100
    
    # Bảng chéo No-Persona
    no_p_df = df[df["dataset_type"] == "no_persona"]
    ct_np = pd.crosstab(no_p_df["time_bin_4"], no_p_df["macro_behavior"], normalize="index") * 100
    
    # Đảm bảo đủ các cột cho cả 2 bảng
    all_cols = sorted(list(set(ct_p.columns).union(set(ct_np.columns))))
    ct_p = ct_p.reindex(columns=all_cols, fill_value=0.0)
    ct_np = ct_np.reindex(columns=all_cols, fill_value=0.0)
    
    # Bảng gộp so sánh
    merged_records = []
    for q in ct_p.index:
        for beh in all_cols:
            merged_records.append({
                "phase": q,
                "macro_behavior": beh,
                "persona_pct": round(float(ct_p.loc[q, beh]), 1),
                "no_persona_pct": round(float(ct_np.loc[q, beh]), 1),
                "diff_pct (Persona - NoPersona)": round(float(ct_p.loc[q, beh] - ct_np.loc[q, beh]), 1)
            })
    df_beh_comparison = pd.DataFrame(merged_records)
    
    return {
        "crosstab_persona": ct_p,
        "crosstab_nopersona": ct_np,
        "behavior_comparison_table": df_beh_comparison
    }
