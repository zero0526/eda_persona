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

print("1. Nạp dữ liệu actions và sessions từ ActionLoader...")
from loaders.action_loader import ActionLoader
loader = ActionLoader()
df_actions = loader.to_unified_actions_dataframe()
df_sessions = loader.to_unified_sessions_dataframe()
profiles, contracts = loader.load_persona_profiles_and_contracts()

reading_data = []

for pid in PERSONA_ORDER:
    sub_act = df_actions[df_actions['persona_id'] == pid]
    sub_sess = df_sessions[df_sessions['persona_id'] == pid]
    
    # Số bước Scanning: scroll feed, observe DOM, next video
    scan_steps = sub_act[sub_act['intent'].isin(['scroll', 'observe', 'next'])].shape[0]
    
    # Số bước Deep Reading: read post, expand text, scroll comments
    deep_steps = sub_act[sub_act['intent'].isin(['read', 'expand', 'scroll_comments'])].shape[0]
    
    tot_eval = scan_steps + deep_steps
    scan_pct = (scan_steps / tot_eval * 100) if tot_eval > 0 else 0.0
    deep_pct = (deep_steps / tot_eval * 100) if tot_eval > 0 else 0.0
    
    # Dwell time trên các bước đọc sâu (gesture_ms hoặc model_latency_ms)
    read_steps = sub_act[sub_act['intent'] == 'read']
    mean_dwell_gesture_s = (read_steps['gesture_ms'].dropna().mean() / 1000.0) if len(read_steps) > 0 else 0.0
    
    # Số bài đọc sâu tích lũy mỗi phiên trong working memory
    mean_session_reads = sub_sess['session_read_posts_count'].mean()
    std_session_reads = sub_sess['session_read_posts_count'].std() if len(sub_sess) > 1 else 0.0
    total_session_reads = int(sub_sess['session_read_posts_count'].sum())
    
    c = contracts.get(pid, {})
    nav = c.get('navigation', {}) if isinstance(c, dict) else getattr(c, 'navigation', {})
    contract_scan_ratio = nav.get('scanRatio', np.nan)
    
    reading_data.append({
        'persona_id': pid,
        'vai_tro': PERSONA_LABELS[pid].replace('\n', ' '),
        'scan_steps': scan_steps,
        'deep_steps': deep_steps,
        'total_eval_steps': tot_eval,
        'scan_pct': scan_pct,
        'deep_pct': deep_pct,
        'contract_scan_ratio': contract_scan_ratio,
        'mean_session_reads': mean_session_reads,
        'std_session_reads': std_session_reads,
        'total_session_reads': total_session_reads,
        'mean_dwell_gesture_s': mean_dwell_gesture_s,
    })

df_read = pd.DataFrame(reading_data)

# ==============================================================================
# VẼ BIỂU ĐỒ SLIDE 2.3
# ==============================================================================
print("2. Tạo Biểu đồ Slide 2.3: Scanning vs Deep Reading...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 9.2), dpi=300, gridspec_kw={'width_ratios': [1.1, 1], 'wspace': 0.28})

# --- PANEL A: 100% STACKED BAR CHART SCANNING VS DEEP READING ---
bars_scan = ax1.bar(
    range(len(PERSONA_ORDER)),
    df_read['scan_pct'],
    label='Lướt Qua / Quét nhanh (Scanning %)',
    color='#3498db',
    edgecolor='white',
    linewidth=1.2,
    width=0.58
)

bars_deep = ax1.bar(
    range(len(PERSONA_ORDER)),
    df_read['deep_pct'],
    bottom=df_read['scan_pct'],
    label='Đọc Sâu / Tìm hiểu kỹ (Deep Reading %)',
    color='#e67e22',
    edgecolor='white',
    linewidth=1.2,
    width=0.58
)

for i in range(len(PERSONA_ORDER)):
    s_val = df_read.loc[i, 'scan_pct']
    d_val = df_read.loc[i, 'deep_pct']
    # Nhãn scanning
    ax1.text(
        i, s_val / 2.0, f"{s_val:.1f}%\n({df_read.loc[i, 'scan_steps']} bước)",
        ha='center', va='center', color='white', fontweight='bold', fontsize=8.5,
        bbox=dict(boxstyle='round,pad=0.15', facecolor='black', alpha=0.35, edgecolor='none')
    )
    # Nhãn deep reading
    if d_val >= 6.0:
        ax1.text(
            i, s_val + d_val / 2.0, f"{d_val:.1f}%\n({df_read.loc[i, 'deep_steps']} bước)",
            ha='center', va='center', color='white', fontweight='bold', fontsize=8.5,
            bbox=dict(boxstyle='round,pad=0.15', facecolor='black', alpha=0.35, edgecolor='none')
        )

# Đường hợp đồng scanRatio (45%)
ax1.axhline(45.0, color='#e74c3c', linestyle='--', linewidth=1.8, label='Ngưỡng hợp đồng: scanRatio = 45%')

ax1.set_title("(A) Phân Bổ Tỷ Lệ Lướt Qua (Scanning) vs Đọc Sâu (Deep Reading)", fontsize=12.5, fontweight='bold', pad=14)
ax1.set_xlabel("Persona ID (Sắp xếp tăng dần 001 → 006)", fontsize=11.5, fontweight='bold', labelpad=8)
ax1.set_ylabel("Tỷ lệ phân bổ (%)", fontsize=11.5, fontweight='bold')
ax1.set_xticks(range(len(PERSONA_ORDER)))
ax1.set_xticklabels([PERSONA_LABELS[p] for p in PERSONA_ORDER], fontsize=9.2)
ax1.set_ylim(0, 115)
ax1.grid(True, axis='y', alpha=0.5)
ax1.legend(loc='upper right', bbox_to_anchor=(1.0, 0.98), frameon=True, fontsize=8.8, facecolor='#ffffff', edgecolor='#bdc3c7')

# --- PANEL B: SỐ BÀI ĐỌC SÂU TÍCH LŨY TRUNG BÌNH MỖI PHIÊN (WORKING MEMORY) ---
bars_sess = ax2.bar(
    range(len(PERSONA_ORDER)),
    df_read['mean_session_reads'],
    yerr=df_read['std_session_reads'],
    capsize=5,
    color='#16a085',
    edgecolor='#2c3e50',
    linewidth=1.2,
    alpha=0.88,
    width=0.58,
    error_kw=dict(elinewidth=1.5, ecolor='#2c3e50', capthick=1.5)
)

for i, bar in enumerate(bars_sess):
    mr = df_read.loc[i, 'mean_session_reads']
    sr = df_read.loc[i, 'std_session_reads']
    tot_r = df_read.loc[i, 'total_session_reads']
    ax2.text(
        bar.get_x() + bar.get_width() / 2.0,
        mr + sr + 0.25,
        f"{mr:.1f} bài/phiên\n(Tổng {tot_r} bài)",
        ha='center',
        va='bottom',
        fontsize=8.8,
        fontweight='bold',
        color='#1a252f',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffffff', edgecolor='#d0d7de', alpha=0.9, linewidth=0.8)
    )

overall_mean_reads = df_sessions['session_read_posts_count'].mean()
ax2.axhline(overall_mean_reads, color='#2980b9', linestyle='--', linewidth=1.8, label=f"Trung bình toàn hệ thống: {overall_mean_reads:.1f} bài/phiên")

ax2.set_title("(B) Số Lượng Bài Đọc Sâu Tích Lũy Trung Bình Mỗi Phiên (Working Memory)", fontsize=12.5, fontweight='bold', pad=14)
ax2.set_xlabel("Persona ID (Sắp xếp tăng dần 001 → 006)", fontsize=11.5, fontweight='bold', labelpad=8)
ax2.set_ylabel("Số bài đọc tích lũy / phiên", fontsize=11.5, fontweight='bold')
ax2.set_xticks(range(len(PERSONA_ORDER)))
ax2.set_xticklabels([PERSONA_LABELS[p] for p in PERSONA_ORDER], fontsize=9.2)
ax2.set_ylim(0, 8.5)
ax2.grid(True, axis='y', alpha=0.5)
ax2.legend(loc='upper right', frameon=True, fontsize=9.0, facecolor='#ffffff', edgecolor='#bdc3c7')

# --- CALLOUT BOX DƯỚI CHÂN HÌNH ---
# fig.text(
#     0.5, 0.02,
#     "★ NHẬN ĐỊNH THỰC NGHIỆM VỀ MỨC ĐỘ ĐỌC SÂU & TIÊU THỤ THÔNG TIN (H2: PHÙ HỢP VỚI HỒ SƠ PERSONA) ★\n"
#     "• vn_fb_005 (Cơ khí): Tỷ lệ đọc sâu cao nhất (47.0%, 62 bước), tích lũy trung bình 5.2 bài/phiên, tập trung đọc bài kỹ thuật và bình luận chuyên môn.\n"
#     "• vn_fb_001 (Thiết kế) & vn_fb_006 (Gen X): Đọc sâu ở mức 34.5% - 36.8%, tích lũy 4.7 - 5.5 bài/phiên, phù hợp với thói quen thẩm định và tìm hiểu kỹ nội dung.\n"
#     "• vn_fb_004 (Nhà hàng): Tỷ lệ lướt nhanh áp đảo (93.5%), chỉ có 6.5% đọc sâu (1.0 bài/phiên), phản ánh nhịp độ cuộn chuyển nhanh đặc trưng của video ngắn.\n"
#     "• vn_fb_003 (Bảo vệ): Lướt chiếm 76.2% trong ca trực, nhưng kết hợp đọc sâu 23.8% khi gặp bài viết hoặc phần bình luận đáng chú ý.",
#     ha='center',
#     fontsize=9.6,
#     fontweight='bold',
#     color='#196f3d',
#     bbox=dict(boxstyle='round,pad=0.6', facecolor='#eafaf1', edgecolor='#27ae60', linewidth=1.5)
# )

plt.tight_layout(rect=[0, 0.10, 1, 0.98])
fig3_path = FIGURES_DIR / "slide2_3_scanning_vs_deep_reading.png"
fig.savefig(fig3_path, bbox_inches='tight')
plt.close(fig)
print(f"  -> Đã lưu ảnh: {fig3_path}")

# ==============================================================================
# XUẤT CÁC BẢNG DỮ LIỆU CSV
# ==============================================================================
print("3. Xuất bảng dữ liệu CSV chi tiết...")
csv_read_path = TABLES_DIR / "h2_persona_reading_depth_stats.csv"
df_read.to_csv(csv_read_path, index=False, encoding='utf-8-sig')
print(f"  -> Đã lưu CSV 1: {csv_read_path}")

# Bảng phiên đọc tích lũy
df_sess_summary = df_sessions[['session_id', 'persona_id', 'session_read_posts_count', 'total_actions', 'duration_seconds']].copy()
df_sess_summary['vai_tro'] = df_sess_summary['persona_id'].map(lambda p: PERSONA_LABELS[p].replace('\n', ' '))
csv_sess_path = TABLES_DIR / "h2_session_reading_accumulation.csv"
df_sess_summary.to_csv(csv_sess_path, index=False, encoding='utf-8-sig')
print(f"  -> Đã lưu CSV 2: {csv_sess_path}")

print("Hoàn tất tạo biểu đồ và dữ liệu Slide 2.3!")
