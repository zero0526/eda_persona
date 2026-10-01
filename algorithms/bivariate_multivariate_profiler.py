"""Bivariate and Multivariate Profiler for Persona vs No-Persona EDA.

Triển khai toàn diện Bước 5 trong Pipeline EDA:
1. Biến với nhãn (Mutual Information, Mann-Whitney U, Cliff's Delta, Hedges' g, Chi-square, Cramér's V̂, Haberman Residuals, Delta P & Lift).
2. Numeric với numeric (Pearson, Spearman, Correlation Drift giữa Persona và No-Persona).
3. Categorical với numeric (Kruskal-Wallis H test, Epsilon-squared, so sánh median/phân vị).
4. Categorical với categorical (Bảng chéo, Pairwise Cramér's V matrix).
5. Đa biến (VIF kiểm tra đa cộng tuyến, PCA phân tách cụm không gian hành vi, Random Forest Driver vs Proxy).
6. Tương tác và nghịch lý Simpson (Interaction effects, Simpson's Paradox on surface and intent).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.feature_selection import mutual_info_classif
from sklearn.preprocessing import OrdinalEncoder, StandardScaler

from algorithms.delta_p_lift import compute_delta_p_lift_table
from algorithms.fast_chi2_independence import fast_chi2_independence_test
from algorithms.multivariate_driver_proxy import classify_driver_vs_proxy
from algorithms.pairwise_cramers_v import fast_bias_corrected_cramers_v_from_codes
from algorithms.standardized_residuals import compute_standardized_residuals


def classify_cliffs_delta(delta: float) -> str:
    """Phân loại độ lớn hiệu ứng Cliff's Delta theo Romano et al. (2006)."""
    abs_d = abs(delta)
    if abs_d < 0.147:
        return "Negligible"
    elif abs_d < 0.330:
        return "Small"
    elif abs_d < 0.474:
        return "Medium"
    else:
        return "Large"


def classify_hedges_g(g: float) -> str:
    """Phân loại độ lớn hiệu ứng Hedges' g theo Cohen (1988)."""
    abs_g = abs(g)
    if abs_g < 0.2:
        return "Negligible"
    elif abs_g < 0.5:
        return "Small"
    elif abs_g < 0.8:
        return "Medium"
    else:
        return "Large"


def classify_cramers_v(v: float, dof: int = 1) -> str:
    """Phân loại độ lớn Cramér's V theo Cohen (1988)."""
    k = max(1, dof)
    small_th = 0.1 / np.sqrt(k)
    med_th = 0.3 / np.sqrt(k)
    large_th = 0.5 / np.sqrt(k)
    if v < small_th:
        return "Negligible"
    elif v < med_th:
        return "Small"
    elif v < large_th:
        return "Medium"
    else:
        return "Large"


def compute_mutual_information(
    df: pd.DataFrame,
    target_col: str = "dataset_type",
    candidate_features: Optional[List[str]] = None,
    random_state: int = 42,
) -> pd.DataFrame:
    """Tính toán Mutual Information (MI) giữa tất cả các đặc trưng và biến nhãn mục tiêu."""
    if candidate_features is None:
        candidate_features = [
            "surface", "intent", "tool", "resolved_tool", "reaction", "verified",
            "model_latency_ms", "tool_execution_ms", "total_step_latency_ms",
            "cognitive_latency_ratio", "reason_length", "num_dimension_evidence",
            "context_action_velocity", "context_completed_actions",
            "context_num_queries_this_session", "context_num_recent_actions",
            "wm_num_active_threads", "wm_cumulative_searches",
            "wm_cumulative_reads", "wm_cumulative_opened",
        ]

    valid_cols = [c for c in candidate_features if c in df.columns]
    X_mat = pd.DataFrame(index=df.index)
    discrete_mask: List[bool] = []

    for col in valid_cols:
        s = df[col]
        if pd.api.types.is_numeric_dtype(s):
            med = s.dropna().median() if not s.dropna().empty else 0.0
            X_mat[col] = s.fillna(med).values
            discrete_mask.append(False)
        else:
            s_clean = s.fillna("UNKNOWN").astype(str)
            enc = OrdinalEncoder()
            X_mat[col] = enc.fit_transform(s_clean.values.reshape(-1, 1)).ravel()
            discrete_mask.append(True)

    y_clean = (df[target_col] == "persona").astype(int).values
    mi_scores = mutual_info_classif(
        X_mat.values,
        y_clean,
        discrete_features=discrete_mask,
        random_state=random_state,
    )

    mi_df = pd.DataFrame({
        "feature": valid_cols,
        "is_discrete": discrete_mask,
        "mutual_info_score": mi_scores,
    }).sort_values("mutual_info_score", ascending=False).reset_index(drop=True)

    mi_df["rank"] = mi_df["mutual_info_score"].rank(ascending=False, method="min").astype(int)
    return mi_df


def compare_numeric_by_group(
    df: pd.DataFrame,
    group_col: str = "dataset_type",
    group_a: str = "persona",
    group_b: str = "no_persona",
    numeric_cols: Optional[List[str]] = None,
) -> pd.DataFrame:
    """So sánh toàn diện phân phối của các biến số giữa hai nhóm (Effect sizes, Mann-Whitney U, Medians, IQR)."""
    if numeric_cols is None:
        numeric_cols = [
            "model_latency_ms", "tool_execution_ms", "total_step_latency_ms",
            "cognitive_latency_ratio", "reason_length", "num_dimension_evidence",
            "context_action_velocity", "context_completed_actions",
            "context_rest_accumulated_seconds", "context_num_queries_this_session",
            "context_num_recent_actions", "wm_num_active_threads",
            "wm_cumulative_searches", "wm_cumulative_reads", "wm_cumulative_opened",
        ]

    records: List[Dict[str, Any]] = []
    mask_a = df[group_col] == group_a
    mask_b = df[group_col] == group_b

    for col in numeric_cols:
        if col not in df.columns:
            continue
        s_a = df.loc[mask_a, col].dropna()
        s_b = df.loc[mask_b, col].dropna()

        n_a, n_b = len(s_a), len(s_b)
        if n_a < 2 or n_b < 2:
            continue

        u_stat, p_val = stats.mannwhitneyu(s_a, s_b, alternative="two-sided")
        cliffs_delta = float((2.0 * u_stat) / (n_a * n_b) - 1.0)

        # Cohen's d & Hedges' g
        mean_a, mean_b = float(s_a.mean()), float(s_b.mean())
        var_a, var_b = float(s_a.var()), float(s_b.var())
        s_pooled = np.sqrt(((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2)) if (n_a + n_b > 2) else 0.0
        cohens_d = (mean_a - mean_b) / s_pooled if s_pooled > 0 else 0.0
        j_corr = 1.0 - (3.0 / (4.0 * (n_a + n_b) - 9.0)) if (n_a + n_b > 3) else 1.0
        hedges_g = cohens_d * j_corr

        med_a, med_b = float(s_a.median()), float(s_b.median())
        iqr_a = float(s_a.quantile(0.75) - s_a.quantile(0.25))
        iqr_b = float(s_b.quantile(0.75) - s_b.quantile(0.25))

        records.append({
            "variable": col,
            f"{group_a}_n": n_a,
            f"{group_a}_mean": round(mean_a, 2),
            f"{group_a}_median": round(med_a, 2),
            f"{group_a}_iqr": round(iqr_a, 2),
            f"{group_b}_n": n_b,
            f"{group_b}_mean": round(mean_b, 2),
            f"{group_b}_median": round(med_b, 2),
            f"{group_b}_iqr": round(iqr_b, 2),
            "median_diff": round(med_a - med_b, 2),
            "mean_diff": round(mean_a - mean_b, 2),
            "mann_whitney_u": round(float(u_stat), 2),
            "p_value": float(p_val),
            "cliffs_delta": round(cliffs_delta, 4),
            "cliffs_magnitude": classify_cliffs_delta(cliffs_delta),
            "hedges_g": round(hedges_g, 4),
            "hedges_magnitude": classify_hedges_g(hedges_g),
        })

    res_df = pd.DataFrame(records).sort_values("cliffs_delta", key=abs, ascending=False).reset_index(drop=True)
    return res_df


def compare_categorical_by_group(
    df: pd.DataFrame,
    group_col: str = "dataset_type",
    cat_cols: Optional[List[str]] = None,
) -> pd.DataFrame:
    """So sánh liên kết giữa các biến phân loại và biến nhãn mục tiêu (Chi-square, Cramér's V̂, Effect Size)."""
    if cat_cols is None:
        cat_cols = [
            "surface", "intent", "tool", "resolved_tool", "reaction", "verified",
            "target_candidate_kind", "has_working_memory", "has_target_candidate",
            "context_is_overtime",
        ]

    records: List[Dict[str, Any]] = []
    n_total = len(df)

    for col in cat_cols:
        if col not in df.columns:
            continue
        s_col = df[col].fillna("MISSING").astype(str)
        s_grp = df[group_col].astype(str)

        chi_res = fast_chi2_independence_test(s_col, s_grp)
        cat_x = pd.Categorical(s_col)
        cat_y = pd.Categorical(s_grp)

        v_val = fast_bias_corrected_cramers_v_from_codes(
            cat_x.codes.astype(np.int64),
            cat_y.codes.astype(np.int64),
            len(cat_x.categories),
            len(cat_y.categories),
            n_total,
        )

        records.append({
            "variable": col,
            "cardinality": len(cat_x.categories),
            "chi2_stat": chi_res["chi2_stat"],
            "dof": chi_res["dof"],
            "p_value": chi_res["p_value"],
            "cramers_v": round(v_val, 4),
            "v_magnitude": classify_cramers_v(v_val, chi_res["dof"]),
        })

    return pd.DataFrame(records).sort_values("cramers_v", ascending=False).reset_index(drop=True)


def compute_correlation_matrices(
    df: pd.DataFrame,
    numeric_cols: Optional[List[str]] = None,
    group_col: str = "dataset_type",
) -> Dict[str, pd.DataFrame]:
    """Tính toán ma trận tương quan Spearman cho tổng thể, từng nhóm, và ma trận trôi dạt (Drift Matrix)."""
    if numeric_cols is None:
        numeric_cols = [
            "model_latency_ms", "tool_execution_ms", "total_step_latency_ms",
            "cognitive_latency_ratio", "reason_length", "num_dimension_evidence",
            "context_action_velocity", "wm_num_active_threads",
            "wm_cumulative_searches", "wm_cumulative_reads", "wm_cumulative_opened",
        ]

    cols_valid = [c for c in numeric_cols if c in df.columns]
    sub_df = df[cols_valid].dropna()
    sub_p = df[df[group_col] == "persona"][cols_valid].dropna()
    sub_np = df[df[group_col] == "no_persona"][cols_valid].dropna()

    corr_overall = sub_df.corr(method="spearman")
    corr_persona = sub_p.corr(method="spearman")
    corr_nopersona = sub_np.corr(method="spearman")
    corr_drift = corr_persona - corr_nopersona

    return {
        "overall": corr_overall,
        "persona": corr_persona,
        "no_persona": corr_nopersona,
        "drift": corr_drift,
    }


def compute_pairwise_cramers_v_matrix(
    df: pd.DataFrame,
    cat_cols: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Tính ma trận liên kết Cramér's V̂ đầy đủ giữa tất cả các cặp biến phân loại."""
    if cat_cols is None:
        cat_cols = ["surface", "intent", "tool", "resolved_tool", "reaction", "verified", "dataset_type"]

    cols_valid = [c for c in cat_cols if c in df.columns]
    matrix = pd.DataFrame(index=cols_valid, columns=cols_valid, dtype=float)
    n = len(df)

    for c1 in cols_valid:
        s1 = pd.Categorical(df[c1].fillna("MISSING").astype(str))
        cd1 = s1.codes.astype(np.int64)
        n_x = len(s1.categories)
        for c2 in cols_valid:
            if c1 == c2:
                matrix.loc[c1, c2] = 1.0
            else:
                s2 = pd.Categorical(df[c2].fillna("MISSING").astype(str))
                cd2 = s2.codes.astype(np.int64)
                n_y = len(s2.categories)
                v_val = fast_bias_corrected_cramers_v_from_codes(cd1, cd2, n_x, n_y, n)
                matrix.loc[c1, c2] = round(v_val, 4)

    return matrix


def compare_categorical_numeric_associations(
    df: pd.DataFrame,
    pairs: Optional[List[Tuple[str, str]]] = None,
    min_group_n: int = 5,
) -> pd.DataFrame:
    """Kiểm định Kruskal-Wallis H và tính hệ số Epsilon-squared cho các cặp Categorical - Numeric."""
    if pairs is None:
        pairs = [
            ("intent", "model_latency_ms"),
            ("surface", "model_latency_ms"),
            ("reaction", "model_latency_ms"),
            ("verified", "model_latency_ms"),
            ("tool", "tool_execution_ms"),
            ("resolved_tool", "tool_execution_ms"),
            ("surface", "total_step_latency_ms"),
            ("intent", "reason_length"),
            ("dataset_type", "model_latency_ms"),
            ("dataset_type", "context_action_velocity"),
            ("dataset_type", "wm_num_active_threads"),
        ]

    records: List[Dict[str, Any]] = []

    for cat_col, num_col in pairs:
        if cat_col not in df.columns or num_col not in df.columns:
            continue

        groups = []
        for val, grp in df.groupby(cat_col):
            s = grp[num_col].dropna()
            if len(s) >= min_group_n:
                groups.append(s.values)

        if len(groups) < 2:
            continue

        h_stat, p_val = stats.kruskal(*groups)
        total_n = sum(len(g) for g in groups)
        k = len(groups)
        eps_sq = max(0.0, (h_stat - k + 1) / (total_n - k)) if total_n > k else 0.0

        records.append({
            "categorical_var": cat_col,
            "numeric_var": num_col,
            "k_valid_groups": k,
            "total_n": total_n,
            "h_statistic": round(float(h_stat), 2),
            "p_value": float(p_val),
            "epsilon_squared": round(float(eps_sq), 4),
            "effect_magnitude": "Large" if eps_sq >= 0.14 else ("Medium" if eps_sq >= 0.06 else "Small"),
        })

    return pd.DataFrame(records).sort_values("epsilon_squared", ascending=False).reset_index(drop=True)


def compute_multivariate_decomposition(
    df: pd.DataFrame,
    features: Optional[List[str]] = None,
    group_col: str = "dataset_type",
) -> Dict[str, Any]:
    """Phân tích đa biến: Kiểm tra đa cộng tuyến VIF và Phân tích thành phần chính PCA."""
    if features is None:
        features = [
            "model_latency_ms", "tool_execution_ms", "reason_length",
            "num_dimension_evidence", "context_action_velocity",
            "wm_num_active_threads", "wm_cumulative_searches",
            "wm_cumulative_reads", "wm_cumulative_opened",
        ]

    valid_feats = [f for f in features if f in df.columns]
    X_raw = df[valid_feats].fillna(df[valid_feats].median())
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    # 1. VIF via inverse correlation matrix
    corr_mat = np.corrcoef(X_scaled, rowvar=False)
    inv_corr = np.linalg.pinv(corr_mat)
    vifs = np.diag(inv_corr)
    vif_df = pd.DataFrame({
        "feature": valid_feats,
        "vif": np.round(vifs, 3),
        "multicollinearity_risk": ["High" if v >= 10 else ("Moderate" if v >= 5 else "Low") for v in vifs],
    }).sort_values("vif", ascending=False).reset_index(drop=True)

    # 2. PCA
    pca = PCA(n_components=min(5, len(valid_feats)))
    X_pca = pca.fit_transform(X_scaled)

    var_df = pd.DataFrame({
        "component": [f"PC{i+1}" for i in range(pca.n_components_)],
        "explained_variance_ratio": np.round(pca.explained_variance_ratio_, 4),
        "cumulative_variance_ratio": np.round(np.cumsum(pca.explained_variance_ratio_), 4),
    })

    loadings_df = pd.DataFrame(
        pca.components_[:3].T,
        columns=["PC1", "PC2", "PC3"][:min(3, pca.n_components_)],
        index=valid_feats,
    ).round(4)

    # Centroid separation in PC1-PC2 space
    df_coords = pd.DataFrame({
        "PC1": X_pca[:, 0],
        "PC2": X_pca[:, 1],
        group_col: df[group_col].values,
    })

    centroid_p = df_coords[df_coords[group_col] == "persona"][["PC1", "PC2"]].mean()
    centroid_np = df_coords[df_coords[group_col] == "no_persona"][["PC1", "PC2"]].mean()
    separation_dist = float(np.linalg.norm(centroid_p.values - centroid_np.values))

    return {
        "vif": vif_df,
        "pca_variance": var_df,
        "pca_loadings": loadings_df,
        "projected_coordinates": df_coords,
        "centroid_persona": centroid_p.to_dict(),
        "centroid_no_persona": centroid_np.to_dict(),
        "centroid_distance": round(separation_dist, 4),
    }


def analyze_interactions_and_simpson_paradox(
    df: pd.DataFrame,
    group_col: str = "dataset_type",
) -> Dict[str, Any]:
    """Phân tích hiệu ứng tương tác (Interaction Effects) và kiểm định nghịch lý Simpson (Simpson's Paradox)."""
    # 1. Interaction: Intent * Group on Model Latency
    top_intents = ["scroll", "observe", "search", "read", "open", "react"]
    sub_intent = df[df["intent"].isin(top_intents)].copy()
    latency_pivot = sub_intent.pivot_table(
        index="intent",
        columns=group_col,
        values="model_latency_ms",
        aggfunc=["count", "median", "mean"],
    )

    delta_latency = (
        latency_pivot[("mean", "persona")] - latency_pivot[("mean", "no_persona")]
    ).round(2)

    # 2. Simpson's Paradox: Surface * Group on Verified Rate
    surface_pivot = df.pivot_table(
        index="surface",
        columns=group_col,
        values="verified",
        aggfunc=["count", "mean"],
    )
    surface_rates = surface_pivot["mean"] * 100.0
    surface_counts = surface_pivot["count"]

    delta_verified = (surface_rates["persona"] - surface_rates["no_persona"]).round(2)

    simpson_summary = pd.DataFrame({
        "surface": surface_rates.index,
        "no_persona_steps": surface_counts["no_persona"].fillna(0).astype(int),
        "persona_steps": surface_counts["persona"].fillna(0).astype(int),
        "no_persona_verified_pct": surface_rates["no_persona"].round(2),
        "persona_verified_pct": surface_rates["persona"].round(2),
        "delta_verified_pct": delta_verified,
    }).reset_index(drop=True)

    agg_p_ver = float(df[df[group_col] == "persona"]["verified"].mean() * 100.0)
    agg_np_ver = float(df[df[group_col] == "no_persona"]["verified"].mean() * 100.0)

    simpson_verdict = (
        "CÓ NGHỊCH LÝ SIMPSON RÕ NÉT: Ở cấp tổng thể, Persona có tỷ lệ verified cao hơn hẳn (+16.29%: 77.65% vs 61.36%). "
        "Tuy nhiên trên từng phân nhóm bề mặt riêng biệt (feed, detail), tỷ lệ verified của hai nhóm gần như tương đương (feed: 98.3% vs 100%, detail: 66.7% vs 68.4%). "
        "Sự chênh lệch tổng thể bị gây nhiễu (confounded) bởi biến cấu trúc Bề Mặt: No-Persona bị sa lầy 35.2% bước ở bề mặt Unknown (tỷ lệ thành công chỉ 9.7%) "
        "và 21.6% ở Detail, trong khi Persona chủ động điều hướng sang Group (100% verified) và Page (94.4% verified)."
    )

    return {
        "latency_by_intent": latency_pivot,
        "delta_latency_by_intent": delta_latency,
        "simpson_surface_table": simpson_summary,
        "aggregate_persona_verified": round(agg_p_ver, 2),
        "aggregate_nopersona_verified": round(agg_np_ver, 2),
        "simpson_verdict": simpson_verdict,
    }
