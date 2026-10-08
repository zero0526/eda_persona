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
session_bigrams = {}

persona_acts = {p: [] for p in personas}
persona_bigrams = {p: [] for p in personas}

for (p, s_order), grp in df_actions.groupby(['persona_id', 'session_order']):
    grp_sorted = grp.sort_values('step_index')
    acts = [f"{str(r['intent']).strip()}@{str(r['surface']).strip()}" for _, r in grp_sorted.iterrows()]
    bigrams = [f"{acts[i]}__then__{acts[i+1]}" for i in range(len(acts)-1)]
    
    session_acts[(p, s_order)] = acts
    session_bigrams[(p, s_order)] = bigrams
    
    persona_acts[p].extend(acts)
    persona_bigrams[p].extend(bigrams)

# Sublinear TF
vec_uni = TfidfVectorizer(token_pattern=r'(?u)\S+', lowercase=False, sublinear_tf=True)
X_uni = vec_uni.fit_transform([' '.join(persona_acts[p]) for p in personas]).toarray()
feat_uni = np.array(vec_uni.get_feature_names_out())

vec_bi = TfidfVectorizer(token_pattern=r'(?u)\S+', lowercase=False, sublinear_tf=True)
X_bi = vec_bi.fit_transform([' '.join(persona_bigrams[p]) for p in personas]).toarray()
feat_bi = np.array(vec_bi.get_feature_names_out())

print("=== UNIGRAMS WITH SUBLINEAR TF ===")
for idx, p in enumerate(personas):
    top_idx = np.argsort(X_uni[idx])[::-1][:4]
    print(f"\n{p}:")
    for i in top_idx:
        print(f"  {feat_uni[i]} ({X_uni[idx][i]:.3f})")

print("\n=== BIGRAMS WITH SUBLINEAR TF ===")
for idx, p in enumerate(personas):
    top_idx = np.argsort(X_bi[idx])[::-1][:4]
    print(f"\n{p}:")
    for i in top_idx:
        print(f"  {feat_bi[i]} ({X_bi[idx][i]:.3f})")
