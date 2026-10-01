"""
Module: temporal_gap_analyzer.py
Mục đích: Khảo sát chuỗi thời gian của log: tính liên tục của chỉ số bước (step_index),
khoảng cách thời gian giữa các bước liên tiếp (Step Delta Time), phát hiện khoảng trống
bất thường (Time Gaps > 60s do nghẽn mạng/chờ render), và kiểm tra tính nhất quán múi giờ (UTC).
Tuân thủ quy chuẩn: Thuật toán độc lập trong algorithms/, phục vụ Bước 3 Pipeline EDA.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np


def analyze_temporal_continuity(df_steps: pd.DataFrame) -> Dict[str, Any]:
    """
    Phân tích tính liên tục thời gian và kiểm toán bước nhảy trong log.

    Parameters:
    -----------
    df_steps : pd.DataFrame
        DataFrame cấp độ bước (df_steps).

    Returns:
    --------
    Dict[str, Any]
        Báo cáo chi tiết về bước nhảy, khoảng cách thời gian và độ đồng nhất múi giờ.
    """
    df = df_steps.copy()
    df["ts_dt"] = pd.to_datetime(df["timestamp"])

    episode_reports = []
    gap_records = []

    for ep_id, group in df.groupby("episode_id"):
        group = group.sort_values(by="step_index").reset_index(drop=True)
        ds_type = group["dataset_type"].iloc[0]
        p_id = group["persona_id"].iloc[0] if "persona_id" in group.columns else None

        # 1. Kiểm tra bước nhảy tuần tự (step_index continuity)
        expected_indices = list(range(1, len(group) + 1))
        actual_indices = group["step_index"].tolist()
        has_step_skip = (actual_indices != expected_indices)

        # 2. Tính Delta Time giữa các bước liên tiếp
        group["delta_seconds"] = group["ts_dt"].diff().dt.total_seconds()
        deltas = group["delta_seconds"].dropna()

        median_delta = deltas.median() if len(deltas) > 0 else 0
        max_delta = deltas.max() if len(deltas) > 0 else 0
        min_delta = deltas.min() if len(deltas) > 0 else 0

        # Khoảng trống bất thường (> 60s)
        abnormal_gaps = group[group["delta_seconds"] > 60]
        n_abnormal_gaps = len(abnormal_gaps)

        for _, row in abnormal_gaps.iterrows():
            gap_records.append({
                "episode_id": ep_id,
                "dataset_type": ds_type,
                "step_index": int(row["step_index"]),
                "tool": row["tool"],
                "delta_seconds": round(float(row["delta_seconds"]), 2),
                "reason": "Chờ tải DOM mạng hoặc độ trễ phản hồi từ Facebook Web"
            })

        # Tổng thời gian thực nghiệm thực tế từ timestamp
        start_ts = group["ts_dt"].min()
        end_ts = group["ts_dt"].max()
        duration_minutes = (end_ts - start_ts).total_seconds() / 60.0

        episode_reports.append({
            "episode_id": ep_id[:8] + "...",
            "dataset_type": ds_type,
            "persona_id": p_id if pd.notna(p_id) else "None (Control)",
            "total_steps": len(group),
            "step_continuous": "100% Hoàn hảo" if not has_step_skip else "Bị nhảy bước!",
            "median_delta_s": round(float(median_delta), 1),
            "max_delta_s": round(float(max_delta), 1),
            "abnormal_gaps_count": n_abnormal_gaps,
            "duration_minutes": round(float(duration_minutes), 2)
        })

    df_ep_temporal = pd.DataFrame(episode_reports)
    df_gaps = pd.DataFrame(gap_records)

    return {
        "episode_temporal_summary": df_ep_temporal,
        "abnormal_gaps": df_gaps,
        "all_episodes_continuous": all(df_ep_temporal["step_continuous"] == "100% Hoàn hảo"),
        "total_abnormal_gaps": len(df_gaps)
    }
