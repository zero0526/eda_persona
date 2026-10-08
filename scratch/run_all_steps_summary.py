import sys, os
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
CURRENT_DIR = Path.cwd()
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

import numpy as np
import pandas as pd
from scipy import stats
from loaders.action_loader import ActionLoader

loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)
df_sessions = loader.to_unified_sessions_dataframe(histories)
df_memory = loader.to_unified_memory_evolution_dataframe(histories)
df_windows = loader.load_activity_windows()

print("="*60)
print(f"TOTAL ACTIONS: {len(df_actions)}")
print(f"TOTAL SESSIONS: {len(df_sessions)}")
print(f"TOTAL WINDOWS: {len(df_windows)}")
print("="*60)

# STEP 6: TEMPORAL (CELL 9)
df_obs, df_exp, df_adj_res, test_stats = loader.get_temporal_contingency_and_residuals(df_windows)
df_pct = (df_obs.div(df_obs.sum(axis=1), axis=0) * 100).round(1)
df_pct["Tổng Windows"] = df_obs.sum(axis=1)

print("\n--- STEP 6: TEMPORAL DISTRIBUTION (CELL 9) ---")
print(test_stats)
print("\nObserved counts:")
print(df_obs)
print("\nPercentages:")
print(df_pct)
print("\nAdjusted residuals:")
print(df_adj_res.round(2))

# STEP 7: MACRO SESSIONS (CELL 12)
df_sessions_stop = df_sessions.copy()
df_sessions_stop['duration_min'] = df_sessions_stop['duration_seconds'] / 60.0
sess_macro_stats = df_sessions_stop.groupby('persona_id').agg(
    n_valid_sessions=('session_id', 'count'),
    mean_duration_min=('duration_min', 'mean'),
    mean_actions=('total_actions', 'mean'),
    median_scroll_px=('total_scroll_px', 'median'),
    mean_verified_rate=('verified_rate', lambda x: x.mean() * 100)
).reset_index()
print("\n--- STEP 7: SESSIONS MACRO (CELL 12) ---")
print(sess_macro_stats.to_string())

# STEP 8: SURFACE & INTENT (CELL 14)
ct_surface_pct = (
    pd.crosstab(df_actions['surface'], df_actions['persona_id'], normalize='columns') * 100
).round(2).drop(index='unknown', errors='ignore')
df_actions['is_aer'] = df_actions['intent'].isin(['react', 'comment', 'share'])
aer_df = (df_actions.groupby('persona_id')['is_aer'].mean() * 100).round(2).reset_index()

print("\n--- STEP 8: SURFACE & AER (CELL 14) ---")
print("Surface distribution (%):")
print(ct_surface_pct)
print("\nAER (%):")
print(aer_df.to_string())

# STEP 9: KINEMATICS (CELL 16)
df_gestures = df_actions[df_actions['gesture_total_px'].notnull()].copy()
df_gestures['scroll_speed_px_s'] = (
    df_gestures['gesture_total_px'] / (df_gestures['gesture_ms'] / 1000.0)
).astype(float).round(2)
kin_stats = df_gestures.groupby('persona_id').agg(
    n_gestures=('step_index', 'count'),
    pct_fast=('gesture_pace', lambda x: (x == 'fast').mean() * 100),
    median_scroll_px=('gesture_total_px', 'median'),
    median_gesture_ms=('gesture_ms', 'median'),
    median_speed_px_s=('scroll_speed_px_s', 'median')
).round(2).reset_index()
print("\n--- STEP 9: KINEMATICS (CELL 16) ---")
print(kin_stats.to_string())

# STEP 10: WORKING MEMORY & NOVELTY (CELL 18)
wm_records = []
for p in histories.values():
    for s in p.sessions:
        wm = s.working_memory
        if wm:
            curiosity_count = sum(1 for a in s.actions if a.intent in ['search', 'search_related'])
            wm_records.append({
                'persona_id': p.persona_id,
                'session_id': s.session_id,
                'situational_steps': wm.novelty.situational_steps if wm.novelty else 0,
                'active_threads': len(wm.active_threads) if wm.active_threads else 0,
                'read_posts': len(wm.read_posts) if wm.read_posts else 0,
                'memory_deltas': len(wm.memory_deltas) if wm.memory_deltas else 0,
                'curiosity_actions': curiosity_count
            })
df_wm = pd.DataFrame(wm_records)
wm_stats = df_wm.groupby('persona_id').agg({
    'active_threads': 'mean',
    'read_posts': 'mean',
    'situational_steps': 'mean',
    'curiosity_actions': 'mean',
    'memory_deltas': 'mean'
}).round(2).reset_index()
print("\n--- STEP 10: WORKING MEMORY (CELL 18) ---")
print(wm_stats.to_string())

