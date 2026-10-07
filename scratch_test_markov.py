import sys
import json
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
from loaders.action_loader import ActionLoader

loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)

personas = sorted(df_actions['persona_id'].unique())
print("Personas:", personas)

# 1. Surface Transition Matrix per Persona
surfaces = ['feed', 'detail', 'reels', 'group', 'search', 'unknown']
print("\n=== SURFACE TRANSITION MATRICES ===")
for pid in personas:
    p_df = df_actions[df_actions['persona_id'] == pid].copy()
    p_df = p_df.sort_values(by=['session_id', 'step_index'])
    p_df['next_surface'] = p_df.groupby('session_id')['surface'].shift(-1)
    valid = p_df.dropna(subset=['surface', 'next_surface'])
    ct = pd.crosstab(valid['surface'], valid['next_surface'], normalize='index').round(3)
    print(f"\n--- {pid} (N pairs = {len(valid)}) ---")
    print(ct)

# 2. Intent Transition Matrix per Persona
top_intents = ['scroll', 'read', 'observe', 'next', 'react', 'scroll_comments', 'comment', 'expand', 'open', 'close']
print("\n=== INTENT TRANSITION MATRICES (Top Intents) ===")
for pid in personas:
    p_df = df_actions[df_actions['persona_id'] == pid].copy()
    p_df = p_df.sort_values(by=['session_id', 'step_index'])
    p_df['next_intent'] = p_df.groupby('session_id')['intent'].shift(-1)
    valid = p_df.dropna(subset=['intent', 'next_intent'])
    ct = pd.crosstab(valid['intent'], valid['next_intent'], normalize='index').round(3)
    # filter to top intents
    avail_idx = [i for i in top_intents if i in ct.index]
    avail_cols = [c for c in top_intents if c in ct.columns]
    sub_ct = ct.reindex(index=avail_idx, columns=avail_cols, fill_value=0.0)
    print(f"\n--- {pid} (N pairs = {len(valid)}) ---")
    print(sub_ct.loc[:, (sub_ct != 0).any(axis=0)])
