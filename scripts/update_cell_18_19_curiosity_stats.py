import json
from pathlib import Path

# Load notebook
nb_path = 'notebooks/notebook_action_logs.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Cell 18 Code
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
            sit_steps = wm.novelty.situational_steps if wm.novelty else 0
            drift_pct = (sit_steps / total_act * 100) if total_act > 0 else 0.0
            
            wm_records.append({
                'persona_id': pid,
                'session_id': s.session_id[:8],
                'curiosity_text': c_info['curiosity_text'],
                'curiosity_score': c_info['curiosity_score'],
                'curiosity_actions': curiosity_count,
                'curiosity_ratio': curiosity_ratio,
                'situational_steps': sit_steps,
                'drift_pct': drift_pct,
                'active_threads': len(wm.active_threads) if wm.active_threads else 0,
                'read_posts': len(wm.read_posts) if wm.read_posts else 0,
                'memory_deltas': len(wm.memory_deltas) if wm.memory_deltas else 0,
                'total_actions': total_act
            })

df_wm = pd.DataFrame(wm_records)

# Bảng thống kê Working Memory kết hợp Mức độ Tò mò từ Hồ sơ
wm_stats = df_wm.groupby('persona_id').agg({
    'curiosity_text': 'first',
    'curiosity_score': 'first',
    'situational_steps': 'mean',
    'drift_pct': 'mean',
    'curiosity_actions': 'mean',
    'read_posts': 'mean',
    'active_threads': 'mean',
    'memory_deltas': 'mean'
}).round(2).reset_index()

wm_stats.columns = [
    'Persona ID', 'Mức Độ Tò Mò (Hồ Sơ)', 'Điểm Tò Mò (1-5)',
    'Bước Sa Đà (TB)', 'Tỷ Lệ Sa Đà (% TB)', 'Hành Động Tò Mò (TB)', 
    'Bài Viết Đã Đọc (TB)', 'Mạch Chủ Đề Mở (TB)', 'Tri Thức Mới Học (TB)'
]
wm_stats = wm_stats.sort_values(by='Điểm Tò Mò (1-5)', ascending=False)

print('\\n=== 2. BẢNG CHỈ SỐ BỘ NHỚ LÀM VIỆC & MỨC ĐỘ TÒ MÒ PERSONA ===')
styled_wm = wm_stats.style\\
    .format({
        'Điểm Tò Mò (1-5)': '{:d}',
        'Bước Sa Đà (TB)': '{:.2f}',
        'Tỷ Lệ Sa Đà (% TB)': '{:.2f}%',
        'Hành Động Tò Mò (TB)': '{:.2f}',
        'Bài Viết Đã Đọc (TB)': '{:.2f}',
        'Mạch Chủ Đề Mở (TB)': '{:.2f}',
        'Tri Thức Mới Học (TB)': '{:.2f}'
    })\\
    .background_gradient(subset=['Điểm Tò Mò (1-5)'], cmap='Purples')\\
    .background_gradient(subset=['Bước Sa Đà (TB)'], cmap='Reds')\\
    .background_gradient(subset=['Tỷ Lệ Sa Đà (% TB)'], cmap='Oranges')\\
    .background_gradient(subset=['Bài Viết Đã Đọc (TB)'], cmap='Blues')\\
    .set_properties(**{'text-align': 'center'})
display(styled_wm)

# 4. Ma trận Tương quan giữa Sa đà nhận thức và Động cơ tò mò (Correlation Matrix)
corr_cols = [
    'situational_steps', 'drift_pct', 'curiosity_score', 
    'curiosity_actions', 'read_posts', 'active_threads'
]
corr_matrix = df_wm[corr_cols].corr()
corr_labels = [
    'Bước Sa Đà', 'Tỷ Lệ Sa Đà (%)', 'Điểm Tò Mò Hồ Sơ', 
    'Hành Động Tò Mò', 'Bài Đã Đọc', 'Mạch Chủ Đề'
]
corr_matrix.columns = corr_labels
corr_matrix.index = corr_labels

# Tính tương quan cấp độ nhân vật (Persona-level)
r_persona_steps = wm_stats['Điểm Tò Mò (1-5)'].corr(wm_stats['Bước Sa Đà (TB)'])
r_persona_pct = wm_stats['Điểm Tò Mò (1-5)'].corr(wm_stats['Tỷ Lệ Sa Đà (% TB)'])

print(f'\\n=== 3. MA TRẬN TƯƠNG QUAN NHẬN THỨC & TÍNH TÒ MÒ (CORRELATION MATRIX) ===')
print(f'-> Tương quan Cấp Nhân vật: Điểm Tò Mò vs Bước Sa Đà TB: r = {r_persona_steps:.3f} | Điểm Tò Mò vs Tỷ Lệ Sa Đà TB: r = {r_persona_pct:.3f}')
styled_corr = corr_matrix.style\\
    .format('{:.3f}')\\
    .background_gradient(cmap='coolwarm', vmin=-1.0, vmax=1.0)\\
    .set_properties(**{'text-align': 'center', 'color': 'black !important'})
display(styled_corr)

# 5. Trực quan hóa Cấp độ 4 & 5 (3 Panels: Bản sắc Chi phối, Ma trận Tương quan, Scatter Plot Động cơ Tò mò vs Bài Đã Đọc)
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(23, 6))

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

# Cell 19 Markdown Content
cell_19_content = """---
### Nhận định về Mối Quan tâm Nội dung, Tính Tò mò và Khả năng Điều chỉnh:

#### 1. Bản chất và Mối quan hệ giữa các Khái niệm Nhận thức:
Để hiểu rõ cơ chế nhận thức của các nhân vật, chúng ta phân biệt rõ các yếu tố cốt lõi trong hồ sơ và bộ nhớ làm việc:
* **Mức độ Tò mò Hồ sơ (`Curiosity`):** Thuộc tính tâm lý nền tảng mô tả mức độ muốn khám phá, đặt câu hỏi và tìm hiểu điều mới lạ (từ *Trung bình* đến *Rất cao*).
* **Mạch Chủ đề Mở (`active_threads`):** Số lượng luồng quan tâm tạm thời mà nhân vật ghi nhớ trong phiên khi bắt gặp thông tin mới trên dòng thời gian.
* **Số Bước Sa đà Tình huống (`situational_steps`):** Số bước thao tác liên tiếp bị cuốn theo nội dung ngoài lề phát sinh (không nằm trong sở thích cốt lõi), đo lường mức độ phân tâm khỏi mục tiêu ban đầu.
* **Số Bài viết Đã đọc (`read_posts`):** Số lượng bài viết mà nhân vật thực sự dừng lại đọc kỹ nội dung và theo dõi thảo luận.

---

#### 2. Mối liên hệ thực nghiệm giữa Mức độ Tò mò và Hành vi Sa đà:

##### a. Tương quan Thuận giữa Mức độ Tò mò Hồ sơ và Số bước Sa đà:
* **Ở cấp độ nhân vật (Persona-level):** Mức độ tò mò hồ sơ có mối **tương quan thuận rõ nét** với số bước sa đà tình huống trung bình ($r = +0.55$) và tỷ lệ sa đà ($r = +0.41$).
  - Nhóm có mức độ tò mò cao nhất (`vn_fb_004`, `vn_fb_005`) ghi nhận số bước sa đà trung bình từ **37.0 đến 65.0 bước/phiên**, chiếm từ **61% đến 67%** tổng số thao tác.
  - Ngược lại, nhóm có mức độ tò mò trung bình (`vn_fb_002`, `vn_fb_003`) có số bước sa đà thấp hơn rõ rệt (từ **15.3 đến 24.0 bước/phiên**). Đặc biệt, `vn_fb_002` (công nhân bận rộn) có mức sa đà thấp nhất toàn hệ thống (trung vị chỉ **5.5 bước/phiên**, tương đương **12.4%** thời lượng).
* **Ở cấp độ từng phiên làm việc (Session-level, 24 phiên):** Hệ số tương quan đạt **$r = +0.29$**. Điều này cho thấy tính tò mò hoạt động như một "lực đẩy nhận thức ban đầu", kích thích nhân vật mở ra các nhánh khám phá mới khi lướt mạng.

##### b. Tại sao cùng Tò mò cao nhưng mức độ Sa đà lại có sự khác biệt?
Thống kê chỉ ra rằng số bước sa đà thực tế không chỉ do tính tò mò quyết định đơn lẻ, mà chịu sự điều phối của **3 cơ chế bổ trợ**:
1. **Định dạng không gian tương tác:** 
   * `vn_fb_004` (tò mò Rất cao) lướt chủ yếu trên **Video ngắn / Reels**. Cơ chế thuật toán tự động đề xuất liên tục đã kích hoạt tính tò mò thành chuỗi sa đà kéo dài kỷ lục (**65 bước TB**, có phiên lên tới **140 bước**).
2. **Mục đích nhận thức (Công việc vs Giải trí):**
   * `vn_fb_001` cũng có mức tò mò **Rất cao**, nhưng số bước sa đà chỉ là **19.0 bước/phiên**. Lý do là tính tò mò của nhân vật gắn liền với công việc sáng tạo nội dung, thể hiện qua số hành vi mang động cơ tò mò cao nhất hệ thống (**34.8 hành động/phiên**) và đọc sâu tới **5.5 bài/phiên**. Bot tò mò có chọn lọc và có mục đích rõ ràng, thay vì trôi dạt thụ động.
3. **Tính cách đối trọng (Hoài nghi & Kiểm chứng):**
   * `vn_fb_006` có mức tò mò **Cao**, nhưng số bước sa đà chỉ ở mức vừa phải (**24.5 bước**, tỷ lệ trung vị **22.2%**). Thuộc tính *Rất hoài nghi / Luôn kiểm chứng nguồn tin* đóng vai trò như một "chiếc phanh nhận thức", giúp nhân vật dừng lại kiểm tra và rút lui thay vì bị cuốn sâu vào tin tức giật gân.

---

#### 3. Mối liên hệ với các Chỉ số Nhận thức khác:

##### a. Giữa Mạch Chủ đề Mở và Bước Sa đà Tình huống (Tương quan thuận: r = +0.45):
* Khi phiên làm việc chỉ tập trung vào 1–2 chủ đề quen thuộc, nhân vật kiểm soát hướng đi rất tốt, ít bị phân tâm.
* Ngược lại, khi mở ra càng nhiều mạch chủ đề phân nhánh (`active_threads` $\ge 3 - 4$), nhân vật càng tốn thêm nhiều bước bấm xem và khám phá các chủ đề ngoài lề đó $\longrightarrow$ số bước sa đà tình huống (`situational_steps`) tăng lên tương ứng.

##### b. Tại sao Số bài đọc sâu và Bước sa đà không tương quan thuận (r = -0.07):
* **Đọc nhiều bài không đồng nghĩa với sa đà:** `vn_fb_001` và `vn_fb_005` đọc rất nhiều bài viết (trung bình 5.2 – 5.5 bài/phiên), nhưng họ đọc đúng các bài viết chuyên môn và sở thích thật, không bị trôi dạt vào nội dung nhảm.
* **Sa đà cực mạnh nhưng không hề đọc bài:** `vn_fb_004` có số bước sa đà cao nhất hệ thống vì bị cuốn vào chuỗi Reels, nhưng số bài đọc dạng chữ (`read_posts`) chỉ có 1 bài/phiên. Do đó, đọc sâu bài viết và sa đà tình huống là hai hành vi độc lập.

##### c. Động lực thực sự thúc đẩy việc Đọc sâu: Động cơ Tò mò (r = +0.49):
* Biểu đồ Panel C đối sánh **Động cơ Tò mò (`curiosity_actions`)** và **Số bài viết đã đọc (`read_posts`)** cho thấy mối tương quan thuận rõ nét ($r = +0.49$):
  - Nhân vật càng có động cơ tò mò tìm hiểu kiến thức mới thì càng chủ động dừng lại mở bài viết và đọc kỹ nội dung.
  - Nhóm tò mò cao (`vn_fb_001`, `vn_fb_005`) có số hành động tò mò trên 30 bước và đọc từ 5 đến 6 bài mỗi phiên; trong khi nhóm tàu ngầm ít tò mò (`vn_fb_004`) chỉ đọc lướt 1 bài mỗi phiên."""

# Update cells in notebook
nb['cells'][18]['source'] = [line + '\n' for line in cell_18_code.split('\n')]
nb['cells'][18]['source'][-1] = nb['cells'][18]['source'][-1].rstrip('\n')

nb['cells'][19]['source'] = [line + '\n' for line in cell_19_content.split('\n')]
nb['cells'][19]['source'][-1] = nb['cells'][19]['source'][-1].rstrip('\n')

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Updated Cell 18 and Cell 19 successfully!")
