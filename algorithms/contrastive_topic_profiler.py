"""Thuật toán phân tích đặc trưng đối lập giữa các phân khúc thị hiếu (Contrastive Topic Profiling).

Giải quyết bài toán:
Cho một chủ đề gây phân cực T (ví dụ: 'Interest: Politics' với nhóm Thích vs nhóm Né),
quét toàn bộ các thuộc tính Persona Origin (D >> N) để tìm ra các biến phân hóa mạnh nhất:
1. Phân nhóm Persona thành 2 tập: LIKED (có T trong strong) vs AVOIDED (có T trong avoid).
2. Đo lường mức độ phân hóa bằng:
   - Bergsma's Cramér's V̂ (Effect Size liên kết phi tuyến có hiệu chỉnh bias).
   - Delta P: P(X=v | Liked) - P(X=v | Avoided) (Mức chênh lệch xác suất phân bổ).
3. Trích xuất giá trị đối lập đặc trưng (Top distinguishing category) cho từng thuộc tính.
4. Trực quan hóa bằng biểu đồ phân kỳ (Diverging Bar Chart).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Union, Any
import numpy as np
import pandas as pd
from algorithms.pairwise_cramers_v import compute_pairwise_cramers_v


EXPLAINABLE_ORIGIN_FEATURES: List[str] = [
    "skepticism",
    "facebook_frequency",
    "interest_social_media",
    "attitude_social_media",
    "monthly_personal_income_band",
    "skill_fact_checking",
    "skill_critical_thinking",
    "political_lean",
    "highest_education",
    "gender_identity",
    "age_bracket",
    "reading_frequency",
    "habit_doomscrolling",
    "reading_vs_watching",
    "decision_speed",
]

FEATURE_LABELS: Dict[str, str] = {
    "skepticism": "Mức độ hoài nghi (Skepticism)",
    "facebook_frequency": "Tần suất dùng Facebook",
    "interest_social_media": "Hứng thú với MXH",
    "attitude_social_media": "Thái độ với MXH",
    "monthly_personal_income_band": "Thu nhập cá nhân hàng tháng",
    "skill_fact_checking": "Kỹ năng kiểm chứng tin tức",
    "skill_critical_thinking": "Tư duy phản biện",
    "political_lean": "Khuynh hướng chính trị",
    "highest_education": "Trình độ học vấn cao nhất",
    "gender_identity": "Giới tính",
    "age_bracket": "Độ tuổi",
    "reading_frequency": "Tần suất đọc sách báo",
    "habit_doomscrolling": "Thói quen doomscrolling",
    "reading_vs_watching": "Ưa thích đọc chữ vs xem video",
    "decision_speed": "Tốc độ ra quyết định",
}


def find_contrasting_origin_features(
    df_origin: pd.DataFrame,
    df_fb: pd.DataFrame,
    target_topic: str,
    top_n: int = 15,
    min_unique: int = 2,
    only_explainable: bool = False,
    candidate_features: Optional[List[str]] = None,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Quét thuộc tính Persona Origin để tìm các đặc trưng phân hóa mạnh nhất giữa nhóm Thích và Né.

    Parameters
    ----------
    df_origin : pd.DataFrame
        DataFrame chứa các thuộc tính gốc Persona (origin_personas), bao gồm cột 'persona_id'.
    df_fb : pd.DataFrame
        DataFrame chứa các đặc trưng hành vi Facebook, bao gồm cột 'strong' và 'avoid'.
    target_topic : str
        Tên chủ đề phân cực cần đối chiếu (ví dụ: 'Interest: Politics').
    top_n : int, default=15
        Số lượng thuộc tính phân hóa mạnh nhất cần trích xuất.
    min_unique : int, default=2
        Số lượng giá trị duy nhất tối thiểu của một thuộc tính để đưa vào phân tích.
    only_explainable : bool, default=False
        Nếu True, chỉ quét các trường nhân khẩu học, tâm lý, thói quen số dễ giải thích.
    candidate_features : Optional[List[str]], optional
        Danh sách tùy chọn các trường muốn khảo sát cụ thể.

    Returns
    -------
    Tuple[pd.DataFrame, Dict[str, Any]]
        - contrast_df: Bảng xếp hạng các thuộc tính phân hóa, kèm Cramér's V, giá trị đối lập, p_liked, p_avoided, delta_p.
        - metadata: Từ điển chứa persona_ids của nhóm Liked và nhóm Avoided.
    """
    # 1. Xác định ID của 2 nhóm
    liked_mask = df_fb["strong"].apply(lambda lst: target_topic in lst if isinstance(lst, (list, set, tuple)) else False)
    avoid_mask = df_fb["avoid"].apply(lambda lst: target_topic in lst if isinstance(lst, (list, set, tuple)) else False)

    liked_ids = df_fb.loc[liked_mask, "persona_id"].tolist()
    avoid_ids = df_fb.loc[avoid_mask, "persona_id"].tolist()

    metadata = {
        "target_topic": target_topic,
        "n_liked": len(liked_ids),
        "n_avoided": len(avoid_ids),
        "liked_ids": liked_ids,
        "avoid_ids": avoid_ids,
    }

    if len(liked_ids) == 0 or len(avoid_ids) == 0:
        return pd.DataFrame(), metadata

    # 2. Lọc dữ liệu Origin của 2 nhóm
    target_ids = set(liked_ids) | set(avoid_ids)
    sub_orig = df_origin[df_origin["persona_id"].isin(target_ids)].copy().set_index("persona_id")

    # Xác định danh sách cột cần quét
    if candidate_features is not None:
        target_cols = [c for c in candidate_features if c in sub_orig.columns]
    elif only_explainable:
        target_cols = [c for c in EXPLAINABLE_ORIGIN_FEATURES if c in sub_orig.columns]
    else:
        target_cols = [c for c in sub_orig.columns if c != "persona_id"]

    # Tạo biến nhóm phân loại Y in {'LIKE', 'AVOID'}
    group_series = pd.Series(index=sub_orig.index, dtype=str)
    for pid in sub_orig.index:
        group_series[pid] = "LIKE" if pid in liked_ids else "AVOID"

    records: List[Dict[str, Any]] = []

    # 3. Quét từng cột trong Persona Origin
    for col in target_cols:
        s = sub_orig[col].dropna()
        if s.nunique() < min_unique:
            continue

        valid_idx = s.index.intersection(group_series.index)
        if len(valid_idx) < 2:
            continue

        s_valid = s.loc[valid_idx]
        g_valid = group_series.loc[valid_idx]

        # Tính Cramér's V
        v = compute_pairwise_cramers_v(g_valid, s_valid)

        # Tính tỷ lệ phân bổ của từng giá trị trong nhóm LIKE vs AVOID
        s_liked = s_valid[g_valid == "LIKE"]
        s_avoid = s_valid[g_valid == "AVOID"]

        val_counts_l = s_liked.value_counts(normalize=True)
        val_counts_a = s_avoid.value_counts(normalize=True)
        all_vals = set(val_counts_l.index) | set(val_counts_a.index)

        # Tìm giá trị có chênh lệch xác suất (|Delta P|) cao nhất
        best_val = None
        max_abs_delta = -1.0
        best_p_l, best_p_a = 0.0, 0.0

        for val in all_vals:
            p_l = float(val_counts_l.get(val, 0.0))
            p_a = float(val_counts_a.get(val, 0.0))
            delta = p_l - p_a
            if abs(delta) > max_abs_delta:
                max_abs_delta = abs(delta)
                best_val = val
                best_p_l = p_l
                best_p_a = p_a

        delta_p = round(best_p_l - best_p_a, 3)
        direction = "Over-index in LIKE" if delta_p > 0 else "Over-index in AVOID"

        records.append({
            "feature": col,
            "cramers_v": round(v, 4),
            "contrast_value": str(best_val),
            "p_liked": round(best_p_l, 3),
            "p_avoided": round(best_p_a, 3),
            "delta_p": delta_p,
            "direction": direction,
        })

    contrast_df = pd.DataFrame(records)
    if not contrast_df.empty:
        contrast_df = contrast_df.sort_values(by=["cramers_v", "delta_p"], ascending=[False, False]).head(top_n).reset_index(drop=True)

    return contrast_df, metadata


def get_topic_contrast_matrix(
    df_origin: pd.DataFrame,
    df_fb: pd.DataFrame,
    target_topic: str,
    feature_cols: List[str],
) -> pd.DataFrame:
    """Tạo bảng so sánh chi tiết giữa các Persona nhóm Thích và Né theo các thuộc tính chỉ định.

    Parameters
    ----------
    df_origin : pd.DataFrame
        DataFrame Persona Origin.
    df_fb : pd.DataFrame
        DataFrame Facebook Persona.
    target_topic : str
        Tên chủ đề phân cực.
    feature_cols : List[str]
        Danh sách các cột thuộc tính cần đối chiếu.

    Returns
    -------
    pd.DataFrame
        Bảng so sánh chi tiết có cột 'stance' ('LIKE' vs 'AVOID') và các cột thuộc tính.
    """
    liked_ids = df_fb[df_fb["strong"].apply(lambda x: target_topic in x if isinstance(x, (list, set, tuple)) else False)]["persona_id"].tolist()
    avoid_ids = df_fb[df_fb["avoid"].apply(lambda x: target_topic in x if isinstance(x, (list, set, tuple)) else False)]["persona_id"].tolist()

    sub = df_origin[df_origin["persona_id"].isin(liked_ids + avoid_ids)].copy()
    sub["stance"] = sub["persona_id"].apply(lambda pid: "LIKE" if pid in liked_ids else "AVOID")

    cols = ["persona_id", "stance"] + [c for c in feature_cols if c in sub.columns]
    return sub[cols].sort_values(by="stance", ascending=False).reset_index(drop=True)


def plot_contrasting_features(
    contrast_df: pd.DataFrame,
    target_topic: str = "Interest: Politics",
    top_n: int = 8,
    figsize: Tuple[int, int] = (11, 6),
    show_vietnamese_labels: bool = True,
) -> Any:
    """Trực quan hóa các thuộc tính phân hóa mạnh nhất bằng Biểu đồ Thanh Phân Kỳ (Diverging Bar Chart).

    Parameters
    ----------
    contrast_df : pd.DataFrame
        Bảng kết quả từ `find_contrasting_origin_features`.
    target_topic : str, default='Interest: Politics'
        Tên chủ đề khảo sát đối lập.
    top_n : int, default=8
        Số lượng thuộc tính hiển thị (ưu tiên các trường có Cramér's V > 0 và Delta P đáng kể).
    figsize : Tuple[int, int], default=(11, 6)
        Kích thước biểu đồ (width, height).
    show_vietnamese_labels : bool, default=True
        Nếu True, kết hợp hiển thị nhãn tiếng Việt dễ hiểu.

    Returns
    -------
    matplotlib.figure.Figure
        Figure biểu đồ đã vẽ.
    """
    import matplotlib.pyplot as plt

    if contrast_df.empty:
        print("Không có dữ liệu đối lập để vẽ biểu đồ.")
        return None

    # Lọc lấy các dòng có độ phân hóa thực chất (cramers_v > 0 và delta_p != 0)
    plot_data = contrast_df[
        (contrast_df["cramers_v"] > 0) & (contrast_df["delta_p"] != 0)
    ].copy()

    if plot_data.empty:
        plot_data = contrast_df.head(top_n).copy()
    else:
        plot_data = plot_data.head(top_n).copy()

    # Sắp xếp theo delta_p để thanh hiển thị mượt mà từ âm sang dương
    plot_data = plot_data.sort_values(by="delta_p", ascending=True).reset_index(drop=True)

    # Xây dựng nhãn hiển thị: "Tên nhãn [Tên biến] = Giá trị"
    display_labels = []
    for _, row in plot_data.iterrows():
        feat = row["feature"]
        val = row["contrast_value"]
        vn_label = FEATURE_LABELS.get(feat, feat) if show_vietnamese_labels else feat
        display_labels.append(f"{vn_label}\n[{feat} = '{val}']")

    fig, ax = plt.subplots(figsize=figsize)

    colors = ["#2b7bba" if dp > 0 else "#e05338" for dp in plot_data["delta_p"]]
    bars = ax.barh(range(len(plot_data)), plot_data["delta_p"], color=colors, height=0.6, alpha=0.9, edgecolor="none")

    # Đường phân cách trung tâm tại delta_p = 0
    ax.axvline(0, color="#333333", linestyle="--", linewidth=1.2, alpha=0.7)

    # Hiển thị số liệu chi tiết lên từng thanh (luôn nằm ở bên phải của cột để không đè nhãn trục Y)
    for idx, (bar, (_, row)) in enumerate(zip(bars, plot_data.iterrows())):
        dp = row["delta_p"]
        v = row["cramers_v"]
        p_l = int(row["p_liked"] * 100)
        p_a = int(row["p_avoided"] * 100)

        text_label = f" ΔP={dp:+.2f} (Thích: {p_l}% vs Né: {p_a}%, V={v:.2f})"
        
        # Cột dương: đặt sau đầu mút (dp + 0.02)
        # Cột âm: mút phải của cột là trục 0, đặt vào khoảng trống bên phải trục 0 (0.02)
        pos_x = dp + 0.02 if dp >= 0 else 0.02
        text_color = "#1b4965" if dp >= 0 else "#8c1c13"

        ax.text(
            pos_x,
            idx,
            text_label,
            va="center",
            ha="left",  # Luôn canh trái -> văn bản trải sang phải, không bao giờ chạm nhãn Y
            fontsize=9,
            fontweight="bold",
            color=text_color,
        )

    ax.set_yticks(range(len(plot_data)))
    ax.set_yticklabels(display_labels, fontsize=9.5, fontweight="medium")

    # Giới hạn trục X: Bên trái vừa khít thanh âm (-1.15), bên phải mở rộng (+1.95) để chứa trọn vẹn text label
    min_dp = min(plot_data["delta_p"].min(), -1.0)
    max_dp = max(plot_data["delta_p"].max(), 1.0)
    ax.set_xlim(min(min_dp - 0.15, -1.15), max(max_dp + 0.95, 1.95))

    ax.set_xlabel(
        "← Nghiêng về nhóm NÉ (Over-index in AVOID)  |  Nghiêng về nhóm THÍCH (Over-index in LIKE) →\nΔP = P(Giá trị | Thích) - P(Giá trị | Né)",
        fontsize=10.5,
        fontweight="bold",
        labelpad=10,
    )
    ax.set_title(
        f"ĐẶC TRƯNG PHÂN HÓA DỄ GIẢI THÍCH: NHÓM THÍCH VS NHÓM NÉ [{target_topic.upper()}]",
        fontsize=12,
        fontweight="bold",
        pad=15,
        color="#1f2937",
    )

    ax.grid(axis="x", linestyle=":", alpha=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()

    return fig
