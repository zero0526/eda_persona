import sys
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from loaders.loaders.persona_action import PersonaActionLoader
loader = PersonaActionLoader()
df_steps = loader.load_step_records()
df_ep = loader.load_action_logs()

print("=" * 80)
print("TESTING PART 1: SITUATIONAL STEPS & TEMPORAL DRIFT")
print("=" * 80)

# 1. Onset of drift
for ep_id, ep_df in df_steps.groupby('episode_id'):
    dtype = ep_df['dataset_type'].iloc[0]
    drift_steps = ep_df[ep_df['wm_situational_steps'] > 0]
    if len(drift_steps) > 0:
        first_step = drift_steps['step_index'].min()
        max_drift = ep_df['wm_situational_steps'].max()
        print(f"[{dtype.upper()}] Episode {ep_id[:8]}: Onset at step {first_step}, Max drift = {max_drift}")
    else:
        print(f"[{dtype.upper()}] Episode {ep_id[:8]}: NO DRIFT (All {len(ep_df)} steps = 0)")

# 2. Correlation between step_index and wm_situational_steps
no_p_steps = df_steps[df_steps['dataset_type'] == 'no_persona']
p_steps = df_steps[df_steps['dataset_type'] == 'persona']

spearman_no_p = stats.spearmanr(no_p_steps['step_index'], no_p_steps['wm_situational_steps'])
print(f"\nNo-Persona Spearman (step_index vs wm_situational_steps): rho = {spearman_no_p.statistic:.4f}, p = {spearman_no_p.pvalue:.4e}")

slope, intercept, r_value, p_value, std_err = stats.linregress(no_p_steps['step_index'], no_p_steps['wm_situational_steps'])
print(f"No-Persona OLS: slope = {slope:.4f} steps/step, R^2 = {r_value**2:.4f}, p = {p_value:.4e}")

# Early vs Late within No-Persona (split at median step_index = 22.5)
early_no_p = no_p_steps[no_p_steps['step_index'] <= 22]['wm_situational_steps']
late_no_p = no_p_steps[no_p_steps['step_index'] > 22]['wm_situational_steps']
u_stat, p_early_late = stats.mannwhitneyu(early_no_p, late_no_p, alternative='less')
n1, n2 = len(early_no_p), len(late_no_p)
delta_early_late = (2.0 * u_stat) / (n1 * n2) - 1.0
print(f"No-Persona Early (N={n1}, Mean={early_no_p.mean():.2f}) vs Late (N={n2}, Mean={late_no_p.mean():.2f}):")
print(f"  Mann-Whitney U = {u_stat}, p = {p_early_late:.4e}, Cliff's Delta = {delta_early_late:.4f}")

# 3. Guardrail Warning & Recovery
print("\n--- Guardrail Warning & Recovery in No-Persona ---")
warn_ep = df_steps[df_steps['episode_id'] == '755b1653-927c-48f3-baf4-259c8d9091d8'].sort_values('step_index')
warning_steps = warn_ep[warn_ep['wm_has_novelty_warning'] == True]
print(f"Total warning steps: {len(warning_steps)} / {len(warn_ep)}")

# Check transition delta from t to t+1
warn_ep['drift_diff_next'] = warn_ep['wm_situational_steps'].shift(-1) - warn_ep['wm_situational_steps']
warn_ep['next_recovered'] = warn_ep['drift_diff_next'] < 0

table_rec = pd.crosstab(warn_ep['wm_has_novelty_warning'], warn_ep['next_recovered'])
print("Crosstab warning vs next_step_recovered:")
print(table_rec)

print("\n" + "=" * 80)
print("TESTING PART 2: REST DYNAMICS")
print("=" * 80)

# 1. Episode level Fisher exact test
# Persona: 1 with rest, 5 without
# No-Persona: 1 with rest, 1 without
odds_ratio, p_fish = stats.fisher_exact([[1, 5], [1, 1]])
print(f"Episode-level Rest incidence Fisher's Exact Test: odds_ratio = {odds_ratio:.4f}, p = {p_fish:.4f}")

# 2. Persona Episode 2cbcde75: Pre-rest vs Post-rest
p_ep_rest = df_steps[df_steps['episode_id'] == '2cbcde75-15d8-4223-a1a3-22c69aca9b6d'].sort_values('step_index')
rest_start_step = p_ep_rest[p_ep_rest['context_rest_count'] > 0]['step_index'].min()
print(f"Persona rest starts at step_index = {rest_start_step}")

pre_rest = p_ep_rest[p_ep_rest['step_index'] < rest_start_step]
post_rest = p_ep_rest[p_ep_rest['step_index'] >= rest_start_step]

print(f"Pre-rest N = {len(pre_rest)}, Post-rest N = {len(post_rest)}")

# Velocity comparison
u_vel, p_vel = stats.mannwhitneyu(pre_rest['context_action_velocity'].dropna(), post_rest['context_action_velocity'].dropna())
print(f"Action Velocity: Pre mean = {pre_rest['context_action_velocity'].mean():.2f} (std={pre_rest['context_action_velocity'].std():.2f}) | Post mean = {post_rest['context_action_velocity'].mean():.2f} (std={post_rest['context_action_velocity'].std():.2f})")
print(f"  Mann-Whitney U = {u_vel}, p = {p_vel:.4e}")

# Verified rate comparison
table_ver = pd.crosstab(p_ep_rest['step_index'] >= rest_start_step, p_ep_rest['verified'])
table_ver.index = ['Pre-Rest', 'Post-Rest']
print("Verified rate Pre vs Post:")
print(table_ver)
odds_ver, p_ver = stats.fisher_exact(table_ver)
pre_ver_pct = pre_rest['verified'].mean() * 100
post_ver_pct = post_rest['verified'].mean() * 100
print(f"Pre-rest verified = {pre_ver_pct:.1f}%, Post-rest verified = {post_ver_pct:.1f}%, Fisher's p = {p_ver:.4f}")

# Model latency comparison
u_lat, p_lat = stats.mannwhitneyu(pre_rest['model_latency_ms'].dropna(), post_rest['model_latency_ms'].dropna())
print(f"Model latency: Pre mean = {pre_rest['model_latency_ms'].mean():.1f} ms | Post mean = {post_rest['model_latency_ms'].mean():.1f} ms")
print(f"  Mann-Whitney U = {u_lat}, p = {p_lat:.4e}")
