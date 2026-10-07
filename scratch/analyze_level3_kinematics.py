import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from loaders.action_loader import ActionLoader
loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)

df_gest = df_actions[df_actions['gesture_total_px'].notnull()].copy()
df_gest['scroll_speed_px_s'] = (df_gest['gesture_total_px'] / (df_gest['gesture_ms'] / 1000)).replace([np.inf, -np.inf], np.nan)
df_gest['session_label'] = df_gest['persona_id'] + '_s' + df_gest['session_order'].astype(str)

print("=== CẤP ĐỘ 3: CƠ HỌC VẬT LÝ CUỘN CHUỘT (KINEMATICS) ===")
# Kinematic profile by persona and session
p_gest = df_gest.groupby(['persona_id', 'session_order']).agg(
    count=('gesture_total_px', 'count'),
    mean_speed=('scroll_speed_px_s', 'mean'),
    median_speed=('scroll_speed_px_s', 'median'),
    std_speed=('scroll_speed_px_s', 'std'),
    mean_px=('gesture_total_px', 'mean'),
    mean_ms=('gesture_ms', 'mean')
).reset_index()

print(p_gest.to_string())

# Kinematic rank correlation across sessions
print("\n=== KINEMATIC STABILITY (Rank & Speed Consistency) ===")
personas_with_mult_sess = p_gest['persona_id'].value_counts()
personas_with_mult_sess = personas_with_mult_sess[personas_with_mult_sess >= 2].index.tolist()

speed_s1 = []
speed_s2 = []
for p in sorted(personas_with_mult_sess):
    sub = p_gest[p_gest['persona_id'] == p]
    s1_val = sub[sub['session_order'] == 1]['mean_speed'].values
    s2_val = sub[sub['session_order'] == 2]['mean_speed'].values
    if len(s1_val) > 0 and len(s2_val) > 0:
        speed_s1.append(s1_val[0])
        speed_s2.append(s2_val[0])
        print(f"Persona {p}: S1 mean speed = {s1_val[0]:.1f} px/s, S2 mean speed = {s2_val[0]:.1f} px/s | Diff = {abs(s1_val[0]-s2_val[0]):.1f}")

r_speed, p_speed = pearsonr(speed_s1, speed_s2)
rho_speed, prho_speed = spearmanr(speed_s1, speed_s2)
print(f"\nTương quan tốc độ cuộn chuột liên phiên (S1 vs S2 across personas):")
print(f"  Pearson r = {r_speed:.4f} (p = {p_speed:.4f})")
print(f"  Spearman rho = {rho_speed:.4f} (p = {prho_speed:.4f})")

# Pacing distribution consistency
pacing_dist = df_actions.groupby(['session_label'])['gesture_pace'].value_counts(normalize=True).unstack(fill_value=0)
print("\nPacing distribution by session:")
print(pacing_dist.round(3))
