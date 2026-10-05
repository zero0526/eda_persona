"""Package chứa các thuật toán thống kê và khoa học dữ liệu chuyên sâu cho EDA Persona.

Các thuật toán được module hóa từ pipeline phân tích khảo sát Persona (D >> N, Confounding & LLM Noise):
1. pairwise_cramers_v: Tính Bergsma's bias-corrected Cramér's V̂ cho biến categorical.
2. wilson_score_interval: Khoảng tin cậy 95% Wilson Score cho tỷ lệ nhị thức.
3. jensen_shannon_divergence: Đo khoảng cách phân phối xác suất P(Y|X=v) vs P(Y).
4. cochran_armitage_trend: Kiểm định xu hướng đơn điệu cho biến thứ bậc (ordinal).
5. standardized_residuals: Phần dư chuẩn hóa Haberman (z_vc) cho bảng contingency table.
6. fast_chi2_independence: Kiểm định Chi-square độc lập vector hóa tốc độ cao.
7. permutation_cramers_v: Kiểm định hoán vị Cramér's V xác định ngưỡng P95 phân phối Null.
8. benjamini_hochberg_fdr: Kiểm soát tỷ lệ phát hiện sai (FDR) cho đa kiểm định giả thuyết.
9. delta_p_lift: Đo lường mức độ tác động Delta P, Lift, Support kèm Wilson CI.
10. multivariate_driver_proxy: Tách biệt Confirmed Driver khỏi Likely Proxy bằng Random Forest.
"""

from algorithms.pairwise_cramers_v import (
    compute_pairwise_cramers_v,
    fast_bias_corrected_cramers_v_from_codes,
)
from algorithms.wilson_score_interval import wilson_score_interval
from algorithms.jensen_shannon_divergence import jensen_shannon_divergence
from algorithms.cochran_armitage_trend import cochran_armitage_trend_test
from algorithms.standardized_residuals import compute_standardized_residuals
from algorithms.fast_chi2_independence import (
    fast_chi2_from_codes,
    fast_chi2_independence_test,
)
from algorithms.permutation_cramers_v import (
    permutation_cramers_v_series,
    permutation_cramers_v_test,
)
from algorithms.benjamini_hochberg_fdr import benjamini_hochberg_fdr
from algorithms.delta_p_lift import compute_delta_p_lift_table
from algorithms.multivariate_driver_proxy import classify_driver_vs_proxy
from algorithms.preference_affinity_maps import (
    binarize_preferences,
    compute_affinity_map,
    compute_aversion_map,
    compute_cross_preference_map,
)
from algorithms.contrastive_topic_profiler import (
    find_contrasting_origin_features,
    get_topic_contrast_matrix,
    plot_contrasting_features,
    EXPLAINABLE_ORIGIN_FEATURES,
    FEATURE_LABELS,
)

from algorithms.bivariate_multivariate_profiler import (
    compute_mutual_information,
    compare_numeric_by_group,
    compare_categorical_by_group,
    compute_correlation_matrices,
    compute_pairwise_cramers_v_matrix,
    compare_categorical_numeric_associations,
    compute_multivariate_decomposition,
    analyze_interactions_and_simpson_paradox,
)
from algorithms.drift_and_rest_statistical_profiler import (
    evaluate_temporal_drift_trajectory,
    evaluate_guardrail_warning_recovery,
    evaluate_rest_fatigue_dynamics,
    run_full_statistical_investigation,
)
from algorithms.persona_interest_coverage_profiler import (
    compute_persona_topic_coverage,
)
from algorithms.temporal_velocity_and_behavior_profiler import (
    compute_temporal_velocity_by_pace,
    compute_temporal_behavior_distribution,
)

__all__ = [
    "compute_pairwise_cramers_v",
    "fast_bias_corrected_cramers_v_from_codes",
    "wilson_score_interval",
    "jensen_shannon_divergence",
    "cochran_armitage_trend_test",
    "compute_standardized_residuals",
    "fast_chi2_from_codes",
    "fast_chi2_independence_test",
    "permutation_cramers_v_series",
    "permutation_cramers_v_test",
    "benjamini_hochberg_fdr",
    "compute_delta_p_lift_table",
    "classify_driver_vs_proxy",
    "binarize_preferences",
    "compute_affinity_map",
    "compute_aversion_map",
    "compute_cross_preference_map",
    "find_contrasting_origin_features",
    "get_topic_contrast_matrix",
    "plot_contrasting_features",
    "EXPLAINABLE_ORIGIN_FEATURES",
    "FEATURE_LABELS",
    "compute_mutual_information",
    "compare_numeric_by_group",
    "compare_categorical_by_group",
    "compute_correlation_matrices",
    "compute_pairwise_cramers_v_matrix",
    "compare_categorical_numeric_associations",
    "compute_multivariate_decomposition",
    "analyze_interactions_and_simpson_paradox",
    "evaluate_temporal_drift_trajectory",
    "evaluate_guardrail_warning_recovery",
    "evaluate_rest_fatigue_dynamics",
    "run_full_statistical_investigation",
    "compute_persona_topic_coverage",
    "compute_temporal_velocity_by_pace",
    "compute_temporal_behavior_distribution",
]
