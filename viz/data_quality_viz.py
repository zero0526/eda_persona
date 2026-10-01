"""
Module: data_quality_viz.py
Mục đích: Trực quan hóa chất lượng dữ liệu: Mẫu khuyết thiếu (Missing Patterns) đối sánh Persona vs No-Persona
và Phân bố ngoại lai (Outlier Distribution) trên các đại lượng độ trễ & cử chỉ vật lý.
Tuân thủ quy chuẩn: Module trực quan hóa độc lập trong viz/, xuất ảnh sang output/figures/.
"""

from pathlib import Path
from typing import Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


def plot_missing_patterns_comparison(
    df_missing: pd.DataFrame,
    output_path: Path = None,
    top_n: int = 15
) -> plt.Figure:
    """
    Vẽ biểu đồ so sánh tỷ lệ khuyết thiếu giữa nhóm Persona vs No-Persona của Top N trường khuyết thiếu nhất,
    làm nổi bật bằng chứng thực nghiệm của cơ chế Missing by Design (MAR).
    """
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, ax = plt.subplots(figsize=(12, 7))

    top_df = df_missing[df_missing["Total_Missing"] > 0].head(top_n).copy()
    
    # Định dạng dữ liệu cho biểu đồ nhóm
    melted = []
    for _, row in top_df.iterrows():
        melted.append({
            "Field": row["Field"],
            "Nhóm": "Persona (Can thiệp)",
            "Tỷ lệ Khuyết (%)": row["Persona_Missing_Pct"],
            "Cơ chế": row["Missing_Mechanism"]
        })
        melted.append({
            "Field": row["Field"],
            "Nhóm": "No-Persona (Đối chứng)",
            "Tỷ lệ Khuyết (%)": row["NoPersona_Missing_Pct"],
            "Cơ chế": row["Missing_Mechanism"]
        })
    df_plot = pd.DataFrame(melted)

    # Vẽ barplot ngang
    sns.barplot(
        data=df_plot,
        y="Field",
        x="Tỷ lệ Khuyết (%)",
        hue="Nhóm",
        palette=["#2b5c8f", "#d95f02"],
        ax=ax
    )

    ax.set_title(f"Top {top_n} Biến Khuyết Thiếu: So Sánh Cơ Chế Missing By Design (Persona vs No-Persona)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Tỷ lệ Khuyết Thiếu (%)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Tên Trường Dữ Liệu", fontsize=11, fontweight="bold")
    ax.set_xlim(0, 105)
    ax.legend(title="Nhóm Thực Nghiệm", frameon=True, facecolor="white")

    # Thêm đường gióng 100%
    ax.axvline(100, color="gray", linestyle="--", alpha=0.6)

    plt.tight_layout()
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"[✓] Đã lưu biểu đồ missing pattern tại: {output_path}")

    return fig


def plot_outliers_boxplots(
    df_steps: pd.DataFrame,
    output_path: Path = None
) -> plt.Figure:
    """
    Vẽ 4 boxplot phân bố ngoại lai đối sánh giữa nhóm Persona vs No-Persona
    trên các biến: model_latency_ms, tool_execution_ms, recent_last_gesture_px, context_action_velocity.
    """
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))

    plot_configs = [
        ("model_latency_ms", "Độ trễ Suy luận LLM (ms)", axes[0, 0], False),
        ("tool_execution_ms", "Độ trễ Trình duyệt DOM (ms)", axes[0, 1], False),
        ("recent_last_gesture_px", "Quãng đường Cuộn chuột (px)", axes[1, 0], False),
        ("context_action_velocity", "Vận tốc Thao tác (actions/phút)", axes[1, 1], False)
    ]

    for col, title, ax, is_log in plot_configs:
        valid_df = df_steps.dropna(subset=[col])
        sns.boxplot(
            data=valid_df,
            x="dataset_type",
            y=col,
            palette=["#2b5c8f", "#d95f02"],
            ax=ax,
            width=0.45,
            fliersize=4
        )
        # Thêm stripplot để nhìn rõ từng điểm dữ liệu và outlier
        sns.stripplot(
            data=valid_df,
            x="dataset_type",
            y=col,
            color="black",
            alpha=0.3,
            size=3,
            jitter=0.2,
            ax=ax
        )
        ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
        ax.set_xlabel("Nhóm Thực Nghiệm", fontsize=10, fontweight="bold")
        ax.set_ylabel(col, fontsize=10)
        ax.set_xticklabels(["Persona (Can thiệp)", "No-Persona (Đối chứng)"])

    plt.suptitle("Phân Bố Ngoại Lai (Outliers) & Đối Sánh Hành Vi Giữa Hai Nhóm Thực Nghiệm", fontsize=14, fontweight="bold", y=1.00)
    plt.tight_layout()

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"[✓] Đã lưu biểu đồ outlier distribution tại: {output_path}")

    return fig
