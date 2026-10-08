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

session_chains = {}  # (p, s): list of bigrams and trigrams
persona_chains = {p: [] for p in personas}

for (p, s_order), grp in df_actions.groupby(['persona_id', 'session_order']):
    grp_sorted = grp.sort_values('step_index')
    acts = [f"{str(r['intent']).strip()}@{str(r['surface']).strip()}" for _, r in grp_sorted.iterrows()]
    
    # 2-action chains (Bigrams)
    bigrams = [f"{acts[i]}__THEN__{acts[i+1]}" for i in range(len(acts)-1)]
    # 3-action chains (Trigrams)
    trigrams = [f"{acts[i]}__THEN__{acts[i+1]}__THEN__{acts[i+2]}" for i in range(len(acts)-2)]
    
    chains = bigrams + trigrams
    session_chains[(p, s_order)] = chains
    persona_chains[p].extend(chains)

# Vectorizer on Bigrams + Trigrams
vec = TfidfVectorizer(token_pattern=r'(?u)\S+', lowercase=False, sublinear_tf=True)
corpus = [' '.join(persona_chains[p]) for p in personas]
X = vec.fit_transform(corpus).toarray()
features = np.array(vec.get_feature_names_out())

def format_chain(feat):
    parts = feat.split('__THEN__')
    formatted_parts = [p.replace('@', ' [') + ']' for p in parts]
    label = " ➔ ".join(formatted_parts)
    c_type = f"Chuỗi {len(parts)} bước ({'Bigram' if len(parts)==2 else 'Trigram'})"
    return label, c_type, len(parts)

print("=== TOP 4 SIGNATURE CHAINS (2-3 ACTIONS) PER PERSONA ===")
rows = []
for idx, p in enumerate(personas):
    top_indices = np.argsort(X[idx])[::-1]
    cnt = 0
    print(f"\n--- {p} ---")
    for i in top_indices:
        feat = features[i]
        score = X[idx][i]
        label, c_type, n_steps = format_chain(feat)
        s_counts = [session_chains.get((p, s), []).count(feat) for s in [1, 2, 3, 4]]
        tot = sum(s_counts)
        active_sess = sum(1 for c in s_counts if c > 0)
        
        print(f"  {label} ({c_type}): TF-IDF = {score:.3f}, S1..S4 = {s_counts}, Tot = {tot}")
        rows.append({
            'Persona ID': p,
            'Chuỗi Hành Vi Đặc Trưng (2-3 Bước)': label,
            'Độ Dài': f"{n_steps} bước",
            'Điểm TF-IDF': round(score, 3),
            'Phiên 1': s_counts[0],
            'Phiên 2': s_counts[1],
            'Phiên 3': s_counts[2],
            'Phiên 4': s_counts[3],
            'Tổng Lần': tot,
            'TB / Phiên': round(tot / 4.0, 1),
            'Độ Bền Vững': f"{active_sess}/4 phiên"
        })
        cnt += 1
        if cnt >= 4:
            break

df_top = pd.DataFrame(rows)
print("\n=== SUMMARY TABLE ===")
print(df_top.to_string(index=False))
