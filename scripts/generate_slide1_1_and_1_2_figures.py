import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Đảm bảo mã hóa UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

FIGURES_DIR = PROJECT_ROOT / "output" / "figures"
TABLES_DIR = PROJECT_ROOT / "output" / "tables"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

# Cấu hình thẩm mỹ
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI', 'Liberation Sans']
plt.rcParams['axes.edgecolor'] = '#7f8c8d'
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['grid.color'] = '#ecf0f1'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

PERSONA_PALETTE = {
    'vn_fb_001': '#3498db',  # Xanh dương - Thiết kế đồ họa
    'vn_fb_002': '#e67e22',  # Cam - Lao động / Gia đình
    'vn_fb_003': '#2ecc71',  # Xanh lá - Bảo vệ trực ca
    'vn_fb_004': '#e74c3c',  # Đỏ - Nhân viên nhà hàng (Reels)
    'vn_fb_005': '#9b59b6',  # Tím - Thợ cơ khí
    'vn_fb_006': '#34495e',  # Xám đậm - Gen X Kinh doanh
}

PERSONA_ROLES = {
    'vn_fb_001': 'vn_fb_001\n(Thiết kế đồ họa)',
    'vn_fb_002': 'vn_fb_002\n(Lao động / Gia đình)',
    'vn_fb_003': 'vn_fb_003\n(Bảo vệ trực ca)',
    'vn_fb_004': 'vn_fb_004\n(Nhân viên nhà hàng)',
    'vn_fb_005': 'vn_fb_005\n(Thợ cơ khí)',
    'vn_fb_006': 'vn_fb_006\n(Gen X Kinh doanh)',
}

PERSONA_ORDER = ['vn_fb_001', 'vn_fb_002', 'vn_fb_003', 'vn_fb_004', 'vn_fb_005', 'vn_fb_006']

print("Nạp dữ liệu từ ActionLoader...")
from loaders.action_loader import ActionLoader
loader = ActionLoader()
df_windows = loader.load_activity_windows()

# Sắp xếp đúng thứ tự persona 001 -> 006
df_windows['persona_id'] = pd.Categorical(df_windows['persona_id'], categories=PERSONA_ORDER, ordered=True)
df_windows = df_windows.sort_values(by=['persona_id', 'start_at']).reset_index(drop=True)

# Gán 4 khung thời gian
def assign_slot(h):
    if 6 <= h < 11:
        return 'Sáng (06-11h)'
    elif 11 <= h < 14:
        return 'Trưa (11-14h)'
    elif 14 <= h < 18:
        return 'Chiều (14-18h)'
    elif 18 <= h < 23:
        return 'Tối (18-23h)'
    else:
        return 'Đêm (23-06h)'

df_windows['slot'] = df_windows['start_hour_local'].apply(assign_slot)
slot_order = ['Sáng (06-11h)', 'Trưa (11-14h)', 'Chiều (14-18h)', 'Tối (18-23h)']
wpd = df_windows.groupby(['persona_id', 'local_date'], observed=True).size().reset_index(name='daily_windows')

# ==============================================================================
# ẢNH 1: BỨC TRANH 4 KHUNG GIỜ SINH HOẠT & PHÂN BỔ THEO PERSONA
# ==============================================================================
print("Tạo Ảnh 1: Histogram 4 khung giờ và Phân bổ Persona...")

fig1, (ax1a, ax1b) = plt.subplots(1, 2, figsize=(20, 9.2), dpi=300, gridspec_kw={'width_ratios': [1, 1.25], 'wspace': 0.28})

# Panel A: Histogram 24 Giờ & 4 Khung Giờ Sinh Hoạt
sns.histplot(
    df_windows['start_hour_local'],
    bins=17,
    binrange=(6, 23),
    kde=True,
    color='#2c3e50',
    stat='count',
    alpha=0.35,
    ax=ax1a,
    line_kws={'linewidth': 2.2, 'color': '#1a252f'}
)

# Tô màu 4 dải khung giờ sinh hoạt
ax1a.axvspan(6, 11, color='#ffeaa7', alpha=0.45)
ax1a.axvspan(11, 14, color='#fab1a0', alpha=0.45)
ax1a.axvspan(14, 18, color='#55efc4', alpha=0.35)
ax1a.axvspan(18, 23, color='#74b9ff', alpha=0.40)

# Đường trung vị
median_h = float(df_windows['start_hour_local'].median())
ax1a.axvline(median_h, color='#c0392b', linestyle='--', linewidth=2.0, label=f'Trung vị: {median_h:.1f}h (15h chiều)')

# Thêm nhãn ca sinh hoạt trực tiếp trên đỉnh các dải màu (rất rõ ràng)
ax1a.text(8.5, 12.8, "CA SÁNG\n29 phiên (30.5%)\n[06h - 11h]", ha='center', va='top', fontsize=9.2, fontweight='bold', color='#7f5f00',
          bbox=dict(boxstyle='round,pad=0.25', facecolor='#ffffff', edgecolor='#ffeaa7', alpha=0.85))
ax1a.text(12.5, 12.8, "CA TRƯA\n18 phiên (18.9%)\n[11h - 14h]", ha='center', va='top', fontsize=9.2, fontweight='bold', color='#a83210',
          bbox=dict(boxstyle='round,pad=0.25', facecolor='#ffffff', edgecolor='#fab1a0', alpha=0.85))
ax1a.text(16.0, 12.8, "CA CHIỀU\n12 phiên (12.6%)\n[14h - 18h]", ha='center', va='top', fontsize=9.2, fontweight='bold', color='#00695c',
          bbox=dict(boxstyle='round,pad=0.25', facecolor='#ffffff', edgecolor='#55efc4', alpha=0.85))
ax1a.text(20.5, 12.8, "CA TỐI (ĐỈNH)\n36 phiên (37.9%)\n[18h - 23h]", ha='center', va='top', fontsize=9.2, fontweight='bold', color='#0d47a1',
          bbox=dict(boxstyle='round,pad=0.25', facecolor='#ffffff', edgecolor='#74b9ff', alpha=0.85))

ax1a.set_title("(A) Phân Bổ 24 Giờ & 4 Khung Giờ Sinh Hoạt Trong Ngày (Tổng 95 Phiên)", fontsize=12.5, fontweight='bold', pad=12)
ax1a.set_xlabel("Giờ trong ngày (Local Hour UTC+7)", fontsize=11, fontweight='bold', labelpad=8)
ax1a.set_ylabel("Số lượng phiên hoạt động", fontsize=11, fontweight='bold')
ax1a.set_xlim(5.5, 23.5)
ax1a.set_xticks(range(6, 24, 2))
ax1a.set_xticklabels([f"{h:02d}:00" for h in range(6, 24, 2)], fontsize=9.5)
ax1a.set_ylim(0, 13.8)
ax1a.grid(True, axis='y')
ax1a.legend(loc='upper left', frameon=True, fontsize=9.0, facecolor='#ffffff', edgecolor='#bdc3c7')

# Panel B: Bản đồ Tỷ lệ 4 Ca theo từng Persona & Phân Nhóm Dấu Ấn Nghề Nghiệp
ct_pct = pd.crosstab(df_windows['persona_id'], df_windows['slot'], normalize='index')[slot_order] * 100
ct_pct = ct_pct.reindex(PERSONA_ORDER)

# Tính thêm thời lượng trung bình trong từng ca để bổ sung góc nhìn sâu sắc
dur_by_shift = df_windows.pivot_table(index='persona_id', columns='slot', values='duration_min', aggfunc='mean')
dur_by_shift = dur_by_shift.reindex(index=PERSONA_ORDER, columns=slot_order)

annot_matrix = np.empty(ct_pct.shape, dtype=object)
for r_idx, pid in enumerate(PERSONA_ORDER):
    for c_idx, s_name in enumerate(slot_order):
        val = ct_pct.loc[pid, s_name]
        d_val = dur_by_shift.loc[pid, s_name]
        dur_str = f"~{d_val:.0f}m" if not np.isnan(d_val) else "-"
        
        if pid == 'vn_fb_004' and s_name == 'Trưa (11-14h)':
            annot_matrix[r_idx, c_idx] = f"0.0%\n(NÉ TRƯA)"
        elif pid == 'vn_fb_003' and s_name == 'Chiều (14-18h)':
            annot_matrix[r_idx, c_idx] = f"0.0%\n(NÉ CHIỀU)"
        elif pid == 'vn_fb_006' and s_name == 'Sáng (06-11h)':
            annot_matrix[r_idx, c_idx] = f"{val:.1f}%\n(Ít vào, {dur_str})"
        elif pid == 'vn_fb_003' and s_name in ['Sáng (06-11h)', 'Tối (18-23h)']:
            annot_matrix[r_idx, c_idx] = f"{val:.1f}%\n(Đỉnh, {dur_str})"
        elif pid == 'vn_fb_004' and s_name in ['Chiều (14-18h)', 'Tối (18-23h)']:
            annot_matrix[r_idx, c_idx] = f"{val:.1f}%\n(Đỉnh, {dur_str})"
        elif pid == 'vn_fb_001':
            annot_matrix[r_idx, c_idx] = f"{val:.1f}%\n({dur_str})"
        else:
            annot_matrix[r_idx, c_idx] = f"{val:.1f}%\n({dur_str})"

sns.heatmap(
    ct_pct,
    annot=annot_matrix,
    fmt="",
    cmap="YlGnBu",
    cbar=True,
    ax=ax1b,
    linewidths=1.5,
    linecolor='white',
    annot_kws={'fontsize': 9.2, 'fontweight': 'bold'},
    cbar_kws={'label': 'Tỷ lệ phiên trong ca (%)'}
)

ax1b.set_title("(B) Phân Bổ Ca Hoạt Động & Thời Lượng Trung Bình Theo Persona (% & Phút)", fontsize=12.5, fontweight='bold', pad=12)
ax1b.set_xlabel("4 Khung Giờ Sinh Hoạt Trong Ngày (UTC+7)", fontsize=11, fontweight='bold', labelpad=8)
ax1b.set_ylabel("Persona ID (Sắp xếp tăng dần 001 → 006)", fontsize=11, fontweight='bold')
ax1b.set_xticklabels(["Ca Sáng\n(06-11h)", "Ca Trưa\n(11-14h)", "Ca Chiều\n(14-18h)", "Ca Tối\n(18-23h)"], rotation=0, fontsize=10)
ax1b.set_yticklabels([f"{p} ({p.split('_')[-1]})" for p in PERSONA_ORDER], rotation=0, fontsize=10)

# Hộp nhận định phân nhóm ở chân biểu đồ
# fig1.text(
#     0.5, 0.02,
#     "★ NHẬN ĐỊNH PHÂN NHÓM LỊCH TRÌNH THEO PERSONA (H1) ★\n"
#     "• Nhóm né tránh / giờ đặc thù: vn_fb_004 (Nhà hàng) NÉ TRƯA 0% (bận chạy bàn khách đông); vn_fb_003 (Bảo vệ) NÉ CHIỀU 0% & trưa 8.3% (ca trực nghiêm ngặt, dồn 2 đầu ca sáng/tối); vn_fb_006 (Gen X) ÍT VÀO SÁNG 7.7% (bận việc nhà, dồn trưa/tối).\n"
#     "• Nhóm linh hoạt / rải đều cả ngày: vn_fb_001 (Thiết kế đồ họa) rải đều các cữ sáng, trưa, tối nhờ tính chất tự do; vn_fb_005 (Thợ cơ khí) & vn_fb_002 (Lao động/Gia đình) rải đều theo các quãng nghỉ giải lao.",
#     ha='center',
#     fontsize=9.8,
#     fontweight='bold',
#     color='#196f3d',
#     bbox=dict(boxstyle='round,pad=0.6', facecolor='#eafaf1', edgecolor='#27ae60', linewidth=1.5)
# )

plt.tight_layout(rect=[0, 0.09, 1, 0.98])
fig1_path = FIGURES_DIR / "slide1_1_four_shifts_and_persona_distribution.png"
fig1.savefig(fig1_path, bbox_inches='tight')
plt.close(fig1)
print(f"  -> Đã lưu: {fig1_path}")


# ==============================================================================
# ẢNH 2: TẦN SUẤT SỬ DỤNG MẠNG XÃ HỘI TRÊN NGÀY & THỜI LƯỢNG SỬ DỤNG
# ==============================================================================
print("Tạo Ảnh 2: Tần suất sử dụng mạng xã hội / ngày & Thời lượng sử dụng...")

fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(19, 8.8), dpi=300)

# Panel A: Tần suất sử dụng mạng xã hội trên ngày (lần/ngày)
mean_freqs = [wpd[wpd['persona_id'] == p]['daily_windows'].mean() for p in PERSONA_ORDER]
overall_freq_mean = wpd['daily_windows'].mean()

bars_freq = ax2a.bar(
    range(len(PERSONA_ORDER)),
    mean_freqs,
    color=[PERSONA_PALETTE[p] for p in PERSONA_ORDER],
    edgecolor='#2c3e50',
    linewidth=1.2,
    alpha=0.85
)

for i, (bar, mf) in enumerate(zip(bars_freq, mean_freqs)):
    pid = PERSONA_ORDER[i]
    sub_wpd = wpd[wpd['persona_id'] == pid]['daily_windows']
    min_f = int(sub_wpd.min())
    max_f = int(sub_wpd.max())
    n_days = len(sub_wpd)
    ax2a.text(
        bar.get_x() + bar.get_width() / 2.,
        mf + 0.10,
        f"{mf:.2f} lần/ngày\n[{min_f}-{max_f}] lần\n({n_days} ngày)",
        ha='center',
        va='bottom',
        fontsize=8.8,
        fontweight='bold',
        color='#1a252f',
        bbox=dict(boxstyle='round,pad=0.25', facecolor='#ffffff', edgecolor='#d0d7de', alpha=0.9, linewidth=0.8)
    )

ax2a.axhline(overall_freq_mean, color='#2980b9', linestyle='--', linewidth=1.8, label=f"Toàn hệ thống: {overall_freq_mean:.2f} lần/ngày")
ax2a.set_title("(A) Tần Suất Vào Mạng Trung Bình Mỗi Ngày (Lần/Ngày)", fontsize=13, fontweight='bold', pad=12)
ax2a.set_xlabel("Persona ID (Sắp xếp tăng dần 001 → 006)", fontsize=11.5, fontweight='bold', labelpad=8)
ax2a.set_ylabel("Số lần vào mạng / Ngày", fontsize=11.5, fontweight='bold')
ax2a.set_xticks(range(len(PERSONA_ORDER)))
ax2a.set_xticklabels([PERSONA_ROLES[p] for p in PERSONA_ORDER], fontsize=9.0)
ax2a.set_ylim(0, 3.8)
ax2a.grid(True, axis='y')
ax2a.legend(loc='upper right', frameon=True, fontsize=9.5, facecolor='#ffffff', edgecolor='#bdc3c7')

# Panel B: Thời lượng mỗi lần sử dụng (Phút) kèm Sai số chuẩn và dải Min-Max
means_dur = [df_windows[df_windows['persona_id'] == p]['duration_min'].mean() for p in PERSONA_ORDER]
stds_dur = [df_windows[df_windows['persona_id'] == p]['duration_min'].std() for p in PERSONA_ORDER]
overall_duration_mean = df_windows['duration_min'].mean()

bars_dur = ax2b.bar(
    range(len(PERSONA_ORDER)),
    means_dur,
    yerr=stds_dur,
    capsize=5,
    color=[PERSONA_PALETTE[p] for p in PERSONA_ORDER],
    edgecolor='#2c3e50',
    linewidth=1.2,
    alpha=0.85,
    error_kw=dict(elinewidth=1.5, ecolor='#2c3e50', capthick=1.5)
)

for i, (bar, m, s) in enumerate(zip(bars_dur, means_dur, stds_dur)):
    pid = PERSONA_ORDER[i]
    sub_dur = df_windows[df_windows['persona_id'] == pid]['duration_min']
    min_val = sub_dur.min()
    max_val = sub_dur.max()
    ax2b.text(
        bar.get_x() + bar.get_width() / 2.,
        m + s + 1.2,
        f"{m:.1f}m\n±{s:.1f}m\n[{min_val:.0f}-{max_val:.0f}]m",
        ha='center',
        va='bottom',
        fontsize=8.8,
        fontweight='bold',
        color='#1a252f',
        bbox=dict(boxstyle='round,pad=0.25', facecolor='#ffffff', edgecolor='#d0d7de', alpha=0.9, linewidth=0.8)
    )

ax2b.axhline(8, color='#e74c3c', linestyle=':', linewidth=1.5, label='Biên dưới hợp đồng: 8m')
ax2b.axhline(32, color='#e67e22', linestyle='--', linewidth=1.5, label='Biên trên định mức: 32m')
ax2b.axhline(overall_duration_mean, color='#2980b9', linestyle='-', linewidth=1.8, label=f"Trung bình hệ thống: {overall_duration_mean:.1f} phút")

ax2b.set_title("(B) Thời Lượng Mỗi Lần Sử Dụng (Phút) & Dải Dao Động (Mean ± Std)", fontsize=13, fontweight='bold', pad=12)
ax2b.set_xlabel("Persona ID (Sắp xếp tăng dần 001 → 006)", fontsize=11.5, fontweight='bold', labelpad=8)
ax2b.set_ylabel("Thời lượng phiên (Phút)", fontsize=11.5, fontweight='bold')
ax2b.set_xticks(range(len(PERSONA_ORDER)))
ax2b.set_xticklabels([PERSONA_ROLES[p] for p in PERSONA_ORDER], fontsize=9.0)
ax2b.set_ylim(0, 45)
ax2b.grid(True, axis='y')
ax2b.legend(loc='upper right', frameon=True, fontsize=9.0, facecolor='#ffffff', edgecolor='#bdc3c7')

# Hộp nhận định phân nhóm ở chân biểu đồ
# fig2.text(
#     0.5, 0.02,
#     "★ NHẬN ĐỊNH VỀ TẦN SUẤT & THỜI LƯỢNG SỬ DỤNG (H1: ĐẠT YÊU CẦU) ★\n"
#     "• Tần suất: Nhóm linh hoạt / giải trí cao (001: 2.75, 005: 2.43, 004: 2.29 lần/ngày) vs Nhóm bận gia đình / ca trực nghiêm ngặt (002: 1.67, 003: 1.71 lần/ngày).\n"
#     "• Thời lượng: Phân hóa theo sở thích nội dung: Lướt Reels lâu nhất (004: 23.6m) - Thợ kỹ thuật dứt khoát nhanh nhất (005: 13.1m, std=2.3m) | 100% phiên tự dừng (agent_stop).",
#     ha='center',
#     fontsize=9.8,
#     fontweight='bold',
#     color='#196f3d',
#     bbox=dict(boxstyle='round,pad=0.6', facecolor='#eafaf1', edgecolor='#27ae60', linewidth=1.5)
# )

plt.tight_layout(rect=[0, 0.09, 1, 0.98])
fig2_path = FIGURES_DIR / "slide1_2_duration_and_daily_frequency.png"
fig2.savefig(fig2_path, bbox_inches='tight')
plt.close(fig2)
print(f"  -> Đã lưu: {fig2_path}")

print("\nHoàn tất tạo 2 ảnh mới phục vụ Slide 1.1 và 1.2 thành công!")
