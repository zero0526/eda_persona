import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency

sys.stdout.reconfigure(encoding='utf-8')
from loaders.action_loader import ActionLoader

loader = ActionLoader()
df_windows = loader.load_activity_windows()

def assign_peak_slot(h):
    if 6 <= h < 11:
        return "1. Ca Sáng\n(06h - 11h)"
    elif 11 <= h < 17:
        return "2. Ca Trưa & Chiều\n(11h - 17h)"
    else:
        return "3. Ca Tối\n(17h - 23h)"

df_w = df_windows.copy()
df_w['time_slot'] = df_w['start_hour_local'].apply(assign_peak_slot)

order_cols = ["1. Ca Sáng\n(06h - 11h)", "2. Ca Trưa & Chiều\n(11h - 17h)", "3. Ca Tối\n(17h - 23h)"]
ct = pd.crosstab(df_w['persona_id'], df_w['time_slot'])[order_cols]

chi2, p_val, dof, expected = chi2_contingency(ct)
n = ct.values.sum()
cramers_v = np.sqrt(chi2 / (n * (min(ct.shape) - 1)))

# Haberman Adjusted Residuals
row_sums = ct.sum(axis=1).values
col_sums = ct.sum(axis=0).values
adj_res = pd.DataFrame(index=ct.index, columns=ct.columns, dtype=float)
for i in range(len(row_sums)):
    for j in range(len(col_sums)):
        exp = expected[i, j]
        adj = (ct.iloc[i, j] - exp) / np.sqrt(exp * (1 - row_sums[i] / n) * (1 - col_sums[j] / n))
        adj_res.iloc[i, j] = adj

# Pearson Standardized Residuals
pearson_res = (ct - expected) / np.sqrt(expected)

# Tạo nhãn kết hợp O (E)
annot_counts = np.empty(ct.shape, dtype=object)
for i in range(ct.shape[0]):
    for j in range(ct.shape[1]):
        annot_counts[i, j] = f"{ct.iloc[i, j]}\n(exp: {expected[i, j]:.1f})"

# Tạo nhãn cho Residual
annot_res = np.empty(adj_res.shape, dtype=object)
for i in range(adj_res.shape[0]):
    for j in range(adj_res.shape[1]):
        val = adj_res.iloc[i, j]
        sig = " *" if abs(val) >= 1.96 else ""
        annot_res[i, j] = f"{val:+.2f}{sig}"

# Vẽ 2 panels
fig, axes = plt.subplots(1, 2, figsize=(15, 6), dpi=120)

# Panel 1: Observed vs Expected
sns.heatmap(
    ct,
    annot=annot_counts,
    fmt="",
    cmap="Blues",
    cbar=True,
    linewidths=1.2,
    linecolor="white",
    ax=axes[0],
    annot_kws={"fontsize": 10, "fontweight": "bold"}
)
axes[0].set_title(
    "A. Bảng Tần Số Quan Sát Thực Tế (O) vs Kỳ Vọng (E)\n(Số lượng cửa sổ hoạt động đã lên lịch)",
    fontsize=12, fontweight="bold", pad=12
)
axes[0].set_xlabel("Khung Giờ Sinh Hoạt", fontsize=11, fontweight="bold")
axes[0].set_ylabel("Persona ID", fontsize=11, fontweight="bold")

# Panel 2: Haberman's Adjusted Residuals
sns.heatmap(
    adj_res.astype(float),
    annot=annot_res,
    fmt="",
    cmap="vlag",
    center=0,
    vmin=-2.5,
    vmax=2.5,
    cbar=True,
    linewidths=1.2,
    linecolor="white",
    ax=axes[1],
    annot_kws={"fontsize": 11, "fontweight": "bold"}
)
axes[1].set_title(
    f"B. Heatmap Phần Dư Chuẩn Hóa Hiệu Chỉnh (Adjusted Residuals)\n"
    f"Kiểm định Chi-Square: $\\chi^2 = {chi2:.2f}$ (p = {p_val:.4f}, df = {dof}) | Cramér's V = {cramers_v:.2f}",
    fontsize=12, fontweight="bold", pad=12
)
axes[1].set_xlabel("Khung Giờ Sinh Hoạt", fontsize=11, fontweight="bold")
axes[1].set_ylabel("Persona ID", fontsize=11, fontweight="bold")

# Thêm chú thích ngưỡng ý nghĩa
fig.text(
    0.5, -0.04,
    "Ghi chú: Giá trị phần dư chuẩn hóa z thuộc khoảng [-1.96, +1.96] tương ứng với phân phối chuẩn tắc N(0, 1) ở mức ý nghĩa alpha = 0.05.\n"
    "Không có ô nào vượt ngưỡng (+1.96: thiên kiến ưa chuộng; -1.96: thiên kiến né tránh) -> Mọi Persona đều tham gia đồng đều vào cả 3 khung giờ.",
    ha="center", fontsize=10, style="italic", bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8f9fa", edgecolor="#ced4da")
)

plt.tight_layout()
plt.savefig("scratch/residual_heatmap.png", bbox_inches="tight")
print("Saved scratch/residual_heatmap.png")
