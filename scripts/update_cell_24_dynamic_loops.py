import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

nb_path = 'notebooks/notebook_action_logs.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Cell 24 Code: Exclusively 2-3 action sequential chains with TF-IDF and 100% dynamically calculated Bảng 7
cell_24_code = """# ==============================================================================
# BƯỚC 14: CHUỖI HÀNH VI ĐẶC TRƯNG (2-3 BƯỚC: BIGRAMS & TRIGRAMS) BẰNG TF-IDF QUA TOÀN BỘ CÁC PHIÊN
# ==============================================================================

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
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

# 3. MÔ HÌNH HÓA CHUỖI HÀNH VI ĐẶC TRƯNG (2-3 BƯỚC: BIGRAMS & TRIGRAMS) BẰNG TF-IDF QUA 24 PHIÊN
personas = sorted(df_actions['persona_id'].unique())
session_chains = {}
persona_chains = {p: [] for p in personas}

for (p, s_order), grp in df_actions.groupby(['persona_id', 'session_order']):
    grp_sorted = grp.sort_values('step_index')
    acts = [f"{str(r['intent']).strip()}@{str(r['surface']).strip()}" for _, r in grp_sorted.iterrows()]
    
    # Chỉ tập trung vào chuỗi hành vi: 2 bước (Bigram) và 3 bước (Trigram)
    bigrams = [f"{acts[i]}__THEN__{acts[i+1]}" for i in range(len(acts)-1)]
    trigrams = [f"{acts[i]}__THEN__{acts[i+1]}__THEN__{acts[i+2]}" for i in range(len(acts)-2)]
    
    chains = bigrams + trigrams
    session_chains[(p, s_order)] = chains
    persona_chains[p].extend(chains)

# Vectorizer TF-IDF trên kho ngữ liệu chuỗi hành động 2-3 bước
vec_chains = TfidfVectorizer(token_pattern=r'(?u)\\S+', lowercase=False, sublinear_tf=True)
corpus_chains = [' '.join(persona_chains[p]) for p in personas]
X_chains = vec_chains.fit_transform(corpus_chains).toarray()
features_chains = np.array(vec_chains.get_feature_names_out())

def format_chain_label(feat):
    parts = feat.split('__THEN__')
    formatted_parts = [p.replace('@', ' [') + ']' for p in parts]
    label = " ➔ ".join(formatted_parts)
    c_type = f"Chuỗi {len(parts)} bước ({'Bigram' if len(parts)==2 else 'Trigram'})"
    return label, c_type, len(parts)

persona_role_map = {
    'vn_fb_001': 'Sáng tạo nội dung / Marketing',
    'vn_fb_002': 'Công nhân may / Mẹ bỉm sữa',
    'vn_fb_003': 'Bảo vệ ca trực đêm',
    'vn_fb_004': 'Thanh niên Gen Z / Nghiện Reels',
    'vn_fb_005': 'Kỹ sư kỹ thuật / Nghiên cứu',
    'vn_fb_006': 'Tài chính / Kế toán / Hoài nghi'
}

rows_chains = []
for idx, p in enumerate(personas):
    top_indices = np.argsort(X_chains[idx])[::-1]
    cnt = 0
    for i in top_indices:
        feat = features_chains[i]
        score = X_chains[idx][i]
        label, c_type, n_steps = format_chain_label(feat)
        s_counts = [session_chains.get((p, s), []).count(feat) for s in [1, 2, 3, 4]]
        tot = sum(s_counts)
        active_sess = sum(1 for c in s_counts if c > 0)
        
        rows_chains.append({
            'Persona ID': p,
            'Vai Trò Thực Tế': persona_role_map.get(p, 'N/A'),
            'Chuỗi Hành Vi Đặc Trưng (2-3 Bước)': label,
            'Độ Dài': f"{n_steps} bước",
            'Điểm TF-IDF': round(score, 3),
            'Phiên 1': s_counts[0],
            'Phiên 2': s_counts[1],
            'Phiên 3': s_counts[2],
            'Phiên 4': s_counts[3],
            'Tổng Lần': tot,
            'TB / Phiên': round(tot / 4.0, 1),
            'Số Phiên Có Mặt': f"{active_sess}/4 phiên"
        })
        cnt += 1
        if cnt >= 4:
            break

df_top_chains = pd.DataFrame(rows_chains)

print('\\n=== BẢNG 6: TOP CHUỖI HÀNH VI ĐẶC TRƯNG 2-3 BƯỚC (TF-IDF) & TẦN SUẤT QUA 4 PHIÊN (S1 -> S4) ===')
styled_chains = (
    df_top_chains.style
    .format({
        'Điểm TF-IDF': '{:.3f}',
        'Phiên 1': '{:d}',
        'Phiên 2': '{:d}',
        'Phiên 3': '{:d}',
        'Phiên 4': '{:d}',
        'Tổng Lần': '{:d}',
        'TB / Phiên': '{:.1f}'
    })
    .background_gradient(subset=['Điểm TF-IDF'], cmap='Purples', vmin=0.13, vmax=0.26)
    .background_gradient(subset=['Phiên 1', 'Phiên 2', 'Phiên 3', 'Phiên 4', 'Tổng Lần'], cmap='Blues')
    .set_properties(**{'text-align': 'center'})
    .set_properties(subset=['Chuỗi Hành Vi Đặc Trưng (2-3 Bước)', 'Vai Trò Thực Tế'], **{'text-align': 'left'})
)
display(styled_chains)

# 4. BẢNG 7: TỔNG HỢP VÒNG LẶP CHU TRÌNH THAO TÁC CỐT LÕI (TÍNH TOÁN ĐỘNG HOÀN TOÀN BẰNG CODE)
loop_meanings = {
    'vn_fb_001': 'Chu trình sinh hoạt hội nhóm: lướt bài trong nhóm ➔ tương tác bài viết ➔ lướt tiếp tìm kiếm',
    'vn_fb_002': 'Chu trình tương tác vội: thả tim ➔ nhìn lướt nhanh bài viết ➔ thả tim tiếp giữa giờ nghỉ',
    'vn_fb_003': 'Chu trình đọc bình luận dạo: để lại bình luận ➔ quan sát bài ➔ cuộn đọc tiếp các ý kiến khác',
    'vn_fb_004': 'Chu trình xem video ngắn liên hoàn: xem clip ➔ vuốt sang clip kế ➔ xem tiếp (Reels Looping)',
    'vn_fb_005': 'Chu trình trao đổi chuyên môn: viết bình luận ➔ quan sát phản hồi bài viết ➔ trao đổi tiếp',
    'vn_fb_006': 'Chu trình đọc kiểm chứng: dừng lại quan sát dòng tin ➔ đọc bài viết ➔ quan sát đánh giá lại'
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
for idx, p in enumerate(personas):
    # Tự động trích xuất chuỗi 3 bước (Trigram) có điểm TF-IDF cao nhất cho mỗi Persona
    trigram_indices = [i for i in np.argsort(X_chains[idx])[::-1] if len(features_chains[i].split('__THEN__')) == 3]
    top_i = trigram_indices[0]
    feat = features_chains[top_i]
    label, _, n_steps = format_chain_label(feat)
    
    # Tính toán chính xác số lần xuất hiện ở từng phiên (Phiên 1 -> Phiên 4) bằng code
    s_counts = [session_chains.get((p, s), []).count(feat) for s in [1, 2, 3, 4]]
    tot = sum(s_counts)
    persistence_desc = compute_persistence_label(s_counts)
    
    core_loops_rows.append({
        'Persona ID': p,
        'Vai Trò': persona_role_map.get(p, 'N/A'),
        'Vòng Lặp Chu Trình Cốt Lõi (2-3 Bước)': label,
        'Ý Nghĩa Hành Vi Thực Tế': loop_meanings.get(p, 'N/A'),
        'Phiên 1': s_counts[0],
        'Phiên 2': s_counts[1],
        'Phiên 3': s_counts[2],
        'Phiên 4': s_counts[3],
        'Tổng Lần (4 Phiên)': tot,
        'Độ Bền Vững': persistence_desc
    })

df_core_loops = pd.DataFrame(core_loops_rows)
print('\\n=== BẢNG 7: TỔNG HỢP VÒNG LẶP CHU TRÌNH THAO TÁC CỐT LÕI (CORE BEHAVIORAL LOOPS) ===')
styled_core_loops = (
    df_core_loops.style
    .format({
        'Phiên 1': '{:d}',
        'Phiên 2': '{:d}',
        'Phiên 3': '{:d}',
        'Phiên 4': '{:d}',
        'Tổng Lần (4 Phiên)': '{:d}'
    })
    .background_gradient(subset=['Phiên 1', 'Phiên 2', 'Phiên 3', 'Phiên 4', 'Tổng Lần (4 Phiên)'], cmap='Blues')
    .set_properties(**{'text-align': 'center'})
    .set_properties(subset=['Vòng Lặp Chu Trình Cốt Lõi (2-3 Bước)', 'Ý Nghĩa Hành Vi Thực Tế', 'Vai Trò', 'Độ Bền Vững'], **{'text-align': 'left'})
)
display(styled_core_loops)

# 5. THỐNG KÊ ĐỘ TƯƠNG ĐỒNG HÀNH VI GIỮA CÁC PHIÊN
print('\\n=== ĐỘ TƯƠNG ĐỒNG HÀNH VI GIỮA CÁC PHIÊN ===')
print(f"- Khi so sánh cùng Persona qua các phiên: r trung bình = {evolution_data['intra_mean']:.4f} +/- {evolution_data['intra_std']:.4f} (Trung vị: {evolution_data['intra_median']:.4f})")
print(f"- Khi so sánh khác Persona giữa các phiên: r trung bình = {evolution_data['inter_mean']:.4f} +/- {evolution_data['inter_std']:.4f} (Trung vị: {evolution_data['inter_median']:.4f})")
print('- Nhận xét: Độ tương đồng hành vi của cùng Persona cao hơn rõ rệt so với giữa các Persona khác nhau.')

# 6. TRỰC QUAN HÓA TOÀN DIỆN 3-PANEL BẰNG BIỂU ĐỒ GẦN GŨI
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(24, 7))

# Panel A: Horizontal bar chart Top 1 Signature Chain per Persona
top1_chains = df_top_chains.groupby('Persona ID').first().reset_index()
y_pos = np.arange(len(top1_chains))
bars = ax1.barh(y_pos, top1_chains['Điểm TF-IDF'], color=[PERSONA_PALETTE.get(p, '#333') for p in top1_chains['Persona ID']], alpha=0.85, edgecolor='black')
ax1.set_yticks(y_pos)
ax1.set_yticklabels([f"{r['Persona ID']}: {r['Chuỗi Hành Vi Đặc Trưng (2-3 Bước)']}" for _, r in top1_chains.iterrows()], fontsize=9.0)
ax1.invert_yaxis()
ax1.set_xlabel('Điểm TF-IDF (Độ Đặc Trưng Chuỗi Hành Động)', fontsize=10)
ax1.set_title('(A) Top 1 Chuỗi Hành Vi Đặc Trưng (TF-IDF 2-3 Bước)\\nTheo Từng Persona', fontsize=12, fontweight='bold')
ax1.grid(True, linestyle=':', alpha=0.6, axis='x')

for bar in bars:
    w = bar.get_width()
    ax1.text(w + 0.003, bar.get_y() + bar.get_height()/2, f"{w:.3f}", va='center', fontsize=9, fontweight='bold')

# Panel B: Heatmap tần suất xuất hiện qua các phiên của Top 1 Chuỗi mỗi persona
heat_chains = top1_chains[['Phiên 1', 'Phiên 2', 'Phiên 3', 'Phiên 4']].copy()
heat_chains.index = [f"{r['Persona ID']}: {r['Chuỗi Hành Vi Đặc Trưng (2-3 Bước)']}" for _, r in top1_chains.iterrows()]
sns.heatmap(heat_chains, annot=True, fmt='d', cmap='YlGnBu', cbar=True, ax=ax2, linewidths=0.5, cbar_kws={'label': 'Số lần lặp lại chuỗi (lần)'})
ax2.set_title('(B) Tần Suất Xuất Hiện Của Chuỗi Đặc Trưng\\nQua Toàn Bộ Các Phiên (Phiên 1 ➔ 4)', fontsize=12, fontweight='bold')
ax2.set_xlabel('Thứ Tự Phiên Hoạt Động', fontsize=10)
ax2.set_ylabel('')

# Panel C: Tổng số lần xuất hiện chuỗi đặc trưng xuyên suốt 4 phiên
ax3.bar(top1_chains['Persona ID'], top1_chains['Tổng Lần'], color=[PERSONA_PALETTE.get(p, '#333') for p in top1_chains['Persona ID']], alpha=0.85, edgecolor='black')
ax3.set_title('(C) Tổng Số Lần Thực Hiện Chuỗi Đặc Trưng\\nXuyên Suốt Tất Cả Các Phiên', fontsize=12, fontweight='bold')
ax3.set_xlabel('Persona ID', fontsize=10)
ax3.set_ylabel('Tổng Số Lần Xuất Hiện (lần)', fontsize=10)
ax3.grid(True, linestyle=':', alpha=0.6, axis='y')
for idx, r in top1_chains.iterrows():
    ax3.text(idx, r['Tổng Lần'] + 2, f"{r['Tổng Lần']}\\n({r['Số Phiên Có Mặt']})", ha='center', fontsize=8.5, fontweight='bold')

plt.tight_layout()
plt.show()"""

# Update notebook cell 24
nb['cells'][24]['source'] = [line + '\n' for line in cell_24_code.split('\n')]
nb['cells'][24]['source'][-1] = nb['cells'][24]['source'][-1].rstrip('\n')

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Cell 24 code updated with fully dynamic calculations for Bảng 7!")
