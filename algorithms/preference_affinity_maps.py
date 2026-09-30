"""Thuật toán phân tích bản đồ ái lực và xung đột thị hiếu Persona (Preference Affinity Maps).

Cung cấp các phương pháp tính toán ma trận đồng xuất hiện (Co-occurrence) và chuẩn hóa liên kết:
1. Liked × Liked -> Affinity Map: Đo lường mức độ các chủ đề thường xuyên được yêu thích cùng nhau.
2. Disliked × Disliked -> Aversion Map: Đo lường mức độ các chủ đề thường xuyên bị né tránh/ghét cùng nhau.
3. Liked × Disliked -> Cross-Preference Map: Đo lường xung đột thị hiếu (thích chủ đề A thì thường ghét chủ đề B).

Các chỉ số chuẩn hóa:
- Co-occurrence Count: Số lượng Persona đồng thời có cặp trạng thái.
- Jaccard Similarity: |A ∩ B| / |A ∪ B|.
- Cosine / Ochiai Similarity: |A ∩ B| / sqrt(|A| * |B|).
- Lift / PMI: P(A ∩ B) / (P(A) * P(B)) = (C(A, B) * N) / (C(A) * C(B)).
- Delta P: P(B | A) - P_base(B) (Mức tăng xác suất có điều kiện).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Union, Any
import numpy as np
import pandas as pd


def binarize_preferences(
    series_of_lists: Union[pd.Series, List[List[str]]],
    min_support: int = 1,
    top_k: Optional[int] = None,
) -> pd.DataFrame:
    """Chuyển đổi một Series/List các danh sách chủ đề thành ma trận nhị phân One-Hot (N x M).

    Parameters
    ----------
    series_of_lists : Union[pd.Series, List[List[str]]]
        Dữ liệu đầu vào, mỗi phần tử là một danh sách string (ví dụ: df['strong'] hoặc df['avoid']).
    min_support : int, default=1
        Số lần xuất hiện tối thiểu để giữ lại một chủ đề.
    top_k : Optional[int], optional
        Chỉ giữ lại K chủ đề xuất hiện nhiều nhất (nếu truyền vào).

    Returns
    -------
    pd.DataFrame
        Ma trận nhị phân (N hàng x M cột chủ đề), giá trị thuộc {0, 1}.
    """
    raw_lists = list(series_of_lists)
    all_items = [item for sublist in raw_lists if isinstance(sublist, (list, set, tuple)) for item in sublist]
    
    from collections import Counter
    counts = Counter(all_items)
    
    # Lọc theo min_support
    selected = [item for item, c in counts.items() if c >= min_support]
    
    # Sắp xếp giảm dần theo tần suất
    selected.sort(key=lambda x: counts[x], reverse=True)
    
    if top_k is not None and top_k > 0:
        selected = selected[:top_k]
        
    rows = []
    for lst in raw_lists:
        item_set = set(lst) if isinstance(lst, (list, set, tuple)) else set()
        rows.append({item: (1 if item in item_set else 0) for item in selected})
        
    return pd.DataFrame(rows)


def compute_affinity_map(
    liked_series: Union[pd.Series, List[List[str]]],
    min_support: int = 2,
    top_k: Optional[int] = 15,
    metric: str = "lift",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Tính toán Bản đồ Ái lực (Affinity Map: Liked × Liked).

    Parameters
    ----------
    liked_series : Union[pd.Series, List[List[str]]]
        Danh sách các chủ đề được thích (ví dụ: df['strong']).
    min_support : int, default=2
        Số lần xuất hiện tối thiểu của một chủ đề trong tập dữ liệu.
    top_k : Optional[int], default=15
        Số lượng chủ đề phổ biến nhất để đưa vào ma trận.
    metric : str, default='lift'
        Chỉ số dùng làm giá trị trong ma trận vuông: 'lift', 'jaccard', 'cosine', hoặc 'count'.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        - matrix_df: Ma trận vuông (K x K) chứa giá trị theo metric chỉ định, dùng vẽ Heatmap.
        - edges_df: Bảng danh sách các cặp quan hệ kèm đầy đủ chỉ số [topic_a, topic_b, count, jaccard, cosine, lift].
    """
    bin_df = binarize_preferences(liked_series, min_support=min_support, top_k=top_k)
    n = len(bin_df)
    if n == 0 or bin_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    topics = bin_df.columns.tolist()
    mat = bin_df.to_numpy(dtype=float)
    
    # Tính ma trận đồng xuất hiện bằng tích vô hướng
    cooccur = mat.T @ mat
    freqs = np.diag(cooccur)
    k = len(topics)

    # Khởi tạo ma trận kết quả
    res_mat = np.zeros((k, k), dtype=float)
    edges: List[Dict[str, Any]] = []

    for i in range(k):
        for j in range(k):
            c_ij = cooccur[i, j]
            f_i = freqs[i]
            f_j = freqs[j]

            if i == j:
                jaccard = 1.0
                cosine = 1.0
                lift = (n / f_i) if f_i > 0 else 1.0
            else:
                union = f_i + f_j - c_ij
                jaccard = (c_ij / union) if union > 0 else 0.0
                denom = np.sqrt(f_i * f_j)
                cosine = (c_ij / denom) if denom > 0 else 0.0
                lift = (c_ij * n) / (f_i * f_j) if (f_i * f_j) > 0 else 0.0

            if metric == "jaccard":
                res_mat[i, j] = jaccard
            elif metric == "cosine":
                res_mat[i, j] = cosine
            elif metric == "count":
                res_mat[i, j] = c_ij
            else:  # 'lift'
                res_mat[i, j] = lift

            # Lưu edges cho nửa trên tam giác (i < j)
            if i < j and c_ij > 0:
                edges.append({
                    "topic_a": topics[i],
                    "topic_b": topics[j],
                    "cooccur_count": int(c_ij),
                    "support_a": int(f_i),
                    "support_b": int(f_j),
                    "jaccard": round(jaccard, 4),
                    "cosine": round(cosine, 4),
                    "lift": round(lift, 3),
                })

    matrix_df = pd.DataFrame(res_mat, index=topics, columns=topics)
    edges_df = pd.DataFrame(edges)
    if not edges_df.empty:
        sort_col = metric if metric in edges_df.columns else "lift"
        edges_df = edges_df.sort_values(by=sort_col, ascending=False).reset_index(drop=True)

    return matrix_df, edges_df


def compute_aversion_map(
    avoided_series: Union[pd.Series, List[List[str]]],
    min_support: int = 2,
    top_k: Optional[int] = 15,
    metric: str = "lift",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Tính toán Bản đồ Né tránh Đồng thời (Aversion Map: Disliked × Disliked).

    Parameters
    ----------
    avoided_series : Union[pd.Series, List[List[str]]]
        Danh sách các chủ đề bị né tránh (ví dụ: df['avoid']).
    min_support : int, default=2
        Số lần xuất hiện tối thiểu của một chủ đề trong tập né tránh.
    top_k : Optional[int], default=15
        Số lượng chủ đề né tránh phổ biến nhất đưa vào ma trận.
    metric : str, default='lift'
        Chỉ số dùng làm giá trị trong ma trận: 'lift', 'jaccard', 'cosine', hoặc 'count'.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        - matrix_df: Ma trận vuông (K x K), dùng vẽ Heatmap.
        - edges_df: Bảng các cặp chủ đề đồng né tránh kèm đầy đủ chỉ số.
    """
    return compute_affinity_map(
        liked_series=avoided_series,
        min_support=min_support,
        top_k=top_k,
        metric=metric,
    )


def compute_cross_preference_map(
    liked_series: Union[pd.Series, List[List[str]]],
    avoided_series: Union[pd.Series, List[List[str]]],
    min_support_liked: int = 2,
    min_support_avoided: int = 2,
    top_k_liked: Optional[int] = 12,
    top_k_avoided: Optional[int] = 12,
    metric: str = "lift",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Tính toán Bản đồ Xung đột Thị hiếu (Cross-Preference Map: Liked × Disliked).

    Xác định mối liên hệ giữa việc thích chủ đề A và né tránh chủ đề B.
    - Cross-Lift > 1.0: Thích A làm tăng nguy cơ né tránh B (Xung đột thị hiếu mạnh).
    - Cross-Lift < 1.0: Thích A và né tránh B ít khi xảy ra cùng lúc (Tương thích ngầm).
    - Cross-Lift = 0.0: Thích A thì không bao giờ né B.

    Parameters
    ----------
    liked_series : Union[pd.Series, List[List[str]]]
        Danh sách chủ đề được thích (Liked / strong).
    avoided_series : Union[pd.Series, List[List[str]]]
        Danh sách chủ đề bị né tránh (Disliked / avoid).
    min_support_liked : int, default=2
        Ngưỡng xuất hiện tối thiểu của chủ đề thích.
    min_support_avoided : int, default=2
        Ngưỡng xuất hiện tối thiểu của chủ đề né.
    top_k_liked : Optional[int], default=12
        Số lượng top chủ đề thích.
    top_k_avoided : Optional[int], default=12
        Số lượng top chủ đề né.
    metric : str, default='lift'
        Chỉ số trong ma trận: 'lift', 'delta_p', 'cosine', hoặc 'count'.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        - matrix_df: Ma trận chữ nhật (K_liked x K_avoided), dùng vẽ Bipartite Heatmap.
        - pairs_df: Bảng các cặp Liked x Disliked sắp xếp giảm dần theo xung đột.
    """
    bin_liked = binarize_preferences(liked_series, min_support=min_support_liked, top_k=top_k_liked)
    bin_avoided = binarize_preferences(avoided_series, min_support=min_support_avoided, top_k=top_k_avoided)

    n = len(bin_liked)
    if n == 0 or bin_liked.empty or bin_avoided.empty:
        return pd.DataFrame(), pd.DataFrame()

    liked_topics = bin_liked.columns.tolist()
    avoided_topics = bin_avoided.columns.tolist()

    mat_l = bin_liked.to_numpy(dtype=float)
    mat_a = bin_avoided.to_numpy(dtype=float)

    # Cross co-occurrence
    cross_cooccur = mat_l.T @ mat_a  # K_l x K_a
    freq_l = mat_l.sum(axis=0)       # K_l
    freq_a = mat_a.sum(axis=0)       # K_a

    res_mat = np.zeros((len(liked_topics), len(avoided_topics)), dtype=float)
    pairs: List[Dict[str, Any]] = []

    for i, l_top in enumerate(liked_topics):
        for j, a_top in enumerate(avoided_topics):
            c_la = cross_cooccur[i, j]
            f_l = freq_l[i]
            f_a = freq_a[j]

            # Cross-Lift
            cross_lift = (c_la * n) / (f_l * f_a) if (f_l * f_a) > 0 else 0.0
            
            # Delta P: P(avoided | liked) - P_base(avoided)
            p_cond = (c_la / f_l) if f_l > 0 else 0.0
            p_base = (f_a / n) if n > 0 else 0.0
            delta_p = p_cond - p_base

            # Cosine similarity
            denom = np.sqrt(f_l * f_a)
            cosine = (c_la / denom) if denom > 0 else 0.0

            if metric == "lift":
                res_mat[i, j] = cross_lift
            elif metric == "delta_p":
                res_mat[i, j] = delta_p
            elif metric == "cosine":
                res_mat[i, j] = cosine
            else:  # count
                res_mat[i, j] = c_la

            if c_la > 0:
                pairs.append({
                    "liked_topic": l_top,
                    "avoided_topic": a_top,
                    "cross_count": int(c_la),
                    "liked_support": int(f_l),
                    "avoided_support": int(f_a),
                    "p_cond": round(p_cond, 4),
                    "p_base": round(p_base, 4),
                    "delta_p": round(delta_p, 4),
                    "cross_lift": round(cross_lift, 3),
                })

    matrix_df = pd.DataFrame(res_mat, index=liked_topics, columns=avoided_topics)
    pairs_df = pd.DataFrame(pairs)
    if not pairs_df.empty:
        sort_col = "cross_lift" if metric == "lift" else ("delta_p" if metric == "delta_p" else "cross_count")
        pairs_df = pairs_df.sort_values(by=sort_col, ascending=False).reset_index(drop=True)

    return matrix_df, pairs_df
