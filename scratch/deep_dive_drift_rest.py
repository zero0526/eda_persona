import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from loaders.loaders.persona_action import PersonaActionLoader
loader = PersonaActionLoader()
df_steps = loader.load_step_records()
df_ep = loader.load_action_logs()

print("=" * 80)
print("1. NO-PERSONA EPISODES: PROGRESSION OF SITUATIONAL STEPS & WARNINGS")
print("=" * 80)
no_p_eps = df_ep[df_ep['dataset_type'] == 'no_persona']['episode_id'].tolist()
for ep_id in no_p_eps:
    sub = df_steps[df_steps['episode_id'] == ep_id].sort_values('step_index')
    print(f"\nEpisode {ep_id} (Total steps: {len(sub)}):")
    warn_count = sub['wm_has_novelty_warning'].sum()
    print(f"  Total warning steps: {warn_count} ({warn_count/len(sub)*100:.1f}%)")
    print(f"  Distribution of wm_situational_steps: {sub['wm_situational_steps'].value_counts().sort_index().to_dict()}")
    
    # Print the sequence
    print("  Step-by-step trace of situational steps & warnings:")
    for _, row in sub.iterrows():
        s_idx = row['step_index']
        sit = row['wm_situational_steps']
        w = row['wm_has_novelty_warning']
        intent = row['intent']
        surf = row['surface']
        if sit > 0 or w:
            print(f"    Step {s_idx:02d} | sit_steps: {sit} | warning: {str(w):5s} | intent: {str(intent):15s} | surf: {str(surf)}")

print("\n" + "=" * 80)
print("2. REST ANALYSIS: EPISODES & STEPS WITH REST")
print("=" * 80)
rest_steps = df_steps[df_steps['context_rest_count'] > 0]
print(f"Total steps with rest > 0: {len(rest_steps)}")
print(rest_steps[['episode_id', 'dataset_type', 'step_index', 'context_elapsed_seconds', 'context_rest_accumulated_seconds', 'context_rest_count', 'context_action_velocity', 'verified']].to_string())
