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

# Prepare documents per persona across all sessions
personas = sorted(df_actions['persona_id'].unique())
persona_tokens = {p: [] for p in personas}
session_tokens = {}  # (p, s_order): list of tokens

for (p, s_order), grp in df_actions.groupby(['persona_id', 'session_order']):
    grp_sorted = grp.sort_values('step_index')
    acts = [f"{r['intent']}@{r['surface']}" for _, r in grp_sorted.iterrows()]
    
    # Unigrams + Bigrams
    unigrams = acts
    bigrams = ['_'.join(acts[i:i+2]) for i in range(len(acts)-1)]
    
    tokens = unigrams + bigrams
    persona_tokens[p].extend(tokens)
    session_tokens[(p, s_order)] = tokens

# Build TF-IDF on 6 Persona documents
corpus = [' '.join(persona_tokens[p]) for p in personas]
vec = TfidfVectorizer(token_pattern=r'(?u)\S+')
X = vec.fit_transform(corpus).toarray()
features = np.array(vec.get_feature_names_out())

print('=== TOP 4 TF-IDF PATTERNS PER PERSONA ===')
top_patterns = {}
for idx, p in enumerate(personas):
    top_idx = np.argsort(X[idx])[::-1][:4]
    top_pats = []
    print(f'\nPersona: {p}')
    for i in top_idx:
        score = X[idx][i]
        feat = features[i]
        label = feat.replace('@', ' [') + ']' if '_' not in feat else ' -> '.join([x.replace('@', ' [') + ']' for x in feat.split('_')])
        top_pats.append((feat, label, score))
        print(f'  {label} (TF-IDF: {score:.3f})')
    top_patterns[p] = top_pats

# Count occurrences across sessions
rows = []
for p in personas:
    for feat, label, score in top_patterns[p]:
        row = {
            'Persona': p,
            'Pattern Đặc Trưng': label,
            'TF-IDF': round(score, 3)
        }
        total_count = 0
        for s_order in [1, 2, 3, 4]:
            tokens = session_tokens.get((p, s_order), [])
            cnt = tokens.count(feat)
            row[f'Phiên {s_order}'] = cnt
            total_count += cnt
        row['Tổng số lần'] = total_count
        row['TB / Phiên'] = round(total_count / 4.0, 1)
        rows.append(row)

df_result = pd.DataFrame(rows)
print('\n=== BẢNG PHÂN BỔ TẦN SUẤT THEO PHIÊN CỦA TOP PATTERN ===')
print(df_result.to_string(index=False))
