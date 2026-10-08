import sys
sys.path.append('.')
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from loaders.action_loader import ActionLoader

sys.stdout.reconfigure(encoding='utf-8')

loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)

personas = sorted(df_actions['persona_id'].unique())
persona_chains = {p: [] for p in personas}
session_chains = {}

for (p, s_order), grp in df_actions.groupby(['persona_id', 'session_order']):
    grp_sorted = grp.sort_values('step_index')
    acts = [f"{str(r['intent']).strip()}@{str(r['surface']).strip()}" for _, r in grp_sorted.iterrows()]
    bigrams = [f"{acts[i]}__THEN__{acts[i+1]}" for i in range(len(acts)-1)]
    trigrams = [f"{acts[i]}__THEN__{acts[i+1]}__THEN__{acts[i+2]}" for i in range(len(acts)-2)]
    chains = bigrams + trigrams
    session_chains[(p, s_order)] = chains
    persona_chains[p].extend(chains)

vec_chains = TfidfVectorizer(token_pattern=r'(?u)\S+', lowercase=False, sublinear_tf=True)
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
        return f"4/4 phiên (Xuất hiện liên tục từ Phiên 1 ➔ 4)"
    elif active_sess > 1:
        sess_str = ", ".join(active_sessions)
        return f"{active_sess}/4 phiên ({sess_str}; cao nhất Phiên {max_idx}: {max_val} lần)"
    elif active_sess == 1:
        return f"1/4 phiên (Tập trung tại {active_sessions[0]}: {max_val} lần)"
    else:
        return "0/4 phiên (Chưa ghi nhận)"

core_loops_rows = []
for idx, p in enumerate(personas):
    # Tự động tìm chuỗi 3 bước (Trigram) có điểm TF-IDF cao nhất từ mô hình
    trigram_indices = [i for i in np.argsort(X_chains[idx])[::-1] if len(features_chains[i].split('__THEN__')) == 3]
    top_i = trigram_indices[0]
    feat = features_chains[top_i]
    score = X_chains[idx][top_i]
    label, _, n_steps = format_chain_label(feat)
    
    # Tính toán tần suất xuất hiện theo từng phiên trực tiếp từ dữ liệu log
    s_counts = [session_chains.get((p, s), []).count(feat) for s in [1, 2, 3, 4]]
    tot = sum(s_counts)
    active_sess = sum(1 for c in s_counts if c > 0)
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
print(df_core_loops.to_string())
