import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path
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

# Thử nghiệm 2 cách tạo token:
# Cách 1: Raw actions
# Cách 2: Run-length compressed (nén các bước lặp lại liên tiếp)

def get_sequences(compressed=True, n_gram_sizes=[2, 3]):
    persona_docs = {p: [] for p in personas}
    persona_session_counts = {p: {} for p in personas}
    
    for (p, s_ord), grp in df.groupby(['persona_id', 'session_order']):
        grp_sorted = grp.sort_values('step_index')
        raw_acts = [f"{str(r['intent']).strip()}@{str(r['surface']).strip()}" for _, r in grp_sorted.iterrows()]
        
        if compressed:
            acts = []
            prev = None
            for a in raw_acts:
                if a != prev:
                    acts.append(a)
                    prev = a
        else:
            acts = raw_acts
            
        session_tokens = []
        for n in n_gram_sizes:
            for i in range(len(acts) - n + 1):
                sub = acts[i:i+n]
                # Bỏ nếu có 2 bước liền kề trùng nhau (nếu raw)
                if any(sub[j] == sub[j+1] for j in range(len(sub)-1)):
                    continue
                # Bỏ ping-pong A -> B -> A nếu trigram
                if n == 3 and sub[0] == sub[2]:
                    continue
                token = '__THEN__'.join(sub)
                session_tokens.append(token)
                
        persona_docs[p].extend(session_tokens)
        persona_session_counts[p][s_ord] = Counter(session_tokens)
        
    return persona_docs, persona_session_counts

print("=====================================================================")
print("THỬ NGHIỆM TF-IDF VỚI CHUỖI N-GRAM (2-GRAM VÀ 3-GRAM) NÉN LẶP CƠ HỌC")
print("=====================================================================")

docs, session_counts = get_sequences(compressed=True, n_gram_sizes=[2, 3])

corpus = [' '.join(docs[p]) for p in personas]
vec = TfidfVectorizer(token_pattern=r'(?u)\S+', lowercase=False, sublinear_tf=True)
X_tfidf = vec.fit_transform(corpus).toarray()
features = np.array(vec.get_feature_names_out())

for idx, p in enumerate(personas):
    print(f"\n*** TOP TF-IDF PATTERNS CHO {p} ***")
    top_indices = np.argsort(X_tfidf[idx])[::-1]
    
    shown = 0
    for i in top_indices:
        feat = features[i]
        score = X_tfidf[idx][i]
        
        # Đếm tần suất ở 4 phiên
        s_cnts = [session_counts[p].get(s, Counter())[feat] for s in [1, 2, 3, 4]]
        tot = sum(s_cnts)
        n_sessions = sum(1 for c in s_cnts if c > 0)
        
        # Đếm tần suất ở các persona khác
        other_tot = sum(session_counts[other_p].get(s, Counter())[feat] 
                        for other_p in personas if other_p != p 
                        for s in [1, 2, 3, 4])
        
        excl = (tot / (tot + other_tot)) * 100.0 if (tot + other_tot) > 0 else 0
        
        # Định dạng hiển thị
        parts = feat.split('__THEN__')
        disp = ' ➔ '.join([pt.replace('@', ' [') + ']' for pt in parts])
        n_step = len(parts)
        
        print(f"  [{n_step}-step] {disp}")
        print(f"     TF-IDF: {score:.3f} | Xuất hiện: {s_cnts} (Tổng {tot} lần, {n_sessions}/4 phiên) | Độc quyền: {excl:.1f}%")
        
        shown += 1
        if shown >= 6:
            break
