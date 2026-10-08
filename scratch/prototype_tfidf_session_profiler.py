import sys, os
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np
from loaders.action_loader import ActionLoader
from sklearn.feature_extraction.text import TfidfVectorizer

loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)

personas = sorted(df_actions['persona_id'].unique())

# Extract tokens: unigrams and bigrams
persona_tokens = {p: [] for p in personas}
session_tokens = {}  # (p, s_order): list of tokens

for (p, s_order), grp in df_actions.groupby(['persona_id', 'session_order']):
    grp_sorted = grp.sort_values('step_index')
    acts = [f"{str(r['intent']).strip()}@{str(r['surface']).strip()}" for _, r in grp_sorted.iterrows()]
    bigrams = [f"{acts[i]}__THEN__{acts[i+1]}" for i in range(len(acts)-1)]
    
    tokens = acts + bigrams
    persona_tokens[p].extend(tokens)
    session_tokens[(p, s_order)] = tokens

# TF-IDF
corpus = [' '.join(persona_tokens[p]) for p in personas]
vec = TfidfVectorizer(token_pattern=r'(?u)\S+')
X = vec.fit_transform(corpus).toarray()
features = np.array(vec.get_feature_names_out())

def format_token(tok):
    if '__then__' in tok:
        parts = tok.split('__then__')
        p1 = parts[0].replace('@', ' [') + ']'
        p2 = parts[1].replace('@', ' [') + ']'
        return f"{p1} ➔ {p2}", "Chuỗi 2 bước (Bigram)"
    else:
        return tok.replace('@', ' [') + ']', "Hành vi đơn (Action)"

top_rows = []
for idx, p in enumerate(personas):
    # Sort by TF-IDF descending
    top_indices = np.argsort(X[idx])[::-1]
    
    # Pick top 4 patterns
    selected = 0
    for i in top_indices:
        score = X[idx][i]
        if score <= 0.05:
            continue
        feat = features[i]
        label, p_type = format_token(feat)
        
        # Calculate session frequencies
        s_counts = [session_tokens.get((p, s_order), []).count(feat) for s_order in [1, 2, 3, 4]]
        total_cnt = sum(s_counts)
        active_sessions = sum(1 for c in s_counts if c > 0)
        
        top_rows.append({
            'Persona ID': p,
            'Pattern Hành Vi Đặc Trưng': label,
            'Loại Pattern': p_type,
            'Điểm TF-IDF': round(score, 3),
            'Phiên 1': s_counts[0],
            'Phiên 2': s_counts[1],
            'Phiên 3': s_counts[2],
            'Phiên 4': s_counts[3],
            'Tổng lần': total_cnt,
            'TB / Phiên': round(total_cnt / 4.0, 1),
            'Độ Bền Vững (Số Phiên Có Mặt)': f"{active_sessions}/4 phiên"
        })
        selected += 1
        if selected >= 4:
            break

df_top = pd.DataFrame(top_rows)
print("=== BẢNG TOP PATTERN HÀNH VI ĐẶC TRƯNG TF-IDF & TẦN SUẤT QUA CÁC PHIÊN ===")
print(df_top.to_string(index=False))
