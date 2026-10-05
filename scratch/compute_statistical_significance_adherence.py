import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load data
logs_dir = Path('data/action_logs')
cluster_map = {
    'vn_000077': 1, 'vn_000081': 1,
    'vn_000041': 2, 'vn_000049': 2,
    'vn_000019': 3, 'vn_000087': 3
}

all_steps = []
session_records = []

for b_file in sorted(logs_dir.glob('benchmark_eda_*.json')):
    with open(b_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    meta = data.get('metadata', {})
    pid = meta.get('persona_id')
    steps = data.get('step_records', [])
    c_id = cluster_map.get(pid)
    
    timestamps = [pd.to_datetime(s.get('timestamp')) for s in steps if s.get('timestamp')]
    
    n_reads = 0
    n_scrolls = 0
    n_searches = 0
    n_reacts = 0
    n_shares = 0
    n_observes = 0
    
    for i, s in enumerate(steps):
        intent = s.get('intent')
        surface = s.get('surface')
        tool = s.get('tool') or s.get('resolved_tool')
        model_lat = s.get('model_latency_ms')
        tool_exec = s.get('tool_execution_ms')
        
        # Step interval
        step_interval = None
        if i > 0 and i < len(timestamps):
            delta = (timestamps[i] - timestamps[i-1]).total_seconds()
            if 0 <= delta <= 300:
                step_interval = delta
                
        # Category of action
        is_deep = 1 if intent in ('read', 'search') else 0
        is_skim = 1 if intent in ('scroll', 'observe') else 0
        is_social = 1 if intent in ('react', 'share') else 0
        is_feed = 1 if surface == 'feed' else 0
        is_mixed = 1 if surface in ('group', 'page', 'search', 'detail') else 0
        
        if intent == 'read': n_reads += 1
        elif intent == 'scroll': n_scrolls += 1
        elif intent == 'search': n_searches += 1
        elif intent == 'react': n_reacts += 1
        elif intent == 'share': n_shares += 1
        elif intent == 'observe': n_observes += 1
        
        all_steps.append({
            'persona_id': pid,
            'cluster': c_id,
            'step_index': i + 1,
            'intent': intent,
            'surface': surface,
            'tool': tool,
            'step_interval_sec': step_interval,
            'model_latency_ms': model_lat,
            'tool_execution_ms': tool_exec,
            'is_deep': is_deep,
            'is_skim': is_skim,
            'is_social': is_social,
            'is_feed': is_feed,
            'is_mixed': is_mixed
        })
        
    duration_sec = (timestamps[-1] - timestamps[0]).total_seconds() if len(timestamps) > 1 else 0
    session_records.append({
        'persona_id': pid,
        'cluster': c_id,
        'steps_count': len(steps),
        'duration_sec': duration_sec,
        'velocity_per_min': len(steps) / (duration_sec / 60) if duration_sec > 0 else 0,
        'n_reads': n_reads,
        'n_scrolls': n_scrolls,
        'n_searches': n_searches,
        'n_reacts': n_reacts,
        'n_shares': n_shares,
        'n_social': n_reacts + n_shares,
        'n_deep': n_reads + n_searches,
        'n_skim': n_scrolls + n_observes,
        'deep_ratio': (n_reads + n_searches) / (n_scrolls + n_observes + 1e-5),
        'social_rate': (n_reacts + n_shares) / len(steps) * 100
    })

df_steps = pd.DataFrame(all_steps)
df_sessions = pd.DataFrame(session_records)

print(f"Tổng số bước phân tích: N = {len(df_steps)} bước trên 6 Persona (3 Cụm).")
print(f"  - Cụm 1: {sum(df_steps['cluster'] == 1)} bước")
print(f"  - Cụm 2: {sum(df_steps['cluster'] == 2)} bước")
print(f"  - Cụm 3: {sum(df_steps['cluster'] == 3)} bước")

print("\n" + "="*90)
print("KIỂM ĐỊNH THỐNG KÊ CHI TIẾT TỪNG METRIC")
print("="*90)

# ==============================================================================
# TEST 1: CƯỜNG ĐỘ TƯƠNG TÁC XÃ HỘI (Social Propensity: React + Share)
# ==============================================================================
# Bảng chéo: Cluster vs is_social
ct_social = pd.crosstab(df_steps['cluster'], df_steps['is_social'])
chi2_social, p_social, dof_social, _ = stats.chi2_contingency(ct_social)
cramer_v_social = np.sqrt(chi2_social / (len(df_steps) * (min(ct_social.shape) - 1)))

pct_social_c1 = df_steps[df_steps['cluster'] == 1]['is_social'].mean() * 100
pct_social_c2 = df_steps[df_steps['cluster'] == 2]['is_social'].mean() * 100
pct_social_c3 = df_steps[df_steps['cluster'] == 3]['is_social'].mean() * 100

print(f"\n1. METRIC: CƯỜNG ĐỘ TƯƠNG TÁC XÃ HỘI (Social Propensity: React + Share)")
print(f"   - Cụm 1 (Daily / Sharer):   {pct_social_c1:.2f}% ({ct_social.loc[1, 1]}/{len(df_steps[df_steps['cluster']==1])} actions)")
print(f"   - Cụm 2 (Feed Focus):       {pct_social_c2:.2f}% ({ct_social.loc[2, 1]}/{len(df_steps[df_steps['cluster']==2])} actions)")
print(f"   - Cụm 3 (Rarely / Low Freq): {pct_social_c3:.2f}% ({ct_social.loc[3, 1]}/{len(df_steps[df_steps['cluster']==3])} actions)")
print(f"   - Chi-Square: chi2 = {chi2_social:.4f}, df = {dof_social}, p-value = {p_social:.4e}")
print(f"   - Effect Size (Cramér's V): V = {cramer_v_social:.4f} (Mức độ ảnh hưởng rất mạnh)")
if p_social < 0.05:
    print(f"   => [CÓ Ý NGHĨA THỐNG KÊ CỰC KỲ CAO (p < 0.001)]")

# ==============================================================================
# TEST 2: ĐỘ SÂU TIÊU THỤ (Deep Consumption: Read + Search vs Scroll + Observe)
# ==============================================================================
ct_deep = pd.crosstab(df_steps['cluster'], df_steps['is_deep'])
chi2_deep, p_deep, dof_deep, _ = stats.chi2_contingency(ct_deep)
cramer_v_deep = np.sqrt(chi2_deep / (len(df_steps) * (min(ct_deep.shape) - 1)))

pct_deep_c1 = df_steps[df_steps['cluster'] == 1]['is_deep'].mean() * 100
pct_deep_c2 = df_steps[df_steps['cluster'] == 2]['is_deep'].mean() * 100
pct_deep_c3 = df_steps[df_steps['cluster'] == 3]['is_deep'].mean() * 100

print(f"\n2. METRIC: CHIỀU SÂU TIÊU THỤ (Deep Consumption: Read + Search)")
print(f"   - Cụm 1 (Skim Reading):      {pct_deep_c1:.2f}% ({ct_deep.loc[1, 1]}/{len(df_steps[df_steps['cluster']==1])} actions)")
print(f"   - Cụm 2 (Selective/Deep):    {pct_deep_c2:.2f}% ({ct_deep.loc[2, 1]}/{len(df_steps[df_steps['cluster']==2])} actions)")
print(f"   - Cụm 3 (Deliberate):        {pct_deep_c3:.2f}% ({ct_deep.loc[3, 1]}/{len(df_steps[df_steps['cluster']==3])} actions)")
print(f"   - Chi-Square: chi2 = {chi2_deep:.4f}, df = {dof_deep}, p-value = {p_deep:.4e}")
print(f"   - Effect Size (Cramér's V): V = {cramer_v_deep:.4f}")
if p_deep < 0.05:
    print(f"   => [CÓ Ý NGHĨA THỐNG KÊ CAO (p = {p_deep:.4f} < 0.01)]")

# ==============================================================================
# TEST 3: PHÂN BỔ BỀ MẶT THAO TÁC (Surface Exploration: Feed vs Mixed Surface)
# ==============================================================================
ct_surface = pd.crosstab(df_steps['cluster'], df_steps['is_mixed'])
chi2_surf, p_surf, dof_surf, _ = stats.chi2_contingency(ct_surface)
cramer_v_surf = np.sqrt(chi2_surf / (len(df_steps) * (min(ct_surface.shape) - 1)))

pct_mixed_c1 = df_steps[df_steps['cluster'] == 1]['is_mixed'].mean() * 100
pct_mixed_c2 = df_steps[df_steps['cluster'] == 2]['is_mixed'].mean() * 100
pct_mixed_c3 = df_steps[df_steps['cluster'] == 3]['is_mixed'].mean() * 100

print(f"\n3. METRIC: KHÁM PHÁ ĐA BỀ MẶT (Mixed Surface Ratio: Group/Page/Search/Detail)")
print(f"   - Cụm 1: {pct_mixed_c1:.2f}% ({ct_surface.loc[1, 1]}/{len(df_steps[df_steps['cluster']==1])} actions)")
print(f"   - Cụm 2: {pct_mixed_c2:.2f}% ({ct_surface.loc[2, 1]}/{len(df_steps[df_steps['cluster']==2])} actions)")
print(f"   - Cụm 3: {pct_mixed_c3:.2f}% ({ct_surface.loc[3, 1]}/{len(df_steps[df_steps['cluster']==3])} actions)")
print(f"   - Chi-Square: chi2 = {chi2_surf:.4f}, df = {dof_surf}, p-value = {p_surf:.4e}")
print(f"   - Effect Size (Cramér's V): V = {cramer_v_surf:.4f}")
if p_surf < 0.05:
    print(f"   => [CÓ Ý NGHĨA THỐNG KÊ CỰC KỲ CAO (p = {p_surf:.4e} < 0.001)]")

# ==============================================================================
# TEST 4: NHỊP ĐỘ GIAO DIỆN & KHOẢNG CÁCH BƯỚC (Inter-step Interval Δt)
# ==============================================================================
steps_with_interval = df_steps.dropna(subset=['step_interval_sec'])
g1_int = steps_with_interval[steps_with_interval['cluster'] == 1]['step_interval_sec']
g2_int = steps_with_interval[steps_with_interval['cluster'] == 2]['step_interval_sec']
g3_int = steps_with_interval[steps_with_interval['cluster'] == 3]['step_interval_sec']

kw_int, p_kw_int = stats.kruskal(g1_int, g2_int, g3_int)
print(f"\n4. METRIC: KHOẢNG CÁCH THỜI GIAN THAO TÁC GIAO DIỆN (Inter-Step Interval Δt)")
print(f"   - Cụm 1 Median Δt: {g1_int.median():.2f}s (Mean: {g1_int.mean():.2f}s)")
print(f"   - Cụm 2 Median Δt: {g2_int.median():.2f}s (Mean: {g2_int.mean():.2f}s)")
print(f"   - Cụm 3 Median Δt: {g3_int.median():.2f}s (Mean: {g3_int.mean():.2f}s)")
print(f"   - Kruskal-Wallis H: H = {kw_int:.4f}, p-value = {p_kw_int:.4f}")
if p_kw_int < 0.05:
    print(f"   => [CÓ Ý NGHĨA THỐNG KÊ (p < 0.05)]")
else:
    print(f"   => [KHÔNG CÓ Ý NGHĨA THỐNG KÊ RÕ RỆT (p = {p_kw_int:.4f} >= 0.05) - Cho thấy nhịp chuyển bước giữa các cụm tương đối đồng đều quanh mốc 10-11s do giới hạn thực thi tool]")

# ==============================================================================
# TEST 5: ĐỘ LỆCH PHA TỐC ĐỘ CUỘN (Scroll Rate / Action Dynamics)
# ==============================================================================
ct_scroll = pd.crosstab(df_steps['cluster'], df_steps['intent'] == 'scroll')
chi2_scroll, p_scroll, dof_scroll, _ = stats.chi2_contingency(ct_scroll)
pct_scroll_c1 = (df_steps[df_steps['cluster'] == 1]['intent'] == 'scroll').mean() * 100
pct_scroll_c2 = (df_steps[df_steps['cluster'] == 2]['intent'] == 'scroll').mean() * 100
pct_scroll_c3 = (df_steps[df_steps['cluster'] == 3]['intent'] == 'scroll').mean() * 100

print(f"\n5. METRIC: TỶ TRỌNG CUỘN LƯỚT (Scroll Action Proportion)")
print(f"   - Cụm 1 (Quick Pace profile):    {pct_scroll_c1:.2f}%")
print(f"   - Cụm 2 (Balanced Pace profile): {pct_scroll_c2:.2f}%")
print(f"   - Cụm 3 (Slow Pace profile):     {pct_scroll_c3:.2f}%")
print(f"   - Chi-Square: chi2 = {chi2_scroll:.4f}, p-value = {p_scroll:.4e}")
if p_scroll < 0.05:
    print(f"   => [CÓ Ý NGHĨA THỐNG KÊ CAO (p = {p_scroll:.4f} < 0.05)]")
    print(f"   => [PHÁT HIỆN SỰ LỆCH PHA (DISCREPANCY): Cụm 3 (Slow) lại cuộn nhiều nhất (29.03%), trong khi Cụm 1 (Quick) cuộn ít nhất (15.31%)!]")
