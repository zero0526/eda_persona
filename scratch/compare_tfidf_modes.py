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

persona_raw_bi = {p: [] for p in personas}
persona_raw_tri = {p: [] for p in personas}
persona_comp_bi = {p: [] for p in personas}
persona_comp_tri = {p: [] for p in personas}

for (p, s), grp in df.groupby(['persona_id', 'session_order']):
    grp_s = grp.sort_values('step_index')
    raw_acts = [f"{r['intent']}@{r['surface']}" for _, r in grp_s.iterrows()]
    
    # Raw n-grams
    for i in range(len(raw_acts)-1):
        persona_raw_bi[p].append(f"{raw_acts[i]}__THEN__{raw_acts[i+1]}")
    for i in range(len(raw_acts)-2):
        persona_raw_tri[p].append(f"{raw_acts[i]}__THEN__{raw_acts[i+1]}__THEN__{raw_acts[i+2]}")
        
    # Compressed acts
    comp_acts = []
    prev = None
    for a in raw_acts:
        if a != prev:
            comp_acts.append(a)
            prev = a
            
    for i in range(len(comp_acts)-1):
        persona_comp_bi[p].append(f"{comp_acts[i]}__THEN__{comp_acts[i+1]}")
    for i in range(len(comp_acts)-2):
        if comp_acts[i] != comp_acts[i+2]: # no ping-pong
            persona_comp_tri[p].append(f"{comp_acts[i]}__THEN__{comp_acts[i+1]}__THEN__{comp_acts[i+2]}")

for mode, name, p_dict in [('raw_tri', '1. Raw Trigrams (Như Cell 22 notebook)', persona_raw_tri),
                          ('comp_tri', '2. Compressed Trigrams (Không lặp bước kề)', persona_comp_tri),
                          ('comp_bi', '3. Compressed Bigrams (Không lặp bước kề)', persona_comp_bi)]:
    print(f"\n=======================================================")
    print(f"*** MODE: {name} ***")
    print(f"=======================================================")
    docs = [' '.join(p_dict[p]) for p in personas]
    vec = TfidfVectorizer(token_pattern=r'(?u)\S+', sublinear_tf=True)
    X = vec.fit_transform(docs).toarray()
    feats = np.array(vec.get_feature_names_out())
    for idx, p in enumerate(personas):
        top_idx = np.argsort(X[idx])[::-1][:5]
        print(f"\n[{p}]")
        for i in top_idx:
            if X[idx][i] > 0:
                feat_disp = feats[i].replace('@', ' [').replace('__THEN__', '] ➔ ') + ']'
                # count
                cnt = p_dict[p].count(feats[i])
                other_cnt = sum(p_dict[op].count(feats[i]) for op in personas if op != p)
                excl = (cnt / (cnt + other_cnt) * 100) if (cnt + other_cnt) > 0 else 0
                print(f"   TF-IDF: {X[idx][i]:.3f} | Lần: {cnt:2d} | Độc quyền: {excl:5.1f}% | {feat_disp}")
