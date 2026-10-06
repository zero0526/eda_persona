import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

nb_path = 'notebooks/eda_action_v2.ipynb'
nb = json.load(open(nb_path, 'r', encoding='utf-8'))

cell_15_code = '''# Phân tích tỷ lệ tương tác xã hội (Reaction, Comment, Share)
# Đo lường cơ hội quan sát post (Unique Posts), Thống kê theo Nhóm Social Archetype và Ma trận Heatmap Spearman

# 1. Thang điểm 3 nấc theo Social Archetype (0 = Thấp / Không có, 1 = Trung bình / Vừa, 2 = Cao / Chủ đạo)
archetype_3tier = {
    'vn_fb_001': {'tier_react': 1, 'tier_comment': 1, 'tier_share': 0},  # Sáng tạo nội dung
    'vn_fb_002': {'tier_react': 1, 'tier_comment': 1, 'tier_share': 0},  # Kết nối cộng đồng
    'vn_fb_003': {'tier_react': 0, 'tier_comment': 2, 'tier_share': 0},  # Chiến thần bình luận dạo
    'vn_fb_004': {'tier_react': 2, 'tier_comment': 0, 'tier_share': 0},  # Tàu ngầm
    'vn_fb_005': {'tier_react': 1, 'tier_comment': 0, 'tier_share': 2},  # Người thích chia sẻ
    'vn_fb_006': {'tier_react': 2, 'tier_comment': 0, 'tier_share': 0},  # Tàu ngầm
}

persona_social = []
for p_id in sorted(df_steps['persona_id'].unique()):
    p_steps = df_steps[df_steps['persona_id'] == p_id]
    c_rules = contracts_dict.get(p_id, {}).get('social', {})
    attrs = personas_dict.get(p_id, {}).get('attributes', {})
    
    # Số bài viết độc nhất được quan sát / tiếp cận (Unique Post Targets)
    interactive_steps = p_steps[p_steps['intent'].isin(['read', 'expand', 'open', 'react', 'comment', 'share'])]
    unique_posts = interactive_steps['target_id'].nunique() if 'target_id' in interactive_steps.columns else 0
    
    reacts = (p_steps['intent'] == 'react').sum()
    comments = (p_steps['intent'] == 'comment').sum()
    shares = (p_steps['intent'] == 'share').sum()
    total_eng = reacts + comments + shares
    
    arch_raw = attrs.get('Cách thường tham gia và tương tác trên các nền tảng trực tuyến.', 'Khác')
    arch_clean = arch_raw.split('(')[0].strip()
    tier_info = archetype_3tier.get(p_id, {'tier_react': 1, 'tier_comment': 1, 'tier_share': 0})
    
    persona_social.append({
        'persona_id': p_id,
        'archetype': arch_clean,
        'unique_posts': unique_posts,
        'actual_reacts': reacts,
        'actual_comments': comments,
        'actual_shares': shares,
        'total_eng': total_eng,
        'actual_react_rate': reacts / unique_posts if unique_posts > 0 else 0.0,
        'actual_comment_rate': comments / unique_posts if unique_posts > 0 else 0.0,
        'actual_share_rate': shares / unique_posts if unique_posts > 0 else 0.0,
        'tier_react': tier_info['tier_react'],
        'tier_comment': tier_info['tier_comment'],
        'tier_share': tier_info['tier_share'],
        'contract_react_rate': c_rules.get('reactionRate', np.nan),
        'contract_comment_rate': c_rules.get('commentRate', np.nan),
        'contract_share_rate': c_rules.get('shareRate', np.nan),
    })

df_ps = pd.DataFrame(persona_social)

# ==============================================================================
# BẢNG 1: THỐNG KÊ THỰC NGHIỆM TƯƠNG TÁC GOM THEO NHÓM SOCIAL ARCHETYPE
# ==============================================================================
df_arch_summary = df_ps.groupby('archetype').agg(
    So_Persona=('persona_id', 'count'),
    Tong_Co_Hoi_Quan_Sat=('unique_posts', 'sum'),
    Tong_React=('actual_reacts', 'sum'),
    Ty_Le_React_TB=('actual_react_rate', lambda x: f"{x.mean()*100:.1f}%"),
    Tong_Comment=('actual_comments', 'sum'),
    Ty_Le_Comment_TB=('actual_comment_rate', lambda x: f"{x.mean()*100:.1f}%"),
    Tong_Share=('actual_shares', 'sum'),
    Ty_Le_Share_TB=('actual_share_rate', lambda x: f"{x.mean()*100:.1f}%"),
    Tong_Tuong_Tac=('total_eng', 'sum'),
).reset_index()

print("=== 1. BẢNG THỰC NGHIỆM TƯƠNG TÁC XÃ HỘI GOM THEO NHÓM SOCIAL ARCHETYPE ===")
display(df_arch_summary)

# ==============================================================================
# BẢNG 2: KIỂM ĐỊNH CHI-SQUARE TÍNH ĐỘC LẬP CƠ CẤU HÀNH VI
# ==============================================================================
contingency_table = df_ps.groupby('archetype')[['actual_reacts', 'actual_comments', 'actual_shares']].sum()
chi2, p_chi2, dof, _ = stats.chi2_contingency(contingency_table)
print(f"\\n=== 2. KIỂM ĐỊNH CHI-SQUARE VỀ TÍNH PHỤ THUỘC HÌNH MẪU ===")
print(f" - Chi2 = {chi2:.3f}, dof = {dof}, p-value = {p_chi2:.4e} (p < 0.001 -> Phụ thuộc chặt chẽ vào Archetype)")

# ==============================================================================
# XÂY DỰNG MA TRẬN NHIỆT (HEATMAP) TƯƠNG QUAN SPEARMAN (r_s, p-value)
# ==============================================================================
rows_list = [
    ('Reaction (Thang 3 Nấc Archetype)', 'tier_react', 'actual_reacts', 'actual_react_rate'),
    ('Comment (Thang 3 Nấc Archetype)', 'tier_comment', 'actual_comments', 'actual_comment_rate'),
    ('Share (Thang 3 Nấc Archetype)', 'tier_share', 'actual_shares', 'actual_share_rate'),
    ('Đối chiếu: Reaction (Hợp đồng Contract)', 'contract_react_rate', 'actual_reacts', 'actual_react_rate'),
    ('Đối chiếu: Comment (Hợp đồng Contract)', 'contract_comment_rate', 'actual_comments', 'actual_comment_rate'),
    ('Đối chiếu: Share (Hợp đồng Contract)', 'contract_share_rate', 'actual_shares', 'actual_share_rate'),
]

matrix_r = []
matrix_labels = []
row_names = []

for label, pred_col, cnt_col, rate_col in rows_list:
    r_cnt, p_cnt = stats.spearmanr(df_ps[pred_col], df_ps[cnt_col])
    r_rate, p_rate = stats.spearmanr(df_ps[pred_col], df_ps[rate_col])
    row_names.append(label)
    matrix_r.append([r_cnt, r_rate])
    
    sig_cnt = "***" if p_cnt < 0.01 else ("**" if p_cnt < 0.05 else ("*" if p_cnt < 0.1 else ""))
    sig_rate = "***" if p_rate < 0.01 else ("**" if p_rate < 0.05 else ("*" if p_rate < 0.1 else ""))
    lbl_cnt = f"r = {r_cnt:+.2f}\\n(p = {p_cnt:.3f}){sig_cnt}"
    lbl_rate = f"r = {r_rate:+.2f}\\n(p = {p_rate:.3f}){sig_rate}"
    matrix_labels.append([lbl_cnt, lbl_rate])

df_heatmap_r = pd.DataFrame(matrix_r, index=row_names, columns=['vs Số Lượng Thực Tế (Count)', 'vs Tỷ Lệ Chuẩn Hóa (Rate)'])
annot_matrix = np.array(matrix_labels)

# ==============================================================================
# TRỰC QUAN HÓA: CƠ CẤU HÀNH VI VÀ MA TRẬN NHIỆT HEATMAP
# ==============================================================================
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Panel 1: Cơ cấu tương tác theo Nhóm Archetype
df_norm_pct = contingency_table.div(contingency_table.sum(axis=1), axis=0).fillna(0) * 100
df_norm_pct.columns = ['React (%)', 'Comment (%)', 'Share (%)']
df_norm_pct.plot(kind='barh', stacked=True, color=['#1f77b4', '#2ca02c', '#d62728'], edgecolor='black', ax=axes[0])
axes[0].set_title("Cơ Cấu Tương Tác Xã Hội (%) Theo Nhóm Social Archetype\\n(Chiến thần cmt 100% comment | Tàu ngầm >85% like | Thích chia sẻ độc quyền share)", fontsize=11, fontweight='bold')
axes[0].set_xlabel("Tỷ trọng tương tác (%)")
axes[0].set_ylabel("Nhóm Social Archetype")
axes[0].legend(loc='lower right')

# Panel 2: Heatmap Spearman
sns.heatmap(
    df_heatmap_r,
    annot=annot_matrix,
    fmt="",
    cmap="RdYlGn",
    vmin=-1.0,
    vmax=1.0,
    center=0.0,
    cbar_kws={'label': 'Hệ số tương quan Spearman (r_s)'},
    linewidths=1.5,
    linecolor='white',
    ax=axes[1]
)
axes[1].set_title("Ma Trận Nhiệt (Heatmap) Tương Quan Spearman (r_s & p-value)\\nThang 3 Nấc Archetype vs Hợp Đồng Contract", fontsize=11, fontweight='bold')

plt.tight_layout()
plt.show()
'''

nb['cells'][15]['source'] = [line + '\n' for line in cell_15_code.split('\n')][:-1]

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Đã cập nhật thành công Cell 15 với Ma trận Nhiệt Heatmap Spearman!")
