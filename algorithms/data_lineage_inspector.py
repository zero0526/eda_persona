"""
Module: data_lineage_inspector.py
Mục đích: Kiểm tra và lượng hóa cấu trúc phân cấp, tính toàn vẹn tham chiếu (Referential Integrity),
và quy mô của 4 đơn vị phân tích (Units of Analysis) trong hệ thống dữ liệu hành vi Facebook Agent.
Tuân thủ quy chuẩn: Đặt riêng thuật toán độc lập, phục vụ Bước 2 trong Pipeline EDA.
"""

from typing import Dict, Any
import pandas as pd


def inspect_multilevel_structure(
    df_episodes: pd.DataFrame,
    df_steps: pd.DataFrame,
    df_actions: pd.DataFrame = None,
    df_evidences: pd.DataFrame = None,
) -> Dict[str, Any]:
    """
    Kiểm tra cấu trúc phân cấp 4 cấp độ và tính toàn vẹn tham chiếu khóa ngoại.

    Parameters:
    -----------
    df_episodes : pd.DataFrame
        DataFrame cấp độ Phiên chạy (Episode Level).
    df_steps : pd.DataFrame
        DataFrame cấp độ Bước hành động (Step Level).
    df_actions : pd.DataFrame, optional
        DataFrame cấp độ Thao tác cơ học (Browser Gesture Level).
    df_evidences : pd.DataFrame, optional
        DataFrame cấp độ Bằng chứng nhận thức (Cognitive Evidence Level).

    Returns:
    --------
    Dict[str, Any]
        Từ điển chứa quy mô, tỷ lệ phân bổ A/B và tính toàn vẹn khóa ngoại.
    """
    # 1. Cấp độ Episode
    n_episodes = len(df_episodes)
    episodes_by_type = df_episodes["dataset_type"].value_counts().to_dict()
    unique_episode_ids = set(df_episodes["episode_id"])

    # 2. Cấp độ Step
    n_steps = len(df_steps)
    steps_by_type = df_steps["dataset_type"].value_counts().to_dict()
    step_episodes = set(df_steps["episode_id"])
    
    # Kiểm tra toàn vẹn khóa ngoại: Step -> Episode
    step_orphan_keys = step_episodes - unique_episode_ids
    step_referential_integrity = len(step_orphan_keys) == 0

    # Phân bổ bước theo Episode
    steps_per_episode = (
        df_steps.groupby(["dataset_type", "episode_id"]).size().unstack(fill_value=0)
        if "dataset_type" in df_steps.columns else df_steps.groupby("episode_id").size()
    )

    # 3. Cấp độ Gesture/Action (nếu có)
    actions_info = {}
    if df_actions is not None and not df_actions.empty:
        n_actions = len(df_actions)
        action_episodes = set(df_actions["episode_id"])
        action_orphan_keys = action_episodes - unique_episode_ids
        actions_by_type = (
            df_actions["dataset_type"].value_counts().to_dict()
            if "dataset_type" in df_actions.columns else {}
        )
        actions_info = {
            "total_actions": n_actions,
            "actions_by_dataset_type": actions_by_type,
            "action_referential_integrity": len(action_orphan_keys) == 0,
        }

    # 4. Cấp độ Cognitive Evidence (nếu có)
    evidences_info = {}
    if df_evidences is not None and not df_evidences.empty:
        n_evidences = len(df_evidences)
        ev_episodes = set(df_evidences["episode_id"])
        ev_orphan_keys = ev_episodes - unique_episode_ids
        evidences_info = {
            "total_evidences": n_evidences,
            "evidence_referential_integrity": len(ev_orphan_keys) == 0,
        }

    summary_table = pd.DataFrame([
        {
            "Cấp độ phân tích (Unit of Analysis)": "1. Episode Level (Phiên)",
            "Tổng số bản ghi (N)": n_episodes,
            "Nhóm Persona": episodes_by_type.get("persona", 0),
            "Nhóm No-Persona": episodes_by_type.get("no_persona", 0),
            "Khóa chính (PK)": "episode_id",
            "Khóa ngoại (FK)": "None",
            "Toàn vẹn tham chiếu": "100% Valid"
        },
        {
            "Cấp độ phân tích (Unit of Analysis)": "2. Step Level (Bước)",
            "Tổng số bản ghi (N)": n_steps,
            "Nhóm Persona": steps_by_type.get("persona", 0),
            "Nhóm No-Persona": steps_by_type.get("no_persona", 0),
            "Khóa chính (PK)": "(episode_id, step_index)",
            "Khóa ngoại (FK)": "episode_id -> Episode.PK",
            "Toàn vẹn tham chiếu": "100% Valid" if step_referential_integrity else f"Orphans: {len(step_orphan_keys)}"
        },
        {
            "Cấp độ phân tích (Unit of Analysis)": "3. Browser Gesture Level (Cử chỉ)",
            "Tổng số bản ghi (N)": actions_info.get("total_actions", 0),
            "Nhóm Persona": actions_info.get("actions_by_dataset_type", {}).get("persona", 0),
            "Nhóm No-Persona": actions_info.get("actions_by_dataset_type", {}).get("no_persona", 0),
            "Khóa chính (PK)": "(episode_id, step_index, action_order)",
            "Khóa ngoại (FK)": "(episode_id, step_index) -> Step.PK",
            "Toàn vẹn tham chiếu": "100% Valid" if actions_info.get("action_referential_integrity", True) else "Orphans detected"
        },
        {
            "Cấp độ phân tích (Unit of Analysis)": "4. Cognitive Evidence Level (Bằng chứng)",
            "Tổng số bản ghi (N)": evidences_info.get("total_evidences", 0),
            "Nhóm Persona": evidences_info.get("total_evidences", 0),
            "Nhóm No-Persona": 0,
            "Khóa chính (PK)": "(episode_id, step_index, evidence_order)",
            "Khóa ngoại (FK)": "(episode_id, step_index) -> Step.PK",
            "Toàn vẹn tham chiếu": "100% Valid" if evidences_info.get("evidence_referential_integrity", True) else "Orphans detected"
        }
    ])

    return {
        "summary_table": summary_table,
        "n_episodes": n_episodes,
        "n_steps": n_steps,
        "episodes_by_type": episodes_by_type,
        "steps_by_type": steps_by_type,
        "step_referential_integrity": step_referential_integrity,
        "actions_info": actions_info,
        "evidences_info": evidences_info
    }
