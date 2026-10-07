import sqlite3
import json
import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics.pairwise import cosine_similarity
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from loaders.action_loader import ActionLoader
loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)
df_sessions = loader.to_unified_sessions_dataframe(histories)

df_actions['session_label'] = df_actions['persona_id'] + '_s' + df_actions['session_order'].astype(str)

print("=== CHECKING DATA AVAILABILITY FOR 4 LEVELS ===")

# --- CẤP ĐỘ 1: VĨ MÔ CẤP PHIÊN ---
# Metrics: duration_seconds, total_actions, action_velocity (actions/min)
df_s1 = df_sessions.copy()
df_s1['velocity'] = df_s1['total_actions'] / (df_s1['duration_seconds'] / 60)
print("\n[Cấp độ 1] Sample Session Metrics:")
print(df_s1[['persona_id', 'session_order', 'total_actions', 'duration_seconds', 'velocity']].dropna().head(8))

# --- CẤP ĐỘ 2: BỀ MẶT & Ý ĐỊNH ---
all_intents = sorted(df_actions['intent'].dropna().unique())
all_surfaces = sorted(df_actions['surface'].dropna().unique())
intent_by_sess = df_actions.groupby('session_label')['intent'].value_counts(normalize=True).unstack(fill_value=0).reindex(columns=all_intents, fill_value=0)
surface_by_sess = df_actions.groupby('session_label')['surface'].value_counts(normalize=True).unstack(fill_value=0).reindex(columns=all_surfaces, fill_value=0)
print(f"\n[Cấp độ 2] Intent vector shape: {intent_by_sess.shape}, Surface vector shape: {surface_by_sess.shape}")

# --- CẤP ĐỘ 3: CƠ HỌC VẬT LÝ CUỘN CHUỘT ---
df_gest = df_actions[df_actions['gesture_total_px'].notnull()].copy()
df_gest['scroll_speed_px_s'] = (df_gest['gesture_total_px'] / (df_gest['gesture_ms'] / 1000)).replace([np.inf, -np.inf], np.nan)
gest_metrics = df_gest.groupby('session_label').agg(
    mean_speed=('scroll_speed_px_s', 'mean'),
    median_speed=('scroll_speed_px_s', 'median'),
    mean_px=('gesture_total_px', 'mean'),
    mean_ms=('gesture_ms', 'mean')
).dropna()
print(f"\n[Cấp độ 3] Physical Gesture metrics sessions: {len(gest_metrics)}")
print(gest_metrics.head(8))

# --- CẤP ĐỘ 4: BẢN SẮC & BỘ NHỚ LÀM VIỆC ---
top_dims = df_actions['primary_dimension'].value_counts().head(12).index.tolist()
dim_by_sess = df_actions.groupby('session_label')['primary_dimension'].value_counts(normalize=True).unstack(fill_value=0).reindex(columns=top_dims, fill_value=0)
print(f"\n[Cấp độ 4] Identity Dimensions vector shape: {dim_by_sess.shape}")

# Function to compute intra-persona cross-session correlation vs inter-persona for any feature matrix
def analyze_level_consistency(matrix, name):
    print(f"\n=======================================================")
    print(f"PHÂN TÍCH NHẤT QUÁN {name}")
    print(f"=======================================================")
    corr_mat = matrix.T.corr()
    session_labels = matrix.index.tolist()
    
    intra_corrs = []
    inter_corrs = []
    
    for i, s1 in enumerate(session_labels):
        p1 = s1.split('_s')[0]
        for j, s2 in enumerate(session_labels):
            if i < j:
                p2 = s2.split('_s')[0]
                val = corr_mat.loc[s1, s2]
                if not np.isnan(val):
                    if p1 == p2:
                        intra_corrs.append((s1, s2, val))
                    else:
                        inter_corrs.append((s1, s2, val))
                        
    print(f"--- Tương quan Nội tại (Cùng Persona qua các phiên) ---")
    for s1, s2, v in intra_corrs:
        print(f"  {s1} <-> {s2}: r = {v:.4f}")
        
    intra_vals = [v for _, _, v in intra_corrs]
    inter_vals = [v for _, _, v in inter_corrs]
    
    mean_intra = np.mean(intra_vals) if intra_vals else 0
    std_intra = np.std(intra_vals) if intra_vals else 0
    mean_inter = np.mean(inter_vals) if inter_vals else 0
    std_inter = np.std(inter_vals) if inter_vals else 0
    
    print(f"\n  => Mean Intra Correlation: {mean_intra:.4f} +/- {std_intra:.4f}")
    print(f"  => Mean Inter Correlation: {mean_inter:.4f} +/- {std_inter:.4f}")
    print(f"  => Tỷ lệ vượt trội (Intra / Inter): {mean_intra / (mean_inter if mean_inter != 0 else 1):.2f}x")
    return {'name': name, 'mean_intra': mean_intra, 'mean_inter': mean_inter, 'intra_corrs': intra_corrs}

# Run for Level 2 (Intent & Surface) and Level 4 (Identity Dimensions)
res_intent = analyze_level_consistency(intent_by_sess, "CẤP ĐỘ 2: Ý ĐỊNH VI THAO TÁC (INTENT)")
res_surface = analyze_level_consistency(surface_by_sess, "CẤP ĐỘ 2: PHÂN BỐ BỀ MẶT (SURFACE)")
res_dim = analyze_level_consistency(dim_by_sess, "CẤP ĐỘ 4: ĐỘNG CƠ BẢN SẮC (DIMENSIONS)")
