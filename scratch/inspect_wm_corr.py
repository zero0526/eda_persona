import sys, os
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')
import json
from pathlib import Path
import pandas as pd
import numpy as np
from loaders.action_loader import ActionLoader

loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)

curiosity_scale = {'Rất thấp': 1, 'Thấp': 2, 'Trung bình': 3, 'Cao': 4, 'Rất cao': 5}
persona_curiosity_map = {}
jsonl_path = 'data/selected_6_facebook_personas_description.jsonl'
with open(jsonl_path, 'r', encoding='utf-8') as f:
    for line in f:
        p = json.loads(line)
        pid = p['persona_id']
        c_text = p['attributes'].get('Mức độ muốn khám phá, đặt câu hỏi và tìm hiểu những điều mới.', 'Trung bình')
        persona_curiosity_map[pid] = {
            'curiosity_text': c_text,
            'curiosity_score': curiosity_scale.get(c_text, 3)
        }

wm_records = []
for pid, h in histories.items():
    c_info = persona_curiosity_map.get(pid, {'curiosity_text': 'Trung bình', 'curiosity_score': 3})
    for s in h.sessions:
        wm = s.working_memory
        if wm:
            s_actions = df_actions[df_actions['session_id'] == s.session_id]
            total_act = len(s_actions)
            curiosity_count = len(s_actions[s_actions['primary_dimension'] == 'curiosity'])
            curiosity_ratio = curiosity_count / total_act if total_act > 0 else 0.0
            
            wm_records.append({
                'persona_id': pid,
                'session_id': s.session_id[:8],
                'curiosity_score': c_info['curiosity_score'],
                'curiosity_actions': curiosity_count,
                'curiosity_ratio': curiosity_ratio,
                'situational_steps': wm.novelty.situational_steps if wm.novelty else 0,
                'active_threads': len(wm.active_threads) if wm.active_threads else 0,
                'read_posts': len(wm.read_posts) if wm.read_posts else 0,
                'memory_deltas': len(wm.memory_deltas) if wm.memory_deltas else 0,
                'total_actions': total_act
            })

df_wm = pd.DataFrame(wm_records)
print("df_wm rows:", len(df_wm))
print(df_wm.head(10))

corr_cols = [
    'situational_steps', 'curiosity_actions',  
    'curiosity_score', 'read_posts', 'active_threads', 'memory_deltas', 'total_actions'
]
corr_matrix = df_wm[corr_cols].corr().round(3)
print("\n=== CORRELATION MATRIX ===")
print(corr_matrix)

from scipy import stats
r_val, p_val = stats.pearsonr(df_wm['read_posts'], df_wm['situational_steps'])
print(f"\nPearson correlation read_posts vs situational_steps: r = {r_val:.3f}, p = {p_val:.4f}")

# Also check correlation between curiosity_actions vs active_threads or memory_deltas
for c1 in corr_cols:
    for c2 in corr_cols:
        if c1 < c2:
            r, p = stats.pearsonr(df_wm[c1], df_wm[c2])
            if abs(r) >= 0.4:
                print(f"Strong/Moderate correlation: {c1} vs {c2}: r = {r:.3f}, p = {p:.4f}")
