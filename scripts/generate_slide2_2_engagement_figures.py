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

print("1. Nạp dữ liệu actions và contracts...")
from loaders.action_loader import ActionLoader
loader = ActionLoader()
df_actions = loader.to_unified_actions_dataframe()
profiles, contracts = loader.load_persona_profiles_and_contracts()

# Tính toán các chỉ số tương tác theo từng Persona
eng_data = []
react_breakdown = []

for pid in PERSONA_ORDER:
    sub = df_actions[df_actions['persona_id'] == pid]
    interactive_steps = sub[sub['intent'].isin(['read', 'expand', 'open', 'react', 'comment', 'share', 'observe'])]
    unique_posts = interactive_steps['target_id'].dropna().nunique()
    
    reacts = (sub['intent'] == 'react').sum()
    comments = (sub['intent'] == 'comment').sum()
    shares = (sub['intent'] == 'share').sum()
    total_eng = reacts + comments + shares
    total_actions = len(sub)
    
    # Reaction breakdown khi intent == 'react'
    react_sub = sub[sub['intent'] == 'react']
    r_counts = react_sub['reaction'].value_counts()
    
    c = contracts.get(pid, {})
    social = c.get('social', {}) if isinstance(c, dict) else getattr(c, 'social', {})
    
    p = profiles.get(pid, {})
    attrs = p.get('attributes', {}) if isinstance(p, dict) else getattr(p, 'attributes', {})
    style_raw = attrs.get('Cách thường tham gia và tương tác trên các nền tảng trực tuyến.', 'Khác')
    style_clean = style_raw.split('(')[0].strip()
    
    row = {
        'persona_id': pid,
        'vai_tro': PERSONA_LABELS[pid].replace('\n', ' '),
        'phong_cach_xh': style_clean,
        'tong_actions': total_actions,
        'co_hoi_tiep_can_post': unique_posts,
        'so_react': reacts,
        'so_comment': comments,
        'so_share': shares,
        'tong_tuong_tac': total_eng,
        'ty_le_react_post': reacts / unique_posts if unique_posts > 0 else 0.0,
        'ty_le_comment_post': comments / unique_posts if unique_posts > 0 else 0.0,
        'ty_le_share_post': shares / unique_posts if unique_posts > 0 else 0.0,
        'ty_le_aer_actions': total_eng / total_actions,
        'contract_reaction_rate': social.get('reactionRate', np.nan),
        'contract_comment_rate': social.get('commentRate', np.nan),
        'contract_share_rate': social.get('shareRate', np.nan),
    }
    eng_data.append(row)
    
    # Ghi nhận phân loại reaction
    for r_type in ['like', 'love', 'care', 'wow', 'haha', 'sad', 'angry']:
        react_breakdown.append({
            'persona_id': pid,
            'reaction_type': r_type,
            'count': int(r_counts.get(r_type, 0))
        })

df_eng = pd.DataFrame(eng_data)
df_rb = pd.DataFrame(react_breakdown)

# ==============================================================================
# VẼ BIỂU ĐỒ SLIDE 2.2
# ==============================================================================
print("2. Tạo Biểu đồ Slide 2.2: Cường độ & Phong cách Tương tác...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 9.2), dpi=300, gridspec_kw={'width_ratios': [1.1, 1], 'wspace': 0.28})

# --- PANEL A: CƯỜNG ĐỘ TƯƠNG TÁC (TỶ LỆ REACT & COMMENT TRÊN SỐ BÀI TIẾP CẬN) ---
x = np.arange(len(PERSONA_ORDER))
width = 0.36

rects1 = ax1.bar(
    x - width/2,
    df_eng['ty_le_react_post'] * 100,
    width,
    label='Tỷ lệ Thả cảm xúc (React Rate %)',
    color='#3498db',
    edgecolor='#2c3e50',
    linewidth=1.2,
    alpha=0.88
)

rects2 = ax1.bar(
    x + width/2,
    df_eng['ty_le_comment_post'] * 100,
    width,
    label='Tỷ lệ Bình luận (Comment Rate %)',
    color='#2ecc71',
    edgecolor='#2c3e50',
    linewidth=1.2,
    alpha=0.88
)

# Thêm nhãn trên thanh bar
for rect in rects1:
    h = rect.get_height()
    if h > 0:
        ax1.annotate(f'{h:.1f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8.8, fontweight='bold', color='#1b4f72')

for rect in rects2:
    h = rect.get_height()
    if h > 0:
        ax1.annotate(f'{h:.1f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8.8, fontweight='bold', color='#145a32')

# Đường AER (Active Engagement Rate trên tổng actions)
ax1_twin = ax1.twinx()
line_aer = ax1_twin.plot(
    x,
    df_eng['ty_le_aer_actions'] * 100,
    color='#e74c3c',
    marker='o',
    linewidth=2.2,
    markersize=8,
    label='Tỷ lệ Tương tác Chủ động (AER / Actions %)'
)
for i, txt in enumerate(df_eng['ty_le_aer_actions'] * 100):
    ax1_twin.annotate(f'{txt:.1f}%', (x[i], txt + 0.6), ha='center', fontsize=8.5, fontweight='bold', color='#922b21')

ax1_twin.set_ylabel('AER trên Tổng Actions (%)', color='#922b21', fontsize=11, fontweight='bold')
ax1_twin.set_ylim(0, 16)
ax1_twin.grid(False)

ax1.set_title("(A) Tỷ Lệ Tương Tác Trên Bài Viết (React & Comment Rate) & AER", fontsize=12.5, fontweight='bold', pad=14)
ax1.set_xlabel("Persona ID (Sắp xếp tăng dần 001 → 006)", fontsize=11.5, fontweight='bold', labelpad=8)
ax1.set_ylabel("Tỷ lệ tương tác trên bài tiếp cận (%)", fontsize=11.5, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels([PERSONA_LABELS[p] for p in PERSONA_ORDER], fontsize=9.2)
ax1.set_ylim(0, 75)
ax1.grid(True, axis='y', alpha=0.5)

# Gộp chú thích của cả 2 trục
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1_twin.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True, fontsize=8.8, facecolor='#ffffff', edgecolor='#bdc3c7')

# --- PANEL B: CƠ CẤU SẮC THÁI CẢM XÚC & BÌNH LUẬN THEO PERSONA ---
df_rb_pivot = df_rb.pivot(index='persona_id', columns='reaction_type', values='count').reindex(PERSONA_ORDER)
# Bổ sung cột bình luận và chia sẻ để có bức tranh toàn cảnh cơ cấu tương tác
df_rb_pivot['comment'] = df_eng.set_index('persona_id')['so_comment']
df_rb_pivot['share'] = df_eng.set_index('persona_id')['so_share']

# Chuẩn hóa về phần trăm cơ cấu tương tác
df_eng_structure = df_rb_pivot[['like', 'love', 'care', 'wow', 'haha', 'sad', 'angry', 'comment', 'share']]
df_eng_structure_pct = df_eng_structure.div(df_eng_structure.sum(axis=1), axis=0).fillna(0) * 100

colors_structure = {
    'like': '#3498db',      # Xanh like
    'love': '#e84393',      # Hồng love
    'care': '#fdcb6e',      # Vàng cam thương thương
    'wow': '#f39c12',       # Vàng wow
    'haha': '#f1c40f',      # Vàng haha
    'sad': '#74b9ff',       # Xanh lam sad
    'angry': '#d63031',     # Đỏ phẫn nộ
    'comment': '#2ecc71',   # Xanh lá bình luận
    'share': '#9b59b6',     # Tím chia sẻ
}

bottom_b = np.zeros(len(PERSONA_ORDER))
for col in df_eng_structure_pct.columns:
    vals = df_eng_structure_pct[col].values
    if vals.sum() > 0:
        bars_b = ax2.bar(
            range(len(PERSONA_ORDER)),
            vals,
            bottom=bottom_b,
            color=colors_structure[col],
            edgecolor='white',
            linewidth=1.0,
            label=f"{col.capitalize()}",
            width=0.62
        )
        for i, (v, b) in enumerate(zip(vals, bottom_b)):
            if v >= 8.0:
                ax2.text(
                    i,
                    b + v / 2.0,
                    f"{v:.0f}%",
                    ha='center',
                    va='center',
                    color='white',
                    fontweight='bold',
                    fontsize=8.5,
                    bbox=dict(boxstyle='round,pad=0.15', facecolor='black', alpha=0.35, edgecolor='none')
                )
        bottom_b += vals

# Thêm nhãn tổng số tương tác thực tế trên đỉnh cột
for i, pid in enumerate(PERSONA_ORDER):
    tot_i = int(df_eng.loc[df_eng['persona_id'] == pid, 'tong_tuong_tac'].values[0])
    ax2.text(
        i,
        101.5,
        f"n={tot_i}\ntương tác",
        ha='center',
        va='bottom',
        fontsize=9.0,
        fontweight='bold',
        color='#2c3e50'
    )

ax2.set_title("(B) Cơ Cấu Sắc Thái Cảm Xúc, Bình Luận & Chia Sẻ (%)", fontsize=12.5, fontweight='bold', pad=14)
ax2.set_xlabel("Persona ID (Sắp xếp tăng dần 001 → 006)", fontsize=11.5, fontweight='bold', labelpad=8)
ax2.set_ylabel("Tỷ trọng trong tổng hành vi tương tác (%)", fontsize=11.5, fontweight='bold')
ax2.set_xticks(range(len(PERSONA_ORDER)))
ax2.set_xticklabels([PERSONA_LABELS[p] for p in PERSONA_ORDER], fontsize=9.2)
ax2.set_ylim(0, 114)
ax2.grid(True, axis='y', alpha=0.5)
ax2.legend(loc='upper right', bbox_to_anchor=(1.0, 0.98), frameon=True, fontsize=8.5, facecolor='#ffffff', edgecolor='#bdc3c7', ncol=2)

# --- CALLOUT BOX DƯỚI CHÂN HÌNH ---
fig.text(
    0.5, 0.02,
    "★ NHẬN ĐỊNH THỰC NGHIỆM VỀ PHONG CÁCH TƯƠNG TÁC XÃ HỘI (H2: PHÙ HỢP VỚI HỒ SƠ PERSONA) ★\n"
    "• vn_fb_003 (Bảo vệ, 'Chiến thần bình luận dạo'): Tỷ lệ comment đạt mức cao nhất (58.1% trên số bài tiếp cận, 18 bình luận), chú trọng thảo luận trực tiếp hơn thả reaction.\n"
    "• vn_fb_005 (Cơ khí, 'Người thích chia sẻ'): Đạt AER cao nhất (11.8%), kết hợp 12 comment (26.1%) và là persona duy nhất thực hiện hành vi share (shareRate = 2.2%).\n"
    "• vn_fb_002 (Gia đình): Xu hướng tình cảm rõ nét với 6 lượt 'love' và 1 'care' (chiếm 36.8% tổng reaction của persona), phù hợp với vai trò kết nối cộng đồng.\n"
    "• vn_fb_004 & vn_fb_006 ('Tàu ngầm'): Tỷ lệ comment ở mức 0% đến 2.2%, phản ánh tính chất quan sát và tiêu thụ nội dung thụ động.",
    ha='center',
    fontsize=9.6,
    fontweight='bold',
    color='#196f3d',
    bbox=dict(boxstyle='round,pad=0.6', facecolor='#eafaf1', edgecolor='#27ae60', linewidth=1.5)
)

plt.tight_layout(rect=[0, 0.10, 1, 0.98])
fig2_path = FIGURES_DIR / "slide2_2_interaction_intensity_and_style.png"
fig.savefig(fig2_path, bbox_inches='tight')
plt.close(fig)
print(f"  -> Đã lưu ảnh: {fig2_path}")

# ==============================================================================
# XUẤT CÁC BẢNG DỮ LIỆU CSV
# ==============================================================================
print("3. Xuất bảng dữ liệu CSV chi tiết...")
csv_eng_path = TABLES_DIR / "h2_persona_engagement_rates.csv"
df_eng.to_csv(csv_eng_path, index=False, encoding='utf-8-sig')
print(f"  -> Đã lưu CSV 1: {csv_eng_path}")

csv_rb_path = TABLES_DIR / "h2_persona_reaction_breakdown.csv"
df_eng_structure.reset_index().to_csv(csv_rb_path, index=False, encoding='utf-8-sig')
print(f"  -> Đã lưu CSV 2: {csv_rb_path}")

print("Hoàn tất tạo biểu đồ và dữ liệu Slide 2.2!")
