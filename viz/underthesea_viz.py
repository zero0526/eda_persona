"""
Module: underthesea_viz.py
Mục đích: Trực quan hóa phân phối token và Log-Odds Ratio (Diverging Bar Chart)
giữa 2 nhóm Persona vs No-Persona sau khi tách từ bằng underthesea.

Tuân thủ quy chuẩn: Module trực quan hóa độc lập trong viz/, xuất ảnh sang output/figures/.
"""

from pathlib import Path
from typing import Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


def plot_underthesea_log_ratio_divergence(
    log_ratio_res: Dict[str, Any],
    top_k: int = 12,
    output_path: Path = None
) -> plt.Figure:
    """
    Vẽ biểu đồ phân hóa từ vựng (Diverging Horizontal Bar Chart & Probability Comparison):
    - Subplot 1 (Trái): Biểu đồ thanh lệch hướng (Diverging Bar Chart) của Log-Ratio:
      * Thanh sang phải (Xanh #2b5c8f): Từ đặc trưng của Persona (LR > 0)
      * Thanh sang trái (Cam #d95f02): Từ đặc trưng của No-Persona (LR < 0)
    - Subplot 2 (Phải): So sánh xác suất xuất hiện P_P(w) vs P_N(w) của các từ tiêu biểu.
    """
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, axes = plt.subplots(1, 2, figsize=(16, 8), gridspec_kw={"width_ratios": [1.2, 1.0]})

    df_lr = log_ratio_res["log_ratio_table"]

    # 1. Trích xuất Top K từ mỗi phía
    top_p = df_lr[df_lr["log_ratio"] > 0].head(top_k)
    top_np = df_lr[df_lr["log_ratio"] < 0].tail(top_k).iloc[::-1]

    # Kết hợp lại để vẽ diverging
    combined = pd.concat([top_p, top_np]).sort_values(by="log_ratio", ascending=True)

    # Subplot 1: Diverging Bar Chart
    ax1 = axes[0]
    colors = ["#d95f02" if x < 0 else "#2b5c8f" for x in combined["log_ratio"]]

    bars = ax1.barh(combined["token"], combined["log_ratio"], color=colors, alpha=0.88, edgecolor="black", linewidth=0.6)
    ax1.axvline(0, color="gray", linestyle="--", linewidth=1.2)

    ax1.set_xlabel("Hệ số Log-Ratio: $LR(w) = \\ln\\left(\\frac{P_P(w) + \\epsilon}{P_N(w) + \\epsilon}\\right)$", fontsize=11, fontweight="bold")
    ax1.set_title("1. Phân Hóa Từ Vựng Đặc Trưng Trong Lập Luận CoT\n[Thanh Cam: Thiên về No-Persona ($LR < 0$) | Thanh Xanh: Thiên về Persona ($LR > 0$)]",
                  fontsize=12, fontweight="bold", pad=12)

    for bar, lr in zip(bars, combined["log_ratio"]):
        width = bar.get_width()
        if width > 0:
            ax1.text(width + 0.15, bar.get_y() + bar.get_height()/2, f"+{lr:.2f}",
                     va="center", ha="left", fontsize=9, fontweight="bold", color="#1c3d5a")
        else:
            ax1.text(width - 0.15, bar.get_y() + bar.get_height()/2, f"{lr:.2f}",
                     va="center", ha="right", fontsize=9, fontweight="bold", color="#8c3d00")

    # Subplot 2: Xác suất xuất hiện P_P vs P_N
    ax2 = axes[1]
    # Lấy top 8 từ mỗi phía để so sánh xác suất
    sample_tokens = pd.concat([top_p.head(8), top_np.head(8)])
    
    y = np.arange(len(sample_tokens))
    bar_width = 0.38

    b1 = ax2.barh(y - bar_width/2, sample_tokens["prob_persona"] * 100, bar_width,
                  label="P(Persona) %", color="#2b5c8f", alpha=0.85)
    b2 = ax2.barh(y + bar_width/2, sample_tokens["prob_nopersona"] * 100, bar_width,
                  label="P(No-Persona) %", color="#d95f02", alpha=0.85)

    ax2.set_yticks(y)
    ax2.set_yticklabels(sample_tokens["token"], fontsize=10, fontweight="bold")
    ax2.set_xlabel("Tần suất xác suất trong nhóm (%)", fontsize=11, fontweight="bold")
    ax2.set_title("2. So Sánh Xác Suất Xuất Hiện Tương Đối\n[Persona giàu từ ngữ cảnh; No-Persona áp đảo ở câu template]",
                  fontsize=12, fontweight="bold", pad=12)
    ax2.legend(loc="lower right", fontsize=10)
    ax2.invert_yaxis()

    plt.suptitle("PHÂN TÍCH LOG-RATIO TỪ VỰNG TIẾNG VIỆT (UNDERTHESEA) TRONG SUY NGHĨ: PERSONA VS NO-PERSONA",
                 fontsize=14, fontweight="bold", y=0.99)
    plt.tight_layout()

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"[✓] Đã lưu biểu đồ log-ratio tại: {output_path}")

    return fig
