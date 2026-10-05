import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

project_root = Path(__file__).resolve().parent.parent

# Đọc 2 bảng crosstab
p_csv = project_root / "output" / "tables" / "step5_behavior_crosstab_persona.csv"
np_csv = project_root / "output" / "tables" / "step5_behavior_crosstab_nopersona.csv"

ct_p = pd.read_csv(p_csv, index_col=0)
ct_np = pd.read_csv(np_csv, index_col=0)

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
fig, axes = plt.subplots(1, 2, figsize=(20, 8.5), gridspec_kw={'wspace': 0.18})

phases = ["Q1 (0-25% Early)", "Q2 (25-50% Mid-Early)", "Q3 (50-75% Mid-Late)", "Q4 (75-100% Late)"]
phase_x = np.arange(len(phases))

behavior_colors = {
    "1. Cuộn & Duyệt lướt (Scroll Feed)": "#3498db",
    "2. Đọc sâu bài viết (Deep Read)": "#2ecc71",
    "3. Tương tác xã hội (React/Social)": "#e67e22",
    "4. Tìm kiếm chủ đề (Search Query)": "#9b59b6",
    "5. Điều hướng giao diện (Navigate)": "#1abc9c",
    "6. Quan sát màn hình (Observe)": "#95a5a6",
    "7. Kết thúc phiên (End Session)": "#e74c3c",
    "8. Nghỉ ngơi / Đợi (Rest/Wait)": "#f39c12",
    "9. Khác (Other)": "#bdc3c7"
}

# --- SUBPLOT 1: PERSONA ---
ax1 = axes[0]
bottom_p = np.zeros(len(ct_p))
for col in ct_p.columns:
    vals = ct_p[col].values
    color = behavior_colors.get(col, "#7f8c8d")
    bars = ax1.bar(phase_x, vals, bottom=bottom_p, label=col, color=color, width=0.55, edgecolor="white", linewidth=1.0)
    for i, val in enumerate(vals):
        if val >= 7.0:
            ax1.text(phase_x[i], bottom_p[i] + val/2, f"{val:.1f}%", ha="center", va="center", fontsize=10, fontweight="bold", color="white" if color not in ["#f39c12", "#bdc3c7"] else "black")
    bottom_p += vals

ax1.set_xticks(phase_x)
ax1.set_xticklabels(phases, fontsize=11, fontweight="bold")
ax1.set_ylabel("Tỷ trọng Phân bổ Hành vi (%)", fontsize=12, fontweight="bold")
ax1.set_title("A. NHÓM CÓ PERSONA: Chu trình Nhận thức Định hướng & Tự chủ\n(Tìm kiếm/Navigate ở đầu phiên -> Đọc/Tương tác -> Tự chủ Kết thúc)", fontsize=13, fontweight="bold", pad=12)
ax1.set_ylim(0, 100)
ax1.grid(True, linestyle="--", alpha=0.5)

# Callout trên biểu đồ Persona
ax1.annotate(
    "Search (27.9%) + Navigate (10.5%)\nKhai phá nạp Working Memory",
    xy=(0, 75), xytext=(0.4, 90),
    arrowprops=dict(arrowstyle="->", color="#9b59b6", lw=1.8),
    bbox=dict(boxstyle="round,pad=0.3", fc="#f3e5f5", ec="#9b59b6", lw=1.2),
    fontsize=9.5, fontweight="bold"
)
ax1.annotate(
    "End Session (22.5%)\nChủ động thoát khi đạt mục tiêu",
    xy=(3, 90), xytext=(2.2, 92),
    arrowprops=dict(arrowstyle="->", color="#e74c3c", lw=1.8),
    bbox=dict(boxstyle="round,pad=0.3", fc="#ffebee", ec="#e74c3c", lw=1.2),
    fontsize=9.5, fontweight="bold"
)

# --- SUBPLOT 2: NO-PERSONA ---
ax2 = axes[1]
bottom_np = np.zeros(len(ct_np))
for col in ct_np.columns:
    vals = ct_np[col].values
    color = behavior_colors.get(col, "#7f8c8d")
    bars = ax2.bar(phase_x, vals, bottom=bottom_np, label=col, color=color, width=0.55, edgecolor="white", linewidth=1.0)
    for i, val in enumerate(vals):
        if val >= 7.0:
            ax2.text(phase_x[i], bottom_np[i] + val/2, f"{val:.1f}%", ha="center", va="center", fontsize=10, fontweight="bold", color="white" if color not in ["#f39c12", "#bdc3c7"] else "black")
    bottom_np += vals

ax2.set_xticks(phase_x)
ax2.set_xticklabels(phases, fontsize=11, fontweight="bold")
ax2.set_title("B. NHÓM KHÔNG PERSONA: Quan sát Thụ động & Buông xuôi Bế tắc\n(Observe áp đảo 33-46% -> Pha 4 xuất hiện ~9% Rest 'chán chờ hết giờ')", fontsize=13, fontweight="bold", pad=12)
ax2.set_ylim(0, 100)
ax2.grid(True, linestyle="--", alpha=0.5)

# Callout trên biểu đồ No-Persona
ax2.annotate(
    "Observe áp đảo (33.3% - 45.5%)\nNhìn màn hình thụ động do thiếu mục tiêu",
    xy=(2, 60), xytext=(1.2, 85),
    arrowprops=dict(arrowstyle="->", color="#7f8c8d", lw=1.8),
    bbox=dict(boxstyle="round,pad=0.3", fc="#eceff1", ec="#7f8c8d", lw=1.2),
    fontsize=9.5, fontweight="bold"
)
ax2.annotate(
    "Pha 4: Rest (8.7% ~ 9%)\n'Chán chường buông xuôi, đợi hết giờ'",
    xy=(3, 94), xytext=(1.8, 93),
    arrowprops=dict(arrowstyle="->", color="#f39c12", lw=1.8),
    bbox=dict(boxstyle="round,pad=0.3", fc="#fff8e1", ec="#f39c12", lw=1.2),
    fontsize=9.5, fontweight="bold"
)

# Legend chung
handles, labels = ax1.get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, -0.05), ncol=5, frameon=True, facecolor="white", fontsize=11)

fig_path = project_root / "output" / "figures" / "step5_temporal_behavior_distribution.png"
fig.savefig(fig_path, dpi=300, bbox_inches="tight")
print(f"[✓] Đã tạo thành công biểu đồ: {fig_path}")
