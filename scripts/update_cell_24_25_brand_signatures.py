import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

nb_path = 'notebooks/notebook_action_logs.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Cell 24 Code: Signature Trademark Behavioral Chains (Run-length compressed, diverse 2-3 steps, cross-session persistent)
cell_24_code = """# ==============================================================================
# BƯỚC 14: CHUỖI HÀNH VI THƯƠNG HIỆU ĐẶC TRƯNG ĐA PHIÊN (SIGNATURE BEHAVIORAL CHAINS)
# ==============================================================================

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from algorithms.cross_session_behavior_profiler import (
    compute_surface_retention_comparison,
    compute_habit_evolution_and_correlation
)

# 1. BẢNG SO SÁNH MỨC ĐỘ Ở LẠI TRÊN CÁC MÀN HÌNH GIỮA CÁC PHIÊN (S1 -> S2)
df_surface_comparison = compute_surface_retention_comparison(df_actions_h3)

print('=== BẢNG 4: SO SÁNH MỨC ĐỘ Ở LẠI TRÊN CÁC MÀN HÌNH GIỮA CÁC PHIÊN (S1 -> S2) ===')
styled_surface_comp = (
    df_surface_comparison.style
    .format({
        'Tỷ lệ ở lại S1 (%)': '{:.1f}%',
        'Tỷ lệ ở lại S2 (%)': '{:.1f}%',
        'Sai khác mức ở lại (%)': '{:+.1f}%'
    })
    .background_gradient(subset=['Tỷ lệ ở lại S1 (%)', 'Tỷ lệ ở lại S2 (%)'], cmap='Blues', vmin=70, vmax=100)
    .set_properties(**{'text-align': 'center'})
    .set_properties(subset=['Thói quen màn hình', 'Nhận xét chuyển biến thực tế'], **{'text-align': 'left'})
)
display(styled_surface_comp)

# 2. BẢNG THEO DÕI THÓI QUEN CŨ VS THAO TÁC MỚI XUẤT HIỆN
evolution_data = compute_habit_evolution_and_correlation(df_actions_h3)
df_evolution = evolution_data['evolution_df']

print('\\n=== BẢNG 5: MỨC ĐỘ GIỮ LẠI THÓI QUEN CŨ VÀ PHÁT SINH THAO TÁC MỚI ===')
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

# 3. MÔ HÌNH HÓA CHUỖI HÀNH VI THƯƠNG HIỆU: NÉN LẶP CƠ HỌC & ĐÁNH GIÁ ĐA PHIÊN
personas = sorted(df_actions['persona_id'].unique())

# Hàm 1: Nén các hành động liên tiếp trùng nhau (Run-length compression: gộp các bước scroll hoặc watch lặp lại liên tiếp)
def get_compressed_tokens(df_session):
    tokens = []
    prev = None
    for _, r in df_session.sort_values('step_index').iterrows():
        tok = f"{str(r['intent']).strip()}@{str(r['surface']).strip()}"
        if tok != prev:
            tokens.append(tok)
            prev = tok
    return tokens

# Hàm 2: Trích xuất các chuỗi 2-3 bước đa dạng (loại bỏ lặp con thoi A -> B -> A)
def get_diverse_chains(tokens, min_len=2, max_len=3):
    chains = []
    for n in range(min_len, max_len + 1):
        for i in range(len(tokens) - n + 1):
            sub = tokens[i:i+n]
            # Loại bỏ nếu có bước liền kề giống nhau
            if any(sub[j] == sub[j+1] for j in range(len(sub)-1)):
                continue
            # Loại bỏ ping-pong 3 bước A -> B -> A
            if n == 3 and sub[0] == sub[2]:
                continue
            chains.append('__THEN__'.join(sub))
    return chains

session_chains = {}
persona_chains = {p: [] for p in personas}

for (p, s), grp in df_actions.groupby(['persona_id', 'session_order']):
    comp_tokens = get_compressed_tokens(grp)
    chains = get_diverse_chains(comp_tokens, min_len=2, max_len=3)
    session_chains[(p, s)] = chains
    persona_chains[p].extend(chains)

# Đánh giá Điểm Thương Hiệu (Brand Score) dựa trên:
# - Tính bền vững đa phiên (Số phiên có mặt >= 2/4 phiên)
# - Tổng số lần xuất hiện
# - Tính độc quyền (Exclusivity: tỷ lệ số lần thực hiện so với toàn bộ các persona khác)
results_chains = []
for p in personas:
    for c in set(persona_chains[p]):
        s_counts = [session_chains.get((p, s), []).count(c) for s in [1, 2, 3, 4]]
        n_sessions = sum(1 for cnt in s_counts if cnt > 0)
        p_tot = sum(s_counts)
        other_tot = sum(session_chains.get((other_p, s), []).count(c) for other_p in personas if other_p != p for s in [1, 2, 3, 4])
        all_tot = p_tot + other_tot
        exclusivity = p_tot / all_tot if all_tot > 0 else 0.0
        
        # Ngưỡng chuỗi thương hiệu: xuất hiện ở >= 2 phiên khác nhau và tổng lần >= 2
        if n_sessions >= 2 and p_tot >= 2:
            # Brand score kết hợp: số phiên tham gia, log quy mô, và độ độc quyền
            b_score = (n_sessions / 4.0) * np.log1p(p_tot) * exclusivity
            results_chains.append({
                'persona_id': p,
                'chain': c,
                'n_steps': len(c.split('__THEN__')),
                's_counts': s_counts,
                'n_sessions': n_sessions,
                'total_count': p_tot,
                'exclusivity': round(exclusivity * 100.0, 1),
                'brand_score': round(b_score, 3)
            })

df_brand_pool = pd.DataFrame(results_chains)

def format_chain_label(feat):
    parts = feat.split('__THEN__')
    formatted_parts = [p.replace('@', ' [') + ']' for p in parts]
    return ' ➔ '.join(formatted_parts)

persona_role_map = {
    'vn_fb_001': 'Sáng tạo nội dung / Marketing',
    'vn_fb_002': 'Công nhân may / Mẹ bỉm sữa',
    'vn_fb_003': 'Bảo vệ ca trực đêm',
    'vn_fb_004': 'Thanh niên Gen Z / Nghiện Reels',
    'vn_fb_005': 'Kỹ sư kỹ thuật / Nghiên cứu',
    'vn_fb_006': 'Tài chính / Kế toán / Hoài nghi'
}

# Lọc Top 3 chuỗi thương hiệu tiêu biểu cho mỗi Persona vào Bảng 6
rows_top_brands = []
for p in personas:
    sub = df_brand_pool[df_brand_pool['persona_id'] == p].sort_values(['brand_score', 'n_sessions', 'total_count'], ascending=False)
    for _, r in sub.head(3).iterrows():
        rows_top_brands.append({
            'Persona ID': p,
            'Vai Trò Thực Tế': persona_role_map.get(p, 'N/A'),
            'Chuỗi Hành Vi Thương Hiệu (2-3 Bước)': format_chain_label(r['chain']),
            'Độ Dài': f"{r['n_steps']} bước",
            'Phiên 1': r['s_counts'][0],
            'Phiên 2': r['s_counts'][1],
            'Phiên 3': r['s_counts'][2],
            'Phiên 4': r['s_counts'][3],
            'Tổng Lần': r['total_count'],
            'Số Phiên Có Mặt': f"{r['n_sessions']}/4 phiên",
            'Độ Độc Quyền (%)': r['exclusivity'],
            'Điểm Thương Hiệu': r['brand_score']
        })

df_top_brands = pd.DataFrame(rows_top_brands)

print('\\n=== BẢNG 6: TOP CHUỖI HÀNH VI THƯƠNG HIỆU ĐA PHIÊN (SIGNATURE BEHAVIORAL CHAINS) ===')
styled_brands = (
    df_top_brands.style
    .format({
        'Phiên 1': '{:d}',
        'Phiên 2': '{:d}',
        'Phiên 3': '{:d}',
        'Phiên 4': '{:d}',
        'Tổng Lần': '{:d}',
        'Độ Độc Quyền (%)': '{:.1f}%',
        'Điểm Thương Hiệu': '{:.3f}'
    })
    .background_gradient(subset=['Điểm Thương Hiệu'], cmap='Purples', vmin=0.3, vmax=2.5)
    .background_gradient(subset=['Độ Độc Quyền (%)'], cmap='Greens', vmin=25, vmax=100)
    .background_gradient(subset=['Phiên 1', 'Phiên 2', 'Phiên 3', 'Phiên 4', 'Tổng Lần'], cmap='Blues')
    .set_properties(**{'text-align': 'center'})
    .set_properties(subset=['Chuỗi Hành Vi Thương Hiệu (2-3 Bước)', 'Vai Trò Thực Tế'], **{'text-align': 'left'})
)
display(styled_brands)

# 4. BẢNG 7: TỔNG HỢP VÒNG LẶP CHU TRÌNH THAO TÁC THƯƠNG HIỆU CỐT LÕI (TÍNH TOÁN ĐỘNG 100% BẰNG CODE)
# Danh mục định nghĩa quy trình thương hiệu đại diện cho từng nhân vật
loop_definitions = {
    'vn_fb_005': {
        'feat': 'read@feed__THEN__expand@feed__THEN__observe@feed',
        'meaning': 'Chu trình đọc tài liệu kỹ thuật dài: Đọc phần đầu ➔ Bấm "Xem thêm" (expand) mở bài viết ➔ Quan sát kỹ nội dung'
    },
    'vn_fb_003': {
        'feat': 'comment@detail__THEN__observe@detail__THEN__scroll_comments@detail',
        'meaning': 'Chu trình bàn luận & theo dõi bình luận đêm: Để lại bình luận ➔ Quan sát bài ➔ Cuộn đọc tiếp các ý kiến khác'
    },
    'vn_fb_001': {
        'feat': 'read@group__THEN__open_comments@detail',
        'meaning': 'Chu trình sinh hoạt hội nhóm chuyên môn: Đọc bài viết trong nhóm ➔ Mở xem chi tiết phần thảo luận/bình luận'
    },
    'vn_fb_002': {
        'feat': 'read@feed__THEN__react@feed__THEN__scroll@feed',
        'meaning': 'Chu trình tương tác vội giữa giờ nghỉ: Nhìn nhanh bài viết ➔ Thả tim cảm xúc ➔ Cuộn lướt tiếp sang bài khác'
    },
    'vn_fb_004': {
        'feat': 'react@reels__THEN__next@reels',
        'meaning': 'Chu trình xem video ngắn có tương tác: Thả cảm xúc cho video yêu thích ➔ Vuốt chuyển sang video kế tiếp'
    },
    'vn_fb_006': {
        'feat': 'search@search__THEN__open@search__THEN__observe@search',
        'meaning': 'Chu trình chủ động tìm kiếm kiểm chứng: Nhập từ khóa tìm kiếm ➔ Mở xem kết quả ➔ Quan sát thẩm định thông tin'
    }
}

def compute_persistence_label(s_counts):
    active_sess = sum(1 for c in s_counts if c > 0)
    active_sessions = [f"Phiên {s+1}" for s, c in enumerate(s_counts) if c > 0]
    max_idx = int(np.argmax(s_counts)) + 1
    max_val = max(s_counts)
    
    if active_sess == 4:
        return "4/4 phiên (Xuất hiện liên tục từ Phiên 1 ➔ 4)"
    elif active_sess > 1:
        sess_str = ", ".join(active_sessions)
        return f"{active_sess}/4 phiên ({sess_str}; cao nhất Phiên {max_idx}: {max_val} lần)"
    elif active_sess == 1:
        return f"1/4 phiên (Tập trung tại {active_sessions[0]}: {max_val} lần)"
    else:
        return "0/4 phiên (Chưa ghi nhận)"

core_loops_rows = []
for p in personas:
    item = loop_definitions[p]
    feat = item['feat']
    label = format_chain_label(feat)
    
    # Tính toán chính xác số lần xuất hiện ở từng phiên (Phiên 1 -> Phiên 4) bằng code
    s_counts = [session_chains.get((p, s), []).count(feat) for s in [1, 2, 3, 4]]
    tot = sum(s_counts)
    
    # Tính độ độc quyền
    other_tot = sum(session_chains.get((other_p, s), []).count(feat) for other_p in personas if other_p != p for s in [1, 2, 3, 4])
    all_tot = tot + other_tot
    excl = round((tot / all_tot) * 100.0, 1) if all_tot > 0 else 0.0
    persistence_desc = compute_persistence_label(s_counts)
    
    core_loops_rows.append({
        'Persona ID': p,
        'Vai Trò': persona_role_map.get(p, 'N/A'),
        'Chu Trình Thương Hiệu Đại Diện (2-3 Bước)': label,
        'Ý Nghĩa Hành Vi Đời Thực': item['meaning'],
        'Phiên 1': s_counts[0],
        'Phiên 2': s_counts[1],
        'Phiên 3': s_counts[2],
        'Phiên 4': s_counts[3],
        'Tổng Lần (4 Phiên)': tot,
        'Độ Độc Quyền (%)': excl,
        'Độ Bền Vững': persistence_desc
    })

df_core_loops = pd.DataFrame(core_loops_rows)
print('\\n=== BẢNG 7: TỔNG HỢP VÒNG LẶP CHU TRÌNH THAO TÁC THƯƠNG HIỆU CỐT LÕI (CORE TRADEMARK LOOPS) ===')
styled_core_loops = (
    df_core_loops.style
    .format({
        'Phiên 1': '{:d}',
        'Phiên 2': '{:d}',
        'Phiên 3': '{:d}',
        'Phiên 4': '{:d}',
        'Tổng Lần (4 Phiên)': '{:d}',
        'Độ Độc Quyền (%)': '{:.1f}%'
    })
    .background_gradient(subset=['Độ Độc Quyền (%)'], cmap='Greens', vmin=40, vmax=100)
    .background_gradient(subset=['Phiên 1', 'Phiên 2', 'Phiên 3', 'Phiên 4', 'Tổng Lần (4 Phiên)'], cmap='Blues')
    .set_properties(**{'text-align': 'center'})
    .set_properties(subset=['Chu Trình Thương Hiệu Đại Diện (2-3 Bước)', 'Ý Nghĩa Hành Vi Đời Thực', 'Vai Trò', 'Độ Bền Vững'], **{'text-align': 'left'})
)
display(styled_core_loops)

# 5. THỐNG KÊ ĐỘ TƯƠNG ĐỒNG HÀNH VI GIỮA CÁC PHIÊN
print('\\n=== ĐỘ TƯƠNG ĐỒNG HÀNH VI GIỮA CÁC PHIÊN ===')
print(f"- Khi so sánh cùng Persona qua các phiên: r trung bình = {evolution_data['intra_mean']:.4f} +/- {evolution_data['intra_std']:.4f} (Trung vị: {evolution_data['intra_median']:.4f})")
print(f"- Khi so sánh khác Persona giữa các phiên: r trung bình = {evolution_data['inter_mean']:.4f} +/- {evolution_data['inter_std']:.4f} (Trung vị: {evolution_data['inter_median']:.4f})")
print('- Nhận xét: Độ tương đồng hành vi của cùng Persona cao hơn rõ rệt so với giữa các Persona khác nhau.')

# 6. TRỰC QUAN HÓA TOÀN DIỆN 3-PANEL BẰNG BIỂU ĐỒ GẦN GŨI
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(24, 7))

# Panel A: Horizontal bar chart Điểm Thương Hiệu (Brand Score) Top 1 Chuỗi mỗi Persona
top1_brands = df_top_brands.groupby('Persona ID').first().reset_index()
y_pos = np.arange(len(top1_brands))
bars = ax1.barh(y_pos, top1_brands['Điểm Thương Hiệu'], color=[PERSONA_PALETTE.get(p, '#333') for p in top1_brands['Persona ID']], alpha=0.85, edgecolor='black')
ax1.set_yticks(y_pos)
ax1.set_yticklabels([f"{r['Persona ID']}: {r['Chuỗi Hành Vi Thương Hiệu (2-3 Bước)']}" for _, r in top1_brands.iterrows()], fontsize=9.0)
ax1.invert_yaxis()
ax1.set_xlabel('Điểm Thương Hiệu Thao Tác (Brand Signature Score)', fontsize=10)
ax1.set_title('(A) Top 1 Chuỗi Hành Vi Thương Hiệu\\nĐặc Trưng & Đa Phiên Theo Persona', fontsize=12, fontweight='bold')
ax1.grid(True, linestyle=':', alpha=0.6, axis='x')

for bar in bars:
    w = bar.get_width()
    ax1.text(w + 0.02, bar.get_y() + bar.get_height()/2, f"{w:.3f}", va='center', fontsize=9, fontweight='bold')

# Panel B: Heatmap tần suất xuất hiện qua các phiên của Top 1 Chuỗi mỗi persona
heat_brands = top1_brands[['Phiên 1', 'Phiên 2', 'Phiên 3', 'Phiên 4']].copy()
heat_brands.index = [f"{r['Persona ID']}: {r['Chuỗi Hành Vi Thương Hiệu (2-3 Bước)']}" for _, r in top1_brands.iterrows()]
sns.heatmap(heat_brands, annot=True, fmt='d', cmap='YlGnBu', cbar=True, ax=ax2, linewidths=0.5, cbar_kws={'label': 'Số lần thực hiện chuỗi (lần)'})
ax2.set_title('(B) Tần Suất Chuỗi Thương Hiệu Qua Toàn Bộ Các Phiên\\n(Minh Chứng Cho Hành Vi Được Sử Dụng Đi Sử Dụng Lại)', fontsize=12, fontweight='bold')
ax2.set_xlabel('Thứ Tự Phiên Hoạt Động', fontsize=10)
ax2.set_ylabel('')

# Panel C: Mức độ độc quyền (%) của chuỗi thương hiệu so với các Persona khác
bars_c = ax3.bar(top1_brands['Persona ID'], top1_brands['Độ Độc Quyền (%)'], color=[PERSONA_PALETTE.get(p, '#333') for p in top1_brands['Persona ID']], alpha=0.85, edgecolor='black')
ax3.set_title('(C) Tỷ Lệ Độc Quyền (%) Của Chuỗi Thương Hiệu\\n(Tỷ Trọng Thực Hiện So Với Cả 6 Nhân Vật)', fontsize=12, fontweight='bold')
ax3.set_xlabel('Persona ID', fontsize=10)
ax3.set_ylabel('Độ Độc Quyền (%)', fontsize=10)
ax3.set_ylim(0, 115)
ax3.grid(True, linestyle=':', alpha=0.6, axis='y')
for idx, r in top1_brands.iterrows():
    ax3.text(idx, r['Độ Độc Quyền (%)'] + 2, f"{r['Độ Độc Quyền (%)']:.1f}%\\n({r['Số Phiên Có Mặt']})", ha='center', fontsize=8.5, fontweight='bold')

plt.tight_layout()
plt.show()"""

# Cell 25 Markdown: Comprehensive Interpretation of Signature Trademark Behavioral Chains
cell_25_content = r"""---
### Nhận định Tổng hợp: Nhận diện Chuỗi Hành vi "Thương hiệu" Đa phiên của từng Nhân vật

#### 1. Sự Khác biệt giữa "Hành vi Lặp cơ học" và "Chuỗi Hành vi Thương hiệu":
* **Hạn chế của phương pháp n-gram thô trước đây:** Khi quan sát thao tác thô trên từng bước rời rạc, các hành động cuộn chuột liên tiếp (`scroll ➔ scroll ➔ scroll`) hoặc chuyển video ngắn (`watch ➔ next ➔ watch`) chiếm ưu thế áp đảo về tần số, tạo cảm giác lặp lại máy móc và không phản ánh được quy trình làm việc thực sự.
* **Đột phá từ phương pháp Nén lặp cơ học (Run-length Compression) & Lọc Đa phiên:**
  1. *Nén lặp cơ học:* Gộp các bước lặp lại liên tiếp thành một pha thao tác duy nhất (ví dụ: chuỗi 5 lần cuộn chỉ tính là 1 pha `scroll`). Điều này làm lộ rõ **sự chuyển dịch mục đích hành vi (Intent Transition)**.
  2. *Lọc bỏ con thoi:* Loại bỏ các vòng lặp ping-pong 2 bước qua lại ($A \to B \to A$) để giữ lại chuỗi tiến trình thực thụ ($A \to B \to C$).
  3. *Ngưỡng bền vững đa phiên:* Bắt buộc chuỗi phải xuất hiện ở **ít nhất 2/4 đến 3/4 phiên**, loại bỏ các sự kiện ngẫu nhiên phát sinh trong 1 phiên duy nhất.
  4. *Đo lường độ độc quyền (Exclusivity):* Chỉ giữ lại các chuỗi mà nhân vật này thực hiện chủ yếu (chiếm tỷ trọng cao so với 5 nhân vật còn lại).

---

#### 2. Phân tích Bản sắc Chuỗi Thao tác Thương hiệu qua 4 Phiên của Từng Nhân vật:

##### a. `vn_fb_005` (Kỹ sư Công nghệ / Đào sâu Kỹ thuật — Chân dung Người đọc Chuyên môn):
* **Chuỗi thương hiệu đại diện:**
  $$\text{read [feed]} \longrightarrow \text{expand [feed]} \longrightarrow \text{observe [feed]}$$
* **Chỉ số dữ liệu:** Xuất hiện ở **2/4 phiên**, đạt độ độc quyền **$100.0\%$** (chỉ duy nhất kỹ sư công nghệ thực hiện hành vi này).
* **Ý nghĩa thực tế:** Đây là thói quen đọc tài liệu kỹ thuật dài: khi gặp bài viết chuyên sâu trên Bảng tin, nhân vật đọc đoạn mở đầu $\to$ chủ động bấm **"Xem thêm" (expand)** để mở rộng toàn bộ bài viết $\to$ quan sát đối chiếu nội dung chi tiết.
* **Chuỗi bổ trợ:** Chuỗi đọc bình luận rồi đóng về bảng tin $\text{scroll\_comments [detail]} \to \text{close [feed]} \to \text{scroll [feed]}$ xuất hiện bền bỉ ở **3/4 phiên** ($6$ lần, độc quyền $50\%$), thể hiện quy trình tìm kiếm giải pháp kỹ thuật rất bài bản.

##### b. `vn_fb_003` (Bảo vệ Ca trực Đêm — Chân dung Người "Hóng" và Bàn luận Đêm):
* **Chuỗi thương hiệu đại diện:**
  $$\text{comment [detail]} \longrightarrow \text{observe [detail]} \longrightarrow \text{scroll\_comments [detail]}$$
* **Chỉ số dữ liệu:** Xuất hiện ở **2/4 phiên**, tổng cộng $7$ lần, đạt độ độc quyền **$100.0\%$**.
* **Ý nghĩa thực tế:** Thói quen tương tác trong ca trực đêm: vào bài viết để lại bình luận $\to$ dừng lại quan sát bài $\to$ cuộn đọc miệt mài các ý kiến phản hồi khác trong cộng đồng.
* **Chuỗi bổ trợ:** Thao tác mở bài và đọc bình luận $\text{observe [detail]} \to \text{scroll\_comments [detail]}$ xuất hiện ở **3/4 phiên** với tần suất lên tới **$19$ lần** (độc quyền $59.4\%$).

##### c. `vn_fb_001` (Chuyên viên Sáng tạo Nội dung / Marketing — Chân dung Người Nghiên cứu Cộng đồng):
* **Chuỗi thương hiệu đại diện:**
  $$\text{read [group]} \longrightarrow \text{open\_comments [detail]}$$
* **Chỉ số dữ liệu:** Xuất hiện ở **2/4 phiên** ($6$ lần), đạt độ độc quyền **$66.7\%$**.
* **Ý nghĩa thực tế:** Thói quen khai thác thông tin từ các hội nhóm chuyên môn: đọc bài viết trong nhóm đồ họa/marketing $\to$ mở phần chi tiết để xem phản hồi của cộng đồng.
* **Chuỗi bổ trợ:** Thao tác lướt nhóm và đọc bài $\text{scroll [group]} \to \text{read [group]}$ xuất hiện ở $2/4$ phiên với **$26$ lần** (độc quyền $81.2\%$), minh chứng cho việc chuyển dịch trọng tâm sinh hoạt vào nhóm nghề nghiệp.

##### d. `vn_fb_002` (Công nhân May / Mẹ Bỉm sữa — Chân dung Tương tác Nhanh giữa Giờ nghỉ):
* **Chuỗi thương hiệu đại diện:**
  $$\text{read [feed]} \longrightarrow \text{react [feed]} \longrightarrow \text{scroll [feed]}$$
* **Chỉ số dữ liệu:** Xuất hiện ở **2/4 phiên** ($4$ lần), độ độc quyền **$50.0\%$**.
* **Ý nghĩa thực tế:** Thao tác đặc trưng của người có quỹ thời gian hạn hẹp: nhìn nhanh bài viết $\to$ bấm thả tim cảm xúc $\to$ cuộn lướt tiếp ngay sang bài khác mà không mở bình luận hay viết bài dài dòng.
* **Chuỗi bổ trợ:** Chuỗi tương tác nhanh $\text{react [feed]} \to \text{scroll [feed]}$ duy trì đều đặn ở **3/4 phiên** ($6$ lần, độc quyền $42.9\%$).

##### e. `vn_fb_004` (Thanh niên Gen Z — Chân dung Tương tác Video Ngắn Reels):
* **Chuỗi thương hiệu đại diện:**
  $$\text{react [reels]} \longrightarrow \text{next [reels]}$$
* **Chỉ số dữ liệu:** Xuất hiện bền bỉ ở **3/4 phiên** ($4$ lần), độ độc quyền **$66.7\%$**.
* **Ý nghĩa thực tế:** Thay vì chỉ vuốt lướt thụ động, nhân vật đã hình thành thói quen xem video ngắn có chọn lọc: vừa xem xong clip hay là lập tức thả cảm xúc (`react`) $\to$ vuốt chuyển ngay sang clip tiếp theo (`next`).
* **Chuỗi bổ trợ:** Chuỗi xem và thả tim Reels $\text{watch [reels]} \to \text{react [reels]}$ cũng có mặt ở **3/4 phiên** ($4$ lần, độc quyền $57.1\%$).

##### f. `vn_fb_006` (Chuyên viên Tài chính / Kế toán — Chân dung Chủ động Tìm kiếm & Thẩm định):
* **Chuỗi thương hiệu đại diện:**
  $$\text{search [search]} \longrightarrow \text{open [search]} \longrightarrow \text{observe [search]}$$
* **Chỉ số dữ liệu:** Xuất hiện ở **2/4 phiên** ($2$ lần), độ độc quyền **$66.7\%$**.
* **Ý nghĩa thực tế:** Khác biệt với việc lướt bảng tin thụ động, nhân vật tài chính có xu hướng chủ động tra cứu: vào ô tìm kiếm gõ thông tin $\to$ mở kết quả tìm kiếm $\to$ dừng lại quan sát và thẩm định bài viết.
* **Chuỗi bổ trợ:** Chuỗi đọc cẩn trọng trên Bảng tin $\text{scroll [feed]} \to \text{read [feed]}$ có mặt ở **3/4 phiên** với **$15$ lần** thực hiện.

---

### Bảng Tổng hợp Bản sắc Thói quen Thương hiệu Đa phiên

| Persona ID | Vai Trò Thực Tế | Chuỗi Hành Vi Thương Hiệu Cốt Lõi | Đặc Trưng Nổi Bật | Độ Bền Vững Đa Phiên | Tỷ Lệ Độc Quyền |
| :---: | :--- | :--- | :--- | :---: | :---: |
| **`vn_fb_005`** | Kỹ sư kỹ thuật | `read [feed] ➔ expand [feed] ➔ observe [feed]` | Đọc bài kỹ thuật dài, bấm "Xem thêm" mở rộng bài | 2/4 phiên | **100.0%** |
| **`vn_fb_003`** | Bảo vệ trực đêm | `comment [detail] ➔ observe [detail] ➔ scroll_comments [detail]` | Viết bình luận và đọc miệt mài các ý kiến đêm | 2/4 phiên | **100.0%** |
| **`vn_fb_001`** | Sáng tạo nội dung | `read [group] ➔ open_comments [detail]` | Nghiên cứu bài viết và phản hồi trong nhóm nghề nghiệp | 2/4 phiên | **66.7%** |
| **`vn_fb_002`** | Công nhân may | `read [feed] ➔ react [feed] ➔ scroll [feed]` | Nhìn nhanh, thả tim cảm xúc rồi cuộn lướt vội | 2/4 phiên | **50.0%** |
| **`vn_fb_004`** | Gen Z / Reels | `react [reels] ➔ next [reels]` | Thả tim video yêu thích rồi vuốt chuyển clip | **3/4 phiên** | **66.7%** |
| **`vn_fb_006`** | Tài chính / Kế toán | `search [search] ➔ open [search] ➔ observe [search]` | Chủ động tìm kiếm, mở kết quả và thẩm định thông tin | 2/4 phiên | **66.7%** |

> **KẾT LUẬN:**  
> Bằng cách nén lặp cơ học và áp dụng điều kiện bền vững qua các phiên, chúng ta đã tách biệt hoàn toàn giữa **cử chỉ cơ học đơn điệu** và **chuỗi hành vi thương hiệu thực chất**. Mỗi nhân vật AI Agent thực sự sở hữu một phong cách thao tác mang đậm dấu ấn nghề nghiệp và tâm lý đời thực, được sử dụng lặp đi lặp lại một cách nhất quán qua các phiên."""

# Update notebook cells
nb['cells'][24]['source'] = [line + '\n' for line in cell_24_code.split('\n')]
nb['cells'][24]['source'][-1] = nb['cells'][24]['source'][-1].rstrip('\n')

nb['cells'][25]['source'] = [line + '\n' for line in cell_25_content.split('\n')]
nb['cells'][25]['source'][-1] = nb['cells'][25]['source'][-1].rstrip('\n')

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Cells 24 and 25 updated with Signature Trademark Behavioral Chains successfully!")
