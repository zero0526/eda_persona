import sys, os
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np
from loaders.action_loader import ActionLoader
import json

loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)
profiles, contracts = loader.load_persona_profiles_and_contracts()

# 1. Trích xuất attention_span từ profiles
attention_data = {}
for pid, p in profiles.items():
    attrs = p.get('attributes', {})
    # Tìm các trường liên quan đến attention
    att_key = None
    for k in attrs.keys():
        if 'chú ý' in k.lower() or 'attention' in k.lower() or 'tập trung' in k.lower():
            att_key = k
            break
    att_val = attrs.get(att_key) if att_key else None
    attention_data[pid] = {
        'attention_raw': att_val,
        'attention_key': att_key
    }

print("=== ATTENTION SPAN IN PROFILES ===")
for pid, d in sorted(attention_data.items()):
    print(f"{pid}: {d['attention_raw']} (Field: {d['attention_key']})")

# 2. Tính % bước sao nhãng theo từng phiên
session_drift = []
for pid, h in histories.items():
    for s in h.sessions:
        wm = s.working_memory
        s_actions = df_actions[df_actions['session_id'] == s.session_id]
        total_act = len(s_actions)
        sit_steps = wm.novelty.situational_steps if (wm and wm.novelty) else 0
        drift_pct = (sit_steps / total_act * 100) if total_act > 0 else 0.0
        
        session_drift.append({
            'persona_id': pid,
            'session_id': s.session_id[:8],
            'total_actions': total_act,
            'situational_steps': sit_steps,
            'drift_pct': drift_pct
        })

df_drift = pd.DataFrame(session_drift)
print("\n=== SAMPLE SESSION DRIFT ===")
print(df_drift.head(10))

# 3. Kết tập trung bình theo Persona
drift_summary = df_drift.groupby('persona_id').agg(
    n_sessions=('session_id', 'count'),
    mean_total_act=('total_actions', 'mean'),
    mean_sit_steps=('situational_steps', 'mean'),
    mean_drift_pct=('drift_pct', 'mean'),
    median_drift_pct=('drift_pct', 'median')
).round(2).reset_index()

drift_summary['attention_span'] = drift_summary['persona_id'].map(lambda p: attention_data[p]['attention_raw'])

# Sắp xếp theo mean_drift_pct
drift_summary = drift_summary.sort_values(by='mean_drift_pct', ascending=False)
print("\n=== DRIFT SUMMARY BY PERSONA ===")
print(drift_summary.to_string())

# 4. Ánh xạ attention_span sang thang đo số học để xem tương quan
# 'Tập trung sâu và lâu dài': 3, 'Tập trung tốt': 2.5, 'Trung bình': 2, 'Ngắn': 1
att_scale = {
    'Tập trung sâu và lâu dài': 3,
    'Tập trung tốt': 2.5,
    'Trung bình': 2,
    'Ngắn': 1,
    'Dễ phân tâm': 1
}
drift_summary['attention_score'] = drift_summary['attention_span'].map(att_scale)
print("\n=== CORRELATION CHECK ===")
corr_pearson = drift_summary['mean_drift_pct'].corr(drift_summary['attention_score'])
print(f"Correlation between attention_score and mean_drift_pct: {corr_pearson:.3f}")
