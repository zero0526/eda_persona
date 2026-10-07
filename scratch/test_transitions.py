import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from loaders.action_loader import ActionLoader
import pandas as pd
import numpy as np

loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)

cond_13 = (df_actions['session_order'].isin([1, 2])) | ((df_actions['persona_id'] == 'vn_fb_006') & (df_actions['session_order'] == 3))
df_actions_h3 = df_actions[cond_13].sort_values(['persona_id', 'session_order', 'step_index']).reset_index(drop=True)

macro_surfaces = ['feed', 'group', 'reels', 'search']
df_macro = df_actions_h3[df_actions_h3['surface'].isin(macro_surfaces)].copy()
df_macro['prev_surface'] = df_macro.groupby(['persona_id', 'session_id'])['surface'].shift(1)
df_shifts = df_macro[df_macro['surface'] != df_macro['prev_surface']].copy()
df_shifts['next_surface'] = df_shifts.groupby(['persona_id', 'session_id'])['surface'].shift(-1)
valid_shifts = df_shifts.dropna(subset=['next_surface'])

ct_counts = pd.crosstab(valid_shifts['surface'], valid_shifts['next_surface']).reindex(index=macro_surfaces, columns=macro_surfaces, fill_value=0)
row_sums = ct_counts.sum(axis=1)
prob_matrix = ct_counts.div(row_sums.replace(0, np.nan), axis=0).fillna(0)

print("ct_counts:")
print(ct_counts)

# Extract transitions dynamically
node_positions = {
    'feed': (0.22, 0.65),
    'search': (0.78, 0.65),
    'group': (0.78, 0.28),
    'reels': (0.22, 0.28)
}

color_map = {
    'search': '#f59e0b',
    'reels': '#ec4899',
    'group': '#10b981',
    'feed': '#3b82f6'
}

dynamic_transitions = []
for src in macro_surfaces:
    for dst in macro_surfaces:
        if src == dst:
            continue
        cnt = ct_counts.loc[src, dst]
        if cnt > 0:
            prob = prob_matrix.loc[src, dst]
            dynamic_transitions.append({
                'src': src,
                'dst': dst,
                'count': int(cnt),
                'prob': prob,
                'label': f"{int(cnt)} lần\n({prob:.1%})",
                'color': color_map.get(dst, '#4b5563')
            })

print("\nDynamic transitions count:", len(dynamic_transitions))
for t in dynamic_transitions:
    print(t)
