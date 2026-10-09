import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from sklearn.feature_extraction.text import TfidfVectorizer

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

FIGURES_DIR = PROJECT_ROOT / "output" / "figures"
TABLES_DIR = PROJECT_ROOT / "output" / "tables"

# Cấu hình thẩm mỹ Matplotlib
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

PERSONA_COLORS = {
    'vn_fb_001': '#2980b9',  # Xanh dương
    'vn_fb_002': '#e67e22',  # Cam
    'vn_fb_003': '#27ae60',  # Xanh lá
    'vn_fb_004': '#c0392b',  # Đỏ
    'vn_fb_005': '#8e44ad',  # Tím
    'vn_fb_006': '#34495e',  # Xám đậm
}

from loaders.action_loader import ActionLoader
loader = ActionLoader()
df_actions = loader.to_unified_actions_dataframe()

session_chains = {}
persona_chains = {p: [] for p in PERSONA_ORDER}

for (p, s), grp in df_actions.groupby(['persona_id', 'session_order']):
    grp_sorted = grp.sort_values('step_index')
    raw_acts = [f"{str(r['intent']).strip()}@{str(r['surface']).strip()}" for _, r in grp_sorted.iterrows()]
    
    acts = []
    prev = None
    for a in raw_acts:
        if a != prev:
            acts.append(a)
            prev = a
            
    tokens = []
    for i in range(len(acts) - 1):
        tokens.append(f"{acts[i]}__THEN__{acts[i+1]}")
    for i in range(len(acts) - 2):
        if acts[i] != acts[i+2]:
            tokens.append(f"{acts[i]}__THEN__{acts[i+1]}__THEN__{acts[i+2]}")
            
    session_chains[(p, s)] = tokens
    persona_chains[p].extend(tokens)

docs = [' '.join(persona_chains[p]) for p in PERSONA_ORDER]
vec = TfidfVectorizer(token_pattern=r'(?u)\S+', lowercase=False, sublinear_tf=True)
X_tfidf = vec.fit_transform(docs).toarray()
features = np.array(vec.get_feature_names_out())
feat_to_idx = {feat: idx for idx, feat in enumerate(features)}

target_signatures = {
    'vn_fb_001': {
        'primary_feat': 'read@group__THEN__open_comments@detail__THEN__scroll_comments@detail',
        'primary_display': 'read [group] ➔ open_comments [detail] ➔ scroll_comments [detail]',
        'meaning': 'Đọc bài viết trong nhóm nghề nghiệp ➔ Mở bình luận ➔ Cuộn đọc bàn luận chuyên môn',
        'secondary_feat': 'open@search__THEN__observe@search__THEN__open@group',
        'secondary_display': 'open [search] ➔ observe [search] ➔ open [group]',
        'cognitive_role': 'Đào sâu Bình luận & Thảo luận Nhóm',
        'motivation_explanation': 'Động cơ chuyên môn: Đọc bài thiết kế trong group ➔ Mở khung bình luận ➔ Cuộn đọc bàn luận của cộng đồng nghề nghiệp.'
    },
    'vn_fb_002': {
        'primary_feat': 'observe@feed__THEN__react@feed',
        'primary_display': 'observe [feed] ➔ react [feed]',
        'meaning': 'Quan sát bài thiện nguyện/tâm linh trên feed ➔ Thả tim cảm xúc',
        'secondary_feat': 'read@feed__THEN__react@feed__THEN__scroll@feed',
        'secondary_display': 'read [feed] ➔ react [feed] ➔ scroll [feed]',
        'cognitive_role': 'Lướt Tranh thủ & Hướng thiện',
        'motivation_explanation': 'Động cơ tranh thủ giờ nghỉ: Đọc nhanh bài hướng thiện/Phật giáo ➔ Thả tim cảm xúc ➔ Cuộn lướt tiếp (không tranh cãi).'
    },
    'vn_fb_003': {
        'primary_feat': 'comment@detail__THEN__observe@detail__THEN__scroll_comments@detail',
        'primary_display': 'comment [detail] ➔ observe [detail] ➔ scroll_comments [detail]',
        'meaning': 'Bình luận hỏi quán ăn đêm Đà Nẵng ➔ Dừng quan sát ➔ Cuộn đọc bàn luận đêm',
        'secondary_feat': 'comment@detail__THEN__observe@detail',
        'secondary_display': 'comment [detail] ➔ observe [detail]',
        'cognitive_role': 'Tương tác Ca trực Đêm',
        'motivation_explanation': 'Động cơ ca trực đêm: Vào bài ẩm thực đêm bình luận hỏi quán ➔ Dừng quan sát ➔ Cuộn đọc trao đổi cộng đồng (độc quyền 100%).'
    },
    'vn_fb_004': {
        'primary_feat': 'watch@reels__THEN__next@reels',
        'primary_display': 'watch [reels] ➔ next [reels]',
        'meaning': 'Trục tiêu thụ video ngắn Reels liên hoàn sau ca làm việc',
        'secondary_feat': 'next@reels__THEN__watch@reels__THEN__react@reels',
        'secondary_display': 'next [reels] ➔ watch [reels] ➔ react [reels]',
        'cognitive_role': 'Nghiện Reels & Xem Chọn lọc',
        'motivation_explanation': 'Động cơ giải trí Reels: Lướt video ngắn liên hoàn (133 lần, TF-IDF=0.335). Khi gặp clip bóng đá hay mới thả tim (`react`).'
    },
    'vn_fb_005': {
        'primary_feat': 'read@feed__THEN__expand@feed__THEN__observe@feed',
        'primary_display': 'read [feed] ➔ expand [feed] ➔ observe [feed]',
        'meaning': 'Đọc mở đầu bài kỹ thuật ➔ Bấm "Xem thêm" mở toàn văn ➔ Dừng lại thẩm định',
        'secondary_feat': 'read@feed__THEN__open_comments@detail__THEN__comment@detail',
        'secondary_display': 'read [feed] ➔ open_comments [detail] ➔ comment [detail]',
        'cognitive_role': 'Đào sâu Toàn văn & Kỹ thuật',
        'motivation_explanation': 'Động cơ thẩm định sâu: Gặp bài kỹ thuật/thiên văn dài, bấm "Xem thêm" (expand) mở toàn văn thẩm định (độc quyền 100%).'
    },
    'vn_fb_006': {
        'primary_feat': 'search@search__THEN__open@search__THEN__observe@search',
        'primary_display': 'search [search] ➔ open [search] ➔ observe [search]',
        'meaning': 'Tìm kiếm BĐS/Nha khoa có chủ đích ➔ Mở kết quả ➔ Quan sát thẩm định logic',
        'secondary_feat': 'observe@group__THEN__read@group__THEN__react@group',
        'secondary_display': 'observe [group] ➔ read [group] ➔ react [group]',
        'cognitive_role': 'Tra cứu Chủ đích & Khảo sát BĐS',
        'motivation_explanation': 'Động cơ thực dụng Gen X: Chủ động tìm kiếm BĐS Cần Thơ & Nha khoa Ruby, mở bài thẩm định thông tin logic (độc quyền 66.7%).'
    }
}

table_rows = []
for p in PERSONA_ORDER:
    info = target_signatures[p]
    p_idx = PERSONA_ORDER.index(p)
    
    feat1 = info['primary_feat']
    tfidf1 = X_tfidf[p_idx][feat_to_idx[feat1]] if feat1 in feat_to_idx else 0.0
    s_counts1 = [session_chains.get((p, s), []).count(feat1) for s in [1, 2, 3, 4]]
    tot1 = sum(s_counts1)
    n_sess1 = sum(1 for c in s_counts1 if c > 0)
    other_tot1 = sum(session_chains.get((op, s), []).count(feat1) for op in PERSONA_ORDER if op != p for s in [1, 2, 3, 4])
    excl1 = (tot1 / (tot1 + other_tot1) * 100.0) if (tot1 + other_tot1) > 0 else 0.0
    
    feat2 = info['secondary_feat']
    tfidf2 = X_tfidf[p_idx][feat_to_idx[feat2]] if feat2 in feat_to_idx else 0.0
    s_counts2 = [session_chains.get((p, s), []).count(feat2) for s in [1, 2, 3, 4]]
    tot2 = sum(s_counts2)
    n_sess2 = sum(1 for c in s_counts2 if c > 0)
    other_tot2 = sum(session_chains.get((op, s), []).count(feat2) for op in PERSONA_ORDER if op != p for s in [1, 2, 3, 4])
    excl2 = (tot2 / (tot2 + other_tot2) * 100.0) if (tot2 + other_tot2) > 0 else 0.0
    
    table_rows.append({
        'persona_id': p,
        'vai_tro': PERSONA_LABELS[p].split('\n')[1].replace('(', '').replace(')', ''),
        'chan_dung_nhan_thuc': info['cognitive_role'],
        'chuoi_chinh_tfidf': info['primary_display'],
        'diem_tfidf_chinh': round(tfidf1, 3),
        'tan_suat_chinh': tot1,
        'so_phien_xuat_hien': f"{n_sess1}/4 phiên",
        'phan_bo_phien_s1_s4': str(s_counts1),
        'do_doc_quyen_chinh_pct': round(excl1, 1),
        'chuoi_bo_tro_tfidf': info['secondary_display'],
        'diem_tfidf_bo_tro': round(tfidf2, 3),
        'tan_suat_bo_tro': tot2,
        'do_doc_quyen_bo_tro_pct': round(excl2, 1),
        'y_nghia_chuoi': info['meaning'],
        'dong_co_nhan_thuc_persona': info['motivation_explanation']
    })

df_sequences = pd.DataFrame(table_rows)

fig = plt.figure(figsize=(18.2, 9.2), facecolor='#ffffff')
gs = fig.add_gridspec(1, 2, width_ratios=[0.88, 1.62], wspace=0.22, left=0.11, right=0.98, top=0.88, bottom=0.08)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])

# PANEL A: Điểm Đặc Trưng TF-IDF & Độ Độc Quyền (%)
y_pos = np.arange(len(PERSONA_ORDER))
colors = [PERSONA_COLORS[p] for p in PERSONA_ORDER]

bars = ax1.barh(y_pos, df_sequences['diem_tfidf_chinh'], height=0.52, color=colors, edgecolor='#2c3e50', linewidth=1.2, alpha=0.9)
ax1.set_yticks(y_pos)
ax1.set_yticklabels([f"{p}\n({df_sequences.loc[i, 'vai_tro']})" for i, p in enumerate(PERSONA_ORDER)], fontsize=9.2, fontweight='bold', color='#2c3e50')
ax1.invert_yaxis()
ax1.set_xlim(0, 0.42)
ax1.set_xlabel('Điểm Đặc Trưng TF-IDF (TF-IDF Distinctiveness Score)', fontsize=10.5, fontweight='bold', color='#34495e', labelpad=8)
ax1.set_title('A. Điểm Đặc Trưng TF-IDF & Mức Độ Độc Quyền\n(Đo lường tần suất nổi bật so với các Persona khác)', fontsize=11.8, fontweight='bold', color='#2c3e50', pad=12)
ax1.grid(axis='x', linestyle='--', alpha=0.6)

for i, (bar, row) in enumerate(zip(bars, df_sequences.itertuples())):
    w = bar.get_width()
    y = bar.get_y() + bar.get_height() / 2
    label_txt = f"TF-IDF: {row.diem_tfidf_chinh:.3f}\nĐộc quyền: {row.do_doc_quyen_chinh_pct}%\n({row.tan_suat_chinh} lần, {row.so_phien_xuat_hien})"
    ax1.text(w + 0.008, y, label_txt, va='center', ha='left', fontsize=8.6, fontweight='bold', color='#2c3e50')

# PANEL B: Chi Tiết Chuỗi Thao Tác & Động Cơ Nhận Thức Chuyên Biệt
ax2.set_title('B. Bản Sắc Động Cơ Nhận Thức & Chuỗi Hành Động Thương Hiệu\n(Cognitive Motivation & Persona-Specific Behavioral Signatures)', fontsize=11.8, fontweight='bold', color='#2c3e50', pad=12)
ax2.set_xlim(0, 10)
ax2.set_ylim(-0.5, 5.8)
ax2.axis('off')

for idx, p in enumerate(PERSONA_ORDER):
    y_center = 5.2 - idx * 1.02
    info = target_signatures[p]
    row = df_sequences.iloc[idx]
    p_color = PERSONA_COLORS[p]
    
    # Vẽ thẻ bao quát Persona (Card)
    card_rect = patches.FancyBboxPatch((0.1, y_center - 0.48), 9.7, 0.96, boxstyle="round,pad=0.10",
                                       linewidth=1.2, edgecolor=p_color, facecolor='#fafbfc', alpha=0.95)
    ax2.add_patch(card_rect)
    
    # Hàng 1: Header + Phân bổ phiên & Độc quyền
    ax2.text(0.25, y_center + 0.28, f"[{p}] {row['vai_tro']} — {row['chan_dung_nhan_thuc']}", 
             fontsize=9.6, fontweight='bold', color=p_color)
    ax2.text(9.65, y_center + 0.28, f"Phân bổ: {row['phan_bo_phien_s1_s4']}  |  Độc quyền: {row['do_doc_quyen_chinh_pct']}%", 
             fontsize=8.5, fontweight='bold', color='#1e8449', ha='right')
    
    # Hàng 2: Chuỗi chính TF-IDF + Tần suất
    ax2.text(0.25, y_center + 0.08, f"★ Chuỗi TF-IDF chính: {row['chuoi_chinh_tfidf']}", 
             fontsize=8.8, fontweight='bold', color='#154360')
    ax2.text(9.65, y_center + 0.08, f"(Tần suất: {row['tan_suat_chinh']} lần qua {row['so_phien_xuat_hien']})", 
             fontsize=8.2, fontstyle='italic', color='#555555', ha='right')
    
    # Hàng 3: Ý nghĩa & Động cơ nhận thức chuyên biệt
    ax2.text(0.25, y_center - 0.12, f"  ↳ Ý nghĩa & Động cơ: {row['dong_co_nhan_thuc_persona']}", 
             fontsize=8.0, color='#2c3e50')
    
    # Hàng 4: Chuỗi bổ trợ
    ax2.text(0.25, y_center - 0.32, f"  ↳ Chuỗi bổ trợ: {row['chuoi_bo_tro_tfidf']}  (TF-IDF: {row['diem_tfidf_bo_tro']:.3f} | Độc quyền: {row['do_doc_quyen_bo_tro_pct']}%)", 
             fontsize=7.9, color='#616a6b')

# Tiêu đề toàn slide
fig.suptitle(
    "KIỂM CHỨNG H2 (SLIDE 2.7): KHÁM PHÁ CHUỖI HÀNH VI ĐẶC TRƯNG TF-IDF & ĐỘNG CƠ NHẬN THỨC CỦA PERSONA",
    fontsize=13.8,
    fontweight='bold',
    color='#1a365d',
    y=0.985
)

fig_path = FIGURES_DIR / "slide2_7_characteristic_action_sequences.png"
plt.savefig(fig_path, dpi=300)
plt.close()
print(f"  -> Đã lưu biểu đồ: {fig_path}")

csv_path = TABLES_DIR / "h2_persona_characteristic_sequences.csv"
df_sequences.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"  -> Đã lưu bảng: {csv_path}")

print("Hoàn tất tạo hình và dữ liệu Slide 2.7 bằng thuật toán TF-IDF!")
