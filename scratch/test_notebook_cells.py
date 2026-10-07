import os, sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()
import json
import sqlite3
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

from loaders.action_loader import ActionLoader

loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)
df_sessions = loader.to_unified_sessions_dataframe(histories)

print("1. TEST CẤP ĐỘ 1: PHIÊN TỔNG HỢP (LỌC agent_stop)")
df_sessions_stop = df_sessions[df_sessions['terminal_reason'] == 'agent_stop'].copy()
df_sessions_stop['duration_min'] = df_sessions_stop['duration_seconds'] / 60.0

sess_stats = df_sessions_stop.groupby('persona_id').agg(
    n_sessions=('session_id', 'count'),
    mean_duration_min=('duration_min', 'mean'),
    mean_actions=('total_actions', 'mean'),
    median_scroll_px=('total_scroll_px', 'median'),
    mean_verified_rate=('verified_rate', lambda x: x.mean() * 100)
).round(2).reset_index()
print(sess_stats)

print("\n2. TEST CẤP ĐỘ 2: SURFACE & INTENT")
ct_surface = pd.crosstab(df_actions['surface'], df_actions['persona_id'], normalize='columns') * 100
chi2_s, p_s, _, _ = stats.chi2_contingency(pd.crosstab(df_actions['surface'], df_actions['persona_id']))
print(f"Surface Chi2: {chi2_s:.2f}, p: {p_s}")

ct_intent = pd.crosstab(df_actions['intent'], df_actions['persona_id'], normalize='columns') * 100
chi2_i, p_i, _, _ = stats.chi2_contingency(pd.crosstab(df_actions['intent'], df_actions['persona_id']))
print(f"Intent Chi2: {chi2_i:.2f}, p: {p_i}")

# Active Engagement Rate (AER = react + comment + share)
df_actions['is_aer'] = df_actions['intent'].isin(['react', 'comment', 'share'])
aer_stats = df_actions.groupby('persona_id')['is_aer'].mean() * 100
print("AER (%):", aer_stats.round(2).to_dict())

# Search actions
df_search = df_actions[df_actions['intent'].isin(['search', 'search_related'])][['persona_id', 'session_id', 'step_index', 'intent', 'reason']]
print(f"Total search steps: {len(df_search)}")

print("\n3. TEST CẤP ĐỘ 3: CƠ HỌC VẬT LÝ")
df_gestures = df_actions[df_actions['gesture_total_px'].notnull()].copy()
df_gestures['scroll_speed_px_s'] = (df_gestures['gesture_total_px'] / (df_gestures['gesture_ms'] / 1000.0)).round(2)

kin_stats = df_gestures.groupby('persona_id').agg(
    n_gestures=('step_index', 'count'),
    pct_fast=('gesture_pace', lambda x: (x == 'fast').mean() * 100),
    median_scroll_px=('gesture_total_px', 'median'),
    median_gesture_ms=('gesture_ms', 'median'),
    median_speed_px_s=('scroll_speed_px_s', 'median')
).round(2).reset_index()
print(kin_stats)

# Kruskal-Wallis for scroll speed
kw_groups = [group['scroll_speed_px_s'].dropna().values for _, group in df_gestures.groupby('persona_id')]
h_stat, p_kw = stats.kruskal(*kw_groups)
print(f"Kinematics Speed Kruskal-Wallis: H={h_stat:.2f}, p={p_kw}")

print("\n4. TEST CẤP ĐỘ 4 & 5: DIMENSION & WORKING MEMORY")
top_dims = df_actions['primary_dimension'].value_counts().head(10).index
ct_dim = pd.crosstab(df_actions['primary_dimension'], df_actions['persona_id']).loc[top_dims]
print("Top Dimensions Crosstab:")
print(ct_dim)

# SQLite Working Memory extraction
conn = sqlite3.connect('data/persona-runner.sqlite')
wm_df = pd.read_sql_query("""
    SELECT 
        e.bot_id,
        e.id as episode_id,
        wm.snapshot_json
    FROM episodes e
    LEFT JOIN episode_working_memory wm ON e.id = wm.episode_id
    WHERE e.status = 'done' AND e.terminal_reason = 'agent_stop'
""", conn)

# Map bot_id to persona_id
bot_to_pid = {p.persona_id: pid for pid, p in persona_profiles.items()}
print("Loaded done episodes for WM:", len(wm_df))
