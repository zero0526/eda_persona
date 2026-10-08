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

curiosity_data = {}
attention_data = {}
for pid, p in profiles.items():
    attrs = p.get('attributes', {})
    curiosity_data[pid] = attrs.get('Mức độ muốn khám phá, đặt câu hỏi và tìm hiểu những điều mới.', 'N/A')
    attention_data[pid] = attrs.get('Khả năng duy trì sự tập trung vào một việc.', 'N/A')

session_drift = []
for pid, h in histories.items():
    for s in h.sessions:
        wm = s.working_memory
        s_actions = df_actions[df_actions['session_id'] == s.session_id]
        total_act = len(s_actions)
        sit_steps = wm.novelty.situational_steps if (wm and wm.novelty) else 0
        drift_pct = (sit_steps / total_act * 100) if total_act > 0 else 0.0
        read_posts = len(wm.recent_read_post_ids) if (wm and hasattr(wm, 'recent_read_post_ids')) else 0
        active_threads = len(wm.active_thread_ids) if (wm and hasattr(wm, 'active_thread_ids')) else 0
        
        session_drift.append({
            'persona_id': pid,
            'session_id': s.session_id[:8],
            'total_actions': total_act,
            'situational_steps': sit_steps,
            'drift_pct': drift_pct,
            'read_posts': read_posts,
            'active_threads': active_threads
        })

df_drift = pd.DataFrame(session_drift)
drift_summary = df_drift.groupby('persona_id').agg(
    n_sessions=('session_id', 'count'),
    mean_total_act=('total_actions', 'mean'),
    mean_sit_steps=('situational_steps', 'mean'),
    median_sit_steps=('situational_steps', 'median'),
    mean_drift_pct=('drift_pct', 'mean'),
    median_drift_pct=('drift_pct', 'median'),
    mean_read_posts=('read_posts', 'mean'),
    mean_active_threads=('active_threads', 'mean')
).round(2).reset_index()

drift_summary['Mức độ tò mò'] = drift_summary['persona_id'].map(curiosity_data)
drift_summary['Tập trung'] = drift_summary['persona_id'].map(attention_data)

scale = {'Rất cao': 5, 'Cao': 4, 'Trung bình': 3, 'Thấp': 2, 'Rất thấp': 1}
drift_summary['curiosity_score'] = drift_summary['Mức độ tò mò'].map(scale)

print("=== BẢNG TỔNG HỢP MỨC ĐỘ TÒ MÒ VÀ SA ĐÀ / SAO NHÃNG ===")
print(drift_summary.sort_values(by='curiosity_score', ascending=False).to_string())

corr_sit = drift_summary['mean_sit_steps'].corr(drift_summary['curiosity_score'])
corr_pct = drift_summary['mean_drift_pct'].corr(drift_summary['curiosity_score'])
corr_posts = drift_summary['mean_read_posts'].corr(drift_summary['curiosity_score'])
corr_threads = drift_summary['mean_active_threads'].corr(drift_summary['curiosity_score'])

print(f"\nTương quan Mức độ tò mò vs Số bước sao nhãng (mean_sit_steps): {corr_sit:.3f}")
print(f"Tương quan Mức độ tò mò vs Tỷ lệ sao nhãng (mean_drift_pct): {corr_pct:.3f}")
print(f"Tương quan Mức độ tò mò vs Số bài đã đọc (mean_read_posts): {corr_posts:.3f}")
print(f"Tương quan Mức độ tò mò vs Số luồng quan tâm hoạt động (mean_active_threads): {corr_threads:.3f}")

# Xem chi tiết từng hành vi sa đà (interest_relation = 'situational' hay 'none')
print("\n=== PHÂN BỐ SURFACE CỦA TỪNG PERSONA KHI SA ĐÀ ===")
df_actions_sit = df_actions[df_actions['interest_relation'] == 'situational']
print(pd.crosstab(df_actions_sit['persona_id'], df_actions_sit['surface'], margins=True))

print("\n=== PHÂN BỐ INTENT CỦA TỪNG PERSONA KHI SA ĐÀ ===")
print(pd.crosstab(df_actions_sit['persona_id'], df_actions_sit['intent'], margins=True))
