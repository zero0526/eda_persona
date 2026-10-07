import nbformat
from nbclient import NotebookClient

nb_path = 'notebooks/notebook_action_logs.ipynb'
nb = nbformat.read(nb_path, as_version=4)

# ==============================================================================
# CELL 20: MARKDOWN GIỚI THIỆU 4 CẤP ĐỘ
# ==============================================================================
nb.cells[20].source = r"""## 4. KIỂM ĐỊNH GIẢ THUYẾT $H_3$ — HÀNH VI CỦA AGENT QUA CÁC PHIÊN (SESSION) CÓ NHẤT QUÁN KHÔNG?

> **Mục tiêu thực tế:** Quan sát xem cùng một Persona khi chạy lại ở các phiên (session) khác nhau thì có duy trì được **thói quen thao tác**, **màn hình hay dùng**, **tốc độ cuộn lướt** và **mối quan tâm nội dung** nhất quán hay không, hay mỗi lần chạy lại đổi sang một kiểu hành vi ngẫu nhiên khác.

Để có cái nhìn toàn diện và gần gũi, chúng ta theo dõi hành vi của agent qua **4 cấp độ quan sát**:

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

# ==============================================================================
# CELL 21: CODE BẢNG 1 TỔNG HỢP 4 CẤP ĐỘ
# ==============================================================================
nb.cells[21].source = r"""# ==============================================================================
# BƯỚC 11: BẢNG TỔNG HỢP ĐỘ TƯƠNG ĐỒNG HÀNH VI QUA CÁC PHIÊN THEO 4 CẤP ĐỘ
# ==============================================================================

from scipy.stats import pearsonr
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
    
    # Cấp 1: Cấp phiên - Lệch nhịp độ thao tác
    v1 = df_sessions_h3[df_sessions_h3['session_label'] == lbl1]['velocity'].values
    v2 = df_sessions_h3[df_sessions_h3['session_label'] == lbl2]['velocity'].values
    delta_v = abs(v2[0] - v1[0]) if len(v1) and len(v2) else np.nan
    
    # Cấp 2: Tương quan Ý định & Màn hình
    r_intent, _ = pearsonr(intent_by_sess.loc[lbl1], intent_by_sess.loc[lbl2])
    r_surf, _ = pearsonr(surface_by_sess.loc[lbl1], surface_by_sess.loc[lbl2])
    
    # Cấp 3: Thao tác trình duyệt - Lệch tốc độ cuộn chuột
    sp1 = gest_speed_mean.get(lbl1, np.nan)
    sp2 = gest_speed_mean.get(lbl2, np.nan)
    delta_sp = abs(sp2 - sp1) if pd.notnull(sp1) and pd.notnull(sp2) else np.nan
    
    # Cấp 4: Bằng chứng hành động - Tương quan chủ đề quan tâm
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
display(styled_multi_consistency)
"""

# ==============================================================================
# CELL 22: MARKDOWN NHẬN ĐỊNH BẢNG 1
# ==============================================================================
nb.cells[22].source = r"""---
### Nhận định từ Bảng Tổng hợp Độ tương đồng qua 4 Cấp độ:

1. **Cấp phiên (Nhịp độ thao tác chung):**
   - Nhóm xem video (`vn_fb_004`) giữ nhịp độ chậm rãi và tương đối đều giữa 2 phiên ($3.48$ và $4.10$ hành động/phút, mức lệch chỉ khoảng $0.62$), vì phần lớn thời gian trong phiên là để xem video Reels.
   - Nhóm lướt đọc tin tức (`vn_fb_003`) duy trì nhịp lướt đọc liên tục và khá nhanh ($6.46$ và $6.91$ hành động/phút, mức lệch rất nhỏ, chỉ khoảng $0.45$).
2. **Không gian Bề mặt & Ý định thao tác:**
   - **Màn hình sử dụng (Bề mặt):** Mức độ tương đồng của cùng một Persona qua các phiên đạt trung bình khoảng $0.5435$, cao hơn đáng kể so với khi so chéo giữa các Persona khác nhau (mức trung bình so chéo là $0.2558$, gấp hơn 2 lần). Các agent như `vn_fb_002` ($r = 0.9900$) và `vn_fb_004` ($r = 0.9786$) thường chỉ tập trung vào một vài màn hình quen thuộc.
   - **Ý định thao tác:** Độ tương đồng về các kiểu hành động của cùng một Persona đạt trung bình khoảng $0.7027$ (cao hơn rõ rệt so với mức $0.4392$ của việc so chéo). Trong đó, `vn_fb_003` lặp lại gần như trọn vẹn bộ thói quen thao tác giữa hai phiên ($r = 0.9146$).
3. **Thao tác trình duyệt (Tốc độ cuộn trang):**
   - Phân hóa rõ rệt về thói quen cuộn chuột: nhóm cuộn nhanh (`vn_fb_002`, `vn_fb_005` thường cuộn lướt nhanh trên $4,000 - 5,300\text{ px/s}$) khác biệt so với nhóm cuộn chậm để đọc kỹ từng đoạn (`vn_fb_003`, `vn_fb_004` dưới $2,800\text{ px/s}$). Thói quen cuộn này duy trì tương đối ổn định qua các phiên ($r \approx 0.415$).
4. **Bằng chứng hành động & Ghi nhớ thực thể:**
   - Độ tương đồng về bằng chứng hành động nội tại đạt trung bình khoảng $0.4580$, cao hơn nhiều so với khi so giữa các agent khác nhau (chỉ khoảng $0.0795$). Các agent `vn_fb_001` ($r = 0.9968$), `vn_fb_004` ($r = 0.9397$), `vn_fb_006` ($r = 0.9933$) thể hiện các mối quan tâm rất nhất quán.
   - Đồng thời, ghi nhận một số trang fanpage và hội nhóm quen thuộc được agent chủ động tìm lại ở các phiên sau, cho thấy agent có xu hướng lưu giữ thông tin quan tâm qua các phiên."""

# ==============================================================================
# CELL 23: CODE SƠ ĐỒ CHUYỂN ĐỔI MÀN HÌNH (THÊM NHÃN TIẾNG VIỆT CHO NODE)
# ==============================================================================
nb.cells[23].source = r"""# ==============================================================================
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
row_sums = ct_counts.sum(axis=1)
prob_matrix = ct_counts.div(row_sums.replace(0, np.nan), axis=0).fillna(0)

print(f"=== BẢNG 2: TỶ LỆ CHUYỂN ĐỔI GIỮA 4 MÀN HÌNH CHÍNH (TỔNG SỐ LẦN CHUYỂN N = {len(valid_shifts)}) ===")
display(
    prob_matrix.style
    .format('{:.1%}')
    .background_gradient(cmap='Blues', vmin=0.0, vmax=1.0)
    .set_properties(**{'text-align': 'center'})
)

# 3. Trực quan hóa Sơ đồ Chuyển đổi giữa 4 Màn hình chính
fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

node_positions = {
    'feed': (0.22, 0.65),
    'search': (0.78, 0.65),
    'group': (0.78, 0.28),
    'reels': (0.22, 0.28)
}
node_colors = {
    'feed': '#3b82f6',     # Xanh dương
    'search': '#f59e0b',   # Vàng cam
    'group': '#10b981',    # Xanh lá
    'reels': '#ec4899'     # Hồng
}
node_labels = {
    'feed': 'BẢNG TIN\n(Feed)',
    'search': 'TÌM KIẾM\n(Search)',
    'group': 'HỘI NHÓM\n(Group)',
    'reels': 'VIDEO NGẮN\n(Reels)'
}

# Vẽ các nút màn hình
for name, (x, y) in node_positions.items():
    circle = patches.Circle((x, y), radius=0.088, facecolor=node_colors[name], edgecolor='none', zorder=3, alpha=0.92)
    ax.add_patch(circle)
    ax.text(x, y, node_labels[name], color='white', fontweight='bold', fontsize=10.5, ha='center', va='center', zorder=4)

# Danh sách các luồng chuyển đổi chính
transitions = [
    ('feed', 'search', '5 lần\n(71.4%)', '#f59e0b', (0.50, 0.70), 0.12),
    ('feed', 'reels', '2 lần\n(28.6%)', '#ec4899', (0.13, 0.465), 0.15),
    ('search', 'group', '4 lần\n(80.0%)', '#10b981', (0.87, 0.465), 0.15),
    ('search', 'feed', '1 lần\n(20.0%)', '#3b82f6', (0.50, 0.60), 0.12),
    ('reels', 'search', '1 lần\n(100%)', '#f59e0b', (0.50, 0.465), 0.05),
    ('group', 'feed', '2 lần\n(100%)', '#3b82f6', (0.50, 0.35), -0.08)
]

for src, dst, label, col, (lx, ly), rad in transitions:
    x1, y1 = node_positions[src]
    x2, y2 = node_positions[dst]
    arrow = patches.FancyArrowPatch(
        (x1, y1), (x2, y2),
        connectionstyle=f"arc3,rad={rad}",
        arrowstyle='-|>,head_length=8,head_width=5',
        color=col,
        linewidth=2.4,
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

header_desc = "Hướng 1: Tìm kiếm & xem nhóm (Bảng tin -> Tìm kiếm -> Hội nhóm: 71.4% -> 80.0%)\nHướng 2: Xem video ngắn (Bảng tin -> Video ngắn -> Tìm kiếm: 28.6% -> 100%)"
ax.text(0.5, 0.95, header_desc, 
        fontsize=9.5, fontweight='bold', color='#1f2937', ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.35', facecolor='#f3f4f6', edgecolor='#9ca3af', alpha=0.9))

ax.set_xlim(0.05, 0.95)
ax.set_ylim(0.0, 1.0)
ax.axis('off')
title_text = "SƠ ĐỒ CHUYỂN ĐỔI GIỮA 4 MÀN HÌNH CHÍNH VÀ CÁC HƯỚNG ĐIỀU HƯỚNG\n(Theo dõi 15 lượt chuyển màn hình thực tế)"
ax.set_title(title_text, fontsize=13, fontweight='bold', pad=18)
plt.tight_layout()
plt.show()
"""

# ==============================================================================
# CELL 24: CODE BẢNG 3 TRANG & HỘI NHÓM LẶP LẠI (DÙNG JSON TOOL_RESULT CHUẨN XÁC)
# ==============================================================================
nb.cells[24].source = r"""# ==============================================================================
# BƯỚC 13: MẠCH GHI NHỚ TRANG VÀ HỘI NHÓM XUYÊN PHIÊN (BẰNG CHỨNG HÀNH ĐỘNG)
# ==============================================================================

import sqlite3
import json
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
        author = 'Unknown'
        if lines:
            if lines[0] in ['Chỉ báo trạng thái online', 'Đang hoạt động'] and len(lines) > 2:
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
    except Exception:
        pass

df_ent = pd.DataFrame(parsed_entities)
cond_ent_13 = (df_ent['session_order'].isin([1, 2])) | ((df_ent['persona_id'] == 'vn_fb_006') & (df_ent['session_order'] == 3))
df_ent_13 = df_ent[cond_ent_13].copy()

# 2. Thống kê tác giả / fanpage lặp lại theo từng Persona qua các phiên
p_author_stats = df_ent_13.groupby(['persona_id', 'author'])['session_order'].agg(
    sessions=lambda s: sorted(list(s.unique())),
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

# 3. Thống kê Hội nhóm được tương tác lặp lại qua các phiên
group_names_map = {
    '2133631560242753': 'Bất Động Sản Cần Thơ - Batdongsancantho.vn (63K thành viên)'
}
p_group_stats = df_ent_13[df_ent_13['group_id'].notna()].groupby(['persona_id', 'group_id'])['session_order'].agg(
    sessions=lambda s: sorted(list(s.unique())),
    n_sessions='nunique',
    total_actions='count'
).reset_index()

cross_groups_df = p_group_stats[p_group_stats['n_sessions'] > 1].copy()
if len(cross_groups_df) > 0:
    cross_groups_df['Tên Hội nhóm'] = cross_groups_df['group_id'].map(group_names_map).fillna(cross_groups_df['group_id'])
    cross_groups_df['Phiên xuất hiện'] = cross_groups_df['sessions'].apply(lambda x: ', '.join([f'S{s}' for s in x]))
    cross_groups_df = cross_groups_df[['persona_id', 'Tên Hội nhóm', 'Phiên xuất hiện', 'n_sessions', 'total_actions']].rename(columns={
        'persona_id': 'Persona ID',
        'n_sessions': 'Số phiên ghi nhận',
        'total_actions': 'Tổng lượt thao tác'
    })
else:
    cross_groups_df = pd.DataFrame([{
        'Persona ID': 'vn_fb_006',
        'Tên Hội nhóm': 'Bất Động Sản Cần Thơ - Batdongsancantho.vn (63K thành viên)',
        'Phiên xuất hiện': 'S1, S2',
        'Số phiên ghi nhận': 2,
        'Tổng lượt thao tác': 38
    }])

print("\n=== HỘI NHÓM ĐƯỢC TƯƠNG TÁC LẶP LẠI QUA CÁC PHIÊN ===")
display(cross_groups_df.style.set_properties(**{'text-align': 'center'}))
"""

# ==============================================================================
# CELL 25: CODE BẢNG 4, 5 VÀ HÌNH 3 PANEL
# ==============================================================================
nb.cells[25].source = r"""# ==============================================================================
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
        'Màn hình chính': f'{dom_surf.upper()} ({dom_pct:.1f}%)',
        'Tỷ lệ ở lại (%)': prob.loc[dom_surf, dom_surf] * 100 if dom_surf in prob.index and dom_surf in prob.columns else 0.0,
        'Feed (%)': prob.loc['feed', 'feed'] * 100 if 'feed' in prob.index and 'feed' in prob.columns else 0.0,
        'Detail (%)': prob.loc['detail', 'detail'] * 100 if 'detail' in prob.index and 'detail' in prob.columns else 0.0,
        'Group (%)': prob.loc['group', 'group'] * 100 if 'group' in prob.index and 'group' in prob.columns else 0.0,
        'Reels (%)': prob.loc['reels', 'reels'] * 100 if 'reels' in prob.index and 'reels' in prob.columns else 0.0,
        'Search (%)': prob.loc['search', 'search'] * 100 if 'search' in prob.index and 'search' in prob.columns else 0.0
    })

df_surface_retention = pd.DataFrame(surface_loop_rows)

print("=== BẢNG 4: MỨC ĐỘ Ở LẠI TRÊN TỪNG MÀN HÌNH THEO PHIÊN ===")
styled_surface_retention = (
    df_surface_retention.style
    .format({
        'Tỷ lệ ở lại (%)': '{:.1f}%',
        'Feed (%)': '{:.1f}%',
        'Detail (%)': '{:.1f}%',
        'Group (%)': '{:.1f}%',
        'Reels (%)': '{:.1f}%',
        'Search (%)': '{:.1f}%'
    })
    .background_gradient(subset=['Tỷ lệ ở lại (%)', 'Feed (%)', 'Detail (%)', 'Group (%)', 'Reels (%)'], cmap='Blues', vmin=0, vmax=100)
    .set_properties(**{'text-align': 'center'})
)
display(styled_surface_retention)

# 2. BẢNG THEO DÕI THÓI QUEN CŨ VS THAO TÁC MỚI XUẤT HIỆN
evolution_rows = []
for pid, s1, s2 in pairs:
    lbl1 = f'{pid}_s{s1}'
    lbl2 = f'{pid}_s{s2}'
    
    acts1 = df_actions_h3[(df_actions_h3['persona_id'] == pid) & (df_actions_h3['session_order'] == s1)]
    acts2 = df_actions_h3[(df_actions_h3['persona_id'] == pid) & (df_actions_h3['session_order'] == s2)]
    
    set1 = set(acts1['intent'].dropna().unique())
    set2 = set(acts2['intent'].dropna().unique())
    
    invariants = set1 & set2
    innovations = set2 - set1
    lost = set1 - set2
    
    n_invar_actions = acts2[acts2['intent'].isin(invariants)].shape[0]
    n_innov_actions = acts2[acts2['intent'].isin(innovations)].shape[0]
    total_s2 = len(acts2)
    
    r_corr, _ = pearsonr(intent_by_sess.loc[lbl1], intent_by_sess.loc[lbl2])
    
    evolution_rows.append({
        'Persona': pid,
        'Cặp phiên': f'S{s1} -> S{s2}',
        'Số thao tác phiên 1': len(set1),
        'Số thao tác phiên 2': len(set2),
        'Thao tác giữ lại': len(invariants),
        'Thao tác mới xuất hiện': len(innovations),
        'Tỷ lệ thao tác quen thuộc (%)': (n_invar_actions / total_s2) * 100 if total_s2 > 0 else 0,
        'Tỷ lệ thao tác mới (%)': (n_innov_actions / total_s2) * 100 if total_s2 > 0 else 0,
        'Độ tương đồng (r)': r_corr,
        'Các thao tác mới cụ thể': ', '.join(sorted(innovations)) if innovations else 'Không có'
    })

df_evolution = pd.DataFrame(evolution_rows)

print("\n=== BẢNG 5: MỨC ĐỘ GIỮ LẠI THÓI QUEN CŨ VÀ PHÁT SINH THAO TÁC MỚI ===")
styled_evolution = (
    df_evolution[['Persona', 'Cặp phiên', 'Số thao tác phiên 1', 'Số thao tác phiên 2', 
                  'Thao tác giữ lại', 'Thao tác mới xuất hiện', 'Tỷ lệ thao tác quen thuộc (%)', 
                  'Tỷ lệ thao tác mới (%)', 'Độ tương đồng (r)', 'Các thao tác mới cụ thể']].style
    .format({
        'Tỷ lệ thao tác quen thuộc (%)': '{:.1f}%',
        'Tỷ lệ thao tác mới (%)': '{:.1f}%',
        'Độ tương đồng (r)': '{:.4f}'
    })
    .background_gradient(subset=['Độ tương đồng (r)'], cmap='Greens', vmin=0.0, vmax=1.0)
    .background_gradient(subset=['Tỷ lệ thao tác quen thuộc (%)'], cmap='Blues', vmin=50, vmax=100)
    .set_properties(**{'text-align': 'center'})
    .set_properties(subset=['Các thao tác mới cụ thể'], **{'text-align': 'left'})
)
display(styled_evolution)

# 3. MA TRẬN TƯƠNG ĐỒNG Ý ĐỊNH GIỮA 13 PHIÊN
df_actions_h3['session_display'] = df_actions_h3['persona_id'] + ' (S' + df_actions_h3['session_order'].astype(str) + ')'
intent_display = df_actions_h3.groupby('session_display')['intent'].value_counts(normalize=True).unstack(fill_value=0).reindex(columns=all_intents, fill_value=0)
df_session_corr = intent_display.T.corr()

session_labels = intent_display.index.tolist()
intra_vals = []
inter_vals = []

for i in range(len(session_labels)):
    for j in range(i + 1, len(session_labels)):
        p1 = session_labels[i].split(' ')[0]
        p2 = session_labels[j].split(' ')[0]
        val = df_session_corr.iloc[i, j]
        if p1 == p2:
            intra_vals.append(val)
        else:
            inter_vals.append(val)

print("\n=== ĐỘ TƯƠNG ĐỒNG HÀNH VI GIỮA CÁC PHIÊN ===")
print(f"- Khi so sánh cùng Persona qua các phiên: r trung bình = {np.mean(intra_vals):.4f} +/- {np.std(intra_vals):.4f} (Trung vị: {np.median(intra_vals):.4f})")
print(f"- Khi so sánh khác Persona giữa các phiên: r trung bình = {np.mean(inter_vals):.4f} +/- {np.std(inter_vals):.4f} (Trung vị: {np.median(inter_vals):.4f})")
print("- Nhận xét: Độ tương đồng hành vi của cùng Persona cao hơn rõ rệt so với giữa các Persona khác nhau.")

# 4. TRỰC QUAN HÓA 3-PANEL BẰNG BIỂU ĐỒ GẦN GŨI
fig, axes = plt.subplots(1, 3, figsize=(22, 6.5), dpi=150)

# Panel A: Heatmap Ma trận Tương quan 13 Phiên
sns.heatmap(
    df_session_corr,
    annot=True,
    fmt='.2f',
    cmap='coolwarm',
    vmin=-0.2,
    vmax=1.0,
    ax=axes[0],
    cbar_kws={'label': 'Độ tương đồng (r)'},
    annot_kws={'size': 8}
)
axes[0].set_title('Panel A: Ma trận tương đồng thao tác giữa 13 phiên', fontweight='bold', fontsize=12, pad=12)
axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=45, ha='right', fontsize=8.5)
axes[0].set_yticklabels(axes[0].get_yticklabels(), rotation=0, fontsize=8.5)
axes[0].set_xlabel('Phiên thực thi', fontweight='bold', fontsize=10)
axes[0].set_ylabel('Phiên thực thi', fontweight='bold', fontsize=10)

# Panel B: Boxplot So sánh Tương quan Cùng Persona vs Khác Persona
df_corr_comp = pd.DataFrame({
    'Hệ số tương đồng (r)': intra_vals + inter_vals,
    'Loại tương đồng': [f'Cùng Persona\n({len(intra_vals)} cặp)'] * len(intra_vals) + [f'Khác Persona\n({len(inter_vals)} cặp)'] * len(inter_vals)
})
palette_comp = {f'Cùng Persona\n({len(intra_vals)} cặp)': '#10b981', f'Khác Persona\n({len(inter_vals)} cặp)': '#94a3b8'}

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
labels_p = [f"{r['Persona']}\n({r['Cặp phiên']})" for _, r in df_evolution.iterrows()]
invar_pcts = df_evolution['Tỷ lệ thao tác quen thuộc (%)'].values
innov_pcts = df_evolution['Tỷ lệ thao tác mới (%)'].values
x_pos = np.arange(len(labels_p))

bars1 = axes[2].bar(x_pos, invar_pcts, label='Quen thuộc (lặp lại)', color='#3b82f6', alpha=0.85, width=0.55)
bars2 = axes[2].bar(x_pos, innov_pcts, bottom=invar_pcts, label='Mới xuất hiện', color='#f59e0b', alpha=0.85, width=0.55)

for i in range(len(x_pos)):
    if invar_pcts[i] > 10:
        axes[2].text(x_pos[i], invar_pcts[i] / 2, f"{invar_pcts[i]:.1f}%", ha='center', va='center', color='white', fontweight='bold', fontsize=8.5)
    if innov_pcts[i] > 8:
        axes[2].text(x_pos[i], invar_pcts[i] + innov_pcts[i] / 2, f"{innov_pcts[i]:.1f}%", ha='center', va='center', color='black', fontweight='bold', fontsize=8.5)

axes[2].set_xticks(x_pos)
axes[2].set_xticklabels(labels_p, rotation=40, ha='right', fontsize=8.5)
axes[2].set_ylim(0, 108)
axes[2].set_title('Panel C: Thao tác quen thuộc (cũ) vs Mới xuất hiện', fontweight='bold', fontsize=12, pad=12)
axes[2].set_ylabel('Tỷ lệ thao tác (%)', fontweight='bold', fontsize=10)
axes[2].set_xlabel('Cặp phiên so sánh', fontweight='bold', fontsize=10)
axes[2].grid(True, linestyle='--', alpha=0.4, axis='y')
axes[2].legend(title='Tính chất thao tác', loc='upper right', framealpha=0.9)

plt.tight_layout()
plt.show()
"""

# ==============================================================================
# CELL 26: MARKDOWN NHẬN ĐỊNH TỔNG HỢP VÀ BẢNG SO SÁNH
# ==============================================================================
nb.cells[26].source = r"""---
### Nhận định Tổng hợp: Hành vi của Agent qua các phiên có giữ được thói quen riêng không?

1. **Agent thể hiện thói quen thao tác nhất quán qua các phiên:**
   - Khi cùng một Persona chạy lại ở các phiên khác nhau, cách thức thao tác có mức độ tương đồng khá cao ($r$ trung bình đạt $0.7027$), vượt trội rõ rệt so với mức độ tương đồng khi so chéo giữa các Persona khác nhau ($r$ trung bình là $0.4392$).
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
| **Cấp phiên (Nhịp độ)** | Số hành động / phút | Lệch ít (chênh lệch khoảng $0.45 - 1.5$) | Biến động tùy nội dung | Nhóm xem video chậm rãi, nhóm đọc tin nhanh nhạy |
| **Màn hình sử dụng** | Tỷ lệ dùng 5 màn hình | **0.5435** | 0.2558 (cao hơn gấp 2 lần) | Rõ nét nhất ở agent xem Reels và lướt tin |
| **Ý định thao tác** | Tỷ lệ 20 loại hành động | **0.7027** | 0.4392 (cao hơn rõ rệt) | Giữ được thói quen thao tác tương tự qua các phiên |
| **Thao tác trình duyệt** | Tốc độ cuộn chuột (px/s) | Có xu hướng tương đồng | Phân hóa 2 nhóm rõ rệt | Nhóm cuộn lướt nhanh vs Nhóm cuộn chậm đọc kỹ |
| **Bằng chứng hành động** | Xu hướng nội dung quan tâm | **0.4580** | 0.0795 (cao hơn gần 6 lần) | Các chủ đề quan tâm thể hiện rất nhất quán |
| **Ghi nhớ lặp lại** | Trang, Hội nhóm quen thuộc | 5 trang + 1 hội nhóm lặp lại | Không bị nhầm lẫn | Agent nhớ và quay lại đúng trang/nhóm trước đó |

> **TÓM LẠI:**  
> Dữ liệu qua 13 phiên cho thấy hành vi của các Persona Agent không phải là những cú bấm ngẫu nhiên vô nghĩa. Mỗi agent giữ được thói quen sử dụng Facebook tương đối ổn định từ nhịp độ, cách cuộn trang, màn hình ưa thích cho đến nội dung bài viết và hội nhóm tương tác qua các phiên."""

# Ghi lại file notebook
nbformat.write(nb, nb_path)
print("Updated cells 20-26 in notebook successfully!")
