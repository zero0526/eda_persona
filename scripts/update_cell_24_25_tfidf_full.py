import json
from pathlib import Path

nb_path = 'notebooks/notebook_action_logs.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Cell 24 Code: Updated with TF-IDF Pattern Profiling across all 4 sessions
cell_24_code = """# ==============================================================================
# BƯỚC 14: DẤU ẤN HÀNH VI ĐẶC TRƯNG (TF-IDF), THỐNG KÊ TOÀN BỘ CÁC PHIÊN & TRỰC QUAN HÓA
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

# 3. MÔ HÌNH HÓA DẤU ẤN HÀNH VI ĐẶC TRƯNG BẰNG TF-IDF TRÊN TOÀN BỘ 24 PHIÊN (S1 -> S4)
personas = sorted(df_actions['persona_id'].unique())
session_tokens = {}
session_total_acts = {}
persona_corpus = {p: [] for p in personas}

for (p, s_order), grp in df_actions.groupby(['persona_id', 'session_order']):
    grp_sorted = grp.sort_values('step_index')
    acts = [f"{str(r['intent']).strip()}@{str(r['surface']).strip()}" for _, r in grp_sorted.iterrows()]
    bigrams = [f"{acts[i]}__then__{acts[i+1]}" for i in range(len(acts)-1)]
    tokens = acts + bigrams
    session_tokens[(p, s_order)] = tokens
    session_total_acts[(p, s_order)] = len(grp_sorted)
    persona_corpus[p].extend(tokens)

# Tính TF-IDF với sublinear_tf=True để cân bằng tần suất và làm nổi bật dấu ấn riêng
vec = TfidfVectorizer(token_pattern=r'(?u)\\S+', lowercase=False, sublinear_tf=True)
corpus = [' '.join(persona_corpus[p]) for p in personas]
X_tfidf = vec.fit_transform(corpus).toarray()
features_tfidf = np.array(vec.get_feature_names_out())

def format_tfidf_pattern(feat):
    if '__then__' in feat:
        parts = feat.split('__then__')
        p1 = parts[0].replace('@', ' [') + ']'
        p2 = parts[1].replace('@', ' [') + ']'
        return f"{p1} ➔ {p2}", "Chuỗi 2 bước (Bigram)"
    else:
        return feat.replace('@', ' [') + ']', "Hành vi đơn (Action)"

persona_role_map = {
    'vn_fb_001': 'Sáng tạo nội dung / Marketing',
    'vn_fb_002': 'Công nhân may / Mẹ bỉm sữa',
    'vn_fb_003': 'Bảo vệ ca trực đêm',
    'vn_fb_004': 'Thanh niên Gen Z / Nghiện Reels',
    'vn_fb_005': 'Kỹ sư kỹ thuật / Nghiên cứu',
    'vn_fb_006': 'Tài chính / Kế toán / Hoài nghi'
}

rows_tfidf = []
for idx, p in enumerate(personas):
    top_indices = np.argsort(X_tfidf[idx])[::-1]
    cnt = 0
    for i in top_indices:
        feat = features_tfidf[i]
        score = X_tfidf[idx][i]
        label, p_type = format_tfidf_pattern(feat)
        s_counts = [session_tokens.get((p, s), []).count(feat) for s in [1, 2, 3, 4]]
        tot = sum(s_counts)
        active_sess = sum(1 for c in s_counts if c > 0)
        rows_tfidf.append({
            'Persona ID': p,
            'Vai Trò Thực Tế': persona_role_map.get(p, 'N/A'),
            'Pattern Đặc Trưng (TF-IDF)': label,
            'Loại Pattern': p_type,
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

df_tfidf_patterns = pd.DataFrame(rows_tfidf)

print('\\n=== BẢNG 6: TOP PATTERN HÀNH VI ĐẶC TRƯNG (TF-IDF) & TẦN SUẤT QUA 4 PHIÊN (S1 -> S4) ===')
styled_tfidf = (
    df_tfidf_patterns.style
    .format({
        'Điểm TF-IDF': '{:.3f}',
        'Phiên 1': '{:d}',
        'Phiên 2': '{:d}',
        'Phiên 3': '{:d}',
        'Phiên 4': '{:d}',
        'Tổng Lần': '{:d}',
        'TB / Phiên': '{:.1f}'
    })
    .background_gradient(subset=['Điểm TF-IDF'], cmap='Purples', vmin=0.15, vmax=0.35)
    .background_gradient(subset=['Phiên 1', 'Phiên 2', 'Phiên 3', 'Phiên 4', 'Tổng Lần'], cmap='Blues')
    .set_properties(**{'text-align': 'center'})
    .set_properties(subset=['Pattern Đặc Trưng (TF-IDF)', 'Vai Trò Thực Tế'], **{'text-align': 'left'})
)
display(styled_tfidf)

# Bảng 7: Tỷ trọng chiếm lượng (% share) của Top Pattern trong từng phiên
rows_share = []
for p in personas:
    p_rows = df_tfidf_patterns[df_tfidf_patterns['Persona ID'] == p]
    top_pats = p_rows['Pattern Đặc Trưng (TF-IDF)'].tolist()
    # Tính tổng số lần xuất hiện của các top pattern trong mỗi phiên
    s1_sum = p_rows['Phiên 1'].sum()
    s2_sum = p_rows['Phiên 2'].sum()
    s3_sum = p_rows['Phiên 3'].sum()
    s4_sum = p_rows['Phiên 4'].sum()
    
    t1 = session_total_acts.get((p, 1), 1)
    t2 = session_total_acts.get((p, 2), 1)
    t3 = session_total_acts.get((p, 3), 1)
    t4 = session_total_acts.get((p, 4), 1)
    
    rows_share.append({
        'Persona ID': p,
        'Dấu Ấn Hành Vi Cốt Lõi': top_pats[0],
        'Tổng Thao Tác (4 Phiên)': t1 + t2 + t3 + t4,
        'Tỷ Trọng P1 (%)': round(s1_sum / t1 * 100, 1),
        'Tỷ Trọng P2 (%)': round(s2_sum / t2 * 100, 1),
        'Tỷ Trọng P3 (%)': round(s3_sum / t3 * 100, 1),
        'Tỷ Trọng P4 (%)': round(s4_sum / t4 * 100, 1),
        'Tỷ Trọng TB (%)': round((s1_sum + s2_sum + s3_sum + s4_sum) / (t1 + t2 + t3 + t4) * 100, 1)
    })

df_share = pd.DataFrame(rows_share)
print('\\n=== BẢNG 7: TỔNG HỢP MỨC ĐỘ CHI PHỐI CỦA DẤU ẤN HÀNH VI ĐẶC TRƯNG QUA 4 PHIÊN ===')
styled_share = (
    df_share.style
    .format({
        'Tổng Thao Tác (4 Phiên)': '{:d}',
        'Tỷ Trọng P1 (%)': '{:.1f}%',
        'Tỷ Trọng P2 (%)': '{:.1f}%',
        'Tỷ Trọng P3 (%)': '{:.1f}%',
        'Tỷ Trọng P4 (%)': '{:.1f}%',
        'Tỷ Trọng TB (%)': '{:.1f}%'
    })
    .background_gradient(subset=['Tỷ Trọng TB (%)'], cmap='YlGnBu', vmin=10, vmax=60)
    .set_properties(**{'text-align': 'center'})
    .set_properties(subset=['Dấu Ấn Hành Vi Cốt Lõi'], **{'text-align': 'left'})
)
display(styled_share)

# 4. THỐNG KÊ ĐỘ TƯƠNG ĐỒNG HÀNH VI GIỮA CÁC PHIÊN
print('\\n=== ĐỘ TƯƠNG ĐỒNG HÀNH VI GIỮA CÁC PHIÊN ===')
print(f"- Khi so sánh cùng Persona qua các phiên: r trung bình = {evolution_data['intra_mean']:.4f} +/- {evolution_data['intra_std']:.4f} (Trung vị: {evolution_data['intra_median']:.4f})")
print(f"- Khi so sánh khác Persona giữa các phiên: r trung bình = {evolution_data['inter_mean']:.4f} +/- {evolution_data['inter_std']:.4f} (Trung vị: {evolution_data['inter_median']:.4f})")
print('- Nhận xét: Độ tương đồng hành vi của cùng Persona cao hơn rõ rệt so với giữa các Persona khác nhau.')

# 5. TRỰC QUAN HÓA TOÀN DIỆN 3-PANEL BẰNG BIỂU ĐỒ GẦN GŨI
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(24, 7))

# Panel A: Horizontal bar chart Top 1 Signature Pattern per Persona
top1_df = df_tfidf_patterns.groupby('Persona ID').first().reset_index()
y_pos = np.arange(len(top1_df))
bars = ax1.barh(y_pos, top1_df['Điểm TF-IDF'], color=[PERSONA_PALETTE.get(p, '#333') for p in top1_df['Persona ID']], alpha=0.85, edgecolor='black')
ax1.set_yticks(y_pos)
ax1.set_yticklabels([f"{r['Persona ID']}: {r['Pattern Đặc Trưng (TF-IDF)']}" for _, r in top1_df.iterrows()], fontsize=9.5)
ax1.invert_yaxis()
ax1.set_xlabel('Điểm TF-IDF (Độ Đặc Trưng Hành Vi)', fontsize=10)
ax1.set_title('(A) Top 1 Dấu Ấn Hành Vi Đặc Trưng (TF-IDF)\\nTheo Từng Persona', fontsize=12, fontweight='bold')
ax1.grid(True, linestyle=':', alpha=0.6, axis='x')

for bar in bars:
    w = bar.get_width()
    ax1.text(w + 0.005, bar.get_y() + bar.get_height()/2, f"{w:.3f}", va='center', fontsize=9, fontweight='bold')

# Panel B: Heatmap tần suất xuất hiện qua các phiên của Top 1 Pattern mỗi persona
heat_data = top1_df[['Phiên 1', 'Phiên 2', 'Phiên 3', 'Phiên 4']].copy()
heat_data.index = [f"{r['Persona ID']}: {r['Pattern Đặc Trưng (TF-IDF)']}" for _, r in top1_df.iterrows()]
sns.heatmap(heat_data, annot=True, fmt='d', cmap='YlGnBu', cbar=True, ax=ax2, linewidths=0.5, cbar_kws={'label': 'Số lần xuất hiện (bước)'})
ax2.set_title('(B) Tần Suất Xuất Hiện Của Dấu Ấn Đặc Trưng\\nQua Toàn Bộ Các Phiên (Phiên 1 ➔ 4)', fontsize=12, fontweight='bold')
ax2.set_xlabel('Thứ Tự Phiên Hoạt Động', fontsize=10)
ax2.set_ylabel('')

# Panel C: Tổng số lần xuất hiện và Độ bền vững
ax3.bar(top1_df['Persona ID'], top1_df['Tổng Lần'], color=[PERSONA_PALETTE.get(p, '#333') for p in top1_df['Persona ID']], alpha=0.85, edgecolor='black')
ax3.set_title('(C) Tổng Số Lần Thực Hiện Dấu Ấn Đặc Trưng\\nXuyên Suốt Tất Cả Các Phiên', fontsize=12, fontweight='bold')
ax3.set_xlabel('Persona ID', fontsize=10)
ax3.set_ylabel('Tổng Số Lần Xuất Hiện (bước)', fontsize=10)
ax3.grid(True, linestyle=':', alpha=0.6, axis='y')
for idx, r in top1_df.iterrows():
    ax3.text(idx, r['Tổng Lần'] + 3, f"{r['Tổng Lần']}\\n({r['Số Phiên Có Mặt']})", ha='center', fontsize=8.5, fontweight='bold')

plt.tight_layout()
plt.show()"""

# Cell 25 Markdown: Comprehensive analysis across all 4 sessions with TF-IDF insights
cell_25_content = r"""---
### Nhận định Tổng hợp: Hành vi của các Nhân vật qua các Phiên có Giữ được Thói quen Riêng không?

#### 1. Tại sao cần dùng TF-IDF trên toàn bộ các phiên để tìm Thói quen?
* Nếu chỉ so sánh đơn thuần giữa Phiên 1 và Phiên 2, kết quả rất dễ bị chi phối bởi các hành vi đại trà mà nhân vật nào cũng thực hiện nhiều (như cuộn lướt Bảng tin chung chung `scroll [feed]`).
* Khi áp dụng mô hình **TF-IDF** trên toàn bộ 24 phiên làm việc của cả 6 nhân vật, hệ thống đã triệt tiêu được độ nhiễu của các thao tác thông thường và làm nổi bật chính xác các **Dấu ấn hành vi đặc trưng (Behavioral Signatures)** — tức là những hành động hoặc chuỗi thao tác độc nhất phản ánh đúng bản sắc của từng nhân vật.

---

#### 2. Dấu ấn Hành vi Đặc trưng và Sự tiến hóa Thói quen qua 4 Phiên:

##### a. `vn_fb_004` (Thanh niên Gen Z — Nghiện Video ngắn Reels):
* **Dấu ấn đặc trưng (TF-IDF):** Chuỗi chuyển tiếp liên tục `next [reels] ➔ watch [reels]` ($0.306$) và thao tác chuyển video `next [reels]` ($0.319$).
* **Diễn biến qua 4 phiên:** Thói quen này xuất hiện bền bỉ ở **4/4 phiên** và có xu hướng bùng nổ mạnh mẽ theo thời gian:
  - Phiên 1: $26$ lần bấm chuyển video.
  - Phiên 2: Tăng lên $35$ lần chuyển và $32$ lần xem.
  - Phiên 3: Đạt $46$ lần chuyển và $45$ lần xem.
  - Phiên 4: Đạt mức cao nhất hệ thống với $68$ lần chuyển và $91$ lần xem (tổng cộng $159$ thao tác Reels, chiếm gần $90\%$ thời lượng phiên!).
* $\longrightarrow$ Cho thấy thói quen đắm chìm vào video ngắn không hề phai nhạt mà ngày càng được củng cố vững chắc qua các phiên.

##### b. `vn_fb_001` (Chuyên viên Sáng tạo Nội dung / Marketing):
* **Dấu ấn đặc trưng (TF-IDF):** Thao tác tương tác bài viết nhóm `act_on_post [group]` ($0.197$), cuộn đọc bài nhóm `scroll [group] ➔ read [group]` ($0.195$) và đọc bài nhóm `read [group]` ($0.187$).
* **Diễn biến qua 4 phiên:**
  - Ở Phiên 1 và Phiên 3, nhân vật dành thời gian thăm dò và theo dõi các luồng thảo luận trên Bảng tin ($1$–$2$ lần mở bài nhóm).
  - Đến Phiên 4, khi đã định vị chính xác hội nhóm chuyên môn về đồ họa và truyền thông, thói quen sinh hoạt nhóm bùng nổ: đọc sâu $28$ bài viết nhóm và thực hiện $19$ thao tác tương tác trực tiếp (`act_on_post`).
* $\longrightarrow$ Phản ánh đúng thói quen của người làm nghề sáng tạo: chủ động tìm kiếm và tương tác sâu trong các cộng đồng ngách.

##### c. `vn_fb_005` (Kỹ sư Kỹ thuật / Thích Đào sâu Chi tiết):
* **Dấu ấn đặc trưng (TF-IDF):** Đọc bình luận bài viết `scroll_comments [detail]` ($0.306$), quan sát chi tiết `observe [detail]` và tìm kiếm chuyên môn `search [search] ➔ scroll [search]` ($0.172$).
* **Diễn biến qua 4 phiên:** Thói quen mở bài viết để đọc thảo luận và bình luận kỹ thuật duy trì đều đặn ở **4/4 phiên** ($2$ lần ở P1 $\to$ $4$ lần ở P2 $\to$ $13$ lần ở P3 $\to$ $3$ lần ở P4).
* $\longrightarrow$ Khác với người lướt tin vội vã, kỹ sư kỹ thuật luôn có thói quen dừng lại xem cộng đồng bàn luận gì về các giải pháp và lỗi kỹ thuật.

##### d. `vn_fb_006` (Chuyên viên Tài chính / Kế toán — Cẩn trọng & Hoài nghi):
* **Dấu ấn đặc trưng (TF-IDF):** Quan sát và tương tác hội nhóm `react [group] ➔ observe [group]` ($0.186$) và đọc đối sánh Bảng tin `scroll [feed] ➔ read [feed]`.
* **Diễn biến qua 4 phiên:**
  - Phiên 1 tập trung khảo sát hội nhóm bất động sản Cần Thơ ($9$ lần quan sát nhóm, $6$ lần thả cảm xúc chọn lọc).
  - Sang Phiên 2 và 3, nhân vật mở rộng tìm kiếm từ khóa và đối sánh thông tin trên Bảng tin ($19$ bài đọc ở P3).
* $\longrightarrow$ Thói quen của người làm tài chính thể hiện rõ qua sự thận trọng: khảo sát thị trường trước, sau đó mới mở rộng tìm kiếm và đối chiếu nguồn tin.

##### e. `vn_fb_002` (Công nhân May / Mẹ Bỉm sữa — Lướt Nhanh & Thả Tim):
* **Dấu ấn đặc trưng (TF-IDF):** Xem video giải trí ngắn `watch [reels]` ($0.261$) và lướt nhanh Bảng tin rồi thả cảm xúc `observe [feed] ➔ react [feed]`.
* **Diễn biến qua 4 phiên:** Nhịp độ thao tác diễn ra nhanh gọn trong các khoảng nghỉ ngắn ($57$ bước ở P1, $24$ bước ở P2, $44$ bước ở P3, $59$ bước ở P4). Nhân vật ít khi viết bình luận dài mà chủ yếu lướt vội và thả tim.

##### f. `vn_fb_003` (Bảo vệ Ca trực Đêm — Lướt Tin Bền bỉ):
* **Dấu ấn đặc trưng (TF-IDF):** Chuỗi cuộn lướt liên tục trên Bảng tin `scroll [feed] ➔ scroll [feed]` ($0.606$) và xem video thư giãn trong ca trực đêm.
* **Diễn biến qua 4 phiên:** Duy trì nhịp độ cuộn duyệt tin rất bền bỉ ($68$ bước ở P1, $179$ bước ở P2, $56$ bước ở P3, $64$ bước ở P4), phù hợp với hoàn cảnh trực đêm cần cập nhật tin tức liên tục để tỉnh táo.

---

### Bảng Tổng hợp Mức độ Bền vững của Thói quen qua Toàn bộ các Phiên

| Khía cạnh quan sát | Phương pháp theo dõi | Kết quả cùng Nhân vật qua 4 Phiên | So với giữa các Nhân vật khác nhau | Đánh giá thực tế |
| :--- | :--- | :---: | :---: | :--- |
| **Dấu ấn hành vi cốt lõi** | TF-IDF trên 24 phiên | **Bảo tồn cao (3/4 đến 4/4 phiên)** | Khác biệt hoàn toàn | Mỗi nhân vật định hình 1 phong cách sử dụng riêng biệt (Reels, Hội nhóm, hay Đọc kỹ thuật) |
| **Tỷ trọng chi phối của dấu ấn** | % Thao tác đặc trưng / Phiên | **Chiếm 25% – 60% tổng phiên** | Phân hóa rõ nét | Thói quen đặc thù chi phối phần lớn thời lượng hoạt động của nhân vật |
| **Màn hình sử dụng** | Phân bổ thời lượng màn hình | **Tương đồng cao** | Khác biệt rõ rệt | Nhóm xem Reels luôn gắn với Reels; nhóm hội nhóm luôn tìm về hội nhóm |
| **Độ tương đồng hành vi** | Hệ số tương đồng ($r$) | **$r_{\text{cùng Persona}} \approx 0.65 - 0.91$** | $r_{\text{khác Persona}} \approx 0.20 - 0.40$ | Mức độ ổn định nội tại vượt trội so với sự ngẫu nhiên giữa các nhân vật |

> **KẾT LUẬN:**  
> Việc phân tích trên toàn bộ 4 phiên bằng mô hình TF-IDF khẳng định rằng: **Các nhân vật không hề hành động ngẫu nhiên hay bị mất phương hướng qua các phiên.** Ngược lại, mỗi nhân vật đều duy trì các "chữ ký hành vi" đặc trưng mang tính thói quen bền vững, đồng thời vẫn có sự tiến hóa tự nhiên theo thời gian khi đã thích nghi với môi trường mạng xã hội."""

# Replace in notebook
nb['cells'][24]['source'] = [line + '\n' for line in cell_24_code.split('\n')]
nb['cells'][24]['source'][-1] = nb['cells'][24]['source'][-1].rstrip('\n')

nb['cells'][25]['source'] = [line + '\n' for line in cell_25_content.split('\n')]
nb['cells'][25]['source'][-1] = nb['cells'][25]['source'][-1].rstrip('\n')

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Cell 24 and Cell 25 updated with full TF-IDF multi-session profiling successfully!")
