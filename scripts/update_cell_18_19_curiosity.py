import json

# Read notebook
with open('notebooks/notebook_action_logs.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Update Cell 18 (Code)
cell_18_code = """# ==============================================================================
# BƯỚC 10: CẤP ĐỘ 4 & 5 — ĐỘNG CƠ BẢN SẮC & BỘ NHỚ LÀM VIỆC (DIMENSION & WORKING MEMORY)
# ==============================================================================

# 1. Bảng chéo Bản Sắc Chi Phối (primary_dimension Crosstab)
top_dims = df_actions['primary_dimension'].value_counts().head(10).index
ct_dim = pd.crosstab(df_actions['primary_dimension'], df_actions['persona_id']).loc[top_dims]

print('=== 1. MA TRẬN BẢNG CHÉO BẢN SẮC CHI PHỐI (PRIMARY DIMENSION CROSSTAB) ===')
styled_dim = ct_dim.style\\
    .highlight_max(axis=1, color='#ffe082')\\
    .set_properties(**{'text-align': 'center', 'color': 'black !important'})\\
    .format('{:d}')
display(styled_dim)

# 2. Thu thập thuộc tính Tò mò (Curiosity) từ hồ sơ Persona và liên kết với Working Memory
curiosity_scale = {'Rất thấp': 1, 'Thấp': 2, 'Trung bình': 3, 'Cao': 4, 'Rất cao': 5}
persona_curiosity_map = {}
jsonl_path = '../data/selected_6_facebook_personas_description.jsonl' if Path('../data/selected_6_facebook_personas_description.jsonl').exists() else 'data/selected_6_facebook_personas_description.jsonl'
with open(jsonl_path, 'r', encoding='utf-8') as f:
    for line in f:
        p = json.loads(line)
        pid = p['persona_id']
        c_text = p['attributes'].get('Mức độ muốn khám phá, đặt câu hỏi và tìm hiểu những điều mới.', 'Trung bình')
        persona_curiosity_map[pid] = {
            'curiosity_text': c_text,
            'curiosity_score': curiosity_scale.get(c_text, 3)
        }

# 3. Trích xuất chỉ số Working Memory & Curiosity theo từng Session
wm_records = []
for pid, h in histories.items():
    c_info = persona_curiosity_map.get(pid, {'curiosity_text': 'Trung bình', 'curiosity_score': 3})
    for s in h.sessions:
        wm = s.working_memory
        if wm:
            s_actions = df_actions[df_actions['session_id'] == s.session_id]
            total_act = len(s_actions)
            curiosity_count = len(s_actions[s_actions['primary_dimension'] == 'curiosity'])
            curiosity_ratio = curiosity_count / total_act if total_act > 0 else 0.0
            
            wm_records.append({
                'persona_id': pid,
                'session_id': s.session_id[:8],
                'curiosity_score': c_info['curiosity_score'],
                'curiosity_actions': curiosity_count,
                'curiosity_ratio': curiosity_ratio,
                'situational_steps': wm.novelty.situational_steps if wm.novelty else 0,
                'active_threads': len(wm.active_threads) if wm.active_threads else 0,
                'read_posts': len(wm.read_posts) if wm.read_posts else 0,
                'memory_deltas': len(wm.memory_deltas) if wm.memory_deltas else 0,
                'total_actions': total_act
            })

df_wm = pd.DataFrame(wm_records)

# Bảng thống kê Working Memory theo từng Persona
wm_stats = df_wm.groupby('persona_id').agg({
    'active_threads': 'mean',
    'read_posts': 'mean',
    'situational_steps': 'mean',
    'curiosity_actions': 'mean',
    'memory_deltas': 'mean'
}).round(2).reset_index()

wm_stats.columns = [
    'Persona ID', 'Mạch Chủ Đề Mở (TB)', 'Bài Viết Đã Đọc (TB)', 
    'Bước Sa Đà Tình Huống (TB)', 'Hành Động Tò Mò (TB)', 'Tri Thức Mới Học (TB)'
]

print('\\n=== 2. BẢNG CHỈ SỐ BỘ NHỚ LÀM VIỆC & KIỂM SOÁT SA ĐÀ (WORKING MEMORY) ===')
styled_wm = wm_stats.style\\
    .format({
        'Mạch Chủ Đề Mở (TB)': '{:.2f}',
        'Bài Viết Đã Đọc (TB)': '{:.2f}',
        'Bước Sa Đà Tình Huống (TB)': '{:.2f}',
        'Hành Động Tò Mò (TB)': '{:.2f}',
        'Tri Thức Mới Học (TB)': '{:.2f}'
    })\\
    .background_gradient(subset=['Bài Viết Đã Đọc (TB)'], cmap='Blues')\\
    .background_gradient(subset=['Bước Sa Đà Tình Huống (TB)'], cmap='Reds')\\
    .set_properties(**{'text-align': 'center'})
display(styled_wm)

# 4. Ma trận Tương quan giữa Sa đà nhận thức và Động cơ tò mò (Curiosity Correlation Matrix)
corr_cols = [
    'situational_steps', 'curiosity_actions',  
    'curiosity_score', 'read_posts', 'active_threads'
]
corr_matrix = df_wm[corr_cols].corr()
corr_labels = [
    'Bước Sa Đà', 'Hành Động Tò Mò',
    'Điểm Tò Mò Hồ Sơ', 'Bài Đã Đọc', 'Mạch Chủ Đề'
]
corr_matrix.columns = corr_labels
corr_matrix.index = corr_labels

print('\\n=== 3. MA TRẬN TƯƠNG QUAN SA ĐÀ NHẬN THỨC & TÍNH TÒ MÒ (CORRELATION MATRIX) ===')
styled_corr = corr_matrix.style\\
    .format('{:.3f}')\\
    .background_gradient(cmap='coolwarm', vmin=-1.0, vmax=1.0)\\
    .set_properties(**{'text-align': 'center', 'color': 'black !important'})
display(styled_corr)

# 5. Trực quan hóa Cấp độ 4 & 5 (3 Panels: Bản sắc Chi phối, Ma trận Tương quan, Scatter Plot Động cơ Tò mò vs Bài Đã Đọc)
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(22, 6))

# Panel A: Heatmap Bản Sắc Chi Phối (Primary Dimension)
sns.heatmap(ct_dim, annot=True, fmt='d', cmap='YlGnBu', cbar=True, ax=ax1, linewidths=0.5)
ax1.set_title('(A) Phân Bổ Bản Sắc Chi Phối\\n(Primary Dimension Crosstab)', fontweight='bold', fontsize=12)
ax1.set_xlabel('Persona ID')
ax1.set_ylabel('Chiều Bản Sắc (Dimension)')

# Panel B: Heatmap Ma Trận Tương Quan giữa Sa Đà và Tính Tò Mò
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', vmin=-1.0, vmax=1.0,
            cbar=True, ax=ax2, linewidths=0.5, cbar_kws={'label': 'Hệ số tương quan (r)'})
ax2.set_title('(B) Ma Trận Tương Quan Nhận Thức\\n(Cognitive & Memory Correlation Matrix)', fontweight='bold', fontsize=12)
ax2.set_xticklabels(corr_labels, rotation=45, ha='right', fontsize=9)
ax2.set_yticklabels(corr_labels, rotation=0, fontsize=9)

# Panel C: Scatter Plot Động Cơ Tò Mò vs Số Bài Viết Đã Đọc Sâu (Mỗi điểm là 1 Phiên)
np.random.seed(42)
jitter_x = np.random.uniform(-0.4, 0.4, size=len(df_wm))
jitter_y = np.random.uniform(-0.15, 0.15, size=len(df_wm))

for pid, group in df_wm.groupby('persona_id'):
    p_color = PERSONA_PALETTE.get(pid, '#333333')
    idx = group.index
    ax3.scatter(
        group['curiosity_actions'] + jitter_x[idx], 
        group['read_posts'] + jitter_y[idx],
        color=p_color, label=pid, s=110, alpha=0.85, edgecolors='black', linewidth=0.8, zorder=3
    )

# Đường xu hướng hồi quy tuyến tính (Linear Regression Trendline) giữa curiosity_actions và read_posts
r_val, p_val = stats.pearsonr(df_wm['curiosity_actions'], df_wm['read_posts'])
slope, intercept, _, _, _ = stats.linregress(df_wm['curiosity_actions'], df_wm['read_posts'])
x_vals = np.array([0, df_wm['curiosity_actions'].max()])
ax3.plot(x_vals, intercept + slope * x_vals, color='#2e7d32', linestyle='--', linewidth=2, zorder=2,
         label=f'Hồi quy (r = {r_val:.2f})')

ax3.set_title('(C) Động Cơ Tò Mò vs Số Bài Viết Đã Đọc Sâu\\n(Curiosity Motivation vs Information Depth per Session)', 
              fontweight='bold', fontsize=12)
ax3.set_xlabel('Số Hành Động Tò Mò (curiosity_actions - bước)', fontsize=10)
ax3.set_ylabel('Số Bài Viết Đã Đọc (read_posts - bài)', fontsize=10)
ax3.grid(True, linestyle=':', alpha=0.6)
ax3.legend(frameon=True, fontsize=9, loc='upper left')

plt.tight_layout()
plt.show()"""

# Update Cell 19 (Markdown)
cell_19_content = """---
### Nhận định về Mối Quan tâm Nội dung và Khả năng Điều chỉnh:

#### 1. Bản chất và Mối quan hệ giữa 3 Khái niệm Nhận thức:
Để hiểu rõ cơ chế nhận thức của các nhân vật, chúng ta phân biệt rõ ba khái niệm cốt lõi trong bộ nhớ làm việc:
* **Mạch Chủ đề Mở (`active_threads`):** Là số lượng luồng quan tâm hoặc chủ đề mới mà nhân vật bắt gặp và ghi nhớ tạm thời trong phiên (ví dụ: tin nhà đất Cần Thơ, công cụ AI đồ họa, sự kiện thiên văn).
* **Số Bước Sa đà Tình huống (`situational_steps`):** Là số bước thao tác liên tiếp bị cuốn theo các nội dung ngoài lề phát sinh trên dòng thời gian (không thuộc sở thích cốt lõi), đo lường mức độ phân tâm khỏi mục tiêu ban đầu.
* **Số Bài viết Đã đọc (`read_posts`):** Là số lượng bài viết mà nhân vật thực sự dừng lại đọc kỹ nội dung và theo dõi thảo luận.

---

#### 2. Mối liên hệ thực tế giữa các yếu tố:

##### a. Giữa Mạch Chủ đề Mở và Bước Sa đà Tình huống (Tương quan thuận rõ nét: r = +0.45):
* Khi phiên làm việc chỉ tập trung vào 1–2 chủ đề quen thuộc, nhân vật kiểm soát hướng đi rất tốt, ít bị phân tâm.
* Ngược lại, khi mở ra càng nhiều mạch chủ đề phân nhánh (`active_threads` $\ge 3 - 4$), nhân vật càng tốn thêm nhiều bước bấm xem và khám phá các chủ đề ngoài lề đó $\longrightarrow$ số bước sa đà tình huống (`situational_steps`) tăng lên tương ứng.

##### b. Tại sao Số bài đọc sâu và Bước sa đà KHÔNG CÒN tương quan (r = -0.07):
* **Đọc nhiều bài không đồng nghĩa với sa đà:** `vn_fb_001` (thiết kế đồ họa) và `vn_fb_005` (thợ kỹ thuật) đọc rất nhiều bài viết (trung bình 5.2 – 5.5 bài/phiên), nhưng họ đọc đúng các bài viết chuyên môn và sở thích thật ngoài đời, không bị trôi dạt vào nội dung nhảm.
* **Sa đà cực mạnh nhưng không hề đọc bài:** `vn_fb_004` (nhân viên nhà hàng) có số bước sa đà cao nhất hệ thống (trung bình 65 bước/phiên) vì bị cuốn vào chuỗi video ngắn Reels, nhưng số bài đọc dạng chữ (`read_posts`) chỉ có 1 bài/phiên.
* Do đó, đọc sâu bài viết và sa đà tình huống là hai hành vi độc lập, không tỉ lệ thuận với nhau.

##### c. Động lực thực sự thúc đẩy việc Đọc sâu: Động cơ Tò mò (r = +0.49):
* Biểu đồ Panel C đối sánh **Động cơ Tò mò (`curiosity_actions`)** và **Số bài viết đã đọc (`read_posts`)** cho thấy mối tương quan thuận rõ nét ($r = +0.49$):
  - Nhân vật càng có động cơ tò mò tìm hiểu kiến thức mới thì càng chủ động dừng lại mở bài viết và đọc kỹ nội dung.
  - Nhóm tò mò cao (`vn_fb_001`, `vn_fb_005`) có số hành động tò mò trên 30 bước và đọc từ 5 đến 6 bài mỗi phiên; trong khi nhóm tàu ngầm ít tò mò (`vn_fb_004`) chỉ đọc lướt 1 bài mỗi phiên."""

nb['cells'][18]['source'] = [line + '\n' for line in cell_18_code.split('\n')]
nb['cells'][18]['source'][-1] = nb['cells'][18]['source'][-1].rstrip('\n')

nb['cells'][19]['source'] = [line + '\n' for line in cell_19_content.split('\n')]
nb['cells'][19]['source'][-1] = nb['cells'][19]['source'][-1].rstrip('\n')

with open('notebooks/notebook_action_logs.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Cells 18 and 19 updated successfully!")
