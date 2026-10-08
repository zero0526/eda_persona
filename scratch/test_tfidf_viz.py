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

session_acts = {}
persona_acts = {p: [] for p in personas}

for (p, s_order), grp in df_actions.groupby(['persona_id', 'session_order']):
    grp_sorted = grp.sort_values('step_index')
    acts = [f"{str(r['intent']).strip()}@{str(r['surface']).strip()}" for _, r in grp_sorted.iterrows()]
    bigrams = [f"{acts[i]}__then__{acts[i+1]}" for i in range(len(acts)-1)]
    tokens = acts + bigrams
    session_acts[(p, s_order)] = tokens
    persona_acts[p].extend(tokens)

# Run TF-IDF with sublinear_tf=True
vec = TfidfVectorizer(token_pattern=r'(?u)\S+', lowercase=False, sublinear_tf=True)
corpus = [' '.join(persona_acts[p]) for p in personas]
X = vec.fit_transform(corpus).toarray()
features = np.array(vec.get_feature_names_out())

def format_pat(feat):
    if '__then__' in feat:
        parts = feat.split('__then__')
        p1 = parts[0].replace('@', ' [') + ']'
        p2 = parts[1].replace('@', ' [') + ']'
        return f"{p1} ➔ {p2}", "Chuỗi chuyển tiếp"
    else:
        return feat.replace('@', ' [') + ']', "Hành vi đơn"

rows = []
for idx, p in enumerate(personas):
    top_indices = np.argsort(X[idx])[::-1]
    cnt = 0
    for i in top_indices:
        feat = features[i]
        score = X[idx][i]
        # Ignore extremely generic single scrolls if we want distinctiveness
        label, p_type = format_pat(feat)
        s_counts = [session_acts.get((p, s), []).count(feat) for s in [1, 2, 3, 4]]
        tot = sum(s_counts)
        active_sess = sum(1 for c in s_counts if c > 0)
        rows.append({
            'Persona ID': p,
            'Pattern Đặc Trưng (TF-IDF)': label,
            'Loại Pattern': p_type,
            'Điểm TF-IDF': round(score, 3),
            'Phiên 1': s_counts[0],
            'Phiên 2': s_counts[1],
            'Phiên 3': s_counts[2],
            'Phiên 4': s_counts[3],
            'Tổng số lần': tot,
            'TB / Phiên': round(tot / 4.0, 1),
            'Độ Bền Vững': f"{active_sess}/4 phiên"
        })
        cnt += 1
        if cnt >= 4:
            break

df_summary = pd.DataFrame(rows)
print("=== BẢNG CHỮ KÝ HÀNH VI ĐẶC TRƯNG TF-IDF & TẦN SUẤT QUA 4 PHIÊN ===")
print(df_summary.to_string(index=False))
