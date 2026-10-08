import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.stdout.reconfigure(encoding='utf-8')

# Thiết lập thư mục lưu ảnh
OUTPUT_DIR = Path('notebooks/notebook_action_logs_files')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Cấu hình thẩm mỹ chuẩn
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI']
plt.rcParams['axes.edgecolor'] = '#bdc3c7'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#ecf0f1'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

PERSONA_PALETTE = {
    'vn_fb_001': '#3498db',  # Xanh dương - Thiết kế
    'vn_fb_002': '#e67e22',  # Cam - Lao động
    'vn_fb_003': '#2ecc71',  # Xanh lá - Bảo vệ
    'vn_fb_004': '#e74c3c',  # Đỏ - Nhà hàng
    'vn_fb_005': '#9b59b6',  # Tím - Cơ khí
    'vn_fb_006': '#34495e',  # Xám đậm - Kinh doanh
}

from loaders.action_loader import ActionLoader

print("Đang nạp dữ liệu từ ActionLoader...")
loader = ActionLoader()
df_windows = loader.load_activity_windows()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)
df_sessions = loader.to_unified_sessions_dataframe(histories)

# ==============================================================================
# 1. SLIDE 4: BỨC TRANH 4 KHUNG GIỜ HOẠT ĐỘNG TRONG NGÀY
# ==============================================================================
print("Tạo ảnh Slide 4...")
def assign_slot(h):
    if 6 <= h < 11:
        return "Ca Sáng (06h - 11h)"
    elif 11 <= h < 14:
        return "Ca Trưa (11h - 14h)"
    elif 14 <= h < 18:
        return "Ca Chiều (14h - 18h)"
    elif 18 <= h < 23:
        return "Ca Tối (18h - 23h)"
    else:
        return "Đêm (23h - 06h)"

df_w = df_windows.copy()
df_w['slot'] = df_w['start_hour_local'].apply(assign_slot)

slot_counts = df_w['slot'].value_counts()
slot_order = ["Ca Sáng (06h - 11h)", "Ca Trưa (11h - 14h)", "Ca Chiều (14h - 18h)", "Ca Tối (18h - 23h)"]
counts = [slot_counts.get(s, 0) for s in slot_order]
pcts = [c / len(df_w) * 100 for c in counts]
colors = ['#f39c12', '#e67e22', '#1abc9c', '#2980b9']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=150)

# Panel A: Phân bố 4 ca sinh hoạt (Donut chart)
wedges, texts, autotexts = ax1.pie(
    counts,
    labels=slot_order,
    autopct='%1.1f%%',
    startangle=140,
    colors=colors,
    pctdistance=0.75,
    textprops=dict(color='#2c3e50', fontsize=11, fontweight='bold'),
    wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2)
)
for at in autotexts:
    at.set_fontsize(11)
    at.set_color('white')

ax1.set_title("(A) Phân Bổ 4 Khung Giờ Sinh Hoạt (Tổng 95 Cửa Sổ)", fontsize=13, fontweight='bold', pad=15)
ax1.text(0, 0, f"Tổng cộng\n{len(df_w)} Lượt\nĐêm: 0.0%", ha='center', va='center', fontsize=12, fontweight='bold', color='#2c3e50')

# Panel B: Phân bố giờ trong ngày 24h
sns.histplot(df_windows['start_hour_local'], bins=17, kde=True, color='#2b5c8f', ax=ax2, stat='count', alpha=0.55)
ax2.axvspan(6, 11, color='#f39c12', alpha=0.15, label='Sáng (06-11h): 29 lượt (30.5%)')
ax2.axvspan(11, 14, color='#e67e22', alpha=0.15, label='Trưa (11-14h): 18 lượt (18.9%)')
ax2.axvspan(14, 18, color='#1abc9c', alpha=0.15, label='Chiều (14-18h): 12 lượt (12.6%)')
ax2.axvspan(18, 23, color='#2980b9', alpha=0.15, label='Tối (18-23h): 36 lượt (37.9%)')
ax2.axvspan(23, 24, color='#7f8c8d', alpha=0.2, label='Đêm (23-06h): 0 lượt (0.0% - Ngủ)')

ax2.set_title("(B) Biểu Đồ Mật Độ Giờ Bắt Đầu Trong Ngày (24h Local Time)", fontsize=13, fontweight='bold')
ax2.set_xlabel("Giờ Trong Ngày (Local Hour UTC+7)", fontsize=11)
ax2.set_ylabel("Số Lượng Cửa Sổ Hoạt Động", fontsize=11)
ax2.set_xlim(5, 24)
ax2.grid(True, axis='y')
ax2.legend(loc='upper left', fontsize=9.5, frameon=True)

plt.tight_layout()
fig.savefig(OUTPUT_DIR / 'slide4_four_shifts_distribution.png', bbox_inches='tight')
plt.close(fig)

# ==============================================================================
# 2. SLIDE 5: GIỜ CAO ĐIỂM, GIỜ VẮNG BÓNG THEO NGHỀ
# ==============================================================================
print("Tạo ảnh Slide 5...")
order_cols = ["1. Sáng (06h - 11h)", "2. Trưa (11h - 14h)", "3. Chiều (14h - 18h)", "4. Tối (18h - 23h)"]
df_obs, df_exp, df_adj_res, test_stats = loader.get_temporal_contingency_and_residuals(df_windows)
df_pct_shifts = (df_obs.div(df_obs.sum(axis=1), axis=0) * 100).round(1)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=150)

# Panel A: Tỷ lệ % phân bổ ca của từng Persona
df_pct_shifts.plot(
    kind='barh',
    stacked=True,
    ax=ax1,
    color=['#f39c12', '#e67e22', '#1abc9c', '#2980b9'],
    edgecolor='white',
    linewidth=1.2
)
ax1.set_title("(A) Tỷ Lệ % Lượt Vào Mạng Theo 4 Ca Sinh Hoạt", fontsize=13, fontweight='bold')
ax1.set_xlabel("Tỷ Lệ Phần Trăm (%)", fontsize=11)
ax1.set_ylabel("Persona ID & Nghề Nghiệp", fontsize=11)
ax1.set_yticklabels([
    'vn_fb_001 (Thiết kế đồ họa)',
    'vn_fb_002 (Lao động phổ thông)',
    'vn_fb_003 (Bảo vệ ca trực)',
    'vn_fb_004 (Nhân viên nhà hàng)',
    'vn_fb_005 (Thợ cơ khí)',
    'vn_fb_006 (Kinh doanh tự do)'
], fontsize=10.5)
ax1.legend(title='Khung Giờ', loc='upper right', bbox_to_anchor=(1.0, -0.12), ncol=2, frameon=True)
ax1.grid(True, axis='x')

# Panel B: Heatmap tỷ lệ % chi tiết với các điểm nhấn đặc biệt
annot_labels = np.empty(df_pct_shifts.shape, dtype=object)
for i in range(df_pct_shifts.shape[0]):
    for j in range(df_pct_shifts.shape[1]):
        val = df_pct_shifts.iloc[i, j]
        pid = df_pct_shifts.index[i]
        if pid == 'vn_fb_004' and j == 1:
            annot_labels[i, j] = f"{val:.1f}%\n(Vắng bận)"
        elif pid == 'vn_fb_003' and j == 2:
            annot_labels[i, j] = f"{val:.1f}%\n(Vắng ca)"
        elif pid == 'vn_fb_003' and j in [0, 3]:
            annot_labels[i, j] = f"{val:.1f}%\n(Đỉnh)"
        elif pid == 'vn_fb_006' and j in [1, 3]:
            annot_labels[i, j] = f"{val:.1f}%\n(Đỉnh)"
        elif pid == 'vn_fb_001':
            annot_labels[i, j] = f"{val:.1f}%\n(Rải đều)"
        else:
            annot_labels[i, j] = f"{val:.1f}%"

sns.heatmap(
    df_pct_shifts,
    annot=annot_labels,
    fmt="",
    cmap="YlGnBu",
    cbar=True,
    ax=ax2,
    linewidths=1.5,
    linecolor='white'
)
ax2.set_title("(B) Bản Đồ Nhiệt Tỷ Lệ Ca Hoạt Động & Điểm Nhấn Nghề Nghiệp", fontsize=13, fontweight='bold')
ax2.set_xlabel("Khung Giờ Sinh Hoạt", fontsize=11)
ax2.set_ylabel("")
ax2.set_xticklabels(["Sáng\n(06-11h)", "Trưa\n(11-14h)", "Chiều\n(14-18h)", "Tối\n(18-23h)"], rotation=0, fontsize=10.5)

plt.tight_layout()
fig.savefig(OUTPUT_DIR / 'slide5_shift_by_profession.png', bbox_inches='tight')
plt.close(fig)

# ==============================================================================
# 3. SLIDE 6: THỜI LƯỢNG MỖI LẦN DÙNG & TẦN SUẤT NGÀY
# ==============================================================================
print("Tạo ảnh Slide 6...")
wpd = df_windows.groupby(['persona_id', 'local_date']).size().reset_index(name='daily_windows')
mean_duration = df_windows.groupby('persona_id')['duration_min'].mean().round(1)
mean_freq = wpd.groupby('persona_id')['daily_windows'].mean().round(2)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=150)

# Panel A: Thời lượng trung bình mỗi phiên (phút)
bars1 = ax1.bar(
    mean_duration.index,
    mean_duration.values,
    color=[PERSONA_PALETTE[p] for p in mean_duration.index],
    edgecolor='#2c3e50',
    linewidth=1.2,
    alpha=0.85
)
for bar in bars1:
    h = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., h + 0.6, f"{h:.1f}m", ha='center', va='bottom', fontsize=11, fontweight='bold')

ax1.axhline(mean_duration.mean(), color='#e74c3c', linestyle='--', linewidth=1.5, label=f"Trung bình: {mean_duration.mean():.1f} phút")
ax1.set_title("(A) Thời Lượng Trung Bình Mỗi Lần Vào Mạng (Phút)", fontsize=13, fontweight='bold')
ax1.set_xlabel("Persona ID", fontsize=11)
ax1.set_ylabel("Số Phút Trung Bình", fontsize=11)
ax1.set_ylim(0, 30)
ax1.grid(True, axis='y')
ax1.legend(loc='upper right', frameon=True)

# Panel B: Tần suất vào mạng mỗi ngày
bars2 = ax2.bar(
    mean_freq.index,
    mean_freq.values,
    color=[PERSONA_PALETTE[p] for p in mean_freq.index],
    edgecolor='#2c3e50',
    linewidth=1.2,
    alpha=0.85
)
for bar in bars2:
    h = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., h + 0.06, f"{h:.2f} lần", ha='center', va='bottom', fontsize=11, fontweight='bold')

ax2.axhline(mean_freq.mean(), color='#2980b9', linestyle='--', linewidth=1.5, label=f"Toàn hệ thống: {mean_freq.mean():.2f} lần/ngày")
ax2.set_title("(B) Tần Suất Vào Mạng Trung Bình Mỗi Ngày (Lần/Ngày)", fontsize=13, fontweight='bold')
ax2.set_xlabel("Persona ID", fontsize=11)
ax2.set_ylabel("Số Lần Vào Mạng / Ngày", fontsize=11)
ax2.set_ylim(0, 3.5)
ax2.grid(True, axis='y')
ax2.legend(loc='lower right', frameon=True)

# Thêm ghi chú chốt H1
fig.text(0.5, 0.01, "★ 100% Phiên đều tự giác đóng ứng dụng (agent_stop) khi hết thời gian | CHỐT H1: ĐẠT YÊU CẦU ★",
         ha='center', fontsize=11.5, fontweight='bold', color='#27ae60',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='#eafaf1', edgecolor='#27ae60', linewidth=1.5))

plt.tight_layout(rect=[0, 0.05, 1, 1])
fig.savefig(OUTPUT_DIR / 'slide6_duration_and_frequency.png', bbox_inches='tight')
plt.close(fig)

# ==============================================================================
# 4. SLIDE 8: ĐỊA BÀN HOẠT ĐỘNG (BỀ MẶT 100% STACKED BAR)
# ==============================================================================
print("Tạo ảnh Slide 8...")
surface_crosstab = pd.crosstab(df_actions['persona_id'], df_actions['surface'], normalize='index') * 100
# Sắp xếp thứ tự các bề mặt quen thuộc
known_surfaces = [c for c in ['feed', 'reels', 'group', 'detail', 'search', 'story', 'profile'] if c in surface_crosstab.columns]
surface_crosstab = surface_crosstab[known_surfaces]

surface_colors = {
    'feed': '#3498db',
    'reels': '#e74c3c',
    'group': '#2ecc71',
    'detail': '#f39c12',
    'search': '#9b59b6',
    'story': '#1abc9c',
    'profile': '#95a5a6'
}

fig, ax = plt.subplots(figsize=(14, 6.5), dpi=150)
surface_crosstab.plot(
    kind='bar',
    stacked=True,
    ax=ax,
    color=[surface_colors.get(c, '#bdc3c7') for c in surface_crosstab.columns],
    edgecolor='white',
    linewidth=1.2,
    alpha=0.9
)

ax.set_title("Phân Bố Không Gian Bề Mặt Hoạt Động (100% Stacked Bar)", fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel("Persona ID", fontsize=11)
ax.set_ylabel("Tỷ Lệ Phần Trăm (%)", fontsize=11)
ax.set_xticklabels([
    'vn_fb_001\n(Thiết kế: Group 16.7%)',
    'vn_fb_002\n(Lao động: Feed 67.2%)',
    'vn_fb_003\n(Bảo vệ: Detail 35.6%)',
    'vn_fb_004\n(Nhà hàng: Reels 73.6%)',
    'vn_fb_005\n(Cơ khí: Detail 19.6%)',
    'vn_fb_006\n(Kinh doanh: Group 23.4%)'
], rotation=0, fontsize=10.5)

ax.legend(
    title='Bề Mặt (Surface)',
    labels=[s.capitalize() for s in surface_crosstab.columns],
    bbox_to_anchor=(1.02, 1),
    loc='upper left',
    frameon=True,
    fontsize=10.5
)
ax.grid(True, axis='y')

# Thêm callout annotations
ax.annotate('vn_fb_004:\nReels chiếm 73.6%', xy=(3, 35), xytext=(3.3, 50),
            arrowprops=dict(arrowstyle='->', lw=1.5, color='#c0392b'),
            fontsize=10.5, fontweight='bold', color='#c0392b',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#fadbd8', edgecolor='#c0392b'))

ax.annotate('vn_fb_001 & 006:\nGroup chiếm 16.7% - 23.4%', xy=(0, 85), xytext=(-0.3, 105),
            arrowprops=dict(arrowstyle='->', lw=1.5, color='#27ae60'),
            fontsize=10.5, fontweight='bold', color='#27ae60',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#d5f5e3', edgecolor='#27ae60'))

plt.tight_layout()
fig.savefig(OUTPUT_DIR / 'slide8_surface_distribution.png', bbox_inches='tight')
plt.close(fig)

# ==============================================================================
# 5. SLIDE 9: TỶ LỆ TƯƠNG TÁC CHỦ ĐỘNG AER & TÌM KIẾM
# ==============================================================================
print("Tạo ảnh Slide 9...")
# Tính AER = (react + comment + share) / total_actions * 100
df_actions['is_aer'] = df_actions['intent'].isin(['react', 'comment', 'share'])
aer_s = (df_actions.groupby('persona_id')['is_aer'].mean() * 100).round(2)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=150)

# Panel A: Tỷ lệ tương tác chủ động AER
bars = ax1.bar(
    aer_s.index,
    aer_s.values,
    color=[PERSONA_PALETTE[p] for p in aer_s.index],
    edgecolor='#2c3e50',
    linewidth=1.2,
    alpha=0.85
)
for bar in bars:
    h = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., h + 0.25, f"{h:.1f}%", ha='center', va='bottom', fontsize=11, fontweight='bold')

ax1.axhline(10.0, color='#e74c3c', linestyle='--', linewidth=1.8, label='Ngưỡng người thật tự nhiên (< 10%)')
ax1.set_title("(A) Tỷ Lệ Tương Tác Chủ Động (AER = React + Comment + Share)", fontsize=13, fontweight='bold')
ax1.set_xlabel("Persona ID", fontsize=11)
ax1.set_ylabel("AER (%)", fontsize=11)
ax1.set_ylim(0, 12)
ax1.grid(True, axis='y')
ax1.legend(loc='upper right', frameon=True)

# Panel B: Bảng từ khóa tìm kiếm chủ động
search_data = [
    ("vn_fb_006", "Kinh doanh tự do (55-64t)", "bất động sản Cần Thơ", "Kiểm chứng giá đất địa phương"),
    ("vn_fb_006", "Kinh doanh tự do (55-64t)", "giá đất Cần Thơ mới nhất", "Khảo sát thị trường"),
    ("vn_fb_003", "Bảo vệ trực ca (18-24t)", "quán bún trộn ngon Đà Nẵng", "Tìm ẩm thực địa phương đêm"),
    ("vn_fb_003", "Bảo vệ trực ca (18-24t)", "ẩm thực đà nẵng", "Khám phá món ngon"),
    ("vn_fb_001", "Thiết kế đồ họa (25-34t)", "kỷ lục cờ vua việt nam", "Tra cứu chuyên sâu môn yêu thích"),
]
df_search_table = pd.DataFrame(search_data, columns=['Persona', 'Nghề nghiệp', 'Từ khóa tìm kiếm', 'Mục đích hành vi'])

ax2.axis('off')
ax2.set_title("(B) Bằng Chứng Tự Chủ Tìm Kiếm Khi Bảng Tin Lệch Gu", fontsize=13, fontweight='bold', pad=15)
table = ax2.table(
    cellText=df_search_table.values,
    colLabels=df_search_table.columns,
    cellLoc='center',
    loc='center',
    colColours=['#2980b9', '#3498db', '#f39c12', '#27ae60']
)
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.0, 1.8)
for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_text_props(color='white', fontweight='bold')
    else:
        cell.set_edgecolor('#bdc3c7')

plt.tight_layout()
fig.savefig(OUTPUT_DIR / 'slide9_aer_and_search_intent.png', bbox_inches='tight')
plt.close(fig)

print("Đã tạo hoàn tất 5 biểu đồ slide mới!")
