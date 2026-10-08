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

persona_bigrams = {p: [] for p in personas}
session_bigrams = {}

persona_unigrams = {p: [] for p in personas}
session_unigrams = {}

for (p, s_order), grp in df_actions.groupby(['persona_id', 'session_order']):
    grp_sorted = grp.sort_values('step_index')
    acts = [f"{str(r['intent']).strip()}@{str(r['surface']).strip()}" for _, r in grp_sorted.iterrows()]
    bigrams = [f"{acts[i]}__THEN__{acts[i+1]}" for i in range(len(acts)-1)]
    
    persona_bigrams[p].extend(bigrams)
    session_bigrams[(p, s_order)] = bigrams
    
    persona_unigrams[p].extend(acts)
    session_unigrams[(p, s_order)] = acts

# 1. Bigram TF-IDF
corpus_bi = [' '.join(persona_bigrams[p]) for p in personas]
vec_bi = TfidfVectorizer(token_pattern=r'(?u)\S+')
X_bi = vec_bi.fit_transform(corpus_bi).toarray()
feat_bi = np.array(vec_bi.get_feature_names_out())

print("=== TOP 4 SIGNATURE BIGRAMS (TF-IDF) ===")
for idx, p in enumerate(personas):
    top_idx = np.argsort(X_bi[idx])[::-1][:4]
    print(f"\nPersona: {p}")
    for i in top_idx:
        score = X_bi[idx][i]
        label = feat_bi[i].replace('__then__', ' ➔ ').replace('@', ' [') + ']'
        label = label.replace(' ➔ ', '] ➔ ')
        print(f"  {label} (TF-IDF: {score:.3f})")

# 2. Unigram TF-IDF
corpus_uni = [' '.join(persona_unigrams[p]) for p in personas]
vec_uni = TfidfVectorizer(token_pattern=r'(?u)\S+')
X_uni = vec_uni.fit_transform(corpus_uni).toarray()
feat_uni = np.array(vec_uni.get_feature_names_out())

print("\n=== TOP 4 SIGNATURE UNIGRAMS (TF-IDF) ===")
for idx, p in enumerate(personas):
    top_idx = np.argsort(X_uni[idx])[::-1][:4]
    print(f"\nPersona: {p}")
    for i in top_idx:
        score = X_uni[idx][i]
        label = feat_uni[i].replace('@', ' [') + ']'
        print(f"  {label} (TF-IDF: {score:.3f})")
