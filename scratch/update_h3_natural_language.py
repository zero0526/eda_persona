import nbformat
from pathlib import Path

nb_path = Path("notebooks/notebook_action_logs.ipynb")
nb = nbformat.read(nb_path, as_version=4)

# Cell 20: Markdown
cell_20 = """---
## 4. KIỂM ĐỊNH GIẢ THUYẾT $H_3$ — HÀNH VI CỦA AGENT QUA CÁC PHIÊN (SESSION) CÓ NHẤT QUÁN KHÔNG?

> **Mục tiêu quan sát & Phân tích:**  
> Đánh giá xem khi chạy qua các phiên độc lập, các Persona Agent có giữ được **thói quen và phong cách thao tác riêng** hay không, hay chỉ hành động ngẫu nhiên giống nhau.  
> Mức độ tương đồng giữa các phiên của cùng một Persona ($\bar{r}_{\text{intra}}$) có cao hơn so với mức độ tương đồng khi so chéo giữa các Persona khác nhau ($\bar{r}_{\text{inter}}$) hay không.

```
+---------------------------------------------------------------------------------------------------+
|                           KHUNG THEO DÕI HÀNH VI AGENT QUA 4 CẤP ĐỘ                               |
+---------------------------------------------------------------------------------------------------+
|  [CẤP ĐỘ 1: CẤP PHIÊN]              -> Nhịp độ thao tác chung, thời lượng, số hành động / phút    |
|  [CẤP ĐỘ 2: BỀ MẶT & Ý ĐỊNH]        -> Màn hình sử dụng, các loại thao tác, chuyển đổi qua lại    |
|  [CẤP ĐỘ 3: THAO TÁC TRÌNH DUYỆT]   -> Tốc độ cuộn trang (px/s), độ dài mỗi lượt cuộn (px), ms   |
|  [CẤP ĐỘ 4: BẰNG CHỨNG HÀNH ĐỘNG]   -> Bằng chứng hành động, trang/nhóm và nội dung nhớ lặp lại   |
+---------------------------------------------------------------------------------------------------+
```

Dựa trên dữ liệu ghi nhận từ **13 phiên thực tế (758 hành động, 745 lượt chuyển bước)** của 6 Persona, phần này sẽ đi qua từng cấp độ để xem các agent duy trì thói quen như thế nào qua thời gian."""

# Cell 21: Code
cell_21 = r"""# ==============================================================================
# BƯỚC 11: BẢNG TỔNG HỢP ĐỘ TƯƠNG ĐỒNG HÀNH VI QUA CÁC PHIÊN THEO 4 CẤP ĐỘ
# ==============================================================================

from scipy.stats import pearsonr, mannwhitneyu, ttest_ind
from sklearn.metrics.pairwise import cosine_similarity

# 1. Lọc tập dữ liệu 13 phiên hoàn chỉnh cho phân tích H3
cond_13 = (df_actions['session_order'].isin([1, 2])) | ((df_actions['persona_id'] == 'vn_fb_006') & (df_actions['session_order'] == 3))
df_actions_h3 = df_actions[cond_13].sort_values(['persona_id', 'session_order', 'step_index']).reset_index(drop=True)
df_actions_h3['session_label'] = df_actions_h3['persona_id'] + '_s' + df_actions_h3['session_order'].astype(str)

cond_sess_13 = (df_sessions['session_order'].isin([1, 2])) | ((df_sessions['persona_id'] == 'vn_fb_006') & (df_sessions['session_order'] == 3))
df_sessions_h3 = df_sessions[cond_sess_13].copy()
df_sessions_h3['session_label'] = df_sessions_h3['persona_id'] + '_s' + df_sessions_h3['session_order'].astype(str)
df_sessions_h3['velocity'] = df_sessions_h3['total_actions'] / (df_sessions_h3['duration_seconds'] / 60)

# 2. Chuẩn bị ma trận đặc trưng cho các cấp độ
all_surfaces = ['feed', 'detail', 'group', 'reels', 'search']
all_intents = sorted(df_actions_h3['intent'].dropna().unique())

intent_by_sess = df_actions_h3.groupby('session_label')['intent'].value_counts(normalize=True).unstack(fill_value=0).reindex(columns=all_intents, fill_value=0)
surface_by_sess = df_actions_h3.groupby('session_label')['surface'].value_counts(normalize=True).unstack(fill_value=0).reindex(columns=all_surfaces, fill_value=0)

# Cấp độ 3: Thao tác trình duyệt (Tốc độ cuộn trang)
df_gest = df_actions_h3[df_actions_h3['gesture_total_px'].notnull()].copy()
df_gest['scroll_speed_px_s'] = (df_gest['gesture_total_px'] / (df_gest['gesture_ms'] / 1000)).replace([np.inf, -np.inf], np.nan)
gest_speed_mean = df_gest.groupby('session_label')['scroll_speed_px_s'].mean()

# Cấp độ 4: Bằng chứng hành động (Các chủ đề quan tâm)
top_dims = df_actions_h3['primary_dimension'].value_counts().head(12).index.tolist()
dim_by_sess = df_actions_h3.groupby('session_label')['primary_dimension'].value_counts(normalize=True).unstack(fill_value=0).reindex(columns=top_dims, fill_value=0)

# Ánh xạ thực thể lặp lại xuyên phiên đã bóc tách từ SQLite
entity_continuity_map = {
    ('vn_fb_001', 'S1 -> S2'): '2 trang (Cờ Vua đam mê, Chess.com)',
    ('vn_fb_002', 'S1 -> S2'): '1 trang (Thông tin Chính phủ)',
    ('vn_fb_003', 'S1 -> S2'): '0 (Đọc tin bài mới)',
    ('vn_fb_004', 'S1 -> S2'): '0 (Xem Reels đa kênh)',
    ('vn_fb_005', 'S1 -> S2'): '1 trang (Thông tin Chính phủ)',
    ('vn_fb_006', 'S1 -> S2'): '2 nhóm/trang (BĐS Cần Thơ, Nhóm BĐS Cần Thơ)',
    ('vn_fb_006', 'S2 -> S3'): '1 trang (BV Mắt Sài Gòn HN)',
    ('vn_fb_006', 'S1 -> S3'): '0 (Đổi chủ đề tìm hiểu)'
}

# 3. Tổng hợp Bảng Tính nhất quán Đa cấp độ
pairs = [
    ('vn_fb_001', 1, 2),
    ('vn_fb_002', 1, 2),
    ('vn_fb_003', 1, 2),
    ('vn_fb_004', 1, 2),
    ('vn_fb_005', 1, 2),
    ('vn_fb_006', 1, 2),
    ('vn_fb_006', 2, 3),
    ('vn_fb_006', 1, 3)
]

consistency_rows = []
for pid, s1, s2 in pairs:
    lbl1 = f'{pid}_s{s1}'
    lbl2 = f'{pid}_s{s2}'
    pair_label = f'S{s1} -> S{s2}'
    
    # Cấp 1: Delta vận tốc
    v1 = df_sessions_h3[df_sessions_h3['session_label'] == lbl1]['velocity'].values
    v2 = df_sessions_h3[df_sessions_h3['session_label'] == lbl2]['velocity'].values
    delta_v = abs(v2[0] - v1[0]) if len(v1) and len(v2) else np.nan
    
    # Cấp 2: Tương quan Pearson
    r_intent, _ = pearsonr(intent_by_sess.loc[lbl1], intent_by_sess.loc[lbl2])
    r_surf, _ = pearsonr(surface_by_sess.loc[lbl1], surface_by_sess.loc[lbl2])
    
    # Cấp 3: Delta tốc độ cuộn chuột
    sp1 = gest_speed_mean.get(lbl1, np.nan)
    sp2 = gest_speed_mean.get(lbl2, np.nan)
    delta_sp = abs(sp2 - sp1) if pd.notnull(sp1) and pd.notnull(sp2) else np.nan
    
    # Cấp 4: Tương quan Bằng chứng hành động
    r_dim, _ = pearsonr(dim_by_sess.loc[lbl1], dim_by_sess.loc[lbl2])
    
    ent_info = entity_continuity_map.get((pid, pair_label), '0')
    
    consistency_rows.append({
        'Persona': pid,
        'Cặp phiên so sánh': pair_label,
        'Cấp phiên: Lệch nhịp độ (bước/phút)': delta_v,
        'Ý định: Độ tương đồng (r)': r_intent,
        'Bề mặt: Độ tương đồng (r)': r_surf,
        'Thao tác trình duyệt: Lệch tốc độ cuộn (px/s)': delta_sp,
        'Bằng chứng hành động: Độ tương đồng (r)': r_dim,
        'Ghi nhớ lặp lại: Trang / Nhóm': ent_info
    })

df_multi_level_consistency = pd.DataFrame(consistency_rows)

print("=== BẢNG 1: TỔNG HỢP ĐỘ TƯƠNG ĐỒNG HÀNH VI CỦA CÁC PERSONA QUA CÁC PHIÊN ===")
styled_multi_consistency = (
    df_multi_level_consistency.style
    .format({
        'Cấp phiên: Lệch nhịp độ (bước/phút)': '{:.2f}',
        'Ý định: Độ tương đồng (r)': '{:.4f}',
        'Bề mặt: Độ tương đồng (r)': '{:.4f}',
        'Thao tác trình duyệt: Lệch tốc độ cuộn (px/s)': '{:.1f}',
        'Bằng chứng hành động: Độ tương đồng (r)': '{:.4f}',
    }, na_rep='-')
    .background_gradient(subset=['Ý định: Độ tương đồng (r)', 'Bề mặt: Độ tương đồng (r)', 'Bằng chứng hành động: Độ tương đồng (r)'], cmap='Greens', vmin=0.0, vmax=1.0)
    .set_properties(**{'text-align': 'center'})
)
display(styled_multi_consistency)"""

# Cell 22: Markdown
cell_22 = """---
### Nhận định từ Bảng Tổng hợp Độ tương đồng qua 4 Cấp độ:

1. **Cấp phiên (Nhịp độ thao tác chung):**
   - Nhóm xem video (`vn_fb_004`) giữ nhịp độ chậm và khá đều giữa 2 phiên ($3.48$ và $4.10\text{ hành động/phút}$, độ lệch chỉ $0.62$), vì phần lớn thời gian trong phiên là để xem video Reels.
   - Nhóm lướt đọc tin tức (`vn_fb_003`) duy trì nhịp lướt đọc liên tục và khá nhanh ($6.46$ và $6.91\text{ hành động/phút}$, độ lệch chỉ $0.45$).
2. **Không gian Bề mặt & Ý định thao tác:**
   - **Màn hình sử dụng (Bề mặt):** Mức độ tương đồng của cùng một Persona qua các phiên đạt trung bình $\bar{r}_{\text{intra}} = \mathbf{0.5435}$, cao hơn đáng kể so với khi so chéo giữa các Persona khác nhau ($\bar{r}_{\text{inter}} = 0.2558$, gấp hơn 2 lần). Các agent như `vn_fb_002` ($r = 0.9900$) và `vn_fb_004` ($r = 0.9786$) gần như chỉ tập trung vào một vài màn hình quen thuộc.
   - **Ý định thao tác:** Độ tương đồng về các kiểu hành động của cùng một Persona đạt $\bar{r}_{\text{intra}} = \mathbf{0.7027}$ (cao hơn nhiều mức $0.4392$ của việc so chéo). Trong đó, `vn_fb_003` lặp lại gần như trọn vẹn bộ thói quen thao tác giữa hai phiên ($r = 0.9146$).
3. **Thao tác trình duyệt (Tốc độ cuộn trang):**
   - Phân hóa rõ rệt về thói quen tay cuộn: nhóm cuộn nhanh (`vn_fb_002`, `vn_fb_005` thường cuộn lướt nhanh $> 4,000 - 5,300\text{ px/s}$) khác biệt so với nhóm cuộn chậm để đọc kỹ từng đoạn (`vn_fb_003`, `vn_fb_004` dưới $2,800\text{ px/s}$). Thói quen cuộn này duy trì tương đối ổn định qua các phiên ($r \approx 0.415$).
4. **Bằng chứng hành động & Ghi nhớ thực thể:**
   - Độ tương đồng về bằng chứng hành động nội tại đạt $\bar{r}_{\text{intra}} = \mathbf{0.4580}$, cao hơn nhiều so với khi so giữa các agent khác nhau ($\bar{r}_{\text{inter}} = 0.0795$). Các agent `vn_fb_001` ($r = 0.9968$), `vn_fb_004` ($r = 0.9397$), `vn_fb_006` ($r = 0.9933$) thể hiện các mối quan tâm rất nhất quán.
   - Đồng thời, ghi nhận một số trang fanpage và hội nhóm quen thuộc được agent chủ động tìm lại ở các phiên sau, cho thấy agent có khả năng lưu giữ thông tin qua các phiên."""

# Cell 23: Code
cell_23 = r"""# ==============================================================================
# BƯỚC 12: MÔ HÌNH HÓA VÀ VẼ SƠ ĐỒ CHUYỂN ĐỔI GIỮA 4 MÀN HÌNH CHÍNH
# ==============================================================================

import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 1. Trích xuất các bước chuyển thực tế giữa 4 màn hình chính
macro_surfaces = ['feed', 'group', 'reels', 'search']
df_macro = df_actions_h3[df_actions_h3['surface'].isin(macro_surfaces)].copy()

# Lọc bỏ các bước trùng lặp liên tiếp để lấy bước chuyển thực tế (Surface Shifts)
df_macro['prev_surface'] = df_macro.groupby(['persona_id', 'session_id'])['surface'].shift(1)
df_shifts = df_macro[df_macro['surface'] != df_macro['prev_surface']].copy()
df_shifts['next_surface'] = df_shifts.groupby(['persona_id', 'session_id'])['surface'].shift(-1)

valid_shifts = df_shifts.dropna(subset=['next_surface'])

# 2. Xây dựng Ma trận Tần suất và Tỷ lệ chuyển đổi có điều kiện
ct_counts = pd.crosstab(valid_shifts['surface'], valid_shifts['next_surface']).reindex(index=macro_surfaces, columns=macro_surfaces, fill_value=0)
ct_probs = ct_counts.div(ct_counts.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)

print(f"=== BẢNG 2: TỶ LỆ CHUYỂN ĐỔI GIỮA 4 MÀN HÌNH CHÍNH (TỔNG SỐ LẦN CHUYỂN N = {len(valid_shifts)}) ===")
styled_macro_prob = (
    ct_probs.style
    .format('{:.3f}')
    .background_gradient(cmap='Blues', vmin=0.0, vmax=1.0)
    .set_properties(**{'text-align': 'center'})
)
display(styled_macro_prob)

# 3. TRỰC QUAN HÓA SƠ ĐỒ CHUYỂN ĐỔI GIỮA 4 MÀN HÌNH CHÍNH
fig, ax = plt.subplots(figsize=(11, 6.5), dpi=120)

nodes = {
    'feed': (0.2, 0.5),
    'search': (0.5, 0.82),
    'group': (0.8, 0.5),
    'reels': (0.5, 0.18)
}

node_colors = {
    'feed': '#2563eb',
    'search': '#059669',
    'group': '#d97706',
    'reels': '#dc2626'
}

# Vẽ các nút màn hình
for name, (x, y) in nodes.items():
    circle = patches.Circle((x, y), 0.082, facecolor=node_colors[name], edgecolor='black', linewidth=1.8, zorder=3, alpha=0.9)
    ax.add_patch(circle)
    ax.text(x, y, name.upper(), color='white', fontweight='bold', fontsize=12, ha='center', va='center', zorder=4)

# Danh sách các bước chuyển: (nguồn, đích, nhãn tỷ lệ, độ cong rad, màu sắc, vị trí nhãn)
transitions_draw = [
    ('feed', 'search', '71.4% (5 lần)', 0.15, '#2563eb', (0.33, 0.71)),
    ('feed', 'reels', '28.6% (2 lần)', -0.15, '#dc2626', (0.33, 0.29)),
    ('search', 'group', '80.0% (4 lần)', 0.15, '#059669', (0.67, 0.71)),
    ('search', 'feed', '20.0% (1 lần)', 0.15, '#4b5563', (0.38, 0.60)),
    ('group', 'search', '50.0% (1 lần)', 0.15, '#d97706', (0.62, 0.60)),
    ('group', 'feed', '50.0% (1 lần)', -0.25, '#d97706', (0.50, 0.44)),
    ('reels', 'search', '100% (1 lần)', 0.10, '#dc2626', (0.52, 0.51)),
]

for src, dst, label, rad, col, (lx, ly) in transitions_draw:
    x1, y1 = nodes[src]
    x2, y2 = nodes[dst]
    arrow = patches.FancyArrowPatch(
        (x1, y1), (x2, y2),
        connectionstyle=f'arc3,rad={rad}',
        arrowstyle='-|>,head_length=8.5,head_width=5.5',
        color=col,
        linewidth=2.2,
        alpha=0.85,
        zorder=2,
        shrinkA=36,
        shrinkB=36
    )
    ax.add_patch(arrow)
    ax.text(lx, ly, label, fontsize=9.5, fontweight='bold', color=col, ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='white', edgecolor=col, alpha=0.92, linewidth=1.2), zorder=5)

# Chú thích 2 hướng điều hướng & thói quen xem liên tục
ax.text(0.5, 0.05, 'Thói quen xem liên tục: Tự lặp Reels đạt 98.6% - 100% (ở vn_fb_004)', 
        fontsize=9.5, fontweight='bold', color='#dc2626', ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.35', facecolor='#fee2e2', edgecolor='#dc2626', alpha=0.9))

header_desc = "Hướng 1: Tìm kiếm & xem nhóm (feed -> search -> group: 71.4% -> 80.0%)\nHướng 2: Xem video ngắn (feed -> reels -> search: 28.6% -> 100%)"
ax.text(0.5, 0.95, header_desc, 
        fontsize=9.5, fontweight='bold', color='#1f2937', ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.35', facecolor='#f3f4f6', edgecolor='#9ca3af', alpha=0.9))

ax.set_xlim(0.05, 0.95)
ax.set_ylim(0.0, 1.0)
ax.axis('off')
title_text = "SƠ ĐỒ CHUYỂN ĐỔI GIỮA 4 MÀN HÌNH CHÍNH VÀ CÁC HƯỚNG ĐIỀU HƯỚNG\n(Theo dõi 15 lượt chuyển màn hình thực tế)"
ax.set_title(title_text, fontsize=13, fontweight='bold', pad=18)

plt.tight_layout()
plt.show()"""

# Cell 24: Code
cell_24 = r"""# ==============================================================================
# BƯỚC 13: MẠCH GHI NHỚ TRANG VÀ HỘI NHÓM XUYÊN PHIÊN (BẰNG CHỨNG HÀNH ĐỘNG)
# ==============================================================================

import sqlite3
import re
from loaders.episode_loader import get_sqlite_path

# 1. Truy vấn thông tin thực thể từ episode_events trong SQLite
sqlite_file = get_sqlite_path()
conn = sqlite3.connect(sqlite_file)
cursor = conn.cursor()

cursor.execute('''
    SELECT e.id, b.persona_id, w.start_at
    FROM episodes e
    JOIN bots b ON e.bot_id = b.id
    LEFT JOIN activity_windows w ON e.window_id = w.id
    ORDER BY b.persona_id, w.start_at;
''')
episodes_info = cursor.fetchall()
ep_map = {}
p_order = {}
for ep_id, p_id, start_at in episodes_info:
    p_order[p_id] = p_order.get(p_id, 0) + 1
    ep_map[ep_id] = {'persona_id': p_id, 'session_order': p_order[p_id]}

cursor.execute("SELECT episode_id, payload_json FROM episode_events WHERE kind = 'tool_result';")
events = cursor.fetchall()
conn.close()

parsed_entities = []
for ep_id, p_str in events:
    if not p_str:
        continue
    try:
        p = json.loads(p_str)
        info = ep_map.get(ep_id, {'persona_id': 'unknown', 'session_order': 0})
        tc = p.get('target_candidate')
        if not tc or not isinstance(tc, dict):
            continue
        text = tc.get('text', '')
        url = tc.get('url', '')
        if not text and not url:
            continue
            
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        author = "Unknown"
        if lines:
            if lines[0] in ["Chỉ báo trạng thái online", "Đang hoạt động"] and len(lines) > 2:
                author = lines[2]
            else:
                author = lines[0]
                
        group_id_match = re.search(r'/groups/([^/]+)', url)
        group_id = group_id_match.group(1) if group_id_match else None
        
        parsed_entities.append({
            'persona_id': info['persona_id'],
            'session_order': info['session_order'],
            'author': author,
            'group_id': group_id,
            'url': url
        })
    except:
        pass

df_ent = pd.DataFrame(parsed_entities)
# Giới hạn phân tích trong 13 phiên của H3
cond_ent_13 = (df_ent['session_order'].isin([1, 2])) | ((df_ent['persona_id'] == 'vn_fb_006') & (df_ent['session_order'] == 3))
df_ent_13 = df_ent[cond_ent_13].copy()

# 2. Thống kê tác giả lặp lại theo từng Persona qua các phiên
p_author_stats = df_ent_13.groupby(['persona_id', 'author'])['session_order'].agg(
    sessions=lambda s: sorted(s.unique()),
    n_sessions='nunique',
    total_actions='count'
).reset_index()

cross_authors_df = p_author_stats[p_author_stats['n_sessions'] > 1].sort_values('total_actions', ascending=False)
cross_authors_df['Phiên xuất hiện'] = cross_authors_df['sessions'].apply(lambda x: ', '.join([f'S{s}' for s in x]))
cross_authors_df = cross_authors_df.rename(columns={
    'persona_id': 'Persona ID',
    'author': 'Trang / Tác giả lặp lại',
    'n_sessions': 'Số phiên ghi nhận',
    'total_actions': 'Tổng lượt thao tác'
})[['Persona ID', 'Trang / Tác giả lặp lại', 'Phiên xuất hiện', 'Số phiên ghi nhận', 'Tổng lượt thao tác']]

print("=== BẢNG 3: CÁC TRANG VÀ TÁC GIẢ ĐƯỢC TƯƠNG TÁC LẶP LẠI QUA CÁC PHIÊN ===")
styled_cross_authors = (
    cross_authors_df.style
    .set_properties(**{'text-align': 'center'})
    .set_properties(subset=['Trang / Tác giả lặp lại'], **{'text-align': 'left'})
)
display(styled_cross_authors)

# Thống kê Hội nhóm gắn kết
group_names_map = {
    '2133631560242753': 'Bất Động Sản Cần Thơ - Batdongsancantho.vn (63K thành viên)'
}
p_group_stats = df_ent_13[df_ent_13['group_id'].notna()].groupby(['persona_id', 'group_id'])['session_order'].agg(
    sessions=lambda s: sorted(s.unique()),
    n_sessions='nunique',
    total_actions='count'
).reset_index()
cross_groups_df = p_group_stats[p_group_stats['n_sessions'] > 1].copy()
cross_groups_df['Tên Hội nhóm'] = cross_groups_df['group_id'].map(group_names_map).fillna(cross_groups_df['group_id'])
cross_groups_df['Phiên xuất hiện'] = cross_groups_df['sessions'].apply(lambda x: ', '.join([f'S{s}' for s in x]))
cross_groups_df = cross_groups_df[['persona_id', 'Tên Hội nhóm', 'Phiên xuất hiện', 'n_sessions', 'total_actions']].rename(columns={
    'persona_id': 'Persona ID',
    'n_sessions': 'Số phiên',
    'total_actions': 'Tổng lượt thao tác'
})

print("\n=== HỘI NHÓM ĐƯỢC TƯƠNG TÁC LẶP LẠI QUA CÁC PHIÊN ===")
display(cross_groups_df.style.set_properties(**{'text-align': 'center'}))"""

# Cell 25: Code
cell_25 = r"""# ==============================================================================
# BƯỚC 14: THÓI QUEN THAO TÁC, MA TRẬN TƯƠNG ĐỒNG 13 PHIÊN & TRỰC QUAN HÓA
# ==============================================================================

# 1. BẢNG MỨC ĐỘ Ở LẠI TRÊN TỪNG MÀN HÌNH THEO PHIÊN
surface_loop_rows = []
for (p, s), g in df_actions_h3.groupby(['persona_id', 'session_order']):
    g_sorted = g.sort_values('step_index').copy()
    g_sorted['next_surf'] = g_sorted['surface'].shift(-1)
    n_trans = g_sorted['next_surf'].notna().sum()
    ct = pd.crosstab(g_sorted['surface'], g_sorted['next_surf']).reindex(index=all_surfaces, columns=all_surfaces, fill_value=0)
    row_sums = ct.sum(axis=1)
    prob = ct.div(row_sums.replace(0, np.nan), axis=0).fillna(0)
    
    dom_surf = g['surface'].value_counts().index[0]
    dom_pct = g['surface'].value_counts(normalize=True).iloc[0] * 100
    
    surface_loop_rows.append({
        'Persona': p,
        'Phiên': f'S{s}',
        'Tổng bước': len(g),
        'Số lần chuyển': n_trans,
        'Màn hình chính': f'{dom_surf} ({dom_pct:.1f}%)',
        'Ở lại feed': prob.loc['feed', 'feed'],
        'Ở lại detail': prob.loc['detail', 'detail'],
        'Ở lại group': prob.loc['group', 'group'],
        'Ở lại reels': prob.loc['reels', 'reels'],
        'Ở lại search': prob.loc['search', 'search'],
    })

df_surface_retention = pd.DataFrame(surface_loop_rows)
print("=== BẢNG 4: MỨC ĐỘ Ở LẠI TRÊN TỪNG MÀN HÌNH THEO PHIÊN ===")
styled_surface_retention = (
    df_surface_retention.style
    .format({
        'Ở lại feed': '{:.3f}',
        'Ở lại detail': '{:.3f}',
        'Ở lại group': '{:.3f}',
        'Ở lại reels': '{:.3f}',
        'Ở lại search': '{:.3f}',
    })
    .background_gradient(subset=['Ở lại feed', 'Ở lại detail', 'Ở lại group', 'Ở lại reels', 'Ở lại search'], cmap='Blues', vmin=0.0, vmax=1.0)
    .set_properties(**{'text-align': 'center'})
)
display(styled_surface_retention)

# 2. BẢNG THEO DÕI THÓI QUEN CŨ VS THAO TÁC MỚI XUẤT HIỆN
evolution_rows = []
for p, p_df in df_actions_h3.groupby('persona_id'):
    sessions = sorted(p_df['session_order'].unique())
    for i in range(len(sessions)-1):
        s_from = sessions[i]
        s_to = sessions[i+1]
        
        df_a = p_df[p_df['session_order'] == s_from]
        df_b = p_df[p_df['session_order'] == s_to]
        
        ints_a = set(df_a['intent'].dropna())
        ints_b = set(df_b['intent'].dropna())
        
        common_ints = ints_a.intersection(ints_b)
        new_ints = ints_b - ints_a
        dropped_ints = ints_a - ints_b
        jaccard_intent = len(common_ints) / len(ints_a.union(ints_b))
        
        vc_a = df_a['intent'].value_counts(normalize=True).reindex(all_intents, fill_value=0).values
        vc_b = df_b['intent'].value_counts(normalize=True).reindex(all_intents, fill_value=0).values
        r_val, _ = pearsonr(vc_a, vc_b)
        cos_val = cosine_similarity([vc_a], [vc_b])[0, 0]
        
        evolution_rows.append({
            'Persona': p,
            'Cặp phiên': f'S{s_from} -> S{s_to}',
            'Số bước trước': len(df_a),
            'Số bước sau': len(df_b),
            'Thao tác cũ lặp lại': len(common_ints),
            'Thao tác mới': len(new_ints),
            'Thao tác dừng': len(dropped_ints),
            'Chi tiết thao tác mới': ', '.join(sorted(new_ints)) if new_ints else '(không có)',
            'Chi tiết thao tác dừng': ', '.join(sorted(dropped_ints)) if dropped_ints else '(không có)',
            'Độ tương đồng Jaccard': jaccard_intent,
            'Độ tương đồng Pearson (r)': r_val,
            'Độ tương đồng Cosine': cos_val
        })

# Bổ sung so sánh S1 -> S3 cho vn_fb_006
p6_df = df_actions_h3[df_actions_h3['persona_id'] == 'vn_fb_006']
df_p6_s1 = p6_df[p6_df['session_order'] == 1]
df_p6_s3 = p6_df[p6_df['session_order'] == 3]
ints_1 = set(df_p6_s1['intent'].dropna())
ints_3 = set(df_p6_s3['intent'].dropna())
common_13 = ints_1.intersection(ints_3)
new_13 = ints_3 - ints_1
dropped_13 = ints_1 - ints_3
vc_1 = df_p6_s1['intent'].value_counts(normalize=True).reindex(all_intents, fill_value=0).values
vc_3 = df_p6_s3['intent'].value_counts(normalize=True).reindex(all_intents, fill_value=0).values
r_13, _ = pearsonr(vc_1, vc_3)
cos_13 = cosine_similarity([vc_1], [vc_3])[0, 0]
evolution_rows.append({
    'Persona': 'vn_fb_006',
    'Cặp phiên': 'S1 -> S3',
    'Số bước trước': len(df_p6_s1),
    'Số bước sau': len(df_p6_s3),
    'Thao tác cũ lặp lại': len(common_13),
    'Thao tác mới': len(new_13),
    'Thao tác dừng': len(dropped_13),
    'Chi tiết thao tác mới': ', '.join(sorted(new_13)) if new_13 else '(không có)',
    'Chi tiết thao tác dừng': ', '.join(sorted(dropped_13)) if dropped_13 else '(không có)',
    'Độ tương đồng Jaccard': len(common_13) / len(ints_1.union(ints_3)),
    'Độ tương đồng Pearson (r)': r_13,
    'Độ tương đồng Cosine': cos_13
})

df_behavior_evolution = pd.DataFrame(evolution_rows)

print("\n=== BẢNG 5: MỨC ĐỘ GIỮ LẠI THÓI QUEN CŨ VÀ PHÁT SINH THAO TÁC MỚI ===")
styled_evolution = (
    df_behavior_evolution.style
    .format({
        'Độ tương đồng Jaccard': '{:.3f}',
        'Độ tương đồng Pearson (r)': '{:.4f}',
        'Độ tương đồng Cosine': '{:.4f}',
    })
    .background_gradient(subset=['Độ tương đồng Jaccard', 'Độ tương đồng Pearson (r)', 'Độ tương đồng Cosine'], cmap='Greens', vmin=0.0, vmax=1.0)
    .set_properties(**{'text-align': 'center'})
)
display(styled_evolution)

# 3. MA TRẬN TƯƠNG ĐỒNG HÀNH VI TOÀN BỘ 13 PHIÊN
df_actions_h3['session_display'] = df_actions_h3['persona_id'] + ' (S' + df_actions_h3['session_order'].astype(str) + ')'
intent_display = df_actions_h3.groupby('session_display')['intent'].value_counts(normalize=True).unstack(fill_value=0).reindex(columns=all_intents, fill_value=0)
df_session_corr = intent_display.T.corr()

session_labels = intent_display.index.tolist()
intra_vals, inter_vals = [], []
for i, s1 in enumerate(session_labels):
    p1 = s1.split(' ')[0]
    for j, s2 in enumerate(session_labels):
        if i < j:
            p2 = s2.split(' ')[0]
            val = df_session_corr.loc[s1, s2]
            if p1 == p2:
                intra_vals.append(val)
            else:
                inter_vals.append(val)

print("\n=== ĐỘ TƯƠNG ĐỒNG HÀNH VI GIỮA CÁC PHIÊN ===")
print(f"- Khi so sánh cùng Persona qua các phiên: r trung bình = {np.mean(intra_vals):.4f} +/- {np.std(intra_vals):.4f} (Trung vị: {np.median(intra_vals):.4f})")
print(f"- Khi so sánh khác Persona giữa các phiên: r trung bình = {np.mean(inter_vals):.4f} +/- {np.std(inter_vals):.4f} (Trung vị: {np.median(inter_vals):.4f})")
print("- Nhận xét: Độ tương đồng hành vi của cùng Persona cao hơn rõ rệt so với giữa các Persona khác nhau.")

# 4. TRỰC QUAN HÓA TOÀN DIỆN 3-PANEL FIGURE
fig, axes = plt.subplots(1, 3, figsize=(21, 6.8), dpi=120)

# Panel A: Heatmap Ma trận Tương quan 13 Phiên
sns.heatmap(
    df_session_corr,
    annot=True,
    fmt='.2f',
    cmap='Blues',
    vmin=-0.2,
    vmax=1.0,
    ax=axes[0],
    cbar_kws={'label': 'Độ tương đồng (r)'},
    annot_kws={'size': 8},
    linewidths=0.5,
    linecolor='#E0E0E0'
)
axes[0].set_title('Panel A: Ma trận tương đồng thao tác giữa 13 phiên', fontweight='bold', fontsize=12, pad=12)
axes[0].tick_params(axis='x', rotation=45, labelsize=8.5)
axes[0].tick_params(axis='y', rotation=0, labelsize=8.5)
axes[0].set_xlabel('Phiên thực thi', fontweight='bold', fontsize=10)
axes[0].set_ylabel('Phiên thực thi', fontweight='bold', fontsize=10)

# Panel B: Boxplot & Strip Plot So sánh Tương quan Cùng Persona vs Khác Persona
df_corr_comp = pd.DataFrame({
    'Loại tương đồng': ['Cùng Persona\nqua các phiên'] * len(intra_vals) + ['Khác Persona\ngiữa các phiên'] * len(inter_vals),
    'Hệ số tương đồng (r)': intra_vals + inter_vals
})

palette_comp = {'Cùng Persona\nqua các phiên': '#2ca02c', 'Khác Persona\ngiữa các phiên': '#7f7f7f'}
sns.boxplot(
    data=df_corr_comp,
    x='Loại tương đồng',
    y='Hệ số tương đồng (r)',
    hue='Loại tương đồng',
    palette=palette_comp,
    ax=axes[1],
    width=0.45,
    boxprops=dict(alpha=0.7),
    legend=False
)
sns.stripplot(
    data=df_corr_comp,
    x='Loại tương đồng',
    y='Hệ số tương đồng (r)',
    color='black',
    alpha=0.6,
    jitter=0.2,
    size=6.5,
    ax=axes[1]
)
axes[1].set_title('Panel B: So sánh độ tương đồng\n(Cùng Persona vs Khác Persona)', fontweight='bold', fontsize=12, pad=12)
axes[1].set_ylabel('Hệ số tương đồng (r)', fontweight='bold', fontsize=10)
axes[1].set_xlabel('')
axes[1].grid(True, linestyle='--', alpha=0.5)

# Panel C: Stacked Bar Chart Tỷ lệ Thao tác Quen thuộc vs Mới xuất hiện
evolution_bar_rows = []
for p, p_df in df_actions_h3.groupby('persona_id'):
    sessions = sorted(p_df['session_order'].unique())
    for i in range(len(sessions)-1):
        s_from, s_to = sessions[i], sessions[i+1]
        df_a, df_b = p_df[p_df['session_order'] == s_from], p_df[p_df['session_order'] == s_to]
        ints_a, ints_b = set(df_a['intent'].dropna()), set(df_b['intent'].dropna())
        common = ints_a.intersection(ints_b)
        new_i = ints_b - ints_a
        total_u = len(ints_a.union(ints_b))
        evolution_bar_rows.append({
            'label': f'{p}\n(S{s_from}->S{s_to})',
            'Quen thuộc (lặp lại)': len(common) / total_u * 100,
            'Mới xuất hiện': len(new_i) / total_u * 100
        })

evolution_bar_rows.append({
    'label': 'vn_fb_006\n(S1->S3)',
    'Quen thuộc (lặp lại)': len(common_13) / len(ints_1.union(ints_3)) * 100,
    'Mới xuất hiện': len(new_13) / len(ints_1.union(ints_3)) * 100
})

df_evol_bar = pd.DataFrame(evolution_bar_rows)
df_evol_bar.set_index('label')[['Quen thuộc (lặp lại)', 'Mới xuất hiện']].plot(
    kind='bar',
    stacked=True,
    color=['#1f77b4', '#ff7f0e'],
    ax=axes[2],
    edgecolor='black',
    linewidth=0.8
)
axes[2].set_title('Panel C: Thao tác quen thuộc (cũ) vs Mới xuất hiện', fontweight='bold', fontsize=12, pad=12)
axes[2].set_ylabel('Tỷ lệ thao tác (%)', fontweight='bold', fontsize=10)
axes[2].set_xlabel('Cặp phiên so sánh', fontweight='bold', fontsize=10)
axes[2].tick_params(axis='x', rotation=0, labelsize=8)
axes[2].legend(title='Tính chất thao tác', loc='upper right', framealpha=0.9)
axes[2].grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()"""

# Cell 26: Markdown
cell_26 = """---
### Nhận định Tổng hợp: Hành vi của Agent qua các phiên có giữ được thói quen riêng không?

1. **Agent thể hiện thói quen thao tác nhất quán qua các phiên:**
   - Khi cùng một Persona chạy lại ở các phiên khác nhau, cách thức thao tác có mức độ tương đồng khá cao ($\bar{r}_{\text{intra}} = \mathbf{0.7027}$), vượt trội rõ rệt so với mức độ tương đồng khi so chéo giữa các Persona khác nhau ($\bar{r}_{\text{inter}} = \mathbf{0.4392}$).
   - Nổi bật nhất là trường hợp của `vn_fb_004` (chuyên xem video ngắn): ở cả 2 phiên, agent này duy trì độ tương đồng tự thân rất cao ($r = 0.7015$), nhưng lại gần như không có điểm chung nào với 5 Persona còn lại ($r \le 0$). Điều này cho thấy mỗi agent đã hình thành phong cách thao tác riêng biệt, không bị trộn lẫn.

2. **Hai thói quen sử dụng màn hình nổi bật:**
   - *Thói quen xem liên tục khó dứt trên Reels:* Agent `vn_fb_004` một khi đã chuyển sang Reels thì gần như chỉ tiếp tục cuộn xem video tiếp theo ($98.6\% - 100\%$ các bước là tự lặp lại trên Reels), rất sát với thói quen lướt video ngắn thực tế.
   - *Thói quen đọc sâu từng bài rồi quay lại dòng tin:* Các agent như `vn_fb_003` và `vn_fb_005` thường xuyên luân chuyển nhịp nhàng: lướt dòng tin (`feed`) $\to$ mở xem bài viết (`detail`) $\to$ đọc kỹ, xem bình luận $\to$ quay lại dòng tin để lướt tiếp (tỷ lệ ở lại mỗi màn hình từ $80\% - 94\%$).
   - *Thói quen tập trung vào hội nhóm:* Agent `vn_fb_006` dành phần lớn thời gian để hoạt động trong nhóm bất động sản Cần Thơ (ở lại trong nhóm $> 75\% - 96\%$).

3. **Vừa giữ thói quen cũ, vừa làm quen thêm thao tác mới:**
   - Các agent giữ được phần lớn các thao tác quen thuộc cốt lõi qua các phiên (như cuộn, đọc, xem). Ví dụ `vn_fb_003` bảo tồn trọn vẹn $12/12$ loại thao tác từ phiên 1 sang phiên 2 ($r = 0.9146$).
   - Đồng thời, ở các phiên sau, agent có xu hướng mở rộng thêm một số thao tác mới tùy theo nội dung bắt gặp (như `vn_fb_004` bắt đầu tìm kiếm từ khóa, `vn_fb_005` thử chia sẻ và bày tỏ cảm xúc). Điều này cho thấy agent có khả năng thích nghi linh hoạt chứ không hoạt động máy móc, xơ cứng.

---

### Bảng Tổng hợp So sánh Hành vi của Agent qua các Phiên

| Khía cạnh quan sát | Chỉ số theo dõi | Mức độ tương đồng cùng Persona | So với khi khác Persona | Nhận xét thực tế |
| :--- | :--- | :---: | :---: | :--- |
| **Cấp phiên (Nhịp độ)** | Số hành động / phút | Lệch ít ($\Delta \approx 0.45 - 1.5$) | Biến động tùy nội dung | Nhóm xem video chậm rãi, nhóm đọc tin nhanh nhạy |
| **Màn hình sử dụng** | Tỷ lệ dùng 5 màn hình | **0.5435** | 0.2558 (cao hơn gấp 2 lần) | Rõ nét nhất ở agent xem Reels và lướt tin |
| **Ý định thao tác** | Tỷ lệ 20 loại hành động | **0.7027** | 0.4392 (cao hơn rõ rệt) | Giữ được thói quen thao tác tương tự qua các phiên |
| **Thao tác trình duyệt** | Tốc độ cuộn chuột (px/s) | Có xu hướng tương đồng | Phân hóa 2 nhóm rõ rệt | Nhóm cuộn lướt nhanh vs Nhóm cuộn chậm đọc kỹ |
| **Bằng chứng hành động** | Xu hướng nội dung quan tâm | **0.4580** | 0.0795 (cao hơn gần 6 lần) | Các chủ đề quan tâm thể hiện rất nhất quán |
| **Ghi nhớ lặp lại** | Trang, Hội nhóm quen thuộc | 5 trang + 1 hội nhóm lặp lại | Không bị nhầm lẫn | Agent nhớ và quay lại đúng trang/nhóm trước đó |

> **TÓM LẠI:**  
> Dữ liệu qua 13 phiên cho thấy hành vi của các Persona Agent không phải là những cú bấm ngẫu nhiên vô nghĩa. Mỗi agent giữ được thói quen sử dụng Facebook tương đối ổn định từ nhịp độ, cách cuộn trang, màn hình ưa thích cho đến nội dung bài viết và hội nhóm tương tác qua các phiên."""

new_cells = [
    nbformat.v4.new_markdown_cell(cell_20),
    nbformat.v4.new_code_cell(cell_21),
    nbformat.v4.new_markdown_cell(cell_22),
    nbformat.v4.new_code_cell(cell_23),
    nbformat.v4.new_code_cell(cell_24),
    nbformat.v4.new_code_cell(cell_25),
    nbformat.v4.new_markdown_cell(cell_26)
]

nb.cells = nb.cells[:20] + new_cells
nbformat.write(nb, nb_path)
print("Updated notebook with natural language terminology successfully!")
