import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Đảm bảo UTF-8
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

PERSONA_ORDER = ['vn_fb_001', 'vn_fb_002', 'vn_fb_003', 'vn_fb_004', 'vn_fb_005', 'vn_fb_006']
PERSONA_LABELS = {
    'vn_fb_001': 'vn_fb_001\n(Thiết kế đồ họa)',
    'vn_fb_002': 'vn_fb_002\n(Lao động / Gia đình)',
    'vn_fb_003': 'vn_fb_003\n(Bảo vệ trực ca)',
    'vn_fb_004': 'vn_fb_004\n(Nhân viên nhà hàng)',
    'vn_fb_005': 'vn_fb_005\n(Thợ cơ khí)',
    'vn_fb_006': 'vn_fb_006\n(Gen X Kinh doanh)',
}

PERSONA_PALETTE = {
    'vn_fb_001': '#3498db',
    'vn_fb_002': '#e67e22',
    'vn_fb_003': '#2ecc71',
    'vn_fb_004': '#e74c3c',
    'vn_fb_005': '#9b59b6',
    'vn_fb_006': '#34495e',
}

print("1. Nạp dữ liệu actions và tính toán scroll dynamics...")
from loaders.action_loader import ActionLoader
loader = ActionLoader()
df_actions = loader.to_unified_actions_dataframe()
profiles, contracts = loader.load_persona_profiles_and_contracts()

scroll_stats = []

for pid in PERSONA_ORDER:
    sub = df_actions[df_actions['persona_id'] == pid].sort_values(by=['session_id', 'step_index']).copy()
    
    # Tính độ trễ giữa các step
    sub['prev_elapsed'] = sub.groupby('session_id')['elapsed_seconds'].shift(1)
    sub['latency_s'] = sub['elapsed_seconds'] - sub['prev_elapsed']
    
    # Lọc hành vi cuộn
    scroll_mask = sub['intent'].isin(['scroll', 'scroll_comments'])
    sub_scroll = sub[scroll_mask]
    
    # Quãng đường cuộn px
    px_vals = sub_scroll['gesture_total_px'].dropna()
    px_mean = px_vals.mean() if len(px_vals) > 0 else 0.0
    px_std = px_vals.std() if len(px_vals) > 1 else 0.0
    px_median = px_vals.median() if len(px_vals) > 0 else 0.0
    px_iqr = (px_vals.quantile(0.75) - px_vals.quantile(0.25)) if len(px_vals) > 0 else 0.0
    
    # Độ trễ giữa các lần cuộn (s)
    lat_vals = sub.loc[scroll_mask, 'latency_s'].dropna()
    lat_mean = lat_vals.mean() if len(lat_vals) > 0 else 0.0
    lat_median = lat_vals.median() if len(lat_vals) > 0 else 0.0
    lat_iqr = (lat_vals.quantile(0.75) - lat_vals.quantile(0.25)) if len(lat_vals) > 0 else 0.0
    
    # Chuỗi cuộn liên tiếp
    sub['is_scroll'] = scroll_mask
    sub['prev_is_scroll'] = sub.groupby('session_id')['is_scroll'].shift(1).fillna(False)
    consec_count = (sub['is_scroll'] & sub['prev_is_scroll']).sum()
    tot_scroll = scroll_mask.sum()
    consec_ratio = (consec_count / tot_scroll * 100) if tot_scroll > 0 else 0.0
    
    c = contracts.get(pid, {})
    nav = c.get('navigation', {}) if isinstance(c, dict) else getattr(c, 'navigation', {})
    cadence = nav.get('scrollCadence', 'N/A')
    
    p = profiles.get(pid, {})
    attrs = p.get('attributes', {}) if isinstance(p, dict) else getattr(p, 'attributes', {})
    pacing_desc = attrs.get('Tác phong / Nhịp điệu tương tác', 'Bình thường')
    energy_desc = attrs.get('Trạng thái năng lượng cuối ngày', 'Bình thường')
    
    scroll_stats.append({
        'persona_id': pid,
        'vai_tro': PERSONA_LABELS[pid].replace('\n', ' '),
        'cadence_contract': cadence,
        'so_buoc_cuon': tot_scroll,
        'px_mean': px_mean,
        'px_std': px_std,
        'px_median': px_median,
        'px_iqr': px_iqr,
        'latency_mean_s': lat_mean,
        'latency_median_s': lat_median,
        'latency_iqr_s': lat_iqr,
        'chuoi_cuon_lien_tiep': consec_count,
        'ty_le_cuon_lien_tiep_pct': consec_ratio,
        'nhan_xet_tac_phong': f"Cadence {cadence}. Vuốt {px_mean:.0f}px, trễ median {lat_median:.1f}s, chuỗi liên tiếp {consec_ratio:.1f}%."
    })

df_scroll = pd.DataFrame(scroll_stats)

# ==============================================================================
# VẼ BIỂU ĐỒ SLIDE 2.4
# ==============================================================================
print("2. Tạo Biểu đồ Slide 2.4: Scroll Dynamics...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 9.2), dpi=300, gridspec_kw={'width_ratios': [1.1, 1], 'wspace': 0.28})

# --- PANEL A: QUÃNG ĐƯỜNG CUỘN TRUNG BÌNH MỖI BƯỚC (PX) & HỢP ĐỒNG CADENCE ---
bars_px = ax1.bar(
    range(len(PERSONA_ORDER)),
    df_scroll['px_mean'],
    yerr=df_scroll['px_std'],
    capsize=5,
    color=[PERSONA_PALETTE[p] for p in PERSONA_ORDER],
    edgecolor='#2c3e50',
    linewidth=1.2,
    alpha=0.85,
    width=0.58,
    error_kw=dict(elinewidth=1.5, ecolor='#2c3e50', capthick=1.5)
)

for i, bar in enumerate(bars_px):
    m = df_scroll.loc[i, 'px_mean']
    s = df_scroll.loc[i, 'px_std']
    med = df_scroll.loc[i, 'px_median']
    cad = df_scroll.loc[i, 'cadence_contract']
    ax1.text(
        bar.get_x() + bar.get_width() / 2.0,
        m + s + 45,
        f"{m:.0f} px\n(Med: {med:.0f})\n[{cad}]",
        ha='center',
        va='bottom',
        fontsize=8.5,
        fontweight='bold',
        color='#1a252f',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffffff', edgecolor='#d0d7de', alpha=0.9, linewidth=0.8)
    )

overall_mean_px = df_actions[df_actions['intent'].isin(['scroll', 'scroll_comments'])]['gesture_total_px'].dropna().mean()
ax1.axhline(overall_mean_px, color='#2980b9', linestyle='--', linewidth=1.8, label=f"Trung bình toàn hệ thống: {overall_mean_px:.0f} px")

# Phân vùng nền theo Cadence
ax1.axvspan(-0.4, 0.4, color='#3498db', alpha=0.10)
ax1.axvspan(3.6, 4.4, color='#9b59b6', alpha=0.10)

ax1.set_title("(A) Quãng Đường Cuộn Trung Bình Mỗi Bước (Pixel) & Nhịp Độ Cadence", fontsize=12.5, fontweight='bold', pad=14)
ax1.set_xlabel("Persona ID (Sắp xếp tăng dần 001 → 006)", fontsize=11.5, fontweight='bold', labelpad=8)
ax1.set_ylabel("Quãng đường cuộn (Pixel / Bước)", fontsize=11.5, fontweight='bold')
ax1.set_xticks(range(len(PERSONA_ORDER)))
ax1.set_xticklabels([PERSONA_LABELS[p] for p in PERSONA_ORDER], fontsize=9.2)
ax1.set_ylim(0, 3100)
ax1.grid(True, axis='y', alpha=0.5)
ax1.legend(loc='upper right', frameon=True, fontsize=9.0, facecolor='#ffffff', edgecolor='#bdc3c7')

# --- PANEL B: ĐỘ TRỄ GIỮA CÁC LẦN CUỘN & TỶ LỆ CHUỖI CUỘN LIÊN TIẾP ---
x = np.arange(len(PERSONA_ORDER))
width = 0.36

rects_lat = ax2.bar(
    x - width/2,
    df_scroll['latency_median_s'],
    width,
    label='Độ trễ trung vị giữa các lần cuộn (Giây)',
    color='#16a085',
    edgecolor='#2c3e50',
    linewidth=1.2,
    alpha=0.88
)

for rect in rects_lat:
    h = rect.get_height()
    ax2.annotate(f'{h:.1f}s',
                xy=(rect.get_x() + rect.get_width() / 2, h),
                xytext=(0, 3), textcoords="offset points",
                ha='center', va='bottom', fontsize=8.8, fontweight='bold', color='#0e6251')

ax2_twin = ax2.twinx()
rects_chain = ax2_twin.plot(
    x,
    df_scroll['ty_le_cuon_lien_tiep_pct'],
    color='#d35400',
    marker='s',
    linewidth=2.2,
    markersize=8,
    label='Tỷ lệ chuỗi cuộn liên tiếp (%)'
)

for i, txt in enumerate(df_scroll['ty_le_cuon_lien_tiep_pct']):
    ax2_twin.annotate(f'{txt:.1f}%', (x[i], txt + 2.5), ha='center', fontsize=8.5, fontweight='bold', color='#a04000')

ax2_twin.set_ylabel('Tỷ lệ Chuỗi Cuộn Liên Tiếp (%)', color='#a04000', fontsize=11, fontweight='bold')
ax2_twin.set_ylim(0, 75)
ax2_twin.grid(False)

ax2.set_title("(B) Nhịp Điệu Thao Tác: Độ Trễ Giữa Các Lần Cuộn & Chuỗi Cuộn Liên Tiếp", fontsize=12.5, fontweight='bold', pad=14)
ax2.set_xlabel("Persona ID (Sắp xếp tăng dần 001 → 006)", fontsize=11.5, fontweight='bold', labelpad=8)
ax2.set_ylabel("Độ trễ trung vị (Giây)", fontsize=11.5, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels([PERSONA_LABELS[p] for p in PERSONA_ORDER], fontsize=9.2)
ax2.set_ylim(0, 18)
ax2.grid(True, axis='y', alpha=0.5)

# Gộp chú thích
lines1, labels1 = ax2.get_legend_handles_labels()
lines2, labels2 = ax2_twin.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True, fontsize=8.8, facecolor='#ffffff', edgecolor='#bdc3c7')

# --- CALLOUT BOX DƯỚI CHÂN HÌNH ---
fig.text(
    0.5, 0.02,
    "★ NHẬN ĐỊNH THỰC NGHIỆM VỀ ĐỘNG LỰC HỌC CUỘN TRANG (H2: PHÙ HỢP VỚI HỒ SƠ & HỢP ĐỒNG CADENCE) ★\n"
    "• Nhóm nhịp độ nhanh ('quick'): vn_fb_001 (Thiết kế, 1,719 px/bước) và vn_fb_005 (Cơ khí, 1,378 px/bước) có quãng đường cuộn dài vượt trội so với mức trung bình hệ thống (1,080 px).\n"
    "• Nhóm nhịp độ điều độ ('balanced'): vn_fb_002 (1,056 px), vn_fb_003 (736 px), vn_fb_006 (704 px) duy trì biên độ vuốt vừa phải và ngắn hơn.\n"
    "• Đặc thù chuỗi cuộn liên tiếp: vn_fb_003 (Bảo vệ) có tỷ lệ cuộn liên tiếp đạt 59.5% (78/131 bước) với độ trễ thấp (8.5s), phản ánh thói quen cuộn liên tục khi tuần tra/trực ca.\n"
    "• Đặc thù độ trễ dài: vn_fb_006 (Gen X) ghi nhận độ trễ trung vị cao nhất (12.1s, mean 20.4s), phản ánh tốc độ đọc chậm rãi, cẩn trọng của người lớn tuổi.",
    ha='center',
    fontsize=9.6,
    fontweight='bold',
    color='#196f3d',
    bbox=dict(boxstyle='round,pad=0.6', facecolor='#eafaf1', edgecolor='#27ae60', linewidth=1.5)
)

plt.tight_layout(rect=[0, 0.10, 1, 0.98])
fig4_path = FIGURES_DIR / "slide2_4_scroll_dynamics.png"
fig.savefig(fig4_path, bbox_inches='tight')
plt.close(fig)
print(f"  -> Đã lưu ảnh: {fig4_path}")

# ==============================================================================
# XUẤT CÁC BẢNG DỮ LIỆU CSV
# ==============================================================================
print("3. Xuất bảng dữ liệu CSV chi tiết...")
csv_scroll_path = TABLES_DIR / "h2_persona_scroll_dynamics_stats.csv"
df_scroll.to_csv(csv_scroll_path, index=False, encoding='utf-8-sig')
print(f"  -> Đã lưu CSV: {csv_scroll_path}")

print("Hoàn tất tạo biểu đồ và dữ liệu Slide 2.4!")
