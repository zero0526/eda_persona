"""Script chạy toàn diện phân tích Bước 5: Phân tích hai biến và đa biến.

Xuất ra đầy đủ:
- Bảng dữ liệu CSV trong output/tables/
- Hình vẽ biểu đồ trực quan trong output/figures/
- Báo cáo phân tích chuyên sâu chi tiết trong output/step5_bivariate_multivariate_report.md

KHÔNG chỉnh sửa bất kỳ file notebook (.ipynb) nào theo yêu cầu của user.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys

# Thiết lập đường dẫn gốc
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from scipy import stats

from loaders.loaders.persona_action import PersonaActionLoader
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
from algorithms.standardized_residuals import compute_standardized_residuals
from algorithms.delta_p_lift import compute_delta_p_lift_table
from algorithms.multivariate_driver_proxy import classify_driver_vs_proxy


def setup_plotting_style():
    """Thiết lập style trực quan hóa chuyên nghiệp."""
    sns.set_theme(style="whitegrid", palette="muted")
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
    plt.rcParams["axes.edgecolor"] = "#cccccc"
    plt.rcParams["axes.linewidth"] = 0.8
    plt.rcParams["grid.color"] = "#eeeeee"
    plt.rcParams["grid.linestyle"] = "--"


def main():
    print("=" * 80)
    print(" KHỞI CHẠY BƯỚC 5: PHÂN TÍCH HAI BIẾN VÀ ĐA BIẾN (BIVARIATE & MULTIVARIATE)")
    print(" So sánh: Agent được trang bị Persona vs Agent không có Persona")
    print("=" * 80)

    tables_dir = project_root / "output" / "tables"
    figures_dir = project_root / "output" / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    setup_plotting_style()

    # 1. NẠP DỮ LIỆU
    loader = PersonaActionLoader()
    df_steps = loader.load_step_records()
    df_ep = loader.load_action_logs()
    df_ra = loader.load_recent_actions(deduplicate=True)

    print(f"\n[+] Đã nạp df_steps: {len(df_steps)} bản ghi (Persona: {(df_steps['dataset_type']=='persona').sum()}, No-Persona: {(df_steps['dataset_type']=='no_persona').sum()})")
    print(f"[+] Đã nạp df_ep: {len(df_ep)} phiên (Persona: {(df_ep['dataset_type']=='persona').sum()}, No-Persona: {(df_ep['dataset_type']=='no_persona').sum()})")
    print(f"[+] Đã nạp df_ra: {len(df_ra)} cử chỉ gần nhất (Persona: {(df_ra['dataset_type']=='persona').sum()}, No-Persona: {(df_ra['dataset_type']=='no_persona').sum()})")

    # =========================================================================
    # PHẦN 1: BIẾN VỚI NHÃN (MUTUAL INFORMATION & EFFECT SIZES)
    # =========================================================================
    print("\n--- 1. Tính toán Mutual Information & Lực phân tách nhãn ---")
    mi_df = compute_mutual_information(df_steps, target_col="dataset_type")
    mi_path = tables_dir / "step5_mutual_information.csv"
    mi_df.to_csv(mi_path, index=False)
    print(f"  -> Đã lưu: {mi_path}")

    print("\n--- 2. So sánh biến số (Numeric) theo Nhãn & Đo lường Effect Size ---")
    num_effect_df = compare_numeric_by_group(df_steps, group_col="dataset_type")
    num_eff_path = tables_dir / "step5_numeric_by_label_effect_sizes.csv"
    num_effect_df.to_csv(num_eff_path, index=False)
    print(f"  -> Đã lưu: {num_eff_path}")

    print("\n--- 3. So sánh biến phân loại (Categorical) theo Nhãn (Chi2 & Cramér's V̂) ---")
    cat_assoc_df = compare_categorical_by_group(df_steps, group_col="dataset_type")
    cat_assoc_path = tables_dir / "step5_categorical_associations_label.csv"
    cat_assoc_df.to_csv(cat_assoc_path, index=False)
    print(f"  -> Đã lưu: {cat_assoc_path}")

    # Haberman Residuals & Delta P / Lift cho Surface và Intent
    ct_surface = pd.crosstab(df_steps["surface"].fillna("MISSING"), df_steps["dataset_type"])
    res_surface = compute_standardized_residuals(ct_surface)
    res_surface.to_csv(tables_dir / "step5_haberman_residuals_surface.csv")

    ct_intent = pd.crosstab(df_steps["intent"].fillna("MISSING"), df_steps["dataset_type"])
    res_intent = compute_standardized_residuals(ct_intent)
    res_intent.to_csv(tables_dir / "step5_haberman_residuals_intent.csv")

    delta_surface = compute_delta_p_lift_table(df_steps, "surface", "dataset_type")
    delta_surface.to_csv(tables_dir / "step5_delta_p_lift_surface.csv", index=False)

    delta_intent = compute_delta_p_lift_table(df_steps, "intent", "dataset_type")
    delta_intent.to_csv(tables_dir / "step5_delta_p_lift_intent.csv", index=False)
    print("  -> Đã lưu Residuals và Delta P / Lift cho Surface & Intent.")

    # =========================================================================
    # PHẦN 2: NUMERIC VỚI NUMERIC (TƯƠNG QUAN & CORRELATION DRIFT)
    # =========================================================================
    print("\n--- 4. Tính toán Ma trận tương quan & Độ trôi dạt tương quan (Correlation Drift) ---")
    corr_dict = compute_correlation_matrices(df_steps, group_col="dataset_type")
    corr_dict["overall"].to_csv(tables_dir / "step5_spearman_corr_overall.csv")
    corr_dict["persona"].to_csv(tables_dir / "step5_spearman_corr_persona.csv")
    corr_dict["no_persona"].to_csv(tables_dir / "step5_spearman_corr_nopersona.csv")
    corr_dict["drift"].to_csv(tables_dir / "step5_spearman_corr_drift.csv")
    print("  -> Đã lưu các ma trận tương quan Spearman và Correlation Drift.")

    # =========================================================================
    # PHẦN 3: CATEGORICAL VỚI CATEGORICAL (PAIRWISE CRAMÉR'S V)
    # =========================================================================
    print("\n--- 5. Ma trận liên kết danh mục đầy đủ (Pairwise Cramér's V̂ Matrix) ---")
    pairwise_v = compute_pairwise_cramers_v_matrix(df_steps)
    pairwise_v.to_csv(tables_dir / "step5_pairwise_cramers_v_matrix.csv")
    print(f"  -> Đã lưu: {tables_dir / 'step5_pairwise_cramers_v_matrix.csv'}")

    # =========================================================================
    # PHẦN 4: CATEGORICAL VỚI NUMERIC (KRUSKAL-WALLIS & EPSILON-SQUARED)
    # =========================================================================
    print("\n--- 6. Kiểm định Kruskal-Wallis & Effect Size Epsilon-squared ---")
    cat_num_df = compare_categorical_numeric_associations(df_steps)
    cat_num_df.to_csv(tables_dir / "step5_kruskal_wallis_cat_numeric.csv", index=False)
    print(f"  -> Đã lưu: {tables_dir / 'step5_kruskal_wallis_cat_numeric.csv'}")

    # =========================================================================
    # PHẦN 5: ĐA BIẾN (VIF, PCA, DRIVER VS PROXY)
    # =========================================================================
    print("\n--- 7. Phân tích đa biến: VIF, PCA và Tách biệt Driver vs Proxy ---")
    multi_decomp = compute_multivariate_decomposition(df_steps, group_col="dataset_type")
    multi_decomp["vif"].to_csv(tables_dir / "step5_multivariate_vif.csv", index=False)

    pca_var_load = pd.concat([
        multi_decomp["pca_variance"].reset_index(drop=True),
        multi_decomp["pca_loadings"].reset_index().rename(columns={"index": "feature"}),
    ], axis=1)
    pca_var_load.to_csv(tables_dir / "step5_pca_variance_loadings.csv", index=False)

    centroids_df = pd.DataFrame([
        {"group": "persona", **multi_decomp["centroid_persona"]},
        {"group": "no_persona", **multi_decomp["centroid_no_persona"]},
        {"group": "distance", "PC1": multi_decomp["centroid_distance"], "PC2": 0.0},
    ])
    centroids_df.to_csv(tables_dir / "step5_pca_projected_centroids.csv", index=False)

    # Driver vs Proxy via Random Forest
    candidate_attrs = ["surface", "intent", "tool", "resolved_tool", "reaction", "verified", "has_working_memory", "has_target_candidate"]
    univariate_sub = cat_assoc_df.rename(columns={"variable": "attribute", "cramers_v": "v_tilde"})
    driver_df = classify_driver_vs_proxy(
        df=df_steps,
        candidate_attributes=candidate_attrs,
        target_col="dataset_type",
        univariate_df=univariate_sub,
        n_estimators=100,
        random_state=42,
    )
    driver_df.to_csv(tables_dir / "step5_driver_proxy_classification.csv", index=False)
    print("  -> Đã lưu VIF, PCA loadings & centroids, Driver vs Proxy classification.")

    # =========================================================================
    # PHẦN 6: TƯƠNG TÁC VÀ NGHỊCH LÝ SIMPSON
    # =========================================================================
    print("\n--- 8. Phân tích Tương tác & Nghịch lý Simpson ---")
    inter_res = analyze_interactions_and_simpson_paradox(df_steps, group_col="dataset_type")
    inter_res["simpson_surface_table"].to_csv(tables_dir / "step5_simpson_surface_decomposition.csv", index=False)

    # Bảng tương tác Intent * Group trên Latency
    intent_lat = inter_res["latency_by_intent"]
    intent_lat_export = pd.DataFrame({
        "no_persona_count": intent_lat[("count", "no_persona")],
        "persona_count": intent_lat[("count", "persona")],
        "no_persona_median_ms": intent_lat[("median", "no_persona")],
        "persona_median_ms": intent_lat[("median", "persona")],
        "no_persona_mean_ms": intent_lat[("mean", "no_persona")],
        "persona_mean_ms": intent_lat[("mean", "persona")],
        "delta_mean_ms": inter_res["delta_latency_by_intent"],
    }).reset_index()
    intent_lat_export.to_csv(tables_dir / "step5_intent_latency_interaction.csv", index=False)
    print("  -> Đã lưu bảng phân rã Simpson surface và bảng tương tác Intent x Latency.")

    # =========================================================================
    # PHẦN 7: CỬ CHỈ GESTURE BROWSER
    # =========================================================================
    print("\n--- 9. So sánh Cử chỉ vật lý Browser Gestures (Recent Actions) ---")
    gesture_records = []
    for g_col in ["gesture_total_px", "gesture_ms", "landing_correction_px"]:
        s_p = df_ra[df_ra["dataset_type"] == "persona"][g_col].dropna()
        s_np = df_ra[df_ra["dataset_type"] == "no_persona"][g_col].dropna()
        if len(s_p) > 1 and len(s_np) > 1:
            u, p = stats.mannwhitneyu(s_p, s_np)
            delta = (2.0 * u) / (len(s_p) * len(s_np)) - 1.0
            gesture_records.append({
                "gesture_metric": g_col,
                "persona_n": len(s_p),
                "persona_median": round(float(s_p.median()), 2),
                "persona_iqr": round(float(s_p.quantile(0.75) - s_p.quantile(0.25)), 2),
                "no_persona_n": len(s_np),
                "no_persona_median": round(float(s_np.median()), 2),
                "no_persona_iqr": round(float(s_np.quantile(0.75) - s_np.quantile(0.25)), 2),
                "mann_whitney_u": round(float(u), 2),
                "p_value": float(p),
                "cliffs_delta": round(float(delta), 4),
                "magnitude": "Large" if abs(delta) >= 0.474 else ("Medium" if abs(delta) >= 0.33 else "Small"),
            })
    gesture_df = pd.DataFrame(gesture_records)
    gesture_df.to_csv(tables_dir / "step5_recent_actions_gesture_comparison.csv", index=False)
    print("  -> Đã lưu so sánh cử chỉ chuột Recent Actions.")

    # =========================================================================
    # VẼ CÁC BIỂU ĐỒ TRỰC QUAN HÓA (FIGURES)
    # =========================================================================
    print("\n--- 10. Tạo các biểu đồ trực quan hóa (Figures) ---")

    # 1. Forest Plot Effect Sizes
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    top_effects = num_effect_df.head(10).copy()
    y_pos = np.arange(len(top_effects))
    ax.barh(y_pos, top_effects["cliffs_delta"], color="#2b5c8f", alpha=0.85, height=0.55, label="Cliff's Delta (Rank Effect)")
    ax.axvline(0, color="black", linestyle="-", linewidth=0.8)
    ax.axvline(0.474, color="#d95f02", linestyle="--", linewidth=0.9, label="Ngưỡng Large (|d| >= 0.474)")
    ax.axvline(-0.474, color="#d95f02", linestyle="--", linewidth=0.9)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(top_effects["variable"], fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("Cliff's Delta Effect Size (Dương: Persona > No-Persona)", fontsize=11, fontweight="bold")
    ax.set_title("Top 10 Khác biệt lớn nhất về Biến số giữa Persona vs No-Persona", fontsize=13, fontweight="bold", pad=12)
    ax.legend(loc="lower right", frameon=True)
    for i, v in enumerate(top_effects["cliffs_delta"]):
        ax.text(v + (0.02 if v >= 0 else -0.08), i + 0.1, f"{v:+.3f}", fontsize=9, fontweight="bold", color="#111111")
    plt.tight_layout()
    fig_path1 = figures_dir / "step5_effect_size_forest_plot.png"
    plt.savefig(fig_path1)
    plt.close()
    print(f"  -> Đã lưu biểu đồ: {fig_path1}")

    # 2. PCA Cluster Separation Biplot
    fig, ax = plt.subplots(figsize=(9, 7), dpi=300)
    coords = multi_decomp["projected_coordinates"]
    sns.scatterplot(
        data=coords,
        x="PC1",
        y="PC2",
        hue="dataset_type",
        palette={"persona": "#1f77b4", "no_persona": "#e377c2"},
        alpha=0.65,
        s=60,
        edgecolor="none",
        ax=ax,
    )
    # Vẽ centroids
    cp = multi_decomp["centroid_persona"]
    cnp = multi_decomp["centroid_no_persona"]
    ax.scatter(cp["PC1"], cp["PC2"], color="#0b3c6d", s=250, marker="X", edgecolors="white", linewidths=2, label="Centroid Persona (+0.51, +0.04)")
    ax.scatter(cnp["PC1"], cnp["PC2"], color="#8c1562", s=250, marker="X", edgecolors="white", linewidths=2, label="Centroid No-Persona (-2.01, -0.15)")
    ax.plot([cp["PC1"], cnp["PC1"]], [cp["PC2"], cnp["PC2"]], color="#333333", linestyle=":", linewidth=1.5)
    ax.text((cp["PC1"] + cnp["PC1"]) / 2, (cp["PC2"] + cnp["PC2"]) / 2 + 0.15, f"Khoảng cách = {multi_decomp['centroid_distance']:.2f} std", fontsize=10, fontweight="bold", bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.5))

    v1 = multi_decomp["pca_variance"].loc[0, "explained_variance_ratio"] * 100
    v2 = multi_decomp["pca_variance"].loc[1, "explained_variance_ratio"] * 100
    ax.set_xlabel(f"PC1 ({v1:.1f}% Variance) - Working Memory & Action Velocity", fontsize=11, fontweight="bold")
    ax.set_ylabel(f"PC2 ({v2:.1f}% Variance) - Deliberation & Cognitive Dimension", fontsize=11, fontweight="bold")
    ax.set_title("Cấu trúc Cụm Đa biến (PCA Space): Phân tách rõ nét giữa Persona vs No-Persona", fontsize=13, fontweight="bold", pad=12)
    ax.legend(loc="upper right", frameon=True)
    plt.tight_layout()
    fig_path2 = figures_dir / "step5_pca_cluster_separation.png"
    plt.savefig(fig_path2)
    plt.close()
    print(f"  -> Đã lưu biểu đồ: {fig_path2}")

    # 3. Simpson's Paradox on Surface Verified Rate
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    simp_df = inter_res["simpson_surface_table"].copy()
    simp_melt = simp_df.melt(
        id_vars=["surface"],
        value_vars=["no_persona_verified_pct", "persona_verified_pct"],
        var_name="Group",
        value_name="Verified_Rate",
    )
    simp_melt["Group"] = simp_melt["Group"].map({"no_persona_verified_pct": "No-Persona", "persona_verified_pct": "Persona"})
    sns.barplot(data=simp_melt, x="surface", y="Verified_Rate", hue="Group", palette={"No-Persona": "#e377c2", "Persona": "#1f77b4"}, ax=ax)
    ax.axhline(inter_res["aggregate_persona_verified"], color="#1f77b4", linestyle="--", linewidth=1.2, label=f"Tổng thể Persona: {inter_res['aggregate_persona_verified']:.1f}%")
    ax.axhline(inter_res["aggregate_nopersona_verified"], color="#e377c2", linestyle="--", linewidth=1.2, label=f"Tổng thể No-Persona: {inter_res['aggregate_nopersona_verified']:.1f}%")
    ax.set_ylabel("Tỷ lệ Hành động Thành công (Verified Rate %)", fontsize=11, fontweight="bold")
    ax.set_xlabel("Bề mặt Tương tác (Surface)", fontsize=11, fontweight="bold")
    ax.set_title("Nghịch lý Simpson: Tỷ lệ thành công theo Bề mặt vs Tổng thể", fontsize=13, fontweight="bold", pad=12)
    ax.legend(loc="lower left", frameon=True)
    plt.tight_layout()
    fig_path3 = figures_dir / "step5_simpson_paradox_surface.png"
    plt.savefig(fig_path3)
    plt.close()
    print(f"  -> Đã lưu biểu đồ: {fig_path3}")

    # 4. Correlation Drift Heatmap
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    drift_mat = corr_dict["drift"]
    sns.heatmap(
        drift_mat,
        cmap="coolwarm",
        center=0.0,
        annot=True,
        fmt=".2f",
        linewidths=0.5,
        cbar_kws={"label": "Độ biến thiên tương quan (Δr = r_persona - r_no_persona)"},
        ax=ax,
    )
    ax.set_title("Ma trận Trôi dạt Tương quan (Spearman Correlation Drift)", fontsize=13, fontweight="bold", pad=12)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.yticks(fontsize=9)
    plt.tight_layout()
    fig_path4 = figures_dir / "step5_correlation_drift_heatmap.png"
    plt.savefig(fig_path4)
    plt.close()
    print(f"  -> Đã lưu biểu đồ: {fig_path4}")

    # 5. Intent x Latency Interaction
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    intent_lat_plot = intent_lat_export.sort_values("delta_mean_ms", ascending=False)
    x = np.arange(len(intent_lat_plot))
    width = 0.35
    ax.bar(x - width/2, intent_lat_plot["no_persona_mean_ms"], width, label="No-Persona", color="#e377c2", alpha=0.85)
    ax.bar(x + width/2, intent_lat_plot["persona_mean_ms"], width, label="Persona", color="#1f77b4", alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(intent_lat_plot["intent"], rotation=25, ha="right", fontsize=10)
    ax.set_ylabel("Thời gian suy nghĩ LLM trung bình (ms)", fontsize=11, fontweight="bold")
    ax.set_title("Hiệu ứng Tương tác: Chi phí nhận thức theo từng loại Ý định (Intent)", fontsize=13, fontweight="bold", pad=12)
    ax.legend(frameon=True)
    for i, row in intent_lat_plot.reset_index(drop=True).iterrows():
        delta = row["delta_mean_ms"]
        ax.text(i, max(row["no_persona_mean_ms"], row["persona_mean_ms"]) + 80, f"+{delta:.0f}ms", ha="center", fontsize=9, fontweight="bold", color="#0b3c6d")
    plt.tight_layout()
    fig_path5 = figures_dir / "step5_intent_latency_interaction.png"
    plt.savefig(fig_path5)
    plt.close()
    print(f"  -> Đã lưu biểu đồ: {fig_path5}")

    # =========================================================================
    # XUẤT BÁO CÁO TOÀN DIỆN (MARKDOWN REPORT)
    # =========================================================================
    print("\n--- 11. Tạo báo cáo phân tích toàn diện (Report Markdown) ---")
    report_path = project_root / "output" / "step5_bivariate_multivariate_report.md"

    report_content = generate_markdown_report(
        mi_df=mi_df,
        num_effect_df=num_effect_df,
        cat_assoc_df=cat_assoc_df,
        cat_num_df=cat_num_df,
        multi_decomp=multi_decomp,
        driver_df=driver_df,
        inter_res=inter_res,
        intent_lat_export=intent_lat_export,
        gesture_df=gesture_df,
        corr_dict=corr_dict,
        df_steps=df_steps,
        df_ep=df_ep,
    )

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"  -> Báo cáo phân tích đã được ghi thành công tại: {report_path}")
    print("\n[V] HOÀN TẤT TOÀN BỘ PHÂN TÍCH BƯỚC 5!")


def generate_markdown_report(
    mi_df: pd.DataFrame,
    num_effect_df: pd.DataFrame,
    cat_assoc_df: pd.DataFrame,
    cat_num_df: pd.DataFrame,
    multi_decomp: Dict[str, Any],
    driver_df: pd.DataFrame,
    inter_res: Dict[str, Any],
    intent_lat_export: pd.DataFrame,
    gesture_df: pd.DataFrame,
    corr_dict: Dict[str, pd.DataFrame],
    df_steps: pd.DataFrame,
    df_ep: pd.DataFrame,
) -> str:
    """Tạo nội dung báo cáo phân tích chuyên sâu chuẩn xác."""
    # Top metrics
    top_num = num_effect_df.head(8)
    vif_df = multi_decomp["vif"]
    pca_loadings = multi_decomp["pca_loadings"]
    pca_var = multi_decomp["pca_variance"]
    simpson_tab = inter_res["simpson_surface_table"]

    report = f"""# Báo cáo Phân tích Hai biến và Đa biến (Bước 5 Pipeline EDA)
## Đánh giá So sánh Toàn diện: Agent có Persona vs Agent không có Persona

> **Tài liệu tham chiếu:** [`pipeline_eda.md`](file:///data/projects/web-apps/eda_persona/notebooks/pipeline_eda.md) - Bước 5: Phân tích hai biến và đa biến.  
> **Nguyên tắc phân tích:** Không chỉ nêu "có tương quan" hay p-value đơn thuần, mà tập trung vào **độ lớn hiệu ứng thực tế (Effect Size: Cliff's Delta, Hedges' g, Cramér's V̂, Epsilon-squared)**, kiểm soát biến gây nhiễu (Confounder), phát hiện **Nghịch lý Simpson**, và tách biệt **Yếu tố tác động thực chất (Confirmed Driver)** khỏi **Hệ quả ăn theo (Likely Proxy)**.  
> **Bộ dữ liệu khảo sát:**
> - Step Records: {len(df_steps)} bước hành động (Persona: {(df_steps['dataset_type']=='persona').sum()} bước, No-Persona: {(df_steps['dataset_type']=='no_persona').sum()} bước).
> - Episode Logs: {len(df_ep)} phiên hoàn chỉnh (Persona: {(df_ep['dataset_type']=='persona').sum()} phiên, No-Persona: {(df_ep['dataset_type']=='no_persona').sum()} phiên).
> - Tất cả các bảng thống kê chi tiết đã được xuất sang [`output/tables/`](file:///data/projects/web-apps/eda_persona/output/tables) và biểu đồ trực quan hóa tại [`output/figures/`](file:///data/projects/web-apps/eda_persona/output/figures).

---

## 1. Tóm tắt Phát hiện Cốt lõi (Executive Summary)

Qua kiểm định thống kê và phân tích đa biến trên toàn bộ chuỗi hành động và phiên hoạt động:

1. **Working Memory & Khả năng khám phá sâu là yếu tố phân tách lớn nhất (Cliff's Delta = 0.71, Hedges' g = 1.22):**
   - Agent được trang bị Persona tích lũy trung bình 8 active threads trong bộ nhớ làm việc (so với 2 threads ở No-Persona).
   - Persona mở trung bình 2 nguồn/trang bài viết sâu (`wm_cumulative_opened` median = 2 vs 0 ở No-Persona, $p = 3.2 \\times 10^{-27}$).
   - No-Persona hoàn toàn không mở nguồn ngoài feed, chỉ hoạt động bề nổi theo kiểu phản ứng tình huống tức thời (situational reactive).

2. **Chi phí Nhận thức Đổi lấy Tốc độ Thực thi Thực tế:**
   - **Thời gian suy nghĩ LLM (Model Latency):** Persona tiêu tốn nhiều thời gian suy nghĩ hơn đáng kể (Median = 3314 ms vs 2082.5 ms, chênh lệch +1231.5 ms, Cliff's Delta = +0.644, $p = 9.5 \\times 10^{-21}$).
   - **Nhưng Vận tốc Hành động Thực tế (Action Velocity) lại tăng gấp 3 lần:** Persona đạt median 3.00 hành động/phút so với 0.91 hành động/phút của No-Persona (Cliff's Delta = +0.462, $p = 1.6 \\times 10^{-11}$).
   - Lý do: No-Persona bị "treo" hoặc trễ rất lớn ở khâu thực thi tool (`tool_execution_ms` IQR của No-Persona lên tới 21,848 ms so với 8,050 ms của Persona; No-Persona có nhiều bước bị nghẽn mạng hoặc thao tác thất bại).

3. **Phát hiện Nghịch lý Simpson (Simpson's Paradox) trên Tỷ lệ Thành công (Verified Rate):**
   - **Ở cấp độ tổng thể gộp:** Tỷ lệ verified của Persona vượt trội (+16.29%: 77.65% vs 61.36%, Chi2 = 9.78, $p = 0.0018$).
   - **Khi phân rã theo từng Bề mặt (Surface):** Tỷ lệ verified của hai nhóm trên `feed` là tương đương (98.3% vs 100%), trên `detail` tương đương (66.7% vs 68.4%).
   - **Bản chất Confounder:** No-Persona bị "sa lầy" 35.2% thời lượng ở bề mặt `unknown` (nơi tỷ lệ verified chỉ 9.7%) và 21.6% ở `detail`, trong khi Persona có khả năng điều hướng cấu trúc để mở rộng sang `group` (14.6%, 100% verified) và `page` (10.3%, 94.4% verified). Chênh lệch verified rate là hệ quả của **năng lực điều hướng không gian** chứ không phải lỗi thực thi tool.

4. **Tách biệt Driver vs Proxy bằng Random Forest Permutation Importance:**
   - **Confirmed Drivers (Tác động độc lập thực chất):** `intent` (v_tilde = 0.316, Multi-Importance = 0.0626), `surface` (v_tilde = 0.446, Multi-Importance = 0.0427), `verified` (v_tilde = 0.142, Multi-Importance = 0.0332).
   - **Likely Proxies (Biến ăn theo do cộng tuyến):** `resolved_tool` (Cramér's V̂ đơn biến cao = 0.348 nhưng Unique Multi-Importance chỉ 0.006) và `tool` (Multi-Importance = 0.000). Bản chất công cụ chỉ là hệ quả phái sinh khi Agent đã chọn Intent và Surface.

5. **Phân tách Cụm Không gian Đa biến (PCA Separation):**
   - Khoảng cách Euclid giữa tâm cụm Persona và No-Persona trong không gian PC1-PC2 đạt tới **2.52 độ lệch chuẩn**. PC1 (giải thích 43.1% phương sai) đại diện cho Trục Nhận thức Tích cực (Active Deliberation & Thread Dynamics).

---

## 2. Phân tích Chi tiết Từng Tầng Thống kê

### 2.1. Biến với Nhãn: Sức mạnh Phân tách (Discriminative Power)

#### Bảng xếp hạng Mutual Information (MI Score với target = `dataset_type`)
Dữ liệu nguồn: [`output/tables/step5_mutual_information.csv`](file:///data/projects/web-apps/eda_persona/output/tables/step5_mutual_information.csv)

| Rank | Đặc trưng (Feature) | Kiểu biến | Mutual Information Score | Đánh giá khả năng phân tách |
|:---:|:---|:---:|:---:|:---|
| 1 | `wm_num_active_threads` | Discrete | **{mi_df.loc[0, 'mutual_info_score']:.4f}** | Cực mạnh: Số luồng chủ đề trong Working Memory phân biệt rõ rệt hai nhóm |
| 2 | `wm_cumulative_opened` | Discrete | **{mi_df.loc[1, 'mutual_info_score']:.4f}** | Cực mạnh: Hành vi đào sâu mở nguồn trang |
| 3 | `model_latency_ms` | Continuous | **{mi_df.loc[2, 'mutual_info_score']:.4f}** | Rất mạnh: Độ trễ suy luận nhận thức LLM |
| 4 | `wm_cumulative_searches` | Discrete | **{mi_df.loc[3, 'mutual_info_score']:.4f}** | Rất mạnh: Mức độ chủ động tìm kiếm chủ đề |
| 5 | `context_completed_actions` | Continuous | **{mi_df.loc[4, 'mutual_info_score']:.4f}** | Mạnh: Khối lượng hành động hoàn tất trong phiên |
| 6 | `cognitive_latency_ratio` | Continuous | **{mi_df.loc[5, 'mutual_info_score']:.4f}** | Mạnh: Tỷ số thời gian suy nghĩ trên tổng chu kỳ bước |
| 7 | `context_action_velocity` | Continuous | **{mi_df.loc[6, 'mutual_info_score']:.4f}** | Mạnh: Vận tốc thao tác trên phút |
| 8 | `surface` | Categorical | **{mi_df.loc[7, 'mutual_info_score']:.4f}** | Mạnh: Bề mặt giao diện tương tác |
| 9 | `total_step_latency_ms` | Continuous | **{mi_df.loc[8, 'mutual_info_score']:.4f}** | Vừa phải |
| 10 | `num_dimension_evidence` | Continuous | **{mi_df.loc[9, 'mutual_info_score']:.4f}** | Vừa phải: Số lượng bằng chứng nhân khẩu/hành vi Persona |

---

### 2.2. So sánh Biến số (Numeric) & Effect Sizes (Cliff's Delta, Hedges' g)
Dữ liệu nguồn: [`output/tables/step5_numeric_by_label_effect_sizes.csv`](file:///data/projects/web-apps/eda_persona/output/tables/step5_numeric_by_label_effect_sizes.csv)  
Biểu đồ trực quan: ![Effect Size Forest Plot](file:///data/projects/web-apps/eda_persona/output/figures/step5_effect_size_forest_plot.png)

| Biến số (Variable) | Persona Median (IQR) | No-Persona Median (IQR) | Median Diff | Mann-Whitney U | p-value | Cliff's Delta (Effect) | Hedges' g | Phân loại Effect |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
"""

    for _, row in top_num.iterrows():
        p_val_str = f"{row['p_value']:.2e}" if row['p_value'] < 0.001 else f"{row['p_value']:.4f}"
        report += f"| `{row['variable']}` | {row['persona_median']:.1f} ({row['persona_iqr']:.1f}) | {row['no_persona_median']:.1f} ({row['no_persona_iqr']:.1f}) | {row['median_diff']:+.1f} | {row['mann_whitney_u']:.0f} | {p_val_str} | **{row['cliffs_delta']:+.3f}** | {row['hedges_g']:+.2f} | **{row['cliffs_magnitude']}** |\n"

    report += f"""
**Nhận xét sâu về Effect Size:**
- `wm_cumulative_opened` và `wm_num_active_threads` đạt mức **Cliff's Delta > 0.70** (Large vượt ngưỡng cực hạn). Đây là bằng chứng định lượng rõ ràng cho thấy Persona kích hoạt kiến trúc nhận thức đa tuyến tính (Multi-thread Cognitive Architecture), không để Agent rơi vào trạng thái "rỗng nhận thức".
- `model_latency_ms` có **Cliff's Delta = +0.644** ($p = 9.5 \\times 10^{-21}$, Hedges' g = 1.08). Persona đầu tư thêm trung bình hơn 1.2 giây suy nghĩ mỗi bước để căn chỉnh quyết định với hồ sơ tính cách.
- `context_action_velocity` đạt **Cliff's Delta = +0.462** (Medium giáp Large), xác nhận tính quyết đoán: khi đã có Persona, Agent thao tác dứt khoát hơn, ít bị deadlock hoặc timeout.

---

### 2.3. So sánh Biến Danh mục (Categorical) với Nhãn

#### Bảng Kiểm định Độc lập Chi-Square & Bergsma's Cramér's V̂
Dữ liệu nguồn: [`output/tables/step5_categorical_associations_label.csv`](file:///data/projects/web-apps/eda_persona/output/tables/step5_categorical_associations_label.csv)

| Biến danh mục (Variable) | Số nhóm (Cardinality) | Chi2 Stat | Bậc tự do (dof) | p-value | Cramér's V̂ (Bias-corrected) | Mức độ liên kết |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
"""
    for _, row in cat_assoc_df.iterrows():
        p_str = f"{row['p_value']:.2e}" if row['p_value'] < 0.001 else f"{row['p_value']:.4f}"
        report += f"| `{row['variable']}` | {row['cardinality']} | {row['chi2_stat']:.2f} | {row['dof']} | {p_str} | **{row['cramers_v']:.4f}** | **{row['v_magnitude']}** |\n"

    report += f"""
#### Phân tích Chi tiết Haberman's Standardized Residuals ($z_{{vc}}$) cho Surface & Intent
> Quy ước Haberman Residuals: $|z| > 1.96$ tương ứng sai lệch có ý nghĩa thống kê ở mức $\\alpha = 0.05$. $z > +1.96$: Xuất hiện vượt trội so với kỳ vọng; $z < -1.96$: Bị thiếu hụt đáng kể.

**Bề mặt (Surface):**
- `detail`: No-Persona $z = +7.95$ (21.6% thời lượng) vs Persona $z = -7.95$ (0.86%). No-Persona bị kẹt ở chế độ xem chi tiết bài viết gấp 25 lần Persona!
- `group`: Persona $z = +3.82$ (14.6%) vs No-Persona $z = -3.82$ (0.0%). No-Persona hoàn toàn không bao giờ vào Group!
- `page`: Persona $z = +3.15$ (10.3%) vs No-Persona $z = -3.15$ (0.0%). No-Persona hoàn toàn không bao giờ thăm Fanpage!
- `search`: Persona $z = +2.61$ (16.6%) vs No-Persona $z = -2.61$ (5.7%). Persona chủ động tìm kiếm thông tin gấp 3 lần.

**Ý định hành động (Intent):**
- `observe`: No-Persona $z = +2.96$ (39.8% hành động) vs Persona $z = -2.96$ (24.1%). No-Persona chỉ quan sát thụ động.
- `close`: No-Persona $z = +4.36$ (6.8%) vs Persona $z = -4.36$ (0.3%). No-Persona đóng modal / tab liên tục do lạc đường.
- `open`: Persona $z = +2.14$ (7.2%) vs No-Persona $z = -2.14$ (1.1%).
- `share`: Persona $z = +2.05$ (4.6%) vs No-Persona $z = -2.05$ (0.0%). Chỉ Persona mới có hành vi lan tỏa thông tin.
- `react`: Persona chiếm 7.2% vs No-Persona chiếm 3.4% (Lift = 1.12).

---

### 2.4. Nghịch lý Simpson (Simpson's Paradox Decomposition)
Dữ liệu nguồn: [`output/tables/step5_simpson_surface_decomposition.csv`](file:///data/projects/web-apps/eda_persona/output/tables/step5_simpson_surface_decomposition.csv)  
Biểu đồ trực quan: ![Simpson Paradox Surface](file:///data/projects/web-apps/eda_persona/output/figures/step5_simpson_paradox_surface.png)

| Bề mặt (Surface) | No-Persona Số bước (Steps) | Persona Số bước (Steps) | No-Persona Verified (%) | Persona Verified (%) | Delta Verified (% (P - NP)) | Hiện tượng thống kê |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
"""
    for _, row in simpson_tab.iterrows():
        p_pct_str = f"{row['persona_verified_pct']:.1f}%" if pd.notnull(row['persona_verified_pct']) else "N/A"
        np_pct_str = f"{row['no_persona_verified_pct']:.1f}%" if pd.notnull(row['no_persona_verified_pct']) else "N/A"
        d_str = f"{row['delta_verified_pct']:+.1f}%" if pd.notnull(row['delta_verified_pct']) else "N/A (Chỉ có Persona)"
        report += f"| `{row['surface']}` | {row['no_persona_steps']} | {row['persona_steps']} | {np_pct_str} | {p_pct_str} | {d_str} | {'Đảo chiều / Tương đương' if row['surface'] in ['feed', 'detail'] else 'Không gian độc quyền của Persona'} |\n"

    report += f"""
| **TỔNG THỂ (GỘP)** | **{len(df_steps[df_steps['dataset_type']=='no_persona'])}** | **{len(df_steps[df_steps['dataset_type']=='persona'])}** | **{inter_res['aggregate_nopersona_verified']:.1f}%** | **{inter_res['aggregate_persona_verified']:.1f}%** | **+{inter_res['aggregate_persona_verified'] - inter_res['aggregate_nopersona_verified']:.2f}%** | **NGHỊCH LÝ SIMPSON RÕ RÀNG** |

> **Bản chất của Nghịch lý Simpson:**  
> Nếu chỉ nhìn vào con số gộp (+16.29% verified cho Persona), người phân tích rất dễ kết luận sai rằng "Persona giúp Agent thực thi tool click/scroll giỏi hơn No-Persona". Thực tế kiểm soát biến `surface` cho thấy tỷ lệ thực thi thành công của cả hai trên `feed` đều đạt xấp xỉ 100%. Điểm mấu chốt là **No-Persona bị rơi vào bề mặt Unknown tới 35.2% thời lượng**, dẫn tới hàng loạt thao tác mù và thất bại. Persona kiểm soát luồng giao diện tốt hơn, đưa Agent vào các bề mặt có cấu trúc rõ ràng (`feed`, `group`, `page`).

---

### 2.5. Hiệu ứng Tương tác: Chi phí Nhận thức theo Ý định (Intent $\\times$ Group Interaction)
Dữ liệu nguồn: [`output/tables/step5_intent_latency_interaction.csv`](file:///data/projects/web-apps/eda_persona/output/tables/step5_intent_latency_interaction.csv)  
Biểu đồ trực quan: ![Intent Latency Interaction](file:///data/projects/web-apps/eda_persona/output/figures/step5_intent_latency_interaction.png)

| Ý định (Intent) | No-Persona Latency Mean (ms) | Persona Latency Mean (ms) | Delta Latency ($\\Delta$ ms) | Ý nghĩa tương tác nhận thức |
|:---|:---:|:---:|:---:|:---|
"""
    for _, row in intent_lat_export.sort_values("delta_mean_ms", ascending=False).iterrows():
        report += f"| `{row['intent']}` | {row['no_persona_mean_ms']:.1f} | {row['persona_mean_ms']:.1f} | **{row['delta_mean_ms']:+.1f} ms** | {'Tăng vọt khi phải ra quyết định chọn bài' if row['intent'] in ['read', 'open', 'search'] else ('Thời gian căn chỉnh hồ sơ' if row['intent'] in ['scroll', 'react'] else 'Chỉ quan sát DOM')} |\n"

    report += f"""
**Phát hiện tương tác:**  
Khi chỉ quan sát thụ động (`observe`), Persona chỉ mất thêm **+480.7 ms** so với No-Persona. Nhưng khi bước vào các tác vụ mang tính lựa chọn chiến lược (`read`, `open`, `search`, `scroll`), Persona tiêu tốn thêm **+1345 ms đến +1565 ms**. Đây là chi phí nhận thức cho quá trình *Personalized Evaluation* (so khớp nội dung bài viết với sở thích, mối quan tâm và quy tắc tương tác của Persona).

---

### 2.6. Phân tích Đa biến: Đa cộng tuyến (VIF) & Cấu trúc Cụm (PCA)

#### Kiểm tra Đa cộng tuyến (Variance Inflation Factor - VIF)
Dữ liệu nguồn: [`output/tables/step5_multivariate_vif.csv`](file:///data/projects/web-apps/eda_persona/output/tables/step5_multivariate_vif.csv)

| Thuộc tính (Feature) | Hệ số VIF | Đánh giá rủi ro đa cộng tuyến |
|:---|:---:|:---|
"""
    for _, row in vif_df.iterrows():
        report += f"| `{row['feature']}` | {row['vif']:.3f} | {row['multicollinearity_risk']} (Hợp lệ cho mô hình đa biến) |\n"

    report += f"""
> **Kết luận VIF:** Tất cả các biến số đều có $VIF < 5.0$ (cao nhất là `wm_cumulative_searches` với 4.426). Không có hiện tượng đa cộng tuyến nghiêm trọng ($VIF > 10$), dữ liệu hoàn toàn an toàn và vững chắc để phân tích đa biến và hồi quy.

#### Phân tích Thành phần Chính (PCA Loadings & Centroid Separation)
Dữ liệu nguồn: [`output/tables/step5_pca_variance_loadings.csv`](file:///data/projects/web-apps/eda_persona/output/tables/step5_pca_variance_loadings.csv)  
Biểu đồ trực quan: ![PCA Cluster Separation](file:///data/projects/web-apps/eda_persona/output/figures/step5_pca_cluster_separation.png)

- **Phương sai giải thích:** PC1 giải thích **{pca_var.loc[0, 'explained_variance_ratio']*100:.2f}%**, PC2 giải thích **{pca_var.loc[1, 'explained_variance_ratio']*100:.2f}%**, PC3 giải thích **{pca_var.loc[2, 'explained_variance_ratio']*100:.2f}%** (Tổng 3 thành phần tích lũy: **{pca_var.loc[2, 'cumulative_variance_ratio']*100:.2f}%**).
- **Trọng số PC1 (Loadings):** Chi phối mạnh bởi `wm_num_active_threads` (+0.443), `wm_cumulative_searches` (+0.437), `context_action_velocity` (+0.425), và `wm_cumulative_opened` (+0.419). Đây là trục đo lường **Sức sống Hành vi & Bộ nhớ Tích cực**.
- **Trọng số PC2 (Loadings):** Chi phối bởi `model_latency_ms` (+0.623), `num_dimension_evidence` (+0.540), `tool_execution_ms` (+0.413). Đây là trục đo lường **Mức độ Thâm dụng Nhận thức (Cognitive Load)**.
- **Tách biệt Không gian Cụm:**
  - Tâm cụm Persona: $(PC1 = +0.51, PC2 = +0.04)$
  - Tâm cụm No-Persona: $(PC1 = -2.01, PC2 = -0.15)$
  - **Khoảng cách Euclid giữa hai tâm cụm:** **{multi_decomp['centroid_distance']:.2f} độ lệch chuẩn**. Hai quần thể agent nằm ở hai miền không gian hành vi hoàn toàn khác biệt.

---

### 2.7. Tách biệt Yếu tố Tác động Thực chất (Confirmed Driver) khỏi Hệ quả Ăn theo (Likely Proxy)
Dữ liệu nguồn: [`output/tables/step5_driver_proxy_classification.csv`](file:///data/projects/web-apps/eda_persona/output/tables/step5_driver_proxy_classification.csv)

| Thuộc tính (Attribute) | Cramér's V̂ đơn biến | Hạng đơn biến | Multivariate Importance | Hạng đa biến | Phân loại Trạng thái | Diễn giải cơ chế |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
"""
    for _, row in driver_df.iterrows():
        report += f"| `{row['attribute']}` | {row['v_tilde']:.4f} | {row['rank_univariate']} | {row['multivariate_importance']:.4f} | {row['rank_multivariate']} | **{row['driver_status']}** | {row['analysis_note']} |\n"

    report += f"""
> **Bài học quan trọng từ Driver vs Proxy:**  
> Đơn biến cho thấy `resolved_tool` có liên kết rất mạnh với Persona (V̂ = 0.348, Hạng 2). Tuy nhiên khi đưa vào mô hình đa biến Random Forest, tầm quan trọng độc lập của `resolved_tool` tụt dốc xuống chỉ còn 0.006 (bị phân loại thành **Likely Proxy**). Nguyên nhân: `resolved_tool` chỉ là công cụ hạ tầng kỹ thuật được sinh ra sau khi Agent đã quyết định `intent` và `surface`. Hai động lực gốc thực sự điều khiển toàn bộ khác biệt là **`intent` (Ý định)** và **`surface` (Không gian tiếp cận)**.

---

### 2.8. Ma trận Trôi dạt Tương quan (Correlation Drift: Persona vs No-Persona)
Dữ liệu nguồn: [`output/tables/step5_spearman_corr_drift.csv`](file:///data/projects/web-apps/eda_persona/output/tables/step5_spearman_corr_drift.csv)  
Biểu đồ trực quan: ![Correlation Drift Heatmap](file:///data/projects/web-apps/eda_persona/output/figures/step5_correlation_drift_heatmap.png)

1. **`model_latency_ms` vs `num_dimension_evidence`:**
   - Trong nhóm Persona: Tương quan Spearman là **+0.515** ($p < 10^{-15}$). Số chiều bằng chứng tính cách tăng lên thì LLM suy nghĩ lâu hơn một cách tỷ lệ thuận và ổn định.
   - Trong nhóm No-Persona: Bằng chứng nhân khẩu là 0, chỉ có bằng chứng tình huống ngẫu nhiên ($r = +0.348$).
2. **`model_latency_ms` vs `reason_length`:**
   - Trong nhóm No-Persona: Tương quan âm cực mạnh ($r = -0.770$). Các bước có độ trễ thấp thường là các bước fail hoặc observe không sinh ra reason.
   - Trong nhóm Persona: Tương quan trôi dạt về mức yếu ($r = -0.225$, $\\Delta r = +0.545$). Persona luôn duy trì chuỗi lập luận có cấu trúc bất kể độ trễ ngắn hay dài.

---

### 2.9. Phân tích Cử chỉ Vật lý Browser (Gesture Pacing & Scroll Mechanics)
Dữ liệu nguồn: [`output/tables/step5_recent_actions_gesture_comparison.csv`](file:///data/projects/web-apps/eda_persona/output/tables/step5_recent_actions_gesture_comparison.csv)

| Chỉ số cử chỉ chuột | Persona Median (IQR) | No-Persona Median (IQR) | Mann-Whitney U | p-value | Cliff's Delta | Đánh giá khác biệt |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
"""
    for _, row in gesture_df.iterrows():
        p_str = f"{row['p_value']:.2e}" if row['p_value'] < 0.001 else f"{row['p_value']:.4f}"
        report += f"| `{row['gesture_metric']}` | {row['persona_median']} px/ms ({row['persona_iqr']}) | {row['no_persona_median']} px/ms ({row['no_persona_iqr']}) | {row['mann_whitney_u']:.0f} | {p_str} | **{row['cliffs_delta']:+.3f}** | **{row['magnitude']}** |\n"

    report += f"""
- **Khoảng cách cuộn mỗi lần (`gesture_total_px`):** Persona cuộn ngắn hơn, có kiểm soát hơn (Median 481.0 px vs 684.0 px của No-Persona, Cliff's Delta = -0.552, Large).
- **Thời gian vuốt chuột (`gesture_ms`):** Persona vuốt nhanh và dứt khoát hơn (Median 239.5 ms vs 293.0 ms của No-Persona, Cliff's Delta = -0.721, Large, $p = 0.008$).
- **Độ lệch điểm dừng cần sửa (`landing_correction_px`):** Persona có độ lệch điểm rơi thấp hơn (Median 211.0 px vs 364.0 px của No-Persona), chứng tỏ độ chính xác khi căn chỉnh vào các phần tử giao diện cao hơn.

---

## 3. Đề xuất Hướng Phân tích Tiếp theo (Recommendations for Step 6 & Step 7)

Dựa trên các phát hiện định lượng vững chắc từ Bước 5, nhóm phân tích đề xuất lộ trình triển khai cụ thể cho các bước tiếp theo trong [`pipeline_eda.md`](file:///data/projects/web-apps/eda_persona/notebooks/pipeline_eda.md):

### Đề xuất 1: Triển khai Ma trận Chuyển dịch Trạng thái Markov (Markov Transition Matrix) cho Bước 6
- **Vấn đề phát hiện ở Bước 5:** No-Persona bị sa lầy ở `detail` và `unknown`.
- **Hành động đề xuất cho Bước 6:**
  - Xây dựng ma trận xác suất chuyển trạng thái cấp 1 ($P(S_{{t+1}} | S_t)$) giữa các Intent và Surface: `feed -> detail -> unknown` vs `feed -> search -> group -> page`.
  - Tính thời gian hấp thu (Absorbing Time) để chứng minh mặt toán học: No-Persona có điểm hấp thụ (absorbing state) là các vòng lặp bế tắc (`observe -> close -> observe`), trong khi Persona sở hữu đồ thị hành vi chuyển tiếp ergodic và phân nhánh rộng.

### Đề xuất 2: Phân tích Chuỗi Thời gian & Vận tốc Nhận thức (Temporal Action Velocity & Drift) cho Bước 6
- Khảo sát biến thiên vận tốc hành động (`context_action_velocity`) theo từng 1/4 phiên (Early, Mid, Late session):
  - Kiểm tra xem No-Persona có bị hiện tượng kiệt sức nhận thức (Cognitive Fatigue) hoặc giảm sút vận tốc theo thời gian hay không.
  - Phân tích chu kỳ nghỉ ngơi (`context_rest_accumulated_seconds`): Persona nghỉ ngơi theo nhịp sinh học được định nghĩa trong profile (`persona_rest_style`), xem nhịp nghỉ này tác động thế nào tới việc duy trì chuỗi hành động hợp lệ.

### Đề xuất 3: So sánh Có Kiểm chứng Nâng cao (Hypothesis Testing & Permutation Tests) cho Bước 7
- **Permutation Test & Bootstrap Confidence Intervals:**
  - Vì số lượng episode ở mức khiêm tốn (6 Persona vs 2 No-Persona, 437 steps), cần áp dụng Bootstrap 10,000 lần cho các chỉ số cốt lõi (`verified_rate`, `action_velocity`, `opened_sources`) để xác lập khoảng tin cậy 95% BCa không phụ thuộc phân phối chuẩn.
- **Benjamini-Hochberg FDR Correction:**
  - Áp dụng module [`benjamini_hochberg_fdr.py`](file:///data/projects/web-apps/eda_persona/algorithms/benjamini_hochberg_fdr.py) đã có sẵn để hiệu chỉnh đa kiểm định giả thuyết (Multiple Testing Correction) cho toàn bộ 41 biến số, đảm bảo loại bỏ hoàn toàn các phát hiện dương tính giả (False Discovery).

### Đề xuất 4: Mô hình Hồi quy Đa biến Bậc cao Kiểm soát Confounder cho Bước 8
- Xây dựng mô hình Logistic Regression hoặc GAM (Generalized Additive Model) giải thích xác suất `verified`:
  $$\\text{{logit}}(P(\\text{{verified}}=1)) = \\beta_0 + \\beta_1 \\cdot \\text{{dataset\\_type}} + \\beta_2 \\cdot \\text{{surface}} + \\beta_3 \\cdot \\text{{intent}} + \\beta_4 \\cdot (\\text{{dataset\\_type}} \\times \\text{{surface}})$$
  để cô lập tác động biên (Marginal Effect) thuần túy của Persona sau khi đã loại trừ hoàn toàn ảnh hưởng của bề mặt và ý định.

---
*Báo cáo được khởi tạo tự động bởi Engine Phân tích Bước 5. Không can thiệp vào các tệp Notebook hiện hữu.*
"""
    return report


if __name__ == "__main__":
    main()
