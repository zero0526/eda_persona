"""
Module: data_lineage_viz.py
Mục đích: Trực quan hóa cấu trúc dữ liệu đa cấp (Units of Analysis) và phân bổ cỡ mẫu giữa
nhóm Persona vs No-Persona, phục vụ Bước 2 trong Pipeline EDA.
Tuân thủ quy chuẩn: Module trực quan hóa độc lập trong viz/, xuất ảnh sang output/figures/.
"""

from pathlib import Path
from typing import Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def plot_data_hierarchy_distribution(
    summary_df: pd.DataFrame,
    output_path: Path = None
) -> plt.Figure:
    """
    Vẽ biểu đồ thanh phân bổ số lượng bản ghi qua 4 cấp độ phân tích (Multi-level Hierarchy)
    đối sánh giữa nhóm Persona (Intervention) và No-Persona (Neutral Control).

    Parameters:
    -----------
    summary_df : pd.DataFrame
        Bảng tổng hợp từ algorithms.data_lineage_inspector.
    output_path : Path, optional
        Đường dẫn file ảnh PNG để lưu trữ.

    Returns:
    --------
    plt.Figure
    """
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    # Chuẩn bị dữ liệu vẽ
    plot_data = []
    for _, row in summary_df.iterrows():
        unit = row["Cấp độ phân tích (Unit of Analysis)"].split(" (")[0]
        plot_data.append({
            "Unit": unit,
            "Nhóm": "Persona (Can thiệp)",
            "Số lượng": row["Nhóm Persona"]
        })
        plot_data.append({
            "Unit": unit,
            "Nhóm": "No-Persona (Đối chứng)",
            "Số lượng": row["Nhóm No-Persona"]
        })
    df_plot = pd.DataFrame(plot_data)

    # 1. Bar plot: Phân bổ tuyệt đối theo log scale
    sns.barplot(
        data=df_plot,
        x="Unit",
        y="Số lượng",
        hue="Nhóm",
        palette=["#2b5c8f", "#d95f02"],
        ax=ax1
    )
    ax1.set_yscale("log")
    ax1.set_title("Quy mô 4 Cấp độ Phân tích (Log Scale)", fontsize=12, fontweight="bold", pad=10)
    ax1.set_xlabel("Đơn vị Phân tích (Unit of Analysis)", fontsize=10, fontweight="bold")
    ax1.set_ylabel("Số lượng bản ghi N (Log10)", fontsize=10, fontweight="bold")
    ax1.tick_params(axis="x", rotation=15)
    
    # Hiển thị số liệu trực tiếp trên thanh
    for p in ax1.patches:
        height = p.get_height()
        if height > 0:
            ax1.annotate(
                f"{int(height)}",
                (p.get_x() + p.get_width() / 2., height),
                ha="center", va="bottom",
                fontsize=9, fontweight="bold",
                xytext=(0, 3), textcoords="offset points"
            )

    # 2. Donut plot: Tỷ lệ phân bổ Step giữa 2 nhóm
    step_row = summary_df[summary_df["Cấp độ phân tích (Unit of Analysis)"].str.contains("Step")].iloc[0]
    persona_steps = step_row["Nhóm Persona"]
    nopersona_steps = step_row["Nhóm No-Persona"]
    
    colors = ["#2b5c8f", "#d95f02"]
    wedges, texts, autotexts = ax2.pie(
        [persona_steps, nopersona_steps],
        labels=["Persona Steps", "No-Persona Steps"],
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        textprops=dict(color="black", fontweight="bold"),
        wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2)
    )
    ax2.set_title(f"Tỷ lệ Đơn vị Phân tích Cơ sở (Step Level: N = {persona_steps + nopersona_steps})", fontsize=12, fontweight="bold", pad=10)

    plt.tight_layout()

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"[✓] Đã lưu biểu đồ cấu trúc dữ liệu tại: {output_path}")

    return fig
