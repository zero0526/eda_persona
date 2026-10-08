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
    return ' ➔ '.join(formatted_parts)

print('=== TOP 1 TRIGRAM (3 BƯỚC) CỦA TỪNG PERSONA ===')
for idx, p in enumerate(personas):
    trigram_indices = [i for i in np.argsort(X_chains[idx])[::-1] if len(features_chains[i].split('__THEN__')) == 3]
    top_i = trigram_indices[0]
    feat = features_chains[top_i]
    score = X_chains[idx][top_i]
    label = format_chain_label(feat)
    s_counts = [session_chains.get((p, s), []).count(feat) for s in [1, 2, 3, 4]]
    tot = sum(s_counts)
    active = sum(1 for c in s_counts if c > 0)
    print(f'{p}: {label} (feat: {feat})')
    print(f'   TF-IDF: {score:.3f} | S1..S4: {s_counts} | Tổng: {tot} | Hoạt động: {active}/4 phiên')
