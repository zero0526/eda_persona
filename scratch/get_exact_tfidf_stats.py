import sys
from pathlib import Path
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from loaders.action_loader import ActionLoader
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter

loader = ActionLoader()
df = loader.to_unified_actions_dataframe()
personas = sorted(df['persona_id'].unique())

# Nén lặp cơ học và trích xuất cả bigram và trigram
session_chains = {}
persona_chains = {p: [] for p in personas}

for (p, s), grp in df.groupby(['persona_id', 'session_order']):
    grp_sorted = grp.sort_values('step_index')
    raw_acts = [f"{str(r['intent']).strip()}@{str(r['surface']).strip()}" for _, r in grp_sorted.iterrows()]
    
    # Nén lặp liền kề
    acts = []
    prev = None
    for a in raw_acts:
        if a != prev:
            acts.append(a)
            prev = a
            
    tokens = []
    # Bigrams
    for i in range(len(acts) - 1):
        tokens.append(f"{acts[i]}__THEN__{acts[i+1]}")
    # Trigrams (loại ping-pong A -> B -> A)
    for i in range(len(acts) - 2):
        if acts[i] != acts[i+2]:
            tokens.append(f"{acts[i]}__THEN__{acts[i+1]}__THEN__{acts[i+2]}")
            
    session_chains[(p, s)] = tokens
    persona_chains[p].extend(tokens)

# Tính ma trận TF-IDF
docs = [' '.join(persona_chains[p]) for p in personas]
vec = TfidfVectorizer(token_pattern=r'(?u)\S+', lowercase=False, sublinear_tf=True)
X_tfidf = vec.fit_transform(docs).toarray()
features = np.array(vec.get_feature_names_out())
feat_to_idx = {feat: idx for idx, feat in enumerate(features)}

# Danh sách các chuỗi ứng viên hàng đầu cho từng persona
candidate_chains = {
    'vn_fb_001': [
        ('scroll@group__THEN__read@group__THEN__react@group', 'Đọc sâu & Tương tác trong Nhóm Kiến trúc'),
        ('scroll@group__THEN__read@group', 'Lướt & Đọc tài liệu trong Hội nhóm Chuyên môn'),
        ('open@search__THEN__observe@search__THEN__open@group', 'Tìm kiếm từ khóa kiến trúc ➔ Mở Hội nhóm Chuyên ngành'),
        ('read@group__THEN__open_comments@detail', 'Đọc bài trong nhóm ➔ Mở xem thảo luận chuyên gia')
    ],
    'vn_fb_002': [
        ('observe@feed__THEN__react@feed', 'Dừng nhìn bài thiện nguyện trên Feed ➔ Thả tim cảm xúc'),
        ('read@feed__THEN__react@feed__THEN__scroll@feed', 'Đọc nhanh ➔ Thả tim hướng thiện ➔ Cuộn lướt tiếp (Tranh thủ giờ nghỉ)'),
        ('scroll@feed__THEN__read@feed__THEN__react@feed', 'Lướt bảng tin ➔ Đọc nhanh ➔ Thả tim cảm xúc')
    ],
    'vn_fb_003': [
        ('comment@detail__THEN__observe@detail__THEN__scroll_comments@detail', 'Bình luận hỏi quán ăn đêm ➔ Dừng quan sát ➔ Cuộn đọc bàn luận đêm'),
        ('comment@detail__THEN__observe@detail', 'Để lại bình luận hỏi quán ➔ Dừng quan sát phản hồi'),
        ('observe@feed__THEN__scroll@feed__THEN__search@search', 'Lướt feed đêm ➔ Chủ động tìm kiếm địa điểm ẩm thực')
    ],
    'vn_fb_004': [
        ('watch@reels__THEN__next@reels', 'Trục tiêu thụ video ngắn Reels liên hoàn'),
        ('next@reels__THEN__watch@reels__THEN__react@reels', 'Xem chọn lọc clip bóng đá highlight ➔ Thả tim cảm xúc ➔ Vuốt chuyển tiếp'),
        ('react@reels__THEN__next@reels', 'Thả tim video ưng ý ➔ Vuốt chuyển sang clip tiếp theo')
    ],
    'vn_fb_005': [
        ('read@feed__THEN__expand@feed__THEN__observe@feed', 'Đọc mở đầu bài kỹ thuật dài ➔ Bấm \"Xem thêm\" mở toàn văn ➔ Thẩm định chi tiết'),
        ('read@feed__THEN__open_comments@detail__THEN__comment@detail', 'Đọc bài chuyên ngành ➔ Mở xem bình luận ➔ Viết bình luận thảo luận'),
        ('search@search__THEN__scroll@search', 'Tìm kiếm chuyên sâu từ khóa Hội Thiên văn SAL')
    ],
    'vn_fb_006': [
        ('observe@group__THEN__read@group__THEN__react@group', 'Quan sát nhóm BĐS Cần Thơ ➔ Đọc khảo sát giá ➔ Tương tác bài đăng'),
        ('search@search__THEN__open@search__THEN__observe@search', 'Tìm kiếm BĐS/Nha khoa có chủ đích ➔ Mở kết quả ➔ Quan sát thẩm định logic'),
        ('observe@feed__THEN__search@search', 'Thấy tin tức trên feed ➔ Chuyển ngay sang tìm kiếm kiểm chứng dữ liệu')
    ]
}

print("=== BẢNG TÍNH TOÁN TF-IDF CHI TIẾT THEO TỪNG CHUỖI ỨNG VIÊN ===")
rows = []
for p in personas:
    p_idx = personas.index(p)
    print(f"\n--- PERSONA: {p} ---")
    for feat, desc in candidate_chains[p]:
        if feat in feat_to_idx:
            f_idx = feat_to_idx[feat]
            tfidf_score = X_tfidf[p_idx][f_idx]
        else:
            tfidf_score = 0.0
            
        s_counts = [session_chains.get((p, s), []).count(feat) for s in [1, 2, 3, 4]]
        tot = sum(s_counts)
        n_sess = sum(1 for c in s_counts if c > 0)
        
        other_tot = sum(session_chains.get((op, s), []).count(feat) for op in personas if op != p for s in [1, 2, 3, 4])
        all_tot = tot + other_tot
        excl = (tot / all_tot * 100) if all_tot > 0 else 0.0
        
        parts = feat.split('__THEN__')
        disp = ' ➔ '.join([pt.replace('@', ' [') + ']' for pt in parts])
        
        print(f"  * {disp}")
        print(f"    TF-IDF: {tfidf_score:.3f} | Tổng lần: {tot} ({s_counts}, {n_sess}/4 phiên) | Độc quyền: {excl:.1f}%")
        print(f"    Ý nghĩa: {desc}")
        
        rows.append({
            'persona_id': p,
            'feat_raw': feat,
            'chain_disp': disp,
            'n_steps': len(parts),
            'desc': desc,
            'tfidf': round(tfidf_score, 3),
            'tot': tot,
            's_counts': s_counts,
            'n_sess': n_sess,
            'excl': round(excl, 1)
        })

df_res = pd.DataFrame(rows)
df_res.to_csv('scratch/candidate_tfidf_chains.csv', index=False, encoding='utf-8-sig')
print("\nĐã lưu kết quả vào scratch/candidate_tfidf_chains.csv")
