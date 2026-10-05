"""
Module: temporal_dynamics_viz.py
Trực quan hóa Động lực học Vận tốc theo Pace & Phân bố Hành vi theo Thời gian.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd


def plot_velocity_and_behavior_dynamics(
    df_processed: pd.DataFrame,
    vel_by_pace: pd.DataFrame,
    ct_p: pd.DataFrame,
    ct_np: pd.DataFrame,
    output_path: Path = None
) -> plt.Figure:
    """
    Tạo biểu đồ 4 ô (2x2) chuyên sâu về:
    1. Quỹ đạo vận tốc trung bình theo 3 nhóm Pace (Persona) vs No-Persona qua 4 giai đoạn.
    2. Boxplot phân phối vận tốc theo từng Pace và Giai đoạn.
    3. Phân bố 100% Stacked Bar của Macro-Behaviors ở nhóm PERSONA qua 4 giai đoạn.
    4. Phân bố 100% Stacked Bar của Macro-Behaviors ở nhóm NO-PERSONA qua 4 giai đoạn.
    """
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, axes = plt.subplots(2, 2, figsize=(20, 14), gridspec_kw={'hspace': 0.32, 'wspace': 0.22})
    
    phases = ["Q1 (0-25%)", "Q2 (25-50%)", "Q3 (50-75%)", "Q4 (75-100%)"]
    phase_x = np.arange(len(phases))
    
    # -------------------------------------------------------------
    # SUBPLOT 1 (Top-Left): Quỹ đạo Vận tốc Trung bình theo Pace vs No-Persona
    # -------------------------------------------------------------
    ax1 = axes[0, 0]
    
    # Dữ liệu Persona theo pace
    pace_colors = {"quick": "#e74c3c", "balanced": "#3498db", "slow": "#2ecc71"}
    pace_markers = {"quick": "s", "balanced": "o", "slow": "^"}
    
    for pace in ["quick", "balanced", "slow"]:
        sub_p = vel_by_pace[vel_by_pace["persona_pace"] == pace].sort_values("time_bin_4")
        means = sub_p["mean"].values
        iqrs = sub_p["iqr"].values
        ax1.plot(
            phase_x, means,
            marker=pace_markers[pace], markersize=9, linewidth=2.8,
            color=pace_colors[pace], label=f"Persona: {pace.upper()} pace"
        )
        ax1.fill_between(phase_x, np.maximum(0, means - iqrs/2), means + iqrs/2, color=pace_colors[pace], alpha=0.15)
        for i, m in enumerate(means):
            ax1.annotate(f"{m:.2f}", (phase_x[i], m + 0.12), fontsize=10, fontweight="bold", color=pace_colors[pace], ha="center")
            
    # Dữ liệu No-Persona
    no_p_vel = df_processed[df_processed["dataset_type"] == "no_persona"].groupby("time_bin_4", observed=False)["context_action_velocity"].mean().values
    ax1.plot(
        phase_x, no_p_vel,
        marker="X", markersize=9, linewidth=2.5, linestyle="--",
        color="#7f8c8d", label="NO-PERSONA (Baseline)"
    )
    for i, m in enumerate(no_p_vel):
        ax1.annotate(f"{m:.2f}", (phase_x[i], m - 0.25), fontsize=10, fontweight="bold", color="#555555", ha="center")
        
    ax1.set_xticks(phase_x)
    ax1.set_xticklabels(phases, fontsize=11, fontweight="bold")
    ax1.set_ylabel("Vận tốc thao tác (Hành động / Phút)", fontsize=12, fontweight="bold")
    ax1.set_title("A. Quỹ đạo Vận tốc Biến đổi theo Thời gian & Phân hóa theo Pace", fontsize=14, fontweight="bold", pad=12)
    ax1.legend(loc="upper right", frameon=True, facecolor="white", framealpha=0.9, fontsize=11)
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.set_ylim(-0.2, 5.2)

    # -------------------------------------------------------------
    # SUBPLOT 2 (Top-Right): Phân bố Vận tốc theo Pace ở Q1 vs Q4 (Bar so sánh delta)
    # -------------------------------------------------------------
    ax2 = axes[0, 1]
    
    p_df = df_processed[df_processed["dataset_type"] == "persona"].copy()
    p_df["phase_label"] = p_df["time_bin_4"].map({
        "Q1 (0-25% Early)": "Q1 (Early)",
        "Q2 (25-50% Mid-Early)": "Q2",
        "Q3 (50-75% Mid-Late)": "Q3",
        "Q4 (75-100% Late)": "Q4 (Late)"
    })
    
    sns.boxplot(
        data=p_df, x="persona_pace", y="context_action_velocity", hue="phase_label",
        palette=["#bbdefb", "#90caf9", "#42a5f5", "#1565c0"], ax=ax2, width=0.6,
        showmeans=True, meanprops={"marker":"o", "markerfacecolor":"red", "markeredgecolor":"black", "markersize":"6"}
    )
    ax2.set_xlabel("Thuộc tính Pace trong Facebook Behavior", fontsize=12, fontweight="bold")
    ax2.set_ylabel("Vận tốc thao tác (Hành động / Phút)", fontsize=12, fontweight="bold")
    ax2.set_title("B. Phân phối Vận tốc theo Từng Pace qua 4 Giai đoạn (Persona)", fontsize=14, fontweight="bold", pad=12)
    ax2.legend(title="Giai đoạn", loc="upper right", frameon=True, facecolor="white", framealpha=0.9)
    ax2.grid(True, linestyle="--", alpha=0.6)

    # -------------------------------------------------------------
    # SUBPLOT 3 (Bottom-Left): Phân bố Macro-Behavior theo Thời gian (PERSONA)
    # -------------------------------------------------------------
    ax3 = axes[1, 0]
    
    behavior_colors = {
        "1. Cuộn & Duyệt lướt (Scroll Feed)": "#3498db",
        "2. Đọc sâu bài viết (Deep Read)": "#2ecc71",
        "3. Tương tác xã hội (React/Social)": "#e67e22",
        "4. Tìm kiếm chủ đề (Search Query)": "#9b59b6",
        "5. Điều hướng giao diện (Navigate)": "#1abc9c",
        "6. Quan sát màn hình (Observe)": "#95a5a6",
        "7. Kết thúc phiên (End Session)": "#e74c3c",
        "8. Nghỉ ngơi / Đợi (Rest/Wait)": "#f1c40f",
        "9. Khác (Other)": "#bdc3c7"
    }
    
    # Vẽ Stacked Bar Chart cho Persona
    bottom_p = np.zeros(len(ct_p))
    for col in ct_p.columns:
        vals = ct_p[col].values
        color = behavior_colors.get(col, "#7f8c8d")
        bars = ax3.bar(phase_x, vals, bottom=bottom_p, label=col, color=color, width=0.55, edgecolor="white", linewidth=0.8)
        # Thêm nhãn % nếu > 8%
        for i, val in enumerate(vals):
            if val >= 8.5:
                ax3.text(phase_x[i], bottom_p[i] + val/2, f"{val:.0f}%", ha="center", va="center", fontsize=9, fontweight="bold", color="white" if color not in ["#f1c40f", "#bdc3c7"] else "black")
        bottom_p += vals
        
    ax3.set_xticks(phase_x)
    ax3.set_xticklabels(phases, fontsize=11, fontweight="bold")
    ax3.set_ylabel("Tỷ trọng Hành vi (%)", fontsize=12, fontweight="bold")
    ax3.set_title("C. Phân bố Động lực học Hành vi theo Thời gian: NHÓM PERSONA", fontsize=14, fontweight="bold", pad=12)
    ax3.set_ylim(0, 100)
    ax3.grid(True, linestyle="--", alpha=0.5)

    # -------------------------------------------------------------
    # SUBPLOT 4 (Bottom-Right): Phân bố Macro-Behavior theo Thời gian (NO-PERSONA)
    # -------------------------------------------------------------
    ax4 = axes[1, 1]
    
    bottom_np = np.zeros(len(ct_np))
    for col in ct_np.columns:
        vals = ct_np[col].values
        color = behavior_colors.get(col, "#7f8c8d")
        bars = ax4.bar(phase_x, vals, bottom=bottom_np, label=col, color=color, width=0.55, edgecolor="white", linewidth=0.8)
        for i, val in enumerate(vals):
            if val >= 8.5:
                ax4.text(phase_x[i], bottom_np[i] + val/2, f"{val:.0f}%", ha="center", va="center", fontsize=9, fontweight="bold", color="white" if color not in ["#f1c40f", "#bdc3c7"] else "black")
        bottom_np += vals
        
    ax4.set_xticks(phase_x)
    ax4.set_xticklabels(phases, fontsize=11, fontweight="bold")
    ax4.set_ylabel("Tỷ trọng Hành vi (%)", fontsize=12, fontweight="bold")
    ax4.set_title("D. Phân bố Động lực học Hành vi theo Thời gian: NHÓM NO-PERSONA", fontsize=14, fontweight="bold", pad=12)
    ax4.set_ylim(0, 100)
    ax4.grid(True, linestyle="--", alpha=0.5)

    # Thêm Legend chung cho cả Subplot 3 & 4 ở dưới cùng
    handles, labels = ax3.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, 0.01), ncol=5, frameon=True, facecolor="white", fontsize=10.5)

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"[✓] Đã lưu biểu đồ động lực học thời gian tại: {output_path}")

    return fig
